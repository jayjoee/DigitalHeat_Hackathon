# Vertrauliche Verarbeitung auf Servern in Privathäusern

**Nicht gewählter Forschungspfad.** Das Team hat sich für [L4 mit freigegebenen nicht vertraulichen Aufgaben](../kunden/L4_ANGEBOT.md) entschieden. Die folgenden Implementierungs- und Rechercheangaben dokumentieren eine untersuchte Option, keine zugesagte Funktion des L4-Angebots.

Stand: 21. November 2026. **Softwareintegration vorhanden, reale TEE-Bereitstellung noch nicht erfolgt.** Auf diesem Entwicklungsgerät stehen weder eine nachgewiesene TDX-Plattform noch ein Confidential-GPU-Cluster, Trustee, Kata oder Kubernetes zur Verfügung. Die Tests beweisen Verschlüsselung und Ablehnungsregeln, keinen Schutz auf bereits installierter Hardware. Echte Pharma-Daten dürfen bis zum bestandenen Hardware-Abnahmetest nicht eingesetzt werden.

## Ziel und Hardwarekonflikt

Der Haushalt darf das Gerät besitzen und am Host Administrator sein, ohne die Nutzdaten, Schlüssel oder entschlüsselten Ergebnisse lesen zu können. Das Gehäuse lässt sich durch Code nicht unzugänglich machen. Schutz gegen beliebige invasive Chipangriffe, Seitenkanäle, Stromunterbrechung oder Zerstörung versprechen wir nicht. Verfügbarkeit und absolute physische Manipulationssicherheit sind andere Aufgaben als Vertraulichkeit. Grundlage ist das [CoCo-Vertrauensmodell](https://confidentialcontainers.org/docs/architecture/trust-model/trust-model/).

**Die ursprünglich vorgesehenen L4 sind für diesen GPU-Schutzpfad nicht geeignet.** In [NVIDIAs unterstützter CoCo-Plattformliste](https://docs.nvidia.com/confidential-computing/containers/supported-platforms) stehen andere Beschleuniger sowie passende CPU-TEE-Plattformen. Ein H100/H200/B200-Aufkleber allein reicht ebenfalls nicht: CPU, Firmware, Gastsoftware und Betriebsmodus müssen zusammenpassen. Unsere erste Implementierung unterstützt als Ziel Intel TDX und dedizierte CPU-only- oder Single-GPU-Knoten mit H100, H200 oder B200. Sie erklärt keine vorhandene Maschine automatisch für geeignet. Andere von NVIDIA dokumentierte Varianten sind nicht automatisch in unserer Integration unterstützt.

Auf einer L4 bleiben öffentliche oder synthetische Aufträge möglich. Vertrauliche Aufträge erhalten keine ungeschützte Ausweichroute. Ein CPU-TEE allein schützt GPU-Speicher und den Weg zur L4 nicht ausreichend für diesen Anspruch.

## Datenweg und Vertrauensgrenzen

1. Auf dem vertrauenswürdigen Kundengerät erzeugt `start/confidential_start.py seal` einen zufälligen 256-Bit-Schlüssel und verschlüsselt den Auftrag mit AES-GCM. Kunde, Auftrags-ID und Richtung sind gegen Veränderungen gebunden. Jeder Verschlüsselungsvorgang verwendet einen neuen zufälligen Nonce. Implementierung: etablierte [Cryptography-AEAD-Bibliothek](https://cryptography.io/en/latest/hazmat/primitives/aead/), keine selbst erfundene Chiffre.
2. Der Kunde behält seine private Schlüsseldatei. Die zentrale DigitalHeat-Steuerung nimmt über `/v1/confidential-jobs` ausschliesslich das verschlüsselte Paket und technische Ressourcen-/Fristmetadaten an. Freitexttitel und Klartextfelder sind dort nicht erlaubt. Technische IDs und Paketgrössen bleiben sichtbar; das ist keine Metadaten-Anonymisierung.
3. Der Datenschlüssel wird separat durch den Kunden bzw. einen berechtigten DigitalHeat-Betreiber an einen **externen, vertrauenswürdigen Trustee-Key-Broker** provisioniert. Er wird niemals auf dem Haushaltsserver, im Kubernetes-Secret, im Container-Environment, in Init-Data oder im Repository abgelegt. Trustee und seine Administration dürfen nicht unter Kontrolle des Haushalts liegen. Die erste Integration enthält keinen öffentlichen Provisionierungsdienst für Kunden.
4. Der Scheduler lässt den Auftrag nur auf einen passenden `confidential_coco`-Knoten. Ein exklusiver Ausführungsplatz verhindert das Vermischen verschiedener Aufträge im selben Gast. Eine Typangabe im Inventar ist dabei nur Planung; sie ersetzt keine Attestierung.
5. Der externe CoCo-Executor startet über Kubernetes eine Kata Confidential VM. Der Gast fordert den Schlüssel über den internen Confidential Data Hub an. Der eigentliche Hardware-Nachweis, die Prüfung der Zertifikatsketten, Referenzmesswerte und die geschützte Schlüsselübertragung werden von **CoCo/Trustee** ausgeführt. Wir akzeptieren kein vom Host übermitteltes `verified: true` und bauen keinen Ersatz für diese Protokolle.
6. Die erzeugte Trustee-Ressourcenpolicy erlaubt nur die konkret vorgesehene Schlüsselressource, einen affirmierenden CPU-Nachweis und die freigegebene Init-Data-Prüfsumme. Bei GPU-Aufträgen muss zusätzlich der GPU-Nachweis affirmierend sein. Fehlende oder abweichende Claims führen zur Ablehnung. Vorbild: [CoCo/NVIDIA-Attestierungsbeispiel](https://confidentialcontainers.org/docs/examples/nvidia-nim-confidential-gpu-attestation/), mit zusätzlicher Einschränkung auf die jeweilige Ressource.
7. Erst innerhalb der VM wird entschlüsselt und verarbeitet. Der erste geschützte Anwendungs-Worker berechnet echte Textstatistik. Er führt keine hochgeladenen Programme oder Shellbefehle aus. Ergebnisse verlassen den Gast ausschliesslich als AES-GCM-Paket, auch über Host-lesbare Logs. Fehlerausgaben enthalten keine Eingaben, Schlüssel oder Tracebacks. Nur der Kunde entschlüsselt das Ergebnis.

Der Worker ist noch kein Docking-, Bildanalyse- oder LLM-Modell und führt selbst keine GPU-Berechnung aus. Der GPU-Bereitstellungspfad berücksichtigt GPU-Attestierung und exklusiven Passthrough; ein wissenschaftlicher GPU-Worker benötigt ein eigenes geprüftes Image und passende Policy.

## Der entscheidende Schutz gegen Administratorzugriff

Eine verschlüsselte VM allein genügt nicht, wenn der Host anschliessend per `exec` Befehle im Gast starten darf. Deshalb muss die **Kata Agent Policy innerhalb des Gastes** die erlaubten Images, Startbefehle, Umgebungsvariablen, Mounts und APIs einschränken. Shell-/Debugzugriff, beliebiges Kopieren, zusätzliche Container und Policy-Austausch müssen ausgeschlossen sein. Das beschreibt [NVIDIAs Workload-Konfiguration](https://docs.nvidia.com/confidential-computing/containers/configure-workloads).

`genpolicy` liefert einen Ausgangspunkt, keine automatische Sicherheitsfreigabe. Die Policy muss für das genaue Worker-Image und Manifest geprüft werden. `start/confidential_start.py initdata` verpackt diese Policy zusammen mit der Trustee-Adresse und dessen Zertifikat. Das vollständige Dokument wird gemessen. `load_deployment` akzeptiert nur exakt die zuvor vom vertrauenswürdigen Betreiber freigegebene SHA384-Prüfsumme. Die Erzeugung eines Hashes ist **keine** Prüfung, ob eine Policy sicher ist. Insbesondere darf eine permissive Tutorial-Policy nicht einfach freigegeben werden.

Der externe Broker muss dieselbe Prüfsumme verlangen. Sonst könnte der Host die Agent-Policy austauschen. Referenz: [Init-Data](https://confidentialcontainers.org/docs/features/initdata/) und [drei getrennte Policy-Ebenen](https://confidentialcontainers.org/docs/attestation/policies/). Die Attestation-Service-Policy muss reale Referenzmesswerte und die zulässige TCB bewerten; eine Ressourcenpolicy allein ersetzt diese Bewertung nicht. Ein beliebiger TEE-Nachweis oder ein Sample-Attester genügt nicht.

Zusätzlich erzeugt unser Manifest keine Host-Verzeichnismounts, keinen Kubernetes-Service-Account-Token und keinen privilegierten Container. Das sind zusätzliche Beschränkungen; gegen einen bösartigen Host bleibt die Durchsetzung im gemessenen Gast entscheidend.

Wenn auch Programmcode oder Modellgewichte geheim sind, müssen sie als [verschlüsseltes OCI-Image](https://confidentialcontainers.org/docs/features/encrypted-images/) auf vertrauenswürdiger Kunden-/CI-Infrastruktur vorbereitet werden. CoCo kann die Schichten erst im Gast entschlüsseln. `image_key_resource` in der Betreiberkonfiguration ergänzt dafür eine getrennte Image-Schlüsselressource desselben Kunden. Unsere Integration verschlüsselt OCI-Images nicht selbst; dafür wird der dokumentierte CoCo-Keyprovider genutzt. Das öffentliche Textstatistik-Worker-Image ist kein Nachweis für geheimen Modellcode.

## Einbindung in die bestehenden Mechanismen

- Ressourcen, Kundenfreigaben, Priorität und Kontingente bleiben verbindlich. Nicht öffentliche Klassen werden auf gewöhnlichen CPU-/GPU- oder Planungsknoten blockiert.
- Vertrauliche Laufzeiten enthalten einen konfigurierten Mehraufwand. Fristen, Wartungstermine, Backfill-Reservierungen und Fairness berücksichtigen diese längere Belegung.
- Wärmefreigabe, kritische Wartungssperren, abgelaufene Freigaben und überfällige Gesundheitsmeldungen werden weiterhin geprüft. Weil sichere GPU-Zwischenstände noch fehlen, führt der CoCo-Executor bei einer Laufunterbrechung zu einem kontrollierten Abbruch statt einer behaupteten Pause. Für vertrauliche Aufträge sind manuelles Pause/Resume daher gesperrt.
- Ressourcen werden erst nach bestätigtem Ende des externen Jobs freigegeben. Scheitert die Bestätigung, bleibt die Reservierung bestehen und der Server wird gesperrt. Eine Kubernetes-Bestätigung ist eine Betriebsinformation, kein neuer Hardware-Nachweis.
- Bei jedem neuen Gast erfolgt die echte Schlüsselanforderung über CoCo/Trustee. Die Freigabe ist keine Garantie gegen später entdeckte Schwachstellen oder einen kompromittierten zulässigen Gast. Nach bereits erfolgter Schlüsselfreigabe kann ein Broker die im Gast vorhandenen Bytes nicht rückwirkend zurückholen.

## Zusätzliche Rechenzeit, Energie und Kosten

Die Forschung liefert **keinen allgemeingültigen Prozentaufschlag**. NVIDIA berichtet bei optimierter DeepSeek-Inferenz auf acht B200 96,1–98,2 % des ungeschützten Durchsatzes. Das sind spezielle Bedingungen, keine Messung unseres Pharmasystems. [NVIDIA, September 2026](https://developer.nvidia.com/blog/enabling-private-high-performance-production-ai-inference-with-nvidia-confidential-computing)

Eine IBM-Untersuchung mit häufigem Modellwechsel auf einer H100 zeigt deutlich höhere Nachteile. Dort ist der ungeschützte Durchsatz 45–70 % höher als der geschützte. Das entspricht ungefähr 31–41 % weniger geschütztem Durchsatz, nicht einfach einem 45–70-%-Laufzeitaufschlag. Diese LLM-Daten lassen sich nicht direkt auf unsere Textstatistik oder spätere Pharma-Verfahren übertragen. [IBM, ICDCS 2025](https://research.ibm.com/publications/performance-of-confidential-computing-gpus)

`src/confidential/costs.py` trennt deshalb Durchsatzverlust, zusätzliche Leistung, Setup und Brokerenergie:

```
t_geschützt = t_basis / (1 − Durchsatzverlust) + Setupzeit
E_host = P_basis × (1 + Leistungsaufschlag) × t_basis / (1 − Durchsatzverlust) / 3600
         + P_setup × Setupzeit / 3600
E_total = E_host + Brokerenergie
Mehrkosten = (E_total − E_basis) × Strompreis + zusätzliche fixe Gebühren
```

Konfigurierbare, **ungeprüfte Teamannahmen** für die Planung: 10 % Durchsatzverlust, 5 % Leistungsaufschlag, 30 s Setup bei 1 kW, 0,001 kWh Brokerenergie je Auftrag, CHF 0 fixe Zusatzgebühr. Die Nullgebühr bedeutet ausdrücklich nicht, dass Lizenzierung oder Betrieb kostenlos sind. Diese Werte sind Platzhalter; keine Quelle liefert diese Kombination. Schlüsselprüfungen und Transfers werden mit dem Setup pauschaliert, nicht detailliert gemessen.

Beispiel für einen Auftrag mit einer Stunde Basislaufzeit und 1 kW: 1,000 kWh ohne Schutz gegenüber 1,176 kWh inklusive angenommenem Broker. Das wären 17,6 % mehr Energie und bei 0,3325 CHF/kWh etwa CHF 0,059 zusätzlich. Die Szenarien aus `estimate` sind Sensitivitäten, kein Konfidenzintervall und keine obere Grenze. Zusätzliche Brokerenergie entsteht ausserhalb des Hauses und darf nicht als lokale Heizwärme zählen. Hardwarewechsel, Lizenzpreise, Serverleerlauf, Ersatzheizung und die vollständige Jahresbilanz sind weiterhin separat zu bewerten. Die bestehenden L4-Kosten bleiben dadurch nicht automatisch für H100 gültig.

## Lokaler Test ohne Sicherheitsbehauptung

```sh
python3 -m venv .venv-cc
.venv-cc/bin/python -m pip install -r requirements/confidential.txt
.venv-cc/bin/python -m unittest discover -s tests -p test_confidential.py -v
python3 start/confidential_start.py estimate --seconds 3600
```

Für die Rego-Prüfung zusätzlich das offizielle [OPA-Prüfwerkzeug](https://www.openpolicyagent.org/docs) installieren und `OPA_BIN=/absoluter/pfad/opa` beim Testlauf setzen. Ohne OPA wird nur diese konkrete Prüfung übersprungen. Auch mit OPA sind Test-Claims künstliche Daten und keine Attestierung.

Auf dem Kundengerät einen **öffentlichen** ersten Testtext verschlüsseln:

```sh
mkdir -m 700 cc-client-secrets
.venv-cc/bin/python start/confidential_start.py seal --input public-test.txt --customer pharma-demo --key-file cc-client-secrets/job.cckey --out cc-package
```

Das Verzeichnis `cc-package` enthält nur den verschlüsselten Auftrag. Die `.cckey`-Datei bleibt beim Kunden bzw. beim berechtigten externen Broker. Der neue Endpunkt nimmt den Schlüssel nicht entgegen. `.cckey` und `cc-client-secrets` sind von Git ausgeschlossen.

## Reale Bereitstellung: konkret noch erforderlich

1. Passenden TDX-Server und gegebenenfalls unterstützte Confidential-GPU auswählen. Firmware, CPU-TEE, GPU-CC-Modus, Gast-Image, Treiber und Kata/CoCo nach der aktuellen Herstelleranleitung installieren. Für die erste Abnahme einen dedizierten Testserver nutzen.
2. Trustee auf vertrauenswürdiger Infrastruktur ausserhalb des Hauses betreiben: verifiziertes HTTPS, geschützte Administration, echte Referenzmesswerte für CPU und gegebenenfalls GPU. Zuerst `deploy/confidential/kbs-deny-all.rego` aktivieren. Keine Allow-all- oder Sample-Policy verwenden.
3. Worker-Image aus `deploy/confidential/Dockerfile` mit geprüftem, unveränderlichem Linux-Python-Basisimage auf vertrauenswürdiger CI bauen. Den resultierenden Image-Digest festlegen. Bei geheimem Modellcode verschlüsselte OCI-Schichten und einen separaten Image-Schlüssel verwenden.
4. Für das konkrete Manifest eine Kata-Agent-Policy erzeugen und einschränken. Mit echten Host-Angriffstests nachweisen: Exec, zusätzliches Image, andere Startbefehle/Umgebung, Dateikopieren und Host-Mounts sind im Gast blockiert. Die interne CDH-REST-Schnittstelle darf nur im Gast erreichbar sein.
5. Die geprüfte Policy und das Broker-Zertifikat verpacken:

   ```sh
   python3 start/confidential_start.py initdata --agent-policy reviewed-agent.rego --kbs-url https://TRUSTED-BROKER --kbs-cert broker-cert.pem --out reviewed-initdata.toml
   ```

   Den ausgegebenen Hash und den Image-Digest in einer Kopie von `deploy/confidential/deployment.example.json` eintragen. Diese Beispieldatei ist absichtlich nicht ausführungsbereit. Ein Inventarbeispiel liegt daneben; es bestätigt keine vorhandene Hardware. Der feste Gast muss auch die passende CDH-/Attestation-Agent-Konfiguration und Gast-REST-Schnittstelle enthalten.
6. Mit `start/confidential_start.py plan --request cc-package/request.json --inventory inventory.json --deployment-config deployment.json --out cc-plan` die konkrete Ressourcenpolicy und das CoCo-Manifest erzeugen. Der Plan verändert keinen Cluster. Den Init-Data-Hash auch auf dem Broker festlegen. Mehrere pro Auftrag erzeugte Policies müssen kontrolliert kombiniert bzw. getrennten Brokern zugeordnet werden; nicht die Policy eines produktiven, gemeinsam genutzten Brokers blind überschreiben.
7. Den 32-Byte-Auftragsschlüssel als die vom CLI genannte Ressource provisionieren, ausschliesslich über die authentisierte Admin-Schnittstelle des externen Brokers. Der [offizielle KBS-Client](https://confidentialcontainers.org/docs/attestation/client-tool/) unterstützt `config --admin-token-file ... set-resource --path ... --resource-file ...`; für die Policy `set-resource-policy --policy-file ...`. HTTPS mit verifiziertem Broker-Zertifikat verwenden. Kein `--insecure`, kein Schlüsselwert als Kommandozeilenargument oder Logausgabe.
8. Zentrale Steuerung mit Betreiberinventar, verschiedenen Kundentokens und `--cc-deployment-config deployment.json` starten. Der hierfür verwendete Worker-Prozess und sein Kubernetes-Zugang laufen auf der vertrauenswürdigen DigitalHeat-Steuerung, **nicht** beim Haushalt. Die bisherige CPU-Demo im Haus darf keine Trustee-Administration oder Kunden-Schlüsseldateien erhalten.
9. Der Kunde sendet nur `cc-package/request.json` mit `start/confidential_start.py submit --request ... --worker https://CENTRAL-CONTROL:8443 --credentials CUSTOMER-CREDENTIALS`. Das Ergebnis aus der bestehenden authentisierten Job-API wird als verschlüsseltes Paket gespeichert und auf dem Kundengerät mit `decrypt-result --result ... --request ... --key-file ... --out ...` geöffnet.

Die reale Abnahme muss mindestens einen erfolgreichen verschlüsselten Auftrag, verweigerte Schlüssel bei falscher CPU/GPU/Init-Data, blockierten Host-Exec und unlesbare Host-Dateien/-Logs belegen. Ein Neustart, Netzverlust und Wartungsabbruch müssen ohne ungeschützte Wiederaufnahme getestet werden. Ergebniswiederholungen und Zählung genau einmal sind noch nicht gewährleistet; die bestehende Queue bleibt flüchtig. Bis dahin ist dies eine getestete Softwarebasis für die Bereitstellung, keine bereits abgesicherte Pharma-Produktionsplattform.
