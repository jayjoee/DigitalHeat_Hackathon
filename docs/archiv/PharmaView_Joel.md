> Früher Pharma-Arbeitsentwurf aus dieser Entwicklung. Für den aktuellen gemeinsamen Stand gelten [PHARMA_SICHT.md](../PHARMA_SICHT.md) und [PROJEKTUEBERSICHT.md](../PROJEKTUEBERSICHT.md). Vorschläge sind keine umgesetzten oder zertifizierten Sicherheitsnachweise.

# Pharmaperspektive für DigitalHeat

Stand 21 November 2026

DigitalHeat soll Pharmaunternehmen flexible Rechenleistung für freigegebene Forschungsaufgaben anbieten. Der Kunde kauft verwertbare Ergebnisse zu nachvollziehbaren Kosten und unter einem geprüften Sicherheitskonzept. Die entstehende Wärme wird in Gebäuden genutzt. Für den Pharmakunden stehen Datenvertraulichkeit, Ergebnisqualität und verlässliche Auftragsabwicklung an erster Stelle.

Der Einstieg erfolgt mit einem klar begrenzten Pilot für biomedizinische Literaturverarbeitung. Vertrauliche Forschungsdaten werden erst zugelassen, wenn das Unternehmen die technische Umgebung und die vertraglichen Bedingungen freigegeben hat. NVIDIA-Grafikkarten sind für die spätere Anlage vorgesehen. Ihr konkretes Modell wird anhand von Rechenleistung, Sicherheitsanforderungen, Wärmeintegration und Kosten ausgewählt.

## 1 Zielkunde und Entscheidung

Als erster Ansprechpartner eignet sich ein Forschungs- oder Scientific-Computing-Team, das wiederkehrende Batch-Aufträge auslagern kann. Einkauf und Informationssicherheit entscheiden mit. Ein möglicher Standort in der Region Basel erleichtert Gespräche und den Pilotbetrieb; er belegt noch keine Nachfrage.

| Beteiligte | Was sie beurteilen |
|---|---|
| Forschungsteam | Nutzen und Qualität der Ergebnisse, akzeptable Wartezeit |
| Scientific Computing oder IT | Schnittstellen, Hardware, Reproduzierbarkeit, Integration |
| Informationssicherheit | Datenklassifikation, Bedrohungen, Schlüssel, Zugriff und Betrieb |
| Einkauf und Rechtsabteilung | Gesamtpreis, Verantwortlichkeiten, Datenverwendung, Beendigung |
| Nachhaltigkeitsteam | Gemessene Wärmenutzung und belastbare Bilanzgrenzen |

Roche, Novartis oder andere Unternehmen sind damit potenzielle Gesprächspartner, keine bestätigten Kunden oder Partner des Projekts.

## 2 Nutzen aus Sicht des Pharmakunden

Die Angebotshypothese lautet: Freigegebene, zeitlich flexible Aufträge können ausgelagert werden, ohne zusätzliche eigene Hardware anzuschaffen. Der Kunde erhält einen transparenten Preis, überprüfbare Ergebnisse und Nachweise über den Umgang mit seinen Daten. Wärmenutzung ist ein zusätzlicher Nutzen, ersetzt aber keine fachlichen und sicherheitstechnischen Anforderungen.

Eine Ersparnis besteht erst, wenn die Gesamtkosten für denselben erfolgreich erledigten Auftrag unter der tatsächlichen Alternative des Kunden liegen. Übertragungen, Integration, Wiederholungen, Softwarelizenzen und Ergebnisprüfung gehören in diesen Vergleich.

## 3 Geeignete Anwendungen

