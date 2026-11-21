"""Integration tests over actual local HTTPS sockets; no external service required."""
import hashlib
import http.client
import json
from pathlib import Path
import ssl
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import digitalheat as app


class SystemTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.credentials = Path(cls.temp.name) / "credentials"
        app.init_credentials("127.0.0.1", cls.credentials)
        cls.worker = app.make_worker("127.0.0.1", 0, cls.credentials / "worker")
        cls.worker_thread = threading.Thread(target=cls.worker.serve_forever, daemon=True)
        cls.worker_thread.start()
        cls.sender = app.make_sender(0, f"https://127.0.0.1:{cls.worker.server_port}", cls.credentials / "sender")
        cls.sender_thread = threading.Thread(target=cls.sender.serve_forever, daemon=True)
        cls.sender_thread.start()
        cls.host = app.make_host(0, cls.worker.store)
        cls.host_thread = threading.Thread(target=cls.host.serve_forever, daemon=True)
        cls.host_thread.start()
        cls.origin = f"http://127.0.0.1:{cls.sender.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.host.shutdown()
        cls.host.server_close()
        cls.host_thread.join()
        cls.sender.shutdown()
        cls.worker.shutdown()
        cls.sender.server_close()
        cls.worker.server_close()
        cls.worker.store.close()
        cls.sender_thread.join()
        cls.worker_thread.join()
        cls.temp.cleanup()

    def request(self, method, path, data=None, headers=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.sender.server_port, timeout=8)
        merged = {"Origin": self.origin}
        if data is not None:
            merged.update({"Content-Type": "application/json", "X-DigitalHeat-CSRF": self.sender.csrf})
        merged.update(headers or {})
        connection.request(method, path, json.dumps(data) if data is not None else None, merged)
        response = connection.getresponse()
        content = response.read()
        status, content_type = response.status, response.getheader("Content-Type")
        connection.close()
        return status, json.loads(content) if content_type.startswith("application/json") else content

    def wait(self, jid, predicate, timeout=6):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            status, job = self.request("GET", "/api/status")
            self.assertEqual(status, 200)
            job = next((j for j in job["jobs"] if j["id"] == jid), None)
            if job and predicate(job):
                return job
            time.sleep(0.05)
        self.fail("Auftrag hat den erwarteten Zustand nicht erreicht.")

    def test_end_to_end_result_and_deletion(self):
        text = "Forschung Wärme Forschung sicher"
        code, job = self.request("POST", "/api/jobs", {"title": "Test", "text": text, "duration": 2})
        self.assertEqual(code, 202)
        self.assertNotIn("_text", job)
        job = self.wait(job["id"], lambda j: j["state"] == "completed")
        self.assertEqual(job["result"]["sha256"], hashlib.sha256(text.encode()).hexdigest())
        self.assertEqual(job["result"]["words"], 4)
        self.assertEqual(job["result"]["top_words"][0], {"word": "forschung", "count": 2})
        code, result = self.request("POST", f"/api/jobs/{job['id']}/delete", {})
        self.assertEqual((code, result), (200, {"deleted": True}))
        self.assertNotIn(job["id"], self.worker.store.jobs)

    def test_pause_resume_and_cancel(self):
        _, job = self.request("POST", "/api/jobs", {"title": "Pause", "text": "Öffentliche Daten", "duration": 10})
        jid = job["id"]
        self.wait(jid, lambda j: j["progress"] > 0)
        self.assertEqual(self.request("POST", f"/api/jobs/{jid}/pause", {})[0], 200)
        time.sleep(0.08)
        paused = self.worker.store.get(jid)
        time.sleep(0.2)
        self.assertEqual(self.worker.store.get(jid)["active_seconds"], paused["active_seconds"])
        self.assertEqual(self.worker.store.get(jid)["state"], "paused")
        self.assertEqual(self.request("POST", f"/api/jobs/{jid}/resume", {})[0], 200)
        self.wait(jid, lambda j: j["active_seconds"] > paused["active_seconds"])
        self.assertEqual(self.request("POST", f"/api/jobs/{jid}/cancel", {})[0], 200)
        self.assertEqual(self.worker.store.get(jid)["state"], "cancelled")
        self.assertIsNone(self.worker.store.get(jid)["result"])

    def test_worker_requires_token_and_tls(self):
        context = app.tls_context(str(self.credentials / "sender" / "worker-cert.pem"))
        connection = http.client.HTTPSConnection("127.0.0.1", self.worker.server_port, context=context)
        connection.connect()
        self.assertEqual(connection.sock.version(), "TLSv1.3")
        connection.request("GET", "/v1/status")
        response = connection.getresponse()
        self.assertEqual(response.status, 401)
        response.read()
        connection.close()

    def test_untrusted_certificate_rejected(self):
        connection = http.client.HTTPSConnection("127.0.0.1", self.worker.server_port,
                                                 context=ssl.create_default_context(), timeout=3)
        try:
            with self.assertRaises(ssl.SSLCertVerificationError):
                connection.connect()
        finally:
            connection.close()

    def test_foreign_origin_host_and_missing_csrf_rejected(self):
        self.assertEqual(self.request("GET", "/api/status", headers={"Origin": "https://foreign.example"})[0], 403)
        self.assertEqual(self.request("GET", "/api/session", headers={"Host": "foreign.example"})[0], 403)
        self.assertEqual(self.request("POST", "/api/jobs", {}, {"X-DigitalHeat-CSRF": "wrong"})[0], 403)

    def test_validation_and_no_code_upload(self):
        for data in [{"text": ""}, {"text": "a", "duration": True}, {"text": "a", "duration": 1000},
                     {"text": "a" * (app.MAX_TEXT + 1)}, ["no object"], {"script": "print('no')"}]:
            self.assertEqual(self.request("POST", "/api/jobs", data)[0], 400)

    def test_queue_limit_and_expiry(self):
        store = app.Store()
        try:
            for i in range(app.MAX_JOBS):
                store.jobs[str(i)] = {"id": str(i), "state": "completed", "updated_at": time.time()}
            with self.assertRaises(app.APIError) as caught:
                store.submit({"text": "a", "duration": 2})
            self.assertEqual(caught.exception.status, 429)
            for job in store.jobs.values():
                job["updated_at"] = time.time() - app.RETENTION - 1
            self.assertEqual(store.list(), [])
        finally:
            store.close()

    def test_ui_and_errors_do_not_expose_secret(self):
        for file in ("/", "/pharma.js", "/platform.css", "/wallpaper.svg"):
            code, content = self.request("GET", file)
            self.assertEqual(code, 200)
            self.assertNotIn(self.sender.token.encode(), content)
        self.assertEqual(self.request("GET", "/../../digitalheat.py")[0], 404)
        self.assertEqual(self.request("GET", "/api/jobs/anything")[0], 404)


    def host_request(self, method, path, data=None, headers=None):
        c = http.client.HTTPConnection("127.0.0.1", self.host.server_port, timeout=5)
        h = {"Origin": f"http://127.0.0.1:{self.host.server_port}"}
        if data is not None:
            h.update({"Content-Type": "application/json", "X-DigitalHeat-CSRF": self.host.csrf})
        h.update(headers or {})
        c.request(method, path, json.dumps(data) if data is not None else None, h)
        r = c.getresponse()
        raw = r.read()
        result = r.status, json.loads(raw) if r.getheader("Content-Type").startswith("application/json") else raw
        c.close()
        return result

    def test_host_projection_and_role_endpoints(self):
        _, job = self.request("POST", "/api/jobs", {"title": "Private project title", "text": "private research", "duration": 2})
        code, status = self.host_request("GET", "/api/host/status")
        self.assertEqual(code, 200)
        self.assertEqual(set(status), {"heat_enabled", "running", "waiting", "completed", "processing", "connected"})
        self.assertNotIn("Private project", json.dumps(status))
        self.assertEqual(self.host_request("GET", "/api/status")[0], 404)
        self.assertEqual(self.host_request("POST", "/api/jobs", {"text": "x"})[0], 404)
        self.assertEqual(self.request("GET", "/api/host/status")[0], 404)
        self.assertEqual(self.request("POST", "/api/host/heat", {"enabled": False})[0], 404)
        for path in ("/", "/host.js", "/platform.css", "/wallpaper.svg"):
            self.assertEqual(self.host_request("GET", path)[0], 200)
        self.assertEqual(self.host_request("GET", "/pharma.js")[0], 404)
        self.assertEqual(self.request("GET", "/host.js")[0], 404)
        self.request("POST", f"/api/jobs/{job['id']}/cancel", {})

    def test_host_heat_gates_processing(self):
        try:
            self.assertEqual(self.host_request("POST", "/api/host/heat", {"enabled": False})[0], 200)
            _, job = self.request("POST", "/api/jobs", {"title": "Heat gate", "task_type": "microscopy", "sample_count": 10, "duration": 2})
            self.wait(job["id"], lambda j: j["state"] == "paused")
            time.sleep(.2)
            self.assertEqual(self.worker.store.get(job["id"])["active_seconds"], 0)
            self.request("POST", f"/api/jobs/{job['id']}/resume", {})
            time.sleep(.2)
            self.assertEqual(self.worker.store.get(job["id"])["active_seconds"], 0)
            self.host_request("POST", "/api/host/heat", {"enabled": True})
            done = self.wait(job["id"], lambda j: j["state"] == "completed")
            self.assertEqual(done["result"]["images"], 10)
            self.assertTrue(done["result"]["simulated"])
        finally:
            self.worker.store.set_heat(True)

    def test_pharma_templates_and_validation(self):
        for task in ("virtual_screening", "microscopy", "literature"):
            code, j = self.request("POST", "/api/jobs", {"task_type": task, "sample_count": 3, "text": "public literature", "duration": 2})
            self.assertEqual(code, 202)
            done = self.wait(j["id"], lambda x: x["state"] == "completed")
            if task == "virtual_screening":
                self.assertEqual(len(done["result"]["ranking"]), 3)
                self.assertTrue(done["result"]["simulated"])
            if task == "literature":
                self.assertEqual(done["result"]["words"], 2)
        for data in ({"task_type": "shell", "text": "x"}, {"task_type": "microscopy", "sample_count": True},
                     {"task_type": "virtual_screening", "sample_count": 1000001}, {"task_type": "microscopy", "target": ""}):
            self.assertEqual(self.request("POST", "/api/jobs", data)[0], 400)

    def test_host_origin_csrf_and_boolean_validation(self):
        self.assertEqual(self.host_request("GET", "/api/host/status", headers={"Origin": "https://foreign.example"})[0], 403)
        self.assertEqual(self.host_request("GET", "/api/host/session", headers={"Host": "foreign.example"})[0], 403)
        self.assertEqual(self.host_request("POST", "/api/host/heat", {"enabled": False}, {"X-DigitalHeat-CSRF": self.sender.csrf})[0], 403)
        self.assertEqual(self.host_request("POST", "/api/host/heat", {"enabled": "yes"})[0], 400)


if __name__ == "__main__":
    unittest.main(verbosity=2)
