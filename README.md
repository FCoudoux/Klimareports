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

- `scripts/03_lst_gernsbach.py` – berechnet die Oberflächentemperatur-Anomalie
  für Gernsbach aus Landsat 8/9 Collection 2 Level-2-Daten (Band ST, Sommer
  2021–2025) über den Microsoft Planetary Computer STAC-Katalog. Ergebnis:
  `outputs/gernsbach_lst_anomaly.tif` (nicht versioniert) und
  `outputs/gernsbach_lst_anomaly.png` (Übersichtskarte, versioniert).

Weitere Schritte der Pipeline (Versiegelungsgrad aus CLMS, Zensus-Überlagerung,
Report-Generierung) sind gemäß `PROJECT_CONTEXT.md`, Teil C, geplant, aber
**nicht** Teil dieses Tasks.

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
  python-dotenv numpy -y
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

## Task 3: Oberflächentemperatur-Anomalie aus Landsat 8/9 (Planetary Computer)

`scripts/03_lst_gernsbach.py` fragt Landsat 8/9 Collection 2 Level-2-Szenen
(Band ST, Sommer Juni–August, Jahre 2021–2025) über den Microsoft Planetary
Computer STAC-Katalog ab. Sentinel-2 hat keinen Thermalkanal – die
Oberflächentemperatur kommt ausschließlich aus Landsat.

**Wolkenfilterung erfolgt zweistufig:**
1. Szenen-Ebene: `eo:cloud_cover` unter der Schwelle (Startwert 20 %) und
   nur Tier-1-Szenen (höchste radiometrische/geometrische Präzisionsstufe).
2. Pixel-Ebene: Das QA_PIXEL-Band wird für jede Szene über dem Gemeindegebiet
   ausgewertet (Bits für Wolke, Wolkenschatten, Cirrus, Wolken-Dilatation)
   und maskiert betroffene Pixel einzeln aus – nicht nur szenenweise. Bleiben
   dadurch weniger als 50 % der Gemeindefläche wolkenfrei, wird die Szene
   verworfen, auch wenn ihre Szenen-Wolkenbedeckung unauffällig war (das war
   die Schwäche im NDVI-Skript aus Task 2, die hier gezielt vermieden wird).

Das ST-Band wird nach der offiziellen USGS-Skalierungsformel für Landsat
Collection 2 Level-2 in Grad Celsius umgerechnet
(`Kelvin = DN * 0.00341802 + 149.0`, dann `- 273.15`), auf EPSG:25832
reprojiziert und auf die exakte Gemeindegeometrie maskiert.

**Mittelung ist hierarchisch, nicht flach:** zuerst wird je Sommer über die
nutzbaren Termine gemittelt, dann über die (bis zu) 5 Sommermittel – jeder
Sommer geht damit gleich stark ein, unabhängig davon, wie viele wolkenfreie
Termine er liefert. Ein einfacher Durchschnitt über alle Einzeltermine würde
Sommer mit mehr wolkenfreien Terminen systematisch stärker gewichten – genau
das Bewölkungsproblem, das die Mehrsommer-Aggregation eigentlich ausgleichen
soll. Aus dem hierarchischen Mittelwert je Pixel wird die **Anomalie**
berechnet: Pixelwert minus Mittelwert des gesamten Gemeindegebiets – **keine
absoluten Temperaturschwellen** (siehe `PROJECT_CONTEXT.md`, Methodik-Regel 3).

**Aufruf:**

```bash
python scripts/03_lst_gernsbach.py
# Schwellenwerte bei Bedarf anpassen:
python scripts/03_lst_gernsbach.py --max-cloud-cover 30 --min-flaechenanteil 40
```

Werden über alle Sommer keine nutzbaren Termine gefunden, oder liegen
nutzbare Termine nur in einem einzigen Sommer vor (Aggregation über mehrere
Sommer laut Methodik zwingend, wegen des Bewölkungsproblems in
Mitteleuropa), bricht das Skript mit einer klaren Fehlermeldung ab – **kein
Fallback auf einen einzelnen Termin oder Sommer**. Sind insgesamt oder je
Sommer weniger als 3 nutzbare Termine verfügbar, gibt das Skript eine
explizite Warnung aus, rechnet aber mit den verfügbaren Daten weiter.

**Bekannte Limitierung:** Landsat überfliegt Gernsbach vormittags (Ortszeit ca.
10:30) – das Nachmittagsmaximum der Aufheizung wird dadurch nicht erfasst,
die Anomalie unterschätzt tendenziell die maximale Tagesamplitude (siehe
`PROJECT_CONTEXT.md`).

Ergebnis: `outputs/gernsbach_lst_anomaly.tif` (GeoTIFF, nicht versioniert)
und `outputs/gernsbach_lst_anomaly.png` (Karte mit Farbskala Blau = kühler
als Gemeindemittel, Rot = wärmer als Gemeindemittel). Am Ende gibt das
Skript eine Sichtprüfungs-Zusammenfassung aus: Anzahl verwendeter/verworfener
Szenen je Sommer, Wertebereich der Anomalie in Grad Celsius.

**Wichtig – Begriffsklarheit (Methodik-Regel 2):** Das Ergebnis ist
ausschließlich die Oberflächentemperatur (Landoberfläche), **nicht** die
Lufttemperatur und **nicht** die thermische Belastung von Menschen. Diese
Unterscheidung gilt für jede Interpretation der Karte.

