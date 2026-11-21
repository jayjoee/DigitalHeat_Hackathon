# DigitalHeat · zwei getrennte Oberflächen

Der Prototyp trennt die Serverhalter von den Nutzern der Rechenleistung. Die Gestaltung greift die ruhige Kachelansicht von Apple Home auf und verwendet einen eigenen Landschaftshintergrund. Die Oberflächen laden keine externen Ressourcen.

| Rolle | Oberfläche | Aufgaben |
|---|---|---|
| Serverhalter | **Mein Zuhause**, lokal auf dem Empfänger, Port 8090 | Betriebsstatus sehen, Wärmebedarf ein-/ausschalten, anonyme Auftragszahlen sehen |
| Pharma-Kunde | **Forschungsaufträge**, lokal auf dem Sender, Port 8080 | Pharma-Vorlage wählen, Auftrag senden, Fortschritt verfolgen, Ergebnis ansehen, eigenen Auftrag pausieren/fortsetzen/abbrechen/entfernen |

Es gibt keinen Rollenumschalter und keine vermischte Navigation. Die Serverhalter-Schnittstelle liefert keine Projekttitel, Eingabetexte, Target-Namen, Auftrags-IDs oder Ergebnisse. Der Pharma-Arbeitsbereich bietet keine globale Heizungssteuerung. Das ist eine Trennung der Anwendungsoberflächen und ihrer Schnittstellen, keine Absicherung des Arbeitsspeichers gegen den Besitzer des Empfängergeräts.

## Animierte Tablettenprüfung

Im Ordner `prototyp` starten:

```sh
python3 digitalheat.py demo --port 8081 --host-port 8091 --worker-port 8444 --open
```