| Anwendung | Warum sie zum Konzept passt | Stand im Projekt |
|---|---|---|
| Suchindex für freigegebene biomedizinische Literatur | Dokumente lassen sich in kleine, wiederholbare Arbeitspakete aufteilen | Vorgeschlagener erster Pharma-Pilot; allgemeine Embeddings sind bereits demonstriert |
| Wiederkehrende Aktualisierung eines freigegebenen Dokumentenarchivs | Zeitlich flexible Verarbeitung neuer oder geänderter Dokumente | Kundennutzen und Auftragsvolumen noch zu bestätigen |
| Molekulares Docking in unabhängigen Paketen | Viele Protein-Ligand-Paare lassen sich als getrennte Aufgaben organisieren | Spätere Option; kein eigener Laufzeit- oder Energiebenchmark vorhanden |
| Bildanalyse mit freigegebenen Forschungsbildern | Unabhängige Bilder oder kleine Stapel ermöglichen kurze Arbeitspakete | Allgemeiner Bildanalyse-Job bisher nur modelliert |

NVIDIA beschreibt DiffDock als Modell zur Vorhersage räumlicher Protein-Ligand-Bindungsposen. Das belegt eine mögliche Anwendungsklasse, aber weder die Eignung unserer Anlage noch eine Wirkung eines untersuchten Moleküls. Modell-, Software- und Datensatzlizenzen wären vor einer Umsetzung einzeln zu prüfen. [NVIDIA DiffDock](https://docs.nvidia.com/nim/bionemo/diffdock/overview)

Grosse, eng gekoppelte Trainingsläufe und interaktive Dienste sind für den Einstieg ungünstig: Die vorhandene Steuerung und das verteilte Wärmekonzept belegen dafür noch keine ausreichende Leistungsfähigkeit. Der Pilot umfasst keine klinische Entscheidung, Produktionsfreigabe oder entsprechende Validierungszusage.

## 4 Erster Pilot mit Literaturverarbeitung

Das Forschungsteam wählt einen fachlichen Themenbereich und stellt einen freigegebenen Textbestand bereit. Alternativ wird ein geeigneter öffentlicher Bestand zusammengestellt. Aus den Texten werden Suchvektoren erzeugt; anschliessend wird bewertet, ob relevante Dokumente zuverlässig auffindbar sind.

Als öffentliche Grundlage kommt ein passend lizenzierter Teil des PMC Open Access Subset infrage. Die Lizenzbedingungen unterscheiden sich je Artikel; frei lesbare Artikel sind nicht automatisch beliebig wiederverwendbar. Automatischer Abruf erfolgt über einen von PMC dafür vorgesehenen Dienst. [PMC Open Access Subset](https://pmc.ncbi.nlm.nih.gov/tools/openftlist/)

Vorgeschlagener Umfang: zunächst 10'000 kurze Textabschnitte mit dokumentierten Nutzungsrechten. Diese Menge ist eine Pilotentscheidung und keine gemessene Kapazitätsgrenze. Das Team erstellt dazu einen kleinen, fachlich geprüften Satz von Suchfragen und relevanten Treffern.

Das Ergebnis umfasst Vektoren, Dokumentzuordnung, Modellversion, Laufprotokoll, Kosten und Qualitätsauswertung. Ein vorhandenes allgemeines Sprachmodell wird nicht ohne Prüfung als geeignetes biomedizinisches Modell behandelt. Mindestens die Suchqualität und die Behandlung langer Texte müssen neu bewertet werden.

Der bestehende Embedding-Prozess verarbeitet AG-News-Texte auf einer Laptop-CPU. Er beweist Pause und Wiederanlauf; ein biomedizinischer Datensatz, eine frei wählbare Eingabe und die Ausführung auf NVIDIA-GPUs sind damit noch nicht implementiert oder gemessen.

## 5 Zwei klar getrennte Leistungsangebote

### 5.1 Flexible Verarbeitung

Aufträge dürfen warten und unterbrochen werden. Bei der Annahme erhält der Kunde eine Kapazitätseinschätzung sowie ein Recht auf Abbruch oder Rückgabe nach einer vereinbarten maximalen Wartezeit. Eine verbindliche Fertigstellung zu einem bestimmten Zeitpunkt wird nicht versprochen.

Dieses Angebot liegt dem bisherigen Spot-Szenario am nächsten. Auch hier muss eine reale Auftragswarteschlange die modellierte unbegrenzte Nachfrage ersetzen. Der Verkaufspreis für jederzeit verfügbare Kapazität darf nicht ungeprüft auf dieses eingeschränkte Angebot übertragen werden.

### 5.2 Verarbeitung mit Fertigstellungstermin

Ein Auftrag wird nur angenommen, wenn verfügbare Kapazität und Reserven den Termin tragen. Falls Wärmebedarf oder lokale Kapazität fehlen, ist ein genehmigter Ersatzstandort erforderlich. Alternativ wird der Auftrag vor Annahme abgelehnt. Neue Standorte müssen dieselben vereinbarten Daten- und Sicherheitsbedingungen erfüllen.

Die Ersatzkapazität, zusätzliche Übertragungen und Wiederanläufe gehören in den Preis und in die Firmenrechnung. Das bisherige Abgeben eines Jobs im Modell führt lokal zu keinem Erlös und bildet noch keinen vollständigen bezahlten Ersatzbetrieb ab.

Unterbrechbare Rechenleistung ist ein etabliertes Cloud-Prinzip: AWS dokumentiert für Spot-Instanzen Unterbrechungshinweise, typischerweise zwei Minuten vor Stoppen oder Beenden, mit Ausnahmen und auf Best-Effort-Basis. Daraus folgt keine identische Dienstgüte von DigitalHeat. [AWS Spot-Unterbrechungen](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html)

## 6 Preis und Abrechnung

Die bestehende Firmenrechnung verwendet als Szenarien 0,86 und 1,395 USD je L40S-GPU-Stunde. Der höhere Wert entsteht aus 25 Prozent Abschlag auf den im Projekt hinterlegten Vergleichswert von 1,86 USD. Diese Werte sind übernommene Modellannahmen und keine neu bestätigten Marktpreise oder Kundenangebote.

Rechenbeispiel für 2'000 vergleichbare, erfolgreich abrechenbare GPU-Stunden:

| Preisannahme | Reine Rechenkosten |
|---|---:|
| Hinterlegter Vergleichswert 1,86 USD | 3'720 USD |
| Modellpreis DigitalHeat 1,395 USD | 2'790 USD |
| Rechnerische Differenz | 930 USD beziehungsweise 25 Prozent |

Der Vergleich gilt nur bei gleicher Hardwareleistung, Ergebnisqualität und vergleichbaren Bedingungen. Die Differenz kann durch Integration und Zusatzkosten aufgezehrt werden. Ein rabattierter oder unterbrechbarer Vergleichstarif kann günstiger sein als die bisher verwendete Alternative.

Für den Pilot wird ein Kostendach je angenommenem Auftrag vorgeschlagen. Vor Annahme werden Hardwareklasse, Abrechnungseinheit und Qualitätskriterien festgelegt. Pausen, reine Wartezeit und technisch fehlgeschlagene Versuche werden nach diesem Vorschlag nicht dem Kunden berechnet; sie bleiben Kosten von DigitalHeat. Fachlich gültige negative Forschungsergebnisse sind keine technischen Fehlschläge.

## 7 Verbindung mit der Firmenrechnung

Die Abrechnung muss tatsächliche, akzeptierte Rechenarbeit von Energieverbrauch trennen. Für die weitere Modellierung werden mindestens zwei unabhängige Grössen benötigt:

- Strom für Rechnen, Bereitschaft, Kühlung und Nebenverbrauch.
- Erfolgreich abrechenbare GPU-Zeit auf eindeutig spezifizierter Hardware.

Die derzeitige direkte Umrechnung aus Serverstunden in vollständig verkaufte GPU-Stunden wird durch gemessene Kapazität, tatsächlich angenommene Aufträge und einen Abrechnungsfaktor ersetzt. Wiederholungen und Sicherheitsprüfungen können Strom verbrauchen, ohne abrechenbare Arbeit zu erzeugen.

Die bestehenden Ergebnisse zeigen den kleinen Spielraum: Bei Gratiswärme und 0,86 USD je GPU-Stunde erzielt das Referenzhaus mit flexibler Nachfrage rund 4'982 CHF Modellgewinn pro Jahr, das Durchschnittshaus rund 354 CHF. Bei unveränderten Kosten und fünf Prozent weniger Rechenerlös verbleiben rund 2'222 CHF beziehungsweise ein Verlust von rund 1'254 CHF. Das ist eine Erlössensitivität, keine Prognose eines konkreten Ausfalls.

Sicherheitsbetrieb, passende Hardware, Schlüsselverwaltung, Softwarelizenzen, Prüfungen und Ersatzkapazität müssen zusätzlich mit realen Angeboten in die Rechnung eingehen. Eine Umstellung auf andere GPUs erfordert neue Leistungs-, Strom- und Kostenwerte.

## 8 Nachvollziehbare Wärmenutzung

Der Pharmakunde kann einen Bericht über die seiner Rechenarbeit zugeordnete genutzte Wärme erhalten. Dafür werden Stromverbrauch, Wärmeübergabe, Speicheränderung und abgeführte Wärme gemessen. Eine Zuordnungsmethode verhindert, dass dieselbe Wärme mehreren Rechenkunden vollständig zugerechnet wird.

Das Modell nimmt 80 Prozent nutzbare Wärme an. Der tatsächliche Anteil ist im Pilot zu messen. Aus genutzten Kilowattstunden allein folgt weder CO2-Neutralität noch eine bestimmte Emissionsersparnis. Eine solche Aussage benötigt eine eigene Bilanz mit Stromherkunft, Referenzheizung und klaren Grenzen.

## 9 Auftrag und Ergebnisnachweis

1. Der Kunde klassifiziert Daten und Auftrag und genehmigt die vorgesehenen Standorte.
2. DigitalHeat prüft Ressourcen, Preis und gegebenenfalls Termin vor Annahme.
3. Daten werden verschlüsselt an einen freigegebenen Endpunkt übertragen.
4. Ein berechtigter Auftrag wird in einer geprüften, getrennten Umgebung ausgeführt.
5. Ergebnisse und Checkpoints erhalten eine überprüfbare Zuordnung zum Auftrag.
6. Der Kunde erhält Ergebnis, Laufnachweis und Abrechnung.
7. Daten und Schlüssel werden nach dem vereinbarten Aufbewahrungsplan entfernt oder gesperrt; Backups werden berücksichtigt.

Modellversion, Eingabe-Prüfsumme, Softwareumgebung und relevante Parameter werden dokumentiert. Bei nicht deterministischen GPU-Verfahren wird vorab eine fachliche Ergebnistoleranz festgelegt. Die auf dem Laptop beobachtete bitgenaue Wiederaufnahme ist keine allgemeine Garantie für jede GPU-Anwendung.

## 10 Abnahme des Pilots

| Prüffrage | Vorgeschlagener Nachweis |
|---|---|
| Ist das Ergebnis brauchbar | Fachliche Suchauswertung gegen dieselbe Aufgabe auf der Referenzumgebung |
| Funktionieren Unterbruch und Wiederanlauf | Kontrollierter Stopp, Neustart und Ergebnisvergleich |
| Sind Kosten vergleichbar | Gesamtkosten je akzeptiertem Ergebnis einschliesslich Integration und Wiederholungen |
| Sind Daten geschützt | Prüfung der Anforderungen in Abschnitt 11 mit dokumentierten Ergebnissen |
| Passt die Arbeit zum Wärmebetrieb | Gemessene Wartezeit, Strom, Wärmenutzung und Backupbedarf |
| Gibt es kaufbare Nachfrage | Konkrete Folgeaufträge oder eine schriftliche Mengen- und Preisaussage |

Zielwerte für Qualität, Wartezeit und Kosten werden vor dem Pilot mit dem Kunden festgelegt. Der bestehende Demonstrator liefert dafür noch keine pharmazeutisch validierten Grenzwerte.

## 11 Datensicherheit als Voraussetzung

Die Sicherheitsanforderung des Projekts lautet: Pharma-Daten müssen bei Übertragung und Speicherung verschlüsselt werden. Zusätzlich wird geprüft, wie Daten während der Berechnung vor unberechtigtem Zugriff geschützt werden. Schlüsselkontrolle, Zugriffsschutz und überprüfbarer Betrieb sind Teil des Angebots und keine optionale Zusatzleistung für vertrauliche Aufträge.

Das folgende Konzept beschreibt Anforderungen an die geplante Anlage. Die Schutzfunktionen sind im aktuellen Demonstrator nicht als vollständige Sicherheitsarchitektur umgesetzt oder geprüft.

### 11.1 Daten und Bedrohungen

Geschützt werden Eingabedaten, Forschungsergebnisse, Modellgewichte, Suchvektoren, Checkpoints, temporäre Dateien und Schlüssel. Auch aus einem Embedding kann vertrauliche Information hervorgehen; Vektoren werden nicht automatisch als anonym behandelt.

Das Bedrohungsmodell berücksichtigt unter anderem fremde Netzteilnehmer, andere Kunden, gestohlene Datenträger, physisch zugängliche Geräte im Haus sowie kompromittierte oder zu weit berechtigte Administrationskonten. Der Kunde entscheidet ausdrücklich, ob Daten auch gegenüber dem Betreiber vertraulich bleiben müssen. Davon hängt die erforderliche Laufzeitisolation ab.

### 11.2 Verschlüsselung bei Übertragung und Speicherung

Als Architekturvorgabe werden TLS 1.3 für die Datenübertragung und gegenseitige Geräteauthentisierung vorgesehen. Die Verschlüsselung endet erst an einem für die jeweilige Schutzklasse genehmigten Endpunkt. Ein beliebiger zentraler Proxy darf vertrauliche Inhalte nicht unbemerkt entschlüsseln. Ein zusätzliches VPN kann Netze trennen, ersetzt aber weder Endpunktschutz noch Zugriffsrechte.

Persistente Nutzdaten werden mit etablierten Verfahren verschlüsselt, etwa über LUKS2 für Datenträger und authentifizierte Objektverschlüsselung. Beim Einsatz von AES-256-GCM sind geprüfte Bibliotheken und eine sichere Nonce-Verwaltung erforderlich. Checkpoints, temporäre Dateien, Auslagerungsspeicher und Backups werden einbezogen. Rohinhalte und Geheimnisse gehören nicht in Betriebsprotokolle.

Festplattenverschlüsselung schützt insbesondere ausgeschaltete beziehungsweise gesperrte Datenträger. Sie verhindert allein nicht, dass ein berechtigter oder kompromittierter laufender Host entschlüsselte Daten liest. Transportverschlüsselung hat dieselbe Grenze am entschlüsselnden Endpunkt.

### 11.3 Schlüssel und Zugriffsrechte

Schlüssel werden nach Kunde und Auftrag getrennt, über einen kontrollierten Schlüsseldienst verwaltet und nicht neben verschlüsselten Daten als Klartext abgelegt. Für vertrauliche Aufträge wird eine kundenseitig kontrollierte Freigaberichtlinie angestrebt. Der Hauseigentümer erhält weder Nutzdatenzugang noch Schlüssel.

Personenzugriffe benötigen individuelle Konten, Mehrfaktor-Authentisierung, geringe Berechtigungen und protokollierte Freigaben. Wartungszugänge sind zeitlich begrenzt. Es werden keine gemeinsamen Administratorpasswörter verwendet. Zertifikate und Schlüssel müssen widerrufbar und erneuerbar sein.

Beim Widerruf werden neue Freigaben gesperrt und betroffene laufende Aufträge kontrolliert beendet. Widerruf kann bereits kopierte Klartexte oder bereits offengelegte Schlüssel nicht nachträglich zurückholen. Löschbestätigungen berücksichtigen Aufbewahrungsfristen, Backups und bereits ausgelieferte Ergebnisse.

### 11.4 NVIDIA Grafikkarten und Schutz während der Berechnung

In die geplanten Server werden NVIDIA-Grafikkarten eingebaut. Das konkrete Modell ist noch nicht festgelegt. Die bisherige Firmenrechnung mit L40S beschreibt ein Kosten- und Leistungsszenario; sie ist keine bestätigte Beschaffungsentscheidung und kein Nachweis für geschützte Verarbeitung.

Eine normale GPU-Verarbeitung entschlüsselt Daten für die Berechnung. Deshalb wird für Aufträge, deren Daten auch gegenüber privilegierten Hostadministratoren geschützt werden müssen, eine geeignete Confidential-Computing-Umgebung vorausgesetzt. Das bedeutet geschützte Ausführung mit einer vorab überprüften Vertrauensgrenze, nicht eine beliebige Berechnung auf dauerhaft verschlüsselten Zahlen.

NVIDIA führt für seine Confidential-Containers-Referenzarchitektur unter anderem H100 und H200 auf und verlangt passende Hostplattformen. L40S ist in dieser geprüften Liste nicht aufgeführt; ihre Eignung für diese Architektur wird daher nicht unterstellt. Die gesamte Kombination aus GPU, CPU, Firmware und Software muss unterstützt und geprüft sein. [NVIDIA unterstützte Plattformen](https://docs.nvidia.com/confidential-computing/containers/supported-platforms)

Vor einer Schlüsselfreigabe werden die genehmigte CPU- und GPU-Umgebung sowie die vorgesehene Anwendung überprüft. Dieser Nachweis heisst Attestierung. Veraltete, manipulierte oder nicht genehmigte Konfigurationen erhalten keine neuen Auftragsschlüssel. NVIDIA beschreibt dafür Attestierung und richtliniengesteuerte Freigabe von Geheimnissen. Die konkrete Schutzwirkung bleibt von Architektur und Bedrohungsmodell abhängig. [NVIDIA Confidential Computing](https://docs.nvidia.com/confidential-computing/overview)

Confidential Computing ersetzt keine Prüfung gegen sämtliche physischen Angriffe oder Seitenkanäle. Der Schutz vor Administratoren, anderen Kunden und lokalem Zugriff muss an der tatsächlich aufgebauten Anlage nachgewiesen werden. Bis dahin werden nur ausdrücklich für die Pilotumgebung freigegebene Daten verarbeitet.

### 11.5 Standort und laufender Betrieb

Das Gehäuse wird abgeschlossen und Manipulationen werden erfasst. Server-, Haus- und Verwaltungsnetz werden getrennt; unnötige Dienste und Anschlüsse bleiben gesperrt. Wartung, sichere Aktualisierung, Integritätsprüfung und Sicherheitsvorfälle erhalten dokumentierte Abläufe.

Eine Standortzusage umfasst auch Backups, Protokolle, Schlüsselverwaltung, Administration und Ersatzstandorte. Ein Server in der Schweiz allein beweist keine vollständige Datenhaltung in der Schweiz. Für vertrauliche Aufträge ist jeder Datenweg vorab zu genehmigen.

Für einen Sicherheitsvorfall werden Verantwortliche, Sperrmöglichkeiten, Beweissicherung, Benachrichtigung und Wiederanlauf vereinbart. Sicherheitsüberwachung bleibt auch dann aktiv, wenn gerade keine Wärme gebraucht wird; ihr Stromverbrauch gehört in die Bilanz.

### 11.6 Sicherheitsabnahme

Vor Verarbeitung vertraulicher Daten werden mindestens folgende Nachweise verlangt:

- Verschlüsselte Übertragung mit Prüfung und Ablehnung nicht berechtigter Gegenstellen.
- Schutz gestohlener Datenträger sowie verschlüsselte Checkpoints und Backups.
- Nachweis, dass unberechtigte Kundenkonten und Wartungsrollen keine fremden Daten lesen können.
- Bei gefordertem Betreiberschutz: CPU- und GPU-Attestierung, an die genehmigte Anwendung gebundene Schlüsselfreigabe und ein negativer Test mit veränderter Konfiguration.
- Geprüfte Schlüsselrotation, Widerruf, Auftragsbeendigung und Löschabläufe.
- Unabhängige Sicherheitsprüfung und dokumentierte Freigabe durch den Pharmakunden.

Ein erfolgreicher Pilot mit öffentlichen Daten ersetzt diese Freigabe nicht. Eine Zertifizierung oder regulatorische Eignung wird erst genannt, wenn der entsprechende Nachweis tatsächlich vorliegt.

## 12 Zusammenarbeit der drei Perspektiven

| Pharma benötigt | Firma muss einplanen | Haushalt muss akzeptieren |
|---|---|---|
| Vertrauliche Verarbeitung | Geeignete Hardware, Schlüsselverwaltung und geprüften Sicherheitsbetrieb | Abgeschlossenes Gerät ohne Datenzugang |
| Verwertbare Ergebnisse | Qualitätskontrolle und nicht abrechenbare Wiederholungen | Wärme folgt gegebenenfalls einer unterbrochenen Berechnung |
| Fertigstellungstermine | Genehmigte Ersatzkapazität und deren Kosten | Backup-Heizung bleibt funktionsfähig |
| Transparente Kosten | Abrechnung nach akzeptierter Leistung | Wärmepreis wird separat vereinbart |
| Nachvollziehbare Wärmenutzung | Messung und eindeutige Zuordnung | Zugang für genehmigte Wartung und Messung |

Das Modell trägt nur, wenn diese Bedingungen gleichzeitig erfüllbar sind. Sicherheitskosten dürfen nicht aus der Firmenrechnung verschwinden. Ein Wärmepreis darf nicht gleichzeitig als kostenlose Leistung versprochen und als tatsächlicher Firmenumsatz verbucht werden. Mehr Wärmebedarf ersetzt keine Nachfrage nach bezahlter Rechenarbeit.

## 13 Nächste konkrete Schritte

1. Mit einem Forschungsteam einen freigegebenen Literaturauftrag und fachliche Abnahmekriterien definieren.
2. Den vorhandenen Embedding-Prozess für diesen Datensatz erweitern und Qualität, Pause und Wiederanlauf prüfen.
3. Mit der Informationssicherheit Datenklassen, Bedrohungsmodell und Betreiberzugriff festlegen.
4. Eine dazu passende NVIDIA-GPU samt Hostplattform auswählen und ein reales Angebot einholen.
5. Auf dieser Hardware Durchsatz, Energie, Sicherheitsfunktionen und tatsächlich abrechenbare Arbeit messen.
6. Firmen- und Wärmemodell mit diesen Werten aktualisieren und erst danach ein belastbares Folgeangebot formulieren.

Die sofort nutzbare Positionierung lautet: DigitalHeat entwickelt flexible Rechenleistung für freigegebene Forschungsaufträge mit überprüfbarem Datenschutz- und Sicherheitskonzept und gemessener Wärmenutzung. Ein erster Pilot soll Qualität, Kosten und sichere Verarbeitung belegen.
