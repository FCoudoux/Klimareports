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

- `scripts/02_ndvi_gernsbach.py` – berechnet NDVI (Vegetationsindex) für
  Gernsbach aus Sentinel-2-L2A-Daten (Sommer 2025) über das Copernicus Data
  Space Ecosystem (CDSE), Zugriff per openEO. Ergebnis: `outputs/gernsbach_ndvi.tif`
  (Median-Komposit, nicht versioniert) und `outputs/gernsbach_ndvi.png`
  (Übersichtskarte, versioniert).

Weitere Schritte der Pipeline (Oberflächentemperatur aus Landsat,
Versiegelungsgrad aus CLMS, Zensus-Überlagerung, Report-Generierung) sind
gemäß `PROJECT_CONTEXT.md`, Teil C, geplant, aber **nicht** Teil dieses Tasks.

## Setup

**Empfohlen: conda/conda-forge.** Das Projekt hängt von GDAL/PROJ/GEOS ab
(transitiv über geopandas, rasterio, rioxarray). Diese C-Bibliotheken lassen
sich über `pip install` auf vielen Systemen nur durch Kompilieren aus dem
Quellcode installieren (kein Wheel für die jeweilige Python-/macOS-Version
verfügbar) - das kann fehlschlagen oder unnötig lange dauern. Über
`brew install gdal proj` besteht zusätzlich das Risiko, dass Homebrew ohne
passendes Bottle für ältere macOS-Versionen ebenfalls alles aus dem
Quellcode baut (inkl. schwerer Abhängigkeiten wie LLVM). conda-forge liefert
GDAL/PROJ/GEOS dagegen als fertige Binärpakete aus - deutlich schneller und
zuverlässiger:

```bash
conda create -n klimacheck -c conda-forge python=3.11 geopandas rioxarray rasterio \
  pystac-client planetary-computer openeo shapely pyproj matplotlib contextily \
  python-dotenv -y
conda activate klimacheck
```

**Alternative: venv + pip** (`requirements.txt`), funktioniert nur zuverlässig,
wenn für die eigene Python-Version/Plattform passende Wheels für GDAL/PROJ/GEOS
auf PyPI vorliegen:

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

## Task 2: NDVI aus Sentinel-2 (CDSE / openEO)

`scripts/02_ndvi_gernsbach.py` fragt Sentinel-2-L2A-Szenen (Sommer 2025,
Juni–August, max. 20 % Wolken über der Szene als Startwert) über dem
Gemeindegebiet Gernsbach ab, berechnet NDVI = (B08-B04)/(B08+B04) je Szene,
maskiert auf die exakte Gemeindegrenze und bildet daraus einen Median-Komposit
über alle wolkenfreien Termine.

**Zugang:** Copernicus Data Space Ecosystem (CDSE), OAuth2-Client-Credentials-
Flow. Benötigt einen Sentinel-Hub-OAuth-Client (siehe
https://dataspace.copernicus.eu/ → Kontoeinstellungen). Die Zugangsdaten
werden **ausschließlich** aus der lokalen `.env`-Datei geladen (nicht
versioniert, siehe `.gitignore`) und dürfen nie im Code oder in
Konfigurationsdateien landen, die committet werden:

```bash
# .env (lokal, nicht committen)
CDSE_CLIENT_ID=...
CDSE_CLIENT_SECRET=...
```

**Aufruf:**

```bash
python scripts/02_ndvi_gernsbach.py
# Wolkenbedeckungs-Schwelle (Startwert 20 %) bei Bedarf anpassen:
python scripts/02_ndvi_gernsbach.py --max-cloud-cover 30
```

Fehlen die Umgebungsvariablen oder schlägt die openEO-Authentifizierung fehl,
bricht das Skript mit einer klaren Fehlermeldung ab (kein Platzhalterwert,
kein alternativer Zugang). Sind für den Sommer weniger als 3 wolkenfreie
Termine verfügbar, gibt das Skript eine explizite Warnung aus, rechnet aber
mit den verfügbaren Daten weiter.

Ergebnis: `outputs/gernsbach_ndvi.tif` (GeoTIFF, nicht versioniert) und
`outputs/gernsbach_ndvi.png` (Karte mit Farbskala Braun/Grau = wenig
Vegetation, Grün = viel Vegetation). Am Ende gibt das Skript eine
Sichtprüfungs-Zusammenfassung aus: Anzahl genutzter Szenen, Zeitraum der
Termine, Min/Max/Median-NDVI über dem Gemeindegebiet.

## Projektstruktur

```
.
├── PROJECT_CONTEXT.md          # Businessplan & methodische Leitplanken
├── requirements.txt
├── scripts/
│   ├── 01_load_geometry.py
│   └── 02_ndvi_gernsbach.py
├── data/                       # GeoJSON-Ergebnisse (versioniert)
└── outputs/                    # PNG-Übersichtskarten (versioniert),
                                 # große Rasterdateien (nicht versioniert)
```
