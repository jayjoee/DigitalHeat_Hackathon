# Blisterprüfung auf zwei Leinwänden

Zwei Rechner prüfen einen Batch mit 30 synthetischen Kamerabildern von Blisterpackungen. Die Software misst die Helligkeit in den acht Fächern jedes Bildes und markiert fehlende Tabletten rot. Der Datensatz ist deterministisch auf beiden Geräten verfügbar. Beim Wechsel geht der Checkpoint mit Bildindex und bisherigen Beanstandungen verschlüsselt über das Netzwerk. Die Anzeige bleibt auf dem sendenden Gerät stehen und das Sportbad prüft das nächste Bild.

Benötigt Python 3.10 oder neuer und OpenSSL für die Einrichtung. Alle Befehle aus dem Repository-Stamm ausführen. Beide Geräte benötigen dieselbe Version des Codes.

## Auf einem Laptop starten

```sh
python3 prototyp/blister_demo.py demo --open
```

Auf **Haus · Laptop A** auf **Batch starten** klicken. Nach ein paar Bildern **Zum Sportbad wechseln** drücken und zum Tab **Sportbad · Laptop B** wechseln.

## Auf zwei Laptops starten (einfach)

Beide Laptops im selben WLAN, auf beiden liegt das Repo.

1. **Laptop B (Schwimmbad):** `Schwimmbad_starten.command` doppelklicken, oder `python3 prototyp/schwimmbad.py`. Es zeigt einen 6-stelligen Code. Falls macOS fragt, eingehende Verbindungen für Python **erlauben**.
2. **Laptop A (Haus):** `Haus_starten.command` doppelklicken, oder `python3 prototyp/haus.py`. Es findet das Schwimmbad von selbst und fragt nach dem Code.
3. Beide Leinwände öffnen sich. Auf dem Haus **Batch starten**, dann **Zum Sportbad wechseln**.

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

5. Auf Leinwand A **Batch starten** und nach einigen Bildern **Zum Sportbad wechseln** drücken. Die Bildnummern unter „Hier geprüft“ zeigen, welche Bilder jeweils lokal verarbeitet wurden.

Für die Probe auf einem Laptop in Schritt 1 und 4 die Adresse `127.0.0.1` verwenden und die zwei Webseiten nebeneinander öffnen. Bei unbestätigter Übergabe bleibt der Sender pausiert. Erneutes Drücken versucht denselben Checkpoint erneut. Für einen frischen Demo-Durchlauf beide Prozesse neu starten.

Die Steuerung erfolgt auf Laptop A. Die Demo verwendet einen manuellen Standortwechsel. Der Checkpoint liegt während des Durchlaufs im Arbeitsspeicher. Die Verarbeitungspause zwischen Bildern dient der Sichtbarkeit auf der Leinwand.