## Sinzheim (AGS 08216049)

Zweite Pilotgemeinde nach Gernsbach (siehe `PROJECT_CONTEXT.md`,
Pilotgemeinden-Tabelle), mit eigenen, auf Sinzheim zugeschnittenen Skripten
je Kennzahl – **keine** generische Mehrgemeinden-Automatisierung (die ist
laut `PROJECT_CONTEXT.md` erst für Phase 3 vorgesehen):

- `scripts/01_load_geometry_sinzheim.py`
- `scripts/02_ndvi_sinzheim.py`
- `scripts/03_lst_sinzheim.py`

**Besonderheit – MultiPolygon-Geometrie:** Sinzheim besteht aus 9 Ortsteilen,
von denen 3 als Exklaven vollständig innerhalb der Gemarkung der Stadt
Baden-Baden liegen. Die VG250-Geometrie ist deshalb ein MultiPolygon mit 4
Teilflächen (Hauptkörper + 3 Exklaven), kein einzelnes zusammenhängendes
Polygon wie bei Gernsbach. Alle drei Skripte prüfen den Geometrietyp
explizit (`geometry.geom_type`) und geben ihn aus, statt ihn stillschweigend
vorauszusetzen:

- **Fläche:** shapely summiert `MultiPolygon.area` automatisch über alle
  Teilflächen; `01_load_geometry_sinzheim.py` verifiziert das zusätzlich
  durch eine unabhängige Summierung über `geometry.geoms` und bricht ab,
  falls beide Werte voneinander abweichen. Trifft der AGS-Filter auf mehrere
  VG250-Datensätze zu, werden diese zu einer Geometrie vereinigt (`union`)
  statt stillschweigend nur den ersten Treffer zu verwenden – sonst könnten
  Exklaven unbemerkt verloren gehen.
- **NDVI/LST-Suche:** Bounding Box und räumliche Filter basieren auf
  `gdf.total_bounds`, das automatisch alle Teilflächen (inkl. Exklaven)
  abdeckt, nicht nur den größten zusammenhängenden Teil. `mask_polygon`
  (openEO) und `rasterio.features.geometry_mask` (LST) unterstützen
  MultiPolygon nativ – die Fläche der Stadt Baden-Baden zwischen den
  Exklaven bleibt dabei korrekt außerhalb der Gemeindemaske.
- **Karten:** `geopandas`-Boundary-Plots zeichnen MultiPolygon-Geometrien
  (disjunkte Teilflächen) bereits nativ vollständig; alle drei Kartenskripte
  verzichten deshalb bewusst auf eine Sonderbehandlung, weisen die Anzahl
  der Teilflächen aber explizit im Titel/in der Konsolenausgabe aus.

Ergebnisse: `data/sinzheim_boundary.geojson`, `outputs/sinzheim_boundary.png`,
`outputs/sinzheim_ndvi.tif`/`.png`, `outputs/sinzheim_lst_anomaly.tif`/`.png`.

**Hinweis zum VG250-Download:** Der direkte Remote-Zip-Zugriff
(`zip+https://...`, siehe `--url`-Option) ist bei diesem Datenstand
fehlgeschlagen, obwohl die URL selbst erreichbar war (GDAL/vsicurl konnte
das Zip-Format nicht erkennen). Funktioniert hat stattdessen: Paket lokal
laden (`curl -o ... <url>`), entpacken und `VG250_GEM.shp` über
`--local-shapefile` übergeben – dieselbe Option, die für netzwerk-
eingeschränkte Umgebungen vorgesehen ist (s.o.).

`02_ndvi_sinzheim.py` übernimmt zusätzlich die aus Gernsbach gelernte Lehre
direkt: Wolken/Schatten/Cirrus werden serverseitig über das SCL-Band (Scene
Classification Layer) **pixelgenau** ausmaskiert, bevor auf 10 m resampled
und der Median gebildet wird – nicht nur szenenweise über `eo:cloud_cover`
gefiltert (das war die im Gernsbach-NDVI-Skript offen gelassene Schwäche).

`03_lst_sinzheim.py` übernimmt von Anfang an alle Korrekturen aus dem
Gernsbach-Durchlauf: zweistufige Wolkenfilterung (Szenen-Ebene +
pixelgenau über QA_PIXEL), hierarchische Mittelung (erst je Sommer, dann
über die Sommermittel – kein einfacher Durchschnitt über alle Einzeltermine),
getrennte Konsolen-Ausgabe von Anomalie- und Absolutwerten sowie der
Hinweis auf die Landsat-Vormittags-Überflugzeit als bekannte Limitierung.

## Projektstruktur

```
.
├── PROJECT_CONTEXT.md          # Businessplan & methodische Leitplanken
├── requirements.txt
├── scripts/
│   ├── 01_load_geometry.py
│   ├── 01_load_geometry_sinzheim.py
│   ├── 02_ndvi_gernsbach.py
│   ├── 02_ndvi_sinzheim.py
│   ├── 03_lst_gernsbach.py
│   └── 03_lst_sinzheim.py
├── data/                       # GeoJSON-Ergebnisse (versioniert)
└── outputs/                    # PNG-Übersichtskarten (versioniert),
                                 # große Rasterdateien (nicht versioniert)
```
