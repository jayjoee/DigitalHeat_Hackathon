# Sicht des Hausbesitzers

Was hat ein Haushalt davon, wenn DigitalHeat Server in seinen Keller stellt? Grundlage ist die Kundensicht von Joël (21.11.2026), gekürzt auf das, was für den Pilot zählt. Die Ersparnisse rechnet `src/haushalt.py` (`daten/ergebnisse/haushalt.json`), die Deckung kommt aus der Jahressimulation.

## Das Angebot

- **DigitalHeat zahlt und besitzt alles:** Server, Einbau, Rückbau der Ölheizung, Server-Strom (eigener Zähler) und Unterhalt. Der Haushalt investiert nichts und bekommt die Wärme **gratis**. So arbeiten auch Heata und Deep Green in Grossbritannien; DigitalHeat selbst schreibt «kein Hardwarekauf durch den Wärmeabnehmer» ([digitalheat.ch](https://digitalheat.ch)).
- **Ölkessel und Tank kommen raus.** An den kältesten Tagen heizt der Holzofen oder das Cheminée, das viele ältere Häuser schon haben (Team-Annahme).
- **Warum der Haushalt die Anlage nicht selbst kauft:** Eine 8-kW-Einheit kostet rund 290'000 CHF ([KOSTEN_DH.md](../wirtschaft/KOSTEN_DH.md)), eine Wärmepumpe in Basel 31'500–63'000 CHF. Die Anlage bezahlt sich über verkaufte Rechenzeit, nicht über die Wärme.
- **Zielkunde im Pilot:** Einfamilienhaus mit Ölheizung in Basel-Stadt ausserhalb der Fernwärme (Bruderholz, Riehen, Bettingen). Öl ist am teuersten, neue Öl- und Gasheizungen sind in Basel-Stadt seit 2017 verboten, das Gasnetz geht bis 2037 vom Netz. Danach folgen Öl-Häuser in Basel-Landschaft (rund 19'300 Wohngebäude) und Aargau. Wie der Pilot abläuft: [PILOTPLAN.md](../wirtschaft/PILOTPLAN.md).

## Was der Haushalt spart

Realistisch gerechnet, mit Abschalten der Server (Abschaltmodell). In Klammern das Idealmodell des Case mit 0 W Leerlauf.

| | Referenzhaus des Case | Durchschnitts-Einfamilienhaus |
|---|---|---|
| Wärmebedarf pro Jahr | 31'231 kWh | 17'000 kWh |
| Server | 8 | 5 |
| Wärme von den Servern | **90,5 %** (93,0 %) | **98,7 %** (99,6 %) |
| Rest vom Holzofen | 2'958 kWh | 216 kWh |
| **Spart gegenüber Öl** | **5'538 CHF** pro Jahr (5'686) | **3'288 CHF** pro Jahr (3'317) |
| Spart gegenüber Gas (Anschluss wird aufgegeben) | 4'597 CHF (4'714) | 2'808 CHF (2'831) |
| Spart gegenüber Wärmepumpe | 3'760 CHF (3'861) | 2'232 CHF (2'252) |
| Heizöl heute | 3'674 l, 9,7 t CO2 | 2'000 l, 5,3 t CO2 |

**So ist gerechnet:** Ersparnis = Wärme von den Servern × heutiger Preis pro kWh Wärme. Bei Gas kommt die Grundgebühr dazu, weil der Anschluss wegfällt. Das Brennholz für den Rest ist nicht eingerechnet. Heute kostet 1 kWh Wärme mit **Öl 19,6 Rp.**, mit **Gas 15,6 Rp.** und mit einer **Wärmepumpe 13,3 Rp.** (Herleitung unten).

**Wenn die Wärme etwas kostet** (Wärmeabo statt Gratiswärme), Durchschnitts-Einfamilienhaus, Ersparnis pro Jahr:

| Wärmepreis | gegenüber Öl | gegenüber Gas | gegenüber Wärmepumpe |
|---|---|---|---|
| gratis | 3'288 CHF | 2'808 CHF | 2'232 CHF |
| 3 Rp./kWh | 2'784 CHF | 2'304 CHF | 1'729 CHF |
| 7 Rp./kWh | 2'113 CHF | 1'633 CHF | 1'057 CHF |
| 10 Rp./kWh | 1'609 CHF | 1'129 CHF | 554 CHF |

