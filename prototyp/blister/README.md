# Blisterprüfung auf zwei Leinwänden

Zwei Rechner prüfen einen Batch mit 30 synthetischen Kamerabildern von Blisterpackungen. Die Software vergleicht pro Fach die Helligkeit des Zentrums mit der umgebenden Folie. Sie markiert fehlende Tabletten rot und zeigt, welche Fächer betroffen sind. Der Datensatz ist deterministisch auf beiden Geräten verfügbar.

Der Demo-Ablauf beginnt mit der aufgezeichneten Simulation des Wärme-Routers vom 25. Mai 2025, ab 06:00 Uhr. Um 10:00 Uhr ist der simulierte Hausspeicher mit 35 kWh voll und der Router weist den Auftrag dem Sportbad zu. Das Haus stoppt zwischen zwei Packungen und sendet den Bildindex, die bisherigen Beanstandungen und den Stand der Modellzeit per TLS.

Ab 10:00 Uhr folgt die Demo einem zusätzlichen Szenario. Das Haus entnimmt 0,5 kWh Wärme pro Modellstunde aus dem Speicher. Nach sechs Modellstunden sind noch 32 kWh gespeichert. Um 16:00 Uhr hält das Sportbad zwischen zwei Packungen an und das Haus holt den Prüfstand über dieselbe TLS-Verbindung zurück. Modellzeit und Batch-Zähler bleiben während der Übergaben auf beiden Leinwänden sichtbar. «Hier geprüft» zeigt die Packungsnummern, die der jeweilige Laptop tatsächlich verarbeitet hat.

Die Anzeige führt Modellzeit, Aussentemperatur, Raum-Sollwert, Füllstand und die örtliche Wärmeleistung fürs Wasser auf. Der Raum-Sollwert von 20 °C stammt aus dem Referenzhaus im Case. Bei voller Zuteilung ergeben 1 kW Serverleistung und 80 % Wärmerückgewinnung 0,8 kW für einen Modellserver. Teilzuteilungen ergeben einen niedrigeren Stundendurchschnitt. Bei 0 kW bleibt der Job stehen. Der Vorlauf von 55 °C ist ein illustrativer Annahmewert. Die Rechner führen die Bildprüfung und Übergabe aus, die Wärme ist simuliert.

Benötigt Python 3.10 oder neuer und OpenSSL für die Einrichtung. Alle Befehle aus dem Repository-Stamm ausführen. Beide Geräte benötigen dieselbe Version des Codes.

## Auf einem Laptop starten

```sh
python3 prototyp/blister_demo.py demo --open
```

Auf **Haus · Laptop A** auf **Batch starten** klicken. Packung 3 zeigt das erste leere Fach. Nach rund 14 Sekunden übernimmt **Sportbad · Laptop B** ab Packung 9. Sobald der Hausspeicher auf 32 kWh sinkt, übernimmt das Haus wieder ab Packung 21. Der vollständige Batch enthält 24 vollständige und sechs beanstandete Packungen.

## Auf zwei Laptops starten (einfach)

Beide Laptops im selben WLAN, auf beiden liegt das Repo.

1. **Laptop B (Schwimmbad):** `start/Schwimmbad_starten.command` doppelklicken, oder `python3 prototyp/schwimmbad.py`. Es zeigt einen 6-stelligen Code. Falls macOS fragt, eingehende Verbindungen für Python **erlauben**.
2. **Laptop A (Haus):** `start/Haus_starten.command` doppelklicken, oder `python3 prototyp/haus.py`. Es findet das Schwimmbad von selbst und fragt nach dem Code.
3. Beide Leinwände öffnen sich. Auf dem Haus **Batch starten**. Der Wechsel erfolgt automatisch.

Das Schwimmbad erzeugt bei jedem Start neue Zugangsdaten in einem temporären Ordner; beim Beenden (Ctrl+C) sind sie weg. Das Haus holt Zertifikat und Token mit dem Code über TLS ab. Findet das Haus nichts, trennt das WLAN die Geräte (häufig bei Gast-WLANs): Handy-Hotspot verwenden oder die Adresse direkt angeben, `python3 prototyp/haus.py --bad 192.168.1.42` (die Adresse steht auf dem Schwimmbad-Laptop). Grenze: Der Code schützt vor dem falschen Gerät, nicht vor jemandem, der im selben WLAN genau bei der Paarung aktiv dazwischengeht. Für synthetische Demo-Bilder reicht das.

## Auf zwei Laptops starten (von Hand)

1. Auf Laptop B einmalig die Zugangsdaten erstellen. `192.168.1.42` durch die LAN-Adresse von Laptop B ersetzen.

   ```sh
   python3 prototyp/digitalheat.py init --host 192.168.1.42 --out prototyp/credentials/blister
   ```

2. Nur den Unterordner `sender` sicher auf Laptop A unter `prototyp/credentials/blister/sender` kopieren.
3. Auf Laptop B den Empfänger starten und auf seiner Leinwand `http://127.0.0.1:8092` öffnen.

   ```sh
   python3 prototyp/blister_demo.py worker --credentials prototyp/credentials/blister/worker
   ```

4. Auf Laptop A den Sender starten und auf seiner Leinwand `http://127.0.0.1:8082` öffnen.

   ```sh
   python3 prototyp/blister_demo.py sender --target https://192.168.1.42:8445 --credentials prototyp/credentials/blister/sender
   ```

5. Auf Leinwand A **Batch starten**. Die Bildnummern unter «Hier geprüft» zeigen, welche Bilder jeweils lokal verarbeitet wurden.

Für die Probe auf einem Laptop in Schritt 1 und 4 die Adresse `127.0.0.1` verwenden und die zwei Webseiten nebeneinander öffnen. Bei unbestätigter Übergabe bleibt der Sender pausiert. **Übergabe wiederholen** sendet denselben Checkpoint erneut. Für einen frischen Demo-Durchlauf beide Prozesse neu starten.

Der Checkpoint liegt während des Durchlaufs im Arbeitsspeicher. Zwei Prüftakte entsprechen einer Modellstunde.
