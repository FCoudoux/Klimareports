# PROJECT_CONTEXT.md — Klima-Check für Kommunen

Dieses Dokument ist der Referenzkontext für alle Coding-Aufgaben in diesem Repository.
Lies es vollständig, bevor du Code schreibst oder änderst.

## Was das Projekt ist

Automatisiert erzeugter Klimaanpassungs-Report für kleine und mittlere deutsche
Gemeinden (Zielgröße 5.000–50.000 Einwohner), basierend ausschließlich auf frei
verfügbaren Satelliten- und Geodaten. Kennzahlen: Oberflächentemperatur-Anomalie,
Versiegelungsgrad, Vegetationsausstattung (NDVI), Betroffenheit (Überlagerung mit
Bevölkerung und sensiblen Einrichtungen).

**Aktuelle Phase: Phase 1 — Technischer Durchstich.**
Ziel: für eine einzelne Gemeinde (Gernsbach) die drei Kernkennzahlen manuell/skriptbasiert
erzeugen und per Sichtprüfung validieren. Noch KEINE Automatisierung für beliebige
Gemeinden, noch KEIN Report-Layout, noch KEIN Textgenerierung. Nur: funktionieren die
Daten für eine Gemeinde dieser Größe?

**Erfolgskriterium dieser Phase:** Die Karte muss innerhalb der Gemeinde erkennbar
differenzieren (z. B. Ortskern/Gewerbe wärmer als Wald/Wiesen) — nicht nur technisch
fehlerfrei laufen. Wenn die Auflösung nicht reicht, ist das ein valides Ergebnis, kein
Implementierungsfehler.

## Pilotgemeinden

| Gemeinde | AGS | Charakteristik |
|---|---|---|
| Gernsbach | 08216017 | Verdichtete Kleinstadt im Murgtal, Landkreis Rastatt |
| Sinzheim | 08216049 | Flächige Gemeinde, 9 Ortsteile, davon 3 als Exklaven in der Gemarkung Baden-Baden (Mehrfachpolygon!) |
| Baden-Baden | 08211000 | Stadtkreis, 56.526 EW — Komfort-/Vergleichsfall, nicht repräsentativ fürs Zielsegment |

**Reihenfolge: erst Gernsbach vollständig, dann erst Sinzheim/Baden-Baden.**

## Datenquellen (nur diese verwenden, nichts substituieren ohne Rücksprache)

| Kennzahl | Quelle | Zugang | Wichtig |
|---|---|---|---|
| Gemeindegeometrie | BKG VG250 | Open Data, kein Login | dl-de/by-2-0 Lizenz, Attribution nötig |
| Oberflächentemperatur (LST) | Landsat 8/9 Collection 2 Level-2 (Band ST) | Microsoft Planetary Computer STAC, kein Konto nötig für Lesezugriff | Sentinel-2 hat KEINEN Thermalkanal — LST kommt ausschließlich aus Landsat |
| Vegetation (NDVI) | Sentinel-2 L2A | Copernicus Data Space Ecosystem (CDSE), Login erforderlich | Auflösung 10 m |
| Versiegelungsgrad | Copernicus Land Monitoring Service (HRL Imperviousness) | land.copernicus.eu, Login erforderlich | fertiges Produkt, kein Eigenmodell |

## Methodische Leitplanken (nicht verhandelbar, auch nicht für Prototyp-Code)

1. **Immer in UTM rechnen, nie in WGS84.** EPSG:25832 (West) oder EPSG:25833 (Ost) für
   alle Flächen- und Rasterberechnungen. WGS84 nur für Anzeige/Web.
2. **Oberflächentemperatur ≠ Lufttemperatur ≠ thermische Belastung des Menschen.**
   Diese Unterscheidung muss in jedem Kommentar/jeder Dokumentation, die diese Werte
   beschreibt, sauber bleiben. Niemals "Hitzebelastung" schreiben, wenn eigentlich
   "Oberflächentemperatur-Anomalie" gemeint ist.
3. **Keine absoluten Temperaturschwellen.** Klassifizierung erfolgt als relative
   Anomalie (Abweichung vom Mittelwert des Gemeindegebiets), nicht als fixer °C-Wert.
4. **Wolkenfilterung ist Pflicht, nicht optional.** Landsat-Szenen ohne ausreichende
   Wolkenfreiheit über dem Gemeindegebiet müssen verworfen werden, nicht interpoliert.
5. **Kein stilles Falschergebnis.** Wenn Daten fehlen oder unzureichend sind (z. B. zu
   wenige wolkenfreie Szenen in einem Sommer), muss der Code einen klaren Fehler/Hinweis
   ausgeben — nie einen Platzhalterwert.
6. **Mehrere Sommer aggregieren**, nicht nur einen (Bewölkungsproblem Mitteleuropa).
   Für den Phase-1-Durchstich: mindestens 3 Sommertermine, wenn verfügbar.

## Tech-Stack (bewusst schlicht halten, kein Overengineering)

```
Python 3.11+
Datenzugriff:  openeo, pystac-client, planetary-computer, requests
Raster:        rioxarray, xarray, rasterio, odc-stac
Vektor:        geopandas, shapely, pyproj
Analyse:       numpy, pandas, scipy
Karten:        matplotlib, contextily
```

Keine Datenbank, kein Kubernetes, kein Web-Frontend in dieser Phase. Ziel ist ein
Skript, das für eine Gemeinde eine PNG-Karte pro Kennzahl erzeugt.

## Zugangsdaten — striktes Verbot

**Niemals CDSE-, Sentinel-Hub- oder sonstige API-Zugangsdaten im Code, in Kommentaren,
in Konfigurationsdateien, die committed werden, oder in Umgebungsvariablen-Feldern von
Cloud-/Web-Sessions ablegen.** Zugangsdaten werden ausschließlich lokal über eine
`.env`-Datei geladen, die in `.gitignore` steht. Wenn ein Task Zugangsdaten benötigt,
Platzhalter-Variablennamen im Code verwenden (z. B. `os.environ["CDSE_CLIENT_ID"]`)
und den tatsächlichen Wert nie ausschreiben — auch nicht in Beispielen oder Docstrings.

## Was NICHT gebaut werden soll (noch nicht)

- Kein Report-Template, kein PDF-Export
- Keine Automatisierung für beliebige Gemeinden (Pipeline-Funktion kommt erst Phase 3)
- Keine Textgenerierung
- Keine zusätzlichen Datenquellen/Module über die vier oben genannten hinaus
