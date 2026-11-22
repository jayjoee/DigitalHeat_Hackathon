# Gewähltes Angebot: L4 mit freigegebenen nicht vertraulichen Aufgaben

Entscheidung des Teams vom 21. November 2026: L4-Hardware beibehalten. Im Haus werden öffentliche und synthetische Aufgaben sowie vom Kunden bereits ausreichend anonymisierte und freigegebene Aufgaben verarbeitet. Die untersuchte Hybridvariante wurde verworfen; externe Confidential-Computing-Aufträge sind nicht Teil dieses Angebots.

## Was wir anbieten

Wärmegeführte, unterbrechbare Batch-Rechenleistung auf den bestehenden L4-Hausservern. Mögliche Forschungsaufgaben sind Verarbeitung öffentlicher Texte, öffentliche Molekül-/Bilddatensätze und künstliche Testdaten. Echte Anwendungsleistung, Nutzungsrechte, Auftragseignung und Kundenbedarf müssen je Workflow geprüft werden. Ein Pharma-Kunde kann solche nicht vertraulichen Aufgaben nutzen; ein Auftrag wird nicht allein durch die Branche zulässig.

Vertrauliche Molekülstrukturen, interne Forschungsgeheimnisse, Patientendaten, personenbezogene Rohdaten sowie geheime Modelle, Schlüssel oder Zwischenergebnisse gehören nicht in dieses Angebot. Es muss für **den gesamten Auftrag einschliesslich Programm, Parametern und Ergebnissen** vertretbar sein, dass der Hostbetreiber Einblick erhalten könnte. TLS schützt die Übertragung, verhindert aber keinen Administratorzugriff während der normalen L4-Verarbeitung.

## Kundenseitige Anonymisierung

Die Anonymisierung findet vor der Übermittlung beim Kunden statt. Namen entfernen oder IDs ersetzen beweist nicht, dass Daten ausreichend anonymisiert sind. Auch Forschungsgeheimnisse verschwinden dadurch nicht. DigitalHeat führt keine automatische Anonymisierung durch und bestätigt deren Wirksamkeit nicht durch ein Auswahlfeld.

Für einen solchen Workflow muss der Betreiber den Kunden separat freigeben (`allow_customer_anonymized`). Jeder Auftrag erhält eine technische Freigabereferenz (`release_reference`), die beim Kunden auf die geprüfte Freigabe verweist. Die Referenz selbst enthält keine Personendaten. Die technische Prüfung kontrolliert Vorhandensein und Zuordnung der Erklärung; sie kann den Inhalt nicht semantisch als anonym beweisen.

## Umsetzung im Code

- Die normale lokale Demo startet mit `public_only=True`. Der vertrauliche Auftragseingang wird dort ausdrücklich abgewiesen.
- `daten/beispiele/scheduler_l4_public.json` konfiguriert ausschliesslich öffentliche L4-Knoten und Kunden. Geschützte Inventare oder vertrauliche Kundenfreigaben sind in diesem Modus unzulässig.
- `requirements.classification` bleibt `public`. `data_basis` unterscheidet `public`, `synthetic` und `customer_anonymized`.
- Bei `customer_anonymized` sind Betreiberfreigabe und eine technische Referenz erforderlich. Wird die Freigabe widerrufen, werden neue Zuteilungen blockiert und die laufende CPU-Verarbeitung hält ihre Reservierung bis zum bestätigten Ende.
- Ressourcenprüfung, Kundenpriorität, Kontingente, Backfill, Wärmefreigabe und Wartungssperren bleiben erhalten.

Beispiel für einen bereits freigegebenen anonymisierten Workflow:

```json
{
  "text": "Ausschliesslich bereits freigegebene Testinhalte",
  "requirements": {
    "classification": "public",
    "data_basis": "customer_anonymized",
    "release_reference": "release_20261121"
  }
}
```

Die öffentliche/synthetische CPU-Demo läuft wie bisher. Die Beispiel-L4-Konfiguration ist ein Inventarschema, keine erkannte Hardware. Der reale NVIDIA-Ausführungsagent ist weiterhin anzubinden; eine deklarierte GPU führt noch keinen GPU-Auftrag aus. Confidential Computing ist als Forschungsoption dokumentiert.

## Auswirkung auf die Rechnung

Es werden keine vertraulichen Aufträge zur Finanzierung der Hausheizung ausgelagert. Damit bleibt die vorhandene Wärme-/Speicherlogik als technisches Modell nutzbar. Die bisher berechnete Heizdeckung setzt weiterhin genügend **zulässige und tatsächlich verfügbare** Arbeit voraus; sie wird durch diese Entscheidung nicht garantiert.

Die frühere Pharma-Preisargumentation über vertrauliche Schweizer Verarbeitung gilt nicht als Begründung für dieses Angebot. CHF 0,60 pro L4-Stunde und feste Auslastung sind zu bestätigende Vertragsannahmen. Vertrauliche Pharma-Nachfrage darf nicht als öffentliche Nachfrage weitergezählt werden. Die alten Renditezahlen sind deshalb bedingte Szenarien und kein Nachweis der neuen Marktpositionierung. Anonymisierungskosten beim Kunden sind noch nicht eingerechnet; ein Zusatzaufschlag für echtes Confidential Computing gehört nicht in diesen gewählten L4-Betrieb.

Vor dem Ausbau werden ein zulässiger Kundenworkflow, ein realer L4-Anwendungsbenchmark und ein bezahltes Winterkontingent benötigt. Danach werden Preis, Auslastung und erreichbare Heizdeckung mit diesen Eingangsdaten neu geprüft.