Damit der Wechsel für einen Öl-Haushalt klar attraktiv bleibt (über 2'000 CHF pro Jahr), sollte die Wärme höchstens rund **7 Rp./kWh** kosten. Für DigitalHeat macht Gratiswärme gegenüber 7 Rp. nur rund 1'700 CHF pro Jahr aus ([KOSTEN_DH.md](../wirtschaft/KOSTEN_DH.md)). Darum ist Gratiswärme im Pilot das stärkste Angebot.

**Schlechter Fall:** Gibt es zu wenig flexible Rechenaufträge (Nachfrage wie im Alibaba-Trace), decken die Server nur rund die Hälfte der Wärme. Dann muss der Holzofen viel mehr liefern, und das Angebot ist für den Haushalt deutlich schwächer ([ERGEBNISSE.md](../ergebnisse/ERGEBNISSE.md)).

## Technik aus Sicht des Haushalts

- **Getrennte Kreisläufe:** Direkte Flüssigkeitskühlung an den Prozessoren, eigener Kühlkreis, Wärmetauscher zum Heizwasser. Das Heizwasser kommt nie an die Server.
- **Temperatur:** DigitalHeat nennt 50–70 °C Vorlauf. Das passt zu alten Radiatoren. Ob es auch für Warmwasser reicht (Legionellenschutz rund 60 °C), wird im Pilot zuerst gemessen ([PILOTPLAN.md](../wirtschaft/PILOTPLAN.md)).
- **Speicher:** Ein Wassertank (35 kWh) gleicht aus, wann die Server rechnen und wann das Haus Wärme braucht.
- **Jahresverlauf:** Im Winter laufen die Server fast ohne Pause, im Sommer nur für das Warmwasser. Der Haushalt merkt davon nichts.

## Einwände und Antworten

| Einwand | Antwort |
|---|---|
| «Was, wenn der Server ausfällt?» | Der Speicher überbrückt Stunden, danach heizt der Holzofen. Meldet die Kühlung ein Problem, wird der Server gesperrt. |
| «Ist das laut?» | Flüssigkeitskühlung ohne grosse Lüfter, im Keller hinter einer Tür. Wird im Pilot gemessen. |
| «Wer haftet bei Schäden?» | DigitalHeat, über eine Versicherung. |
| «Kommt jemand an meine Daten oder ich an fremde?» | Getrennte Netze, verplombtes Gehäuse, der Haushalt hat keinen Zugang. Auf den Servern laufen nur öffentliche oder freigegebene Aufgaben ([L4_ANGEBOT.md](L4_ANGEBOT.md)). |
| «Was, wenn ich umziehe?» | Der Vertrag geht auf den neuen Eigentümer über, oder die Anlage wird kostenlos zurückgebaut. |
| «Was, wenn DigitalHeat Konkurs geht?» | Holzofen und Speicher bleiben im Haus. Der Vertrag muss regeln, wer dann für eine vollwertige Heizung sorgt. |

## Offene Punkte

- **Genug flexible Rechenaufträge:** grösstes Risiko für die Ersparnis (siehe oben).
- **Kanton:** Gilt die Serverheizung mit Holzofen als erneuerbarer Heizungsersatz? In Basel-Stadt beim Amt für Umwelt und Energie schriftlich klären, vor Baubeginn. DigitalHeat erwartet eine Förderung wie für eine Wärmepumpe (rund 7'200 CHF pro Haus, an DigitalHeat abgetreten, siehe [FIRMA.md](../wirtschaft/FIRMA.md)).
- **Lärm, Platz und Vorlauftemperatur** im Keller: im Pilot messen.
- **Wetter:** gerechnet mit Basel 2025; die Jahre 2010–2025 zeigen die Spanne ([ANNAHMEN_PRUEFUNG.md](../wirtschaft/ANNAHMEN_PRUEFUNG.md)).

## Annahmen mit Quellen

Die Werte stehen auch in `src/haushalt.py` (`P`).

| Annahme | Wert | Quelle |
|---|---|---|
| Durchschnitts-Einfamilienhaus | 17'000 kWh Wärme pro Jahr | abgeleitet aus [Raiffeisen](https://www.raiffeisen.ch/rch/de/wissen/wohnen/energiesparen-erneuerbare-heizung.html): EFH mit 2'000 l Heizöl × 10 kWh/l × 85 % |
| Referenzhaus | 31'231 kWh (Heizung nach Case-Formel + 12 kWh Warmwasser pro Tag) | Case |
| Heizöl | 1,665 CHF/l, 10 kWh/l, Kessel 85 %, 2,65 kg CO2/l | [weekend.at](https://www.weekend.at/chronik/heizoelpreise-fallen-gruende-marktuebersicht-und-kaufempfehlung) (Anfang Nov. 2026); Heizwert, Wirkungsgrad und Emissionsfaktor als Standardannahmen |
| Gas | 14,0 Rp./kWh (Arbeitspreis 11,57 + CO2-Abgabe 2,333 + Konzession 0,11), Grundgebühr mindestens 194,58 CHF, Kessel 90 %, 0,198 kg CO2/kWh | [IWB Gastarife 2026](https://www.iwb.ch/servicecenter/gastarife/aktuelle-tarife), Stufe M, inkl. MwSt.; Wirkungsgrad und Emissionsfaktor als Annahmen |
| Wärmepumpe | Strompreis 33,25 Rp./kWh ÷ Jahresarbeitszahl 2,5 | Case, [ElCom](https://www.strompreis.elcom.admin.ch) |
| Wärmepumpe neu in Basel | 31'500–63'000 CHF | [handwerker-kosten.ch](https://www.handwerker-kosten.ch/waermepumpe/basel/) |
| Vorlauftemperatur, Kühlung | 50–70 °C, direkte Flüssigkeitskühlung mit Wärmetauscher | [digitalheat.ch](https://digitalheat.ch) |
| Öl-Häuser Basel-Stadt | 1'677 Ölfeuerungen (Juni 2026) | [bs.ch, Open Data AUE](https://www.bs.ch/wsu/aue/abteilung-energie/meldung-fossilbefeuerte-heizungen) |
| Öl-Wohngebäude Basel-Landschaft | rund 19'300 (28,9 % von 66'780, 2024) | [Energiestatistik BL 2024](https://www.baselland.ch/politik-und-behorden/direktionen/finanz-und-kirchendirektion/daten-statistik/abteilung-statistik/publikationen-und-statistiken/energie/webartikel-vom-07-07-2026-energiestatistik-2024) |
| Gasnetz Basel-Stadt | Stilllegung bis 2037 | [IWB](https://www.iwb.ch/klimadreh/ratgeber/heizung-ersetzen/gasstilllegung-basel-stadt) |
| Neue Öl- und Gasheizungen Basel-Stadt | verboten seit 2017 | [BKB](https://www.bkb.ch/de/privatkunden/magazin/2024/heizsysteme-basel-stadt-verzicht-auf-gas-und-oel-bis-2037-lohnt-sich-auch-finanziell) |