Auf [Haus · Laptop A](http://127.0.0.1:8081) **Batch starten**.
Beim automatischen Wechsel läuft die Prüfung auf [Sportbad · Laptop B](http://127.0.0.1:8091)
beim nächsten Bild weiter. Für zwei physische Geräte siehe [Blister-Demo](blister/README.md).

## Klassischen Pharma-Prototyp ausprobieren

Voraussetzungen: Python 3.10 oder neuer mit TLS 1.3 sowie `openssl` für die erstmalige Zertifikaterstellung. Keine Python-Zusatzpakete. Unter Windows gegebenenfalls `python` statt `python3` verwenden und OpenSSL separat bereitstellen.

Eine laufende ältere Version mit `Ctrl+C` beenden. Im entpackten Anwendungsordner starten:

```sh
python3 digitalheat.py demo --pharma --open
```

Auf macOS öffnet ein Doppelklick auf `Demo_starten.command` die animierte Blisterprüfung, wenn Python verfügbar ist.

- Pharma: [http://127.0.0.1:8080](http://127.0.0.1:8080)
- Serverhalter: [http://127.0.0.1:8090](http://127.0.0.1:8090)

`--open` öffnet nur den Pharma-Arbeitsbereich. Die Serverhalter-Adresse separat in einem zweiten Fenster öffnen. Beide Rollen laufen in dieser Demo auf demselben Rechner, kommunizieren aber über die verschlüsselte Schnittstelle für den späteren Betrieb auf zwei Geräten.

### Ein kompletter Testablauf

1. In Pharma **Virtuelles Screening** auswählen, Projekt benennen und senden.
2. Auftragskachel öffnen und das ausdrücklich synthetische Ranking ansehen.
3. Auf der Serverhalter-Seite **Wärmebedarf** ausschalten.
4. In Pharma einen **Cell-Painting**-Auftrag mit beispielsweise 384 Demo-Bildern senden. Er wartet bei 0 %.
5. Auf der Serverhalter-Seite Wärmebedarf einschalten. Die Verarbeitung läuft weiter.
6. In Pharma das synthetische Mikroskopie-Ergebnis ansehen.
7. **Literatur verarbeiten** wählen und einen öffentlichen oder erfundenen Text eingeben. Hier sind Wortzahl, häufige Begriffe und SHA-256-Prüfsumme tatsächlich berechnet.
8. Auf der Serverhalter-Seite prüfen: Es erscheinen nur Betriebszustände und Zahlen, keine Forschungsinhalte.

Mit `Ctrl+C` beenden. Aufträge und Ergebnisse gehen beim Beenden des Empfängers verloren. Diese Version bietet keinen Ergebnisdatei-Download.

Bei belegten Ports können alle drei Ports gewählt werden:

```sh
python3 digitalheat.py demo --pharma --port 8081 --host-port 8091 --worker-port 8444
```

## Auf zwei Geräten im selben Netzwerk

Die Anwendung auf beide Geräte kopieren. Beispiel-IP des Empfängers: `192.168.1.42`. Sie muss durch seine tatsächliche LAN-/WLAN-Adresse ersetzt werden.

### 1. Zugangsdaten auf dem Empfänger erstellen

```sh
python3 digitalheat.py init --host 192.168.1.42
```

Das erzeugt `credentials/worker` mit Zertifikat, privatem Schlüssel und Token sowie `credentials/sender` mit Zertifikat und Token. **Nur den Sender-Unterordner sicher zum Sender übertragen. Den privaten Worker-Schlüssel niemals mitgeben.** Keine Zugangsdaten öffentlich hochladen oder in Git aufnehmen.

Das Zertifikat ist 30 Tage gültig und an die gewählte Adresse gebunden. Bei geänderter Adresse oder Ablauf neue Zugangsdaten in einem neuen Ordner erzeugen und verteilen. Bestehende Ordner werden nicht überschrieben.

### 2. Empfänger starten

```sh
python3 digitalheat.py worker --credentials credentials/worker
```

Die verschlüsselte Auftragsschnittstelle läuft auf Port 8443. Die lokale Serverhalter-Seite ist auf diesem Gerät unter [http://127.0.0.1:8090](http://127.0.0.1:8090) erreichbar. Bei Bedarf `--host-port 8091` angeben.

Beide Geräte müssen sich im privaten Netzwerk erreichen können. Falls die Firewall fragt, den vorgesehenen privaten Zugriff zulassen. Keine Router-Portweiterleitung nötig. Gastnetze können Geräte voneinander trennen. Der Prozess protokolliert nur Auftrags-IDs und Fortschritt, keine Texte oder Target-Namen.

Standardmässig wird ein Auftrag gleichzeitig verarbeitet. Weitere warten. Ein pausierter Auftrag behält seinen Rechenplatz. Mit `--workers 2` bis `--workers 4` sind mehrere parallele CPU-Simulationen möglich.

### 3. Sender starten

```sh
python3 digitalheat.py sender --worker https://192.168.1.42:8443 --credentials credentials/sender --open
```

Pharma öffnet auf dem Sender [http://127.0.0.1:8080](http://127.0.0.1:8080). Beide Browseroberflächen sind nur auf ihrem jeweiligen Gerät erreichbar. Zwischen Senderdienst und Empfänger wird TLS 1.3 mit Zertifikats- und Namensprüfung verwendet.

Wird der Sender beendet, rechnet der Empfänger weiter. Nach erneutem Senderstart mit denselben Zugangsdaten wird der aktuelle Stand angezeigt.

## Die drei Pharma-Vorlagen

| Vorlage | Eingabe | Ergebnis / Grenze |
|---|---|---|
| Virtuelles Screening | Demo-Target, Anzahl Demo-Moleküle | Deterministisches synthetisches Ranking von bis zu fünf Demo-Kandidaten. Kein Docking, keine echte Molekülbibliothek, keine Bindungsaffinität. |
| Cell Painting | Demo-Datensatzname, Anzahl Demo-Bilder | Synthetische Zellanzahl und Qualitätsquote. Keine Bilddateien, keine Bildanalyse, kein trainiertes Modell. |
| Literatur | Öffentlicher oder künstlicher Text | Tatsächliche Wortstatistik und Prüfsumme. Keine Embeddings und keine wissenschaftliche Bewertung. |

Alle Vorlagen erzeugen zusätzlich reale CPU-Last durch PBKDF2 für die gewählte Demo-Dauer. Die Zahl der Moleküle beziehungsweise Bilder ist eine Szenarioangabe und bestimmt keine tatsächliche Analysemenge. Die aktive Zeit misst CPU-Rechenabschnitte; sie ist keine GPU-Abrechnung und keine Energiemessung. Es wird ein Auftrag übertragen, keine physische Rechenleistung.

**NVIDIA-Ausführung, echte Pharma-Modelle, Jahres-/Fristen-Scheduler, Abrechnung und die physische Heizung sind noch nicht angeschlossen.** Wärmebedarf ist ein manueller Demo-Schalter und pausiert die CPU-Schleife. Er schaltet keine Hardware aus und misst keine Temperatur. Die drei Vorlagen lassen sich ausschliesslich über fest implementierte Funktionen verarbeiten; es werden keine Programme oder Shellbefehle angenommen.

## Sicherheit und Grenzen

- Sender und Empfänger verwenden mindestens TLS 1.3 mit geprüftem Zertifikat. Kein unverschlüsselter Ersatzweg und keine abgeschaltete Zertifikatsprüfung.
- Ein zufälliges Bearer-Token schützt den Empfänger. Es bleibt auf dem Senderdienst und wird nicht an die Browseroberfläche ausgeliefert. Wer den Sender-Token besitzt, kann alle Kundenaufträge dieses Demonstrators sehen und steuern.
- Beide lokalen Oberflächen prüfen Host und Herkunft. Änderungen benötigen zusätzlich ihren jeweils eigenen CSRF-Sitzungsschlüssel. Die Kundenoberfläche kann die Serverhalter-Schnittstelle nicht auf ihrem eigenen Dienst aufrufen und umgekehrt.
- Der Serverhalter erhält über seine Oberfläche ausschliesslich aggregierte Zustände. Er besitzt jedoch den verarbeitenden Rechner; die UI-Trennung schützt nicht gegen Betriebssystem-/Administratorzugriff auf RAM oder Prozesse.
- Eingaben und Ergebnisse werden nicht als Dateien gespeichert. Grenzen: 200'000 Textzeichen, 300'000 Byte pro Anfrage, 30 gespeicherte Aufträge, 1 bis 1'000'000 Demo-Moleküle/-Bilder. Die Byte-Grenze kann bei Unicode früher greifen.
- Beendete Aufträge werden ungefähr eine Stunde nach der letzten Zustandsänderung entfernt; die Bereinigung läuft alle 30 Sekunden und auch beim Lesen. Laufende/pausierte Aufträge laufen nicht automatisch ab. Python garantiert keine sichere RAM-Löschung; Swap und Crash-Dumps werden nicht kontrolliert.
- Zugangsdaten werden mit eingeschränkten Dateirechten erstellt. Auf Windows NTFS-Rechte prüfen. Der private Schlüssel hat kein Passwort. Kein Schlüsseldienst und keine verschlüsselte dauerhafte Datenspeicherung.

**Nur öffentliche oder erfundene Testdaten verwenden.** Es gibt einen gemeinsamen Kundenzugang, keine Anmeldung mit individuellen Benutzerrollen, keine Trennung mehrerer Pharma-Kunden, kein MFA, kein Confidential Computing und keine Hardwareattestierung. Die Pharma-Sicherheitsanforderungen sind damit erst teilweise erfüllt. Der Python-Demoserver ist für lokale/LAN-Tests vorgesehen und nicht für eine öffentliche Produktionsbereitstellung.

## Automatisch prüfen

```sh
python3 -m unittest discover -s tests -v
```

Zwölf Integrationstests prüfen reale lokale HTTPS-Verbindungen, Ergebnisse aller drei Vorlagen, Wärmebedarf/Pausen, Fortsetzen/Abbrechen/Entfernen, die getrennten Schnittstellen samt Datenprojektion, Eingabegrenzen, Ablauf, CSRF, Host-/Herkunftsprüfung, Tokenpflicht und Ablehnung fremder Zertifikate. Die Tests verwenden temporäre Zugangsdaten und zufällige lokale Ports.

Bei Startproblemen: richtige IP, passende Zugangsdaten, laufenden Empfänger und freie Ports prüfen. Ein Zertifikatsfehler wird durch korrekt neu eingerichtete Zugangsdaten behoben, nicht durch Abschalten der Prüfung.
