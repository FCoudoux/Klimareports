# Klimareports

Technischer Unterbau für den "Klima-Check für Kommunen" (siehe `PROJECT_CONTEXT.md`
für Businessplan und Methodik-Hintergrund). Dieses Repository enthält den
**Phase-1-Durchstich**: den ersten Baustein der Datenpipeline, der die amtliche
Gemeindegeometrie einer Pilotgemeinde lädt und aufbereitet.

## Aktueller Stand

- `scripts/01_load_geometry.py` – lädt die Gemeindegrenze von **Gernsbach**
  (AGS `08216017`) aus den BKG VG250-Verwaltungsgebieten, filtert nach dem
  amtlichen Gemeindeschlüssel, reprojiziert nach EPSG:25832, berechnet die
  Fläche in km² und vergleicht sie mit dem bekannten Referenzwert (82,03 km²)
  zur Plausibilisierung. Ergebnis: `data/gernsbach_boundary.geojson` und eine
  einfache Übersichtskarte `outputs/gernsbach_boundary.png`.

Weitere Schritte der Pipeline (NDVI aus Sentinel-2, Oberflächentemperatur aus
Landsat, Versiegelungsgrad aus CLMS, Zensus-Überlagerung, Report-Generierung)
sind gemäß `PROJECT_CONTEXT.md`, Teil C, geplant, aber **nicht** Teil dieses
Tasks.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Nutzung

```bash
# Versucht den Download direkt vom BKG-Geodatendienst
python scripts/01_load_geometry.py

# Falls kein Netzwerkzugriff möglich ist: lokal abgelegte VG250-Gemeindeebene verwenden
python scripts/01_load_geometry.py --local-shapefile /pfad/zu/vg250_gem.gpkg
```

## Datenquelle

- **BKG VG250 – Verwaltungsgebiete 1:250.000** (Stand 01.01.), Open Data,
  Lizenz `dl-de/by-2-0`, kein Login/API-Key erforderlich:
  https://gdz.bkg.bund.de/index.php/default/verwaltungsgebiete-1-250-000-stand-01-01-vg250.html

Erforderliche Attribution im späteren Report:
> Verwaltungsgeometrien: © GeoBasis-DE / BKG [Jahr] (dl-de/by-2-0).

## Bekannte Einschränkung: Netzwerkzugriff in dieser Cloud-Umgebung

In der Cloud-Sandbox, in der dieses Repository entwickelt wurde, ist
ausgehender Netzwerkzugriff auf `daten.gdz.bkg.bund.de` durch die
Netzwerk-Policy der Umgebung gesperrt (die Proxy-Gegenstelle antwortet mit
`403` auf den CONNECT-Versuch). Ein direkter Download der VG250-Daten war
in dieser Umgebung daher **nicht möglich** – unabhängig davon, dass die
Daten selbst frei und ohne Login zugänglich sind.

Bewusst **keine** Kompromisslösung mit Zugangsdaten oder Umgehung der
Netzwerk-Policy gebaut (siehe Zugangsdaten-Verbot in `PROJECT_CONTEXT.md`).
Stattdessen unterstützt `scripts/01_load_geometry.py` zwei Wege:

1. **Direkter Download** (`--url`, Standard: BKG-Geodatendienst) – funktioniert
   in Umgebungen mit normalem Internetzugang (z. B. lokal oder in CI ohne
   entsprechende Restriktion).
2. **Lokale Kopie** (`--local-shapefile`) – für Umgebungen wie diese, in denen
   das VG250-Paket vorab auf einem Rechner mit Internetzugang heruntergeladen
   und danach bereitgestellt wird.

Sentinel-2/Landsat/CDSE-Anbindung ist bewusst **nicht** Teil dieses Tasks,
da dafür Zugangsdaten nötig wären, die in dieser Cloud-Umgebung nicht sicher
gespeichert werden können. Das folgt als separater, lokal ausgeführter Schritt.

## Projektstruktur

```
.
├── PROJECT_CONTEXT.md          # Businessplan & methodische Leitplanken
├── requirements.txt
├── scripts/
│   └── 01_load_geometry.py
├── data/                       # GeoJSON-Ergebnisse (versioniert)
└── outputs/                    # PNG-Übersichtskarten (versioniert),
                                 # große Rasterdateien (nicht versioniert)
```
