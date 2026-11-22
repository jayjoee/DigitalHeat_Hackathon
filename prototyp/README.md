# DigitalHeat application prototype

The prototype has separate interfaces for the server host and the customer who submits work. Both load their assets locally.

| Role | Interface | What it does |
|---|---|---|
| Server host | **My home**, on the receiving device, port 8090 | Shows operating status and aggregate job counts, and lets the host set heat demand |
| Pharma customer | **Research jobs**, on the sending device, port 8080 | Starts jobs from templates, shows progress and results, and lets the customer pause, resume, cancel or remove jobs |

The host interface exposes operating data in aggregate. The customer interface controls individual jobs. An administrator of the receiving device can still inspect the processes and memory.

## Virtual screening on two screens

The default demo shows a screening job moving from a house to the sports pool and back as the simulated heat demand changes. It exchanges checkpoint state between devices and replays recorded Vina scores. See the [docking guide](../daten/docking/README.md) for details.

```sh
python3 prototyp/schwimmbad.py     # Laptop B: get the pairing code
python3 prototyp/haus.py           # Laptop A: enter the code, then click Start screening
```

Run from the repository root. To try both screens on one laptop, run `python3 prototyp/docking_demo.py demo --open`.

## Pharma workspace

Use Python 3.10 or later with TLS 1.3 and OpenSSL for certificate setup. The prototype has no extra Python dependencies. On Windows, use `python` if the Python launcher is installed under that name and install OpenSSL separately.

From the `prototyp` directory:

```sh
python3 digitalheat.py demo --open
```

The command opens the [Pharma workspace](http://127.0.0.1:8080). Open [My home](http://127.0.0.1:8090) in a second window. Both services run on the same machine and communicate over the encrypted interface used for two devices.

1. In the Pharma workspace, choose **Virtual screening**, name a project and submit it.
2. Open the completed job to see the synthetic ranking.
3. Turn **Heat demand** off in **My home**.
4. Submit a **Cell Painting** job with 384 demo images. It waits at 0%.
5. Turn **Heat demand** on. The job starts and displays a synthetic microscopy result when it finishes.
6. Choose **Process literature** and enter a public or fictional text. The prototype computes word statistics and a SHA-256 checksum.
7. Check **My home** for operating status and aggregate counts.

Press `Ctrl+C` to stop. The worker keeps jobs and results in memory. They are lost when it shuts down, and this version has no result file download.

If the default ports are in use, select all three explicitly:

```sh
python3 digitalheat.py demo --port 8081 --host-port 8091 --worker-port 8444
```

## Separate devices on the same network

Copy the application to both devices and run the following commands from `prototyp`. Substitute the receiver's LAN address for `192.168.1.42`.

### 1. Create credentials on the receiver

```sh
python3 digitalheat.py init --host 192.168.1.42
```

The command creates `credentials/worker` with the certificate, private key and token, and `credentials/sender` with the certificate and token. Transfer only the sender folder through a private channel. Keep the receiver's key on the receiver and keep all credentials out of Git.

The certificate is valid for 30 days and tied to the chosen address. If the address changes or the certificate expires, generate new credentials in a new directory. Existing directories are preserved.

### 2. Run the receiver

```sh
python3 digitalheat.py worker --credentials credentials/worker
```

The worker accepts jobs on port 8443. Open [My home](http://127.0.0.1:8090) locally on the receiver or set a different local port with `--host-port`.

Use a private network where the devices can reach each other. Guest networks can isolate devices. The worker logs job IDs and progress. It processes one job at a time by default, and a paused job holds its slot. Use `--workers 2` through `--workers 4` for multiple CPU simulations.

### 3. Run the sender

```sh
python3 digitalheat.py sender --worker https://192.168.1.42:8443 --credentials credentials/sender --open
```

The [Pharma workspace](http://127.0.0.1:8080) opens locally on the sender. The sender and receiver use TLS 1.3 and verify the certificate and host name. Jobs continue on the receiver when the sender stops. Restart the sender with the same credentials to see their current state.

## What each customer template does

| Template | Input | Result |
|---|---|---|
| Virtual screening | Demo target and molecule count | A deterministic synthetic ranking of up to five demo candidates |
| Cell Painting | Demo dataset name and image count | Synthetic cell counts and quality figures |
| Literature | Public or fictional text | Computed word statistics and a SHA-256 checksum |

The templates generate CPU activity with PBKDF2. Molecule and image counts are scenario inputs. Active time measures CPU activity and does not represent billable GPU time or measured energy. The **Heat demand** toggle pauses the job loop. GPU execution, physical heating, billing and the annual scheduler are separate from this workspace. The worker accepts only the built-in templates.

## Security and scope

- The worker requires a random bearer token across TLS 1.3. Anyone with the sender token can view and manage all customer jobs on this demo worker.
- The two local interfaces check the request host and origin. Each requires its own session key for changes.
- Jobs and results live in memory. The limits are 200,000 text characters, 300,000 bytes per request, 30 jobs and up to 1,000,000 demo molecules or images. Unicode can reach the byte limit sooner.
- Completed jobs expire about an hour after the last state change. Running and paused jobs do not expire. The demo does not control swap or crash dumps.
- Credentials are created with restricted permissions. On Windows, check NTFS permissions. The private key is unencrypted and there is no key management service.

Use only public or fictional data. The demo has a shared customer access token and no customer isolation, MFA, confidential computing or hardware attestation. Run it on a private network.

## Tests

From the repository root:

```sh
python3 -m unittest discover -s prototyp/tests -v
```

The tests use temporary credentials and local ports to verify the HTTPS connection, templates, heat demand and job states, separation of the interfaces and rejection of invalid requests and certificates.
