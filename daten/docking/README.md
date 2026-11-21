# Docking: virtuelles Screening als echter Rechenauftrag

**Schlüssel-Schloss-Prinzip:** Ein Protein hat eine Bindetasche (das Schloss). Für jedes Molekül (einen Schlüssel) sucht AutoDock Vina die beste Lage in der Tasche und schätzt die Bindungsenergie in kcal/mol. Je negativer, desto besser passt der Schlüssel. Pharmafirmen testen so Millionen Moleküle am Computer, bevor sie die besten im Labor prüfen.

Der Auftrag `src/jobs/docking_job.py` rechnet das echt, auf der CPU, mit Checkpoint nach jedem Molekül. `src/scheduler/live.py --job docking` lässt ihn vom Scheduler pausieren und weiterlaufen.

## Daten und Quellen

| Was | Inhalt | Quelle |
|---|---|---|
| Schloss | Abl-Kinase mit Bindetasche, `1iep_receptor.pdbqt` | Proteinstruktur PDB 1IEP (Nagar et al. 2002, *Cancer Research* 62:4236); vorbereitete Datei aus dem Beispiel `basic_docking` von AutoDock Vina ([github.com/ccsb-scripps/AutoDock-Vina](https://github.com/ccsb-scripps/AutoDock-Vina), Apache-2.0) |
| Suchraum | Zentrum (15,190 / 53,903 / 16,917), Würfel 20 × 20 × 20 Å | `1iep_receptor.box.txt` aus demselben Beispiel |
| Schlüssel | 28 Moleküle: 10 Kinasehemmer, 10 Medikamente, 8 Alltagsmoleküle (`molekuele.csv`) | Strukturformeln (SMILES) bekannter Wirkstoffe; vorbereitet als `liganden/*.pdbqt` mit RDKit 2026.09 und Meeko 0.8 (3D-Struktur mit festem Zufallsstart 42) |
| Docking-Programm | AutoDock Vina 1.2, Suchtiefe (exhaustiveness) 8 | Eberhardt et al. 2021, *J. Chem. Inf. Model.* 61:3891; Trott & Olson 2010, *J. Comput. Chem.* 31:455 |

## Ergebnis eines vollständigen Laufs

Alle 28 Moleküle, Linux-Testrechner mit 4 Kernen (Intel Xeon 2,1 GHz), Vina als Python-Paket, Zufallsstart 1. Gesamt 384 s, im Median 5,5 s pro Molekül.

| Rang | Molekül | Gruppe | Bindungsenergie | Zeit |
|---|---|---|---|---|
| 1 | **Nilotinib** | Kinasehemmer (Leukämie) | **−13,4 kcal/mol** | 33 s |
| 2 | **Imatinib** (Glivec) | Kinasehemmer (Leukämie) | **−12,8 kcal/mol** | 26 s |
| 3 | **Ponatinib** | Kinasehemmer (Leukämie) | **−12,4 kcal/mol** | 16 s |
| 4 | Sorafenib | Kinasehemmer | −11,6 kcal/mol | 16 s |
| 5 | Lapatinib | Kinasehemmer | −11,4 kcal/mol | 51 s |
| … | Mittel der 10 Kinasehemmer | | −10,3 kcal/mol | 26 s |
| … | Mittel der 10 übrigen Medikamente | | −7,7 kcal/mol | 11 s |
| … | Mittel der 8 Alltagsmoleküle (Koffein, Glucose, Ethanol …) | | −6,1 kcal/mol | 2,5 s |

**Die drei besten Schlüssel sind echte Leukämie-Medikamente für genau dieses Protein.** Das Screening findet also, was es finden soll. Docking-Werte sind Schätzungen; sie ersetzen keinen Laborversuch.

## Auf dem Mac einrichten (einmalig)

Für den Mac gibt es Vina nicht als Python-Paket, aber als fertiges Programm. Im Projektordner:

```sh
mkdir -p tools && curl -L -o tools/vina https://github.com/ccsb-scripps/AutoDock-Vina/releases/download/v1.2.5/vina_1.2.5_mac_aarch64 && chmod +x tools/vina && tools/vina --version
```

Intel-Mac: am Ende der Adresse `vina_1.2.5_mac_x86_64` statt `vina_1.2.5_mac_aarch64`. Meldet macOS, das Programm sei nicht vertrauenswürdig: `xattr -d com.apple.quarantine tools/vina`. Der Ordner `tools/` ist nicht im Repo.

Linux oder Windows mit Python 3.10–3.12: `pip install -r requirements/docking.txt`.

## Starten

```sh
# nur das Screening, alle 28 Moleküle
python3 src/jobs/docking_job.py --arbeitsordner messungen/docking_test

# vom Scheduler gesteuert: 7. März, Pause bei vollem Speicher (3D-Modell zeigt es live)
python3 src/scheduler/live.py --tag 2025-03-07 --server 8 --sekunden 3 --job docking
```

Ergebnisse: `stand.json` im Arbeitsordner (Bindungsenergie und Zeit pro Molekül, Rangliste), beste Lage jedes Moleküls in `posen/`.

## Auf zwei Laptops hin und her (wie die Blister-Demo)

Das virtuelle Screening wandert zwischen zwei Geräten: Das Haus dockt, bis sein Wärmespeicher voll ist, übergibt den Stand per TLS ans Sportbad, und holt ihn zurück, wenn es wieder Wärme braucht. Beide Laptops im selben WLAN, auf beiden derselbe Code-Stand.

1. **Laptop B (Schwimmbad):** `python3 prototyp/schwimmbad.py` (zeigt einen 6-stelligen Code).
2. **Laptop A (Haus):** `python3 prototyp/haus.py`, Code eingeben, dann **Screening starten**. Die Übergabe läuft automatisch.

Docking ist der Standard. Für die Blisterprüfung stattdessen `--job blister` anhängen. Die Bindungsenergien stammen aus `daten/docking/ergebnis.json` (echter Vina-Lauf) und werden flüssig abgespielt. Auf einem einzelnen Laptop zum Ausprobieren: `python3 prototyp/docking_demo.py demo --open`.
