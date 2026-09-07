"""
Berechnet den Versiegelungsgrad für Gernsbach (AGS 08216017) aus dem
Copernicus Land Monitoring Service (CLMS), Produkt "High Resolution Layer
Imperviousness Density" (HRL Imperviousness), Epoche 2018 (10 m, EEA38,
Referenzperiode 2017-2019).

WICHTIG (siehe Auftrag/Rücksprache): Dies ist eine ABSOLUTE Prozentkennzahl
(Versiegelungsgrad in %), KEINE Anomalie-Berechnung wie bei der Oberflächen-
temperatur. Versiegelungsgrad ist wetterunabhängig und direkt interpretierbar -
hier wird bewusst NICHT vom Gemeindemittel abweichend normiert.

BEKANNTE LIMITATION - ZEITLICHER VERSATZ ZU DEN ANDEREN KENNZAHLEN: Die
verwendete Epoche IMD 2018 (Referenzperiode 2017-2019) liegt zeitlich VOR den
Datengrundlagen der beiden anderen Kennzahlen dieses Projekts - NDVI basiert
auf Sentinel-2-Sommer 2025, die LST-Anomalie auf Landsat-Sommern 2021-2025.
Der Versiegelungsgrad ist zwar strukturell deutlich stabiler über wenige Jahre
als Vegetation/Temperatur (Bodenversiegelung ändert sich i. d. R. nur durch
Neubau/Rückbau), trotzdem ist ein Vergleich der drei Kennzahlen im Report
NICHT als "gleicher Zeitpunkt" zu verstehen. Grund für die Wahl von 2018 statt
der aktuelleren Epoche IMD 2021 (10 m): IMD 2021 ist nur über die offizielle
CLMS-Download-API abrufbar, die einen EU-Login-Service-Key mit JWT/Private-
Key-Signierung erfordert (manuelle Schlüsselerzeugung in der CLMS-Web-
oberfläche, kein einfaches Client-ID/Secret-Paar wie bei CDSE) - diese
Zugangsdaten liegen (Stand dieser Implementierung) nicht vor. IMD 2018 ist
dagegen über einen öffentlichen, anmeldefreien EEA-ArcGIS-ImageServer direkt
abrufbar (siehe unten). Diese Entscheidung wurde ausdrücklich mit dem Nutzer
abgestimmt (siehe README.md, Abschnitt Task 4).

Datenquelle/Zugangsweg: EEA-Discomap-ArcGIS-ImageServer "GioLandPublic/
HRL_ImperviousnessDensity_2018" (image.discomap.eea.europa.eu) - öffentlicher
Spiegel des offiziellen CLMS-Produkts, kein Login/API-Key nötig. Direkter
Ausschnitt über die exportImage-Operation (bbox in EPSG:25832, Server liefert
das Ergebnis bereits in EPSG:25832 zurück - kein WCS im engeren Sinn, aber
funktional äquivalent: direkter Ausschnitt statt Bulk-Kacheldownload).

Ablauf:
    1. Gemeindegeometrie aus data/gernsbach_boundary.geojson laden.
    2. Bounding Box in EPSG:25832 (+Puffer, auf 10-m-Raster gerundet) berechnen.
    3. Direkten Ausschnitt per exportImage vom EEA-ImageServer abrufen
       (bereits in EPSG:25832, 10 m, bilineare Resampling-Methode, NoData=255).
    4. Auf die exakte Gemeindegeometrie maskieren (rasterio.features.geometry_mask).
    5. Kennzahlen berechnen: Mittelwert, Min/Max, Flächenanteil mit >50 %
       Versiegelung - über das gesamte Gemeindegebiet, ABSOLUT (keine Anomalie).
    6. GeoTIFF und PNG-Karte speichern (Farbskala hell/grün=0% bis dunkel/grau=100%).

Nutzung:
    python scripts/04_imperviousness_gernsbach.py

Benötigt keine Zugangsdaten (öffentlicher EEA-ImageServer, kein Login).
"""

from __future__ import annotations

import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import requests
from matplotlib.colors import LinearSegmentedColormap, Normalize
from rasterio.features import geometry_mask
from rasterio.io import MemoryFile

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUTS_DIR = REPO_ROOT / "outputs"

GEMEINDE_NAME = "Gernsbach"
BOUNDARY_GEOJSON = DATA_DIR / "gernsbach_boundary.geojson"
TIF_OUT = OUTPUTS_DIR / "gernsbach_imperviousness.tif"
PNG_OUT = OUTPUTS_DIR / "gernsbach_imperviousness.png"

ZIEL_CRS_EPSG = 25832  # ETRS89/UTM32N - Vorgabe für alle Flächen-/Rasterberechnungen (Westdeutschland)
AUFLOESUNG_M = 10.0  # native Auflösung der HRL Imperviousness Density
PUFFER_M = 30.0  # Sicherheitsabstand ums Zielraster (3 Pixel) für sauberes Resampling am Rand

IMAGE_SERVER_EXPORT_URL = (
    "https://image.discomap.eea.europa.eu/arcgis/rest/services/GioLandPublic/"
    "HRL_ImperviousnessDensity_2018/ImageServer/exportImage"
)
CLMS_EPOCHE = "IMD 2018 (Referenzperiode 2017-2019)"
CLMS_QUELLE_TEXT = (
    "Copernicus Land Monitoring Service, High Resolution Layer Imperviousness "
    "Density 2018 (10 m), bezogen über den öffentlichen EEA-ArcGIS-ImageServer "
    "(image.discomap.eea.europa.eu), kein Login erforderlich."
)
NODATA_WERT = 255  # HRL-Imperviousness-Konvention: 255 = außerhalb Produktabdeckung
SCHWELLE_STARK_VERSIEGELT = 50.0  # Prozent

# Hell/Grün (0 % versiegelt) -> Übergangston -> Dunkel/Grau (100 % versiegelt), wie gefordert.
IMPERVIOUSNESS_CMAP = LinearSegmentedColormap.from_list(
    "hellgruen_dunkelgrau",
    ["#eaf6df", "#b9d99a", "#8a9a7a", "#5a5a5a", "#262626"],
)


def lade_gemeindegeometrie() -> gpd.GeoDataFrame:
    if not BOUNDARY_GEOJSON.exists():
        raise FileNotFoundError(
            f"Gemeindegeometrie nicht gefunden: {BOUNDARY_GEOJSON}. "
            "Bitte zuerst scripts/01_load_geometry.py ausführen."
        )
    gdf = gpd.read_file(BOUNDARY_GEOJSON)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    geometrie = gdf.geometry.iloc[0]
    if geometrie.geom_type == "MultiPolygon":
        print(
            f"Geometrietyp: MultiPolygon mit {len(geometrie.geoms)} Teilflächen - "
            "Zielraster, Gemeindemaske und Kartendarstellung berücksichtigen im "
            "Folgenden alle Teilflächen."
        )
    elif geometrie.geom_type != "Polygon":
        raise TypeError(
            f"Unerwarteter Geometrietyp '{geometrie.geom_type}' für {GEMEINDE_NAME} - "
            "erwartet wurde Polygon oder MultiPolygon. Abbruch, keine "
            "stillschweigende Weiterverarbeitung."
        )
    return gdf


def berechne_zielbbox(gdf_utm: gpd.GeoDataFrame) -> tuple[float, float, float, float]:
    """Bounding Box über ALLE Teilflächen (gdf_utm.total_bounds deckt bei einem
    MultiPolygon automatisch Hauptkörper + Exklaven/Fragmente ab), mit Puffer,
    auf das 10-m-Zielraster gerundet - analog zum Vorgehen in scripts/03_lst_*.py."""
    minx, miny, maxx, maxy = gdf_utm.total_bounds
    minx -= PUFFER_M
    miny -= PUFFER_M
    maxx += PUFFER_M
    maxy += PUFFER_M
    minx = np.floor(minx / AUFLOESUNG_M) * AUFLOESUNG_M
    miny = np.floor(miny / AUFLOESUNG_M) * AUFLOESUNG_M
    maxx = np.ceil(maxx / AUFLOESUNG_M) * AUFLOESUNG_M
    maxy = np.ceil(maxy / AUFLOESUNG_M) * AUFLOESUNG_M
    return minx, miny, maxx, maxy


def lade_imperviousness_ausschnitt(bbox_utm: tuple[float, float, float, float]) -> tuple[np.ndarray, rasterio.Affine, rasterio.CRS]:
    """Fordert per exportImage-Operation einen direkten Ausschnitt für die
    Bounding Box beim öffentlichen EEA-ImageServer an (kein Bulk-Kacheldownload,
    kein Login) - Server liefert das Ergebnis bereits georeferenziert in
    EPSG:25832 zurück (bilineare Resampling-Methode, da kontinuierliche
    Prozent-Größe, analog zur NDVI-/LST-Reprojektion in scripts/02_.../03_...py).

    Kein stiller Fallback: schlägt die Anfrage fehl oder liefert der Server
    einen Fehler/keine gültige Bilddatei, wird mit klarer Fehlermeldung
    abgebrochen.
    """
    minx, miny, maxx, maxy = bbox_utm
    breite_px = int(round((maxx - minx) / AUFLOESUNG_M))
    hoehe_px = int(round((maxy - miny) / AUFLOESUNG_M))

    params = {
        "bbox": f"{minx},{miny},{maxx},{maxy}",
        "bboxSR": ZIEL_CRS_EPSG,
        "imageSR": ZIEL_CRS_EPSG,
        "size": f"{breite_px},{hoehe_px}",
        "format": "tiff",
        "pixelType": "U8",
        "noData": NODATA_WERT,
        "noDataInterpretation": "esriNoDataMatchAny",
        "interpolation": "RSP_BilinearInterpolation",
        "f": "json",
    }
    print(f"Fordere Versiegelungsgrad-Ausschnitt an ({breite_px}x{hoehe_px} px, {AUFLOESUNG_M:.0f} m) ...")
    antwort = requests.get(IMAGE_SERVER_EXPORT_URL, params=params, timeout=60)
    antwort.raise_for_status()
    meta = antwort.json()
    if "error" in meta:
        raise RuntimeError(
            f"EEA-ImageServer meldet einen Fehler bei der exportImage-Anfrage: {meta['error']}. "
            "Kein Fallback auf einen Platzhalterwert."
        )
    href = meta.get("href")
    if not href:
        raise RuntimeError(
            "EEA-ImageServer-Antwort enthält keine gültige Bild-URL ('href') - "
            f"Rohantwort: {meta}. Abbruch, kein stiller Fallback."
        )

    bild_antwort = requests.get(href, timeout=120)
    bild_antwort.raise_for_status()
    if len(bild_antwort.content) == 0:
        raise RuntimeError("Vom EEA-ImageServer heruntergeladene Bilddatei ist leer.")

    with MemoryFile(bild_antwort.content) as memfile:
        with memfile.open() as src:
            if src.crs is None or src.crs.to_epsg() != ZIEL_CRS_EPSG:
                raise RuntimeError(
                    f"Vom Server geliefertes Raster hat unerwartetes CRS ({src.crs}) - "
                    f"erwartet EPSG:{ZIEL_CRS_EPSG}. Abbruch, keine stillschweigende Annahme."
                )
            array = src.read(1)
            transform = src.transform

    print(f"Versiegelungsgrad-Ausschnitt geladen: {array.shape[1]}x{array.shape[0]} px, EPSG:{ZIEL_CRS_EPSG}.")
    return array, transform, rasterio.CRS.from_epsg(ZIEL_CRS_EPSG)


def maskiere_und_berechne(
    array: np.ndarray, transform: rasterio.Affine, gdf_utm: gpd.GeoDataFrame
) -> tuple[np.ndarray, dict]:
    """Maskiert das Raster auf die exakte Gemeindegeometrie (inkl. aller
    Teilflächen bei MultiPolygon - rasterio.features.geometry_mask unterstützt
    das nativ) UND auf gültige (Nicht-NoData-)Pixel, berechnet die Kennzahlen
    und gibt das für die Ausgabe vorbereitete Float-Raster (NaN außerhalb)
    zurück."""
    gemeinde_maske = geometry_mask(
        gdf_utm.geometry, out_shape=array.shape, transform=transform, invert=True
    )
    gueltige_maske = gemeinde_maske & (array != NODATA_WERT)

    if not np.any(gueltige_maske):
        raise RuntimeError(
            "Nach Maskierung auf die Gemeindegeometrie sind keine gültigen "
            "(Nicht-NoData-)Pixel übrig - Versiegelungsgrad kann nicht berechnet "
            "werden. Kein Platzhalterergebnis."
        )

    werte = array[gueltige_maske].astype("float64")
    gemeinde_pixelzahl = int(gemeinde_maske.sum())
    gueltige_pixelzahl = int(gueltige_maske.sum())
    if gueltige_pixelzahl < gemeinde_pixelzahl:
        fehlend = gemeinde_pixelzahl - gueltige_pixelzahl
        print(
            f"Hinweis: {fehlend} von {gemeinde_pixelzahl} Gemeindepixeln liegen außerhalb "
            "der Produktabdeckung (NoData) und bleiben unberücksichtigt."
        )

    kennzahlen = {
        "mittelwert": float(np.mean(werte)),
        "median": float(np.median(werte)),
        "min": float(np.min(werte)),
        "max": float(np.max(werte)),
        "flaechenanteil_ueber_schwelle": float(
            np.sum(werte > SCHWELLE_STARK_VERSIEGELT) / gueltige_pixelzahl * 100.0
        ),
        "gemeinde_pixelzahl": gemeinde_pixelzahl,
        "gueltige_pixelzahl": gueltige_pixelzahl,
    }

    ausgabe = array.astype("float32")
    ausgabe[~gueltige_maske] = np.nan
    return ausgabe, kennzahlen


def speichere_geotiff(array: np.ndarray, transform: rasterio.Affine, pfad: Path) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff",
        "height": array.shape[0],
        "width": array.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": f"EPSG:{ZIEL_CRS_EPSG}",
        "transform": transform,
        "nodata": np.nan,
        "compress": "deflate",
    }
    with rasterio.open(pfad, "w", **profile) as dst:
        dst.write(array, 1)
    print(f"Versiegelungsgrad-GeoTIFF gespeichert: {pfad}")


def erzeuge_karte(
    array: np.ndarray, transform: rasterio.Affine, gdf_utm: gpd.GeoDataFrame, png_pfad: Path
) -> None:
    hoehe, breite = array.shape
    xmin = transform.c
    ymax = transform.f
    xmax = xmin + breite * transform.a
    ymin = ymax + hoehe * transform.e  # transform.e ist negativ
    extent = (xmin, xmax, ymin, ymax)

    norm = Normalize(vmin=0.0, vmax=100.0)  # absolute Prozentskala, keine Anomalie

    png_pfad.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7.8, 7))
    bild = ax.imshow(array, extent=extent, origin="upper", cmap=IMPERVIOUSNESS_CMAP, norm=norm)
    gdf_utm.boundary.plot(ax=ax, color="black", linewidth=1.2)
    cbar = fig.colorbar(bild, ax=ax, shrink=0.75)
    cbar.set_label("Versiegelungsgrad [%]")
    ax.set_title(f"Versiegelungsgrad {GEMEINDE_NAME}\n({CLMS_EPOCHE}, CLMS HRL Imperviousness)")
    ax.set_xlabel(f"Rechtswert [EPSG:{ZIEL_CRS_EPSG}]")
    ax.set_ylabel(f"Hochwert [EPSG:{ZIEL_CRS_EPSG}]")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(png_pfad, dpi=150)
    plt.close(fig)
    print(f"Versiegelungsgrad-Karte gespeichert: {png_pfad}")


def main() -> int:
    gdf_wgs84 = lade_gemeindegeometrie()
    gdf_utm = gdf_wgs84.to_crs(epsg=ZIEL_CRS_EPSG)

    bbox_utm = berechne_zielbbox(gdf_utm)

    try:
        array, transform, _crs = lade_imperviousness_ausschnitt(bbox_utm)
    except (requests.RequestException, RuntimeError) as exc:
        print(f"\nFEHLER beim Laden des Versiegelungsgrad-Ausschnitts: {exc}", file=sys.stderr)
        return 1

    try:
        ausgabe, kennzahlen = maskiere_und_berechne(array, transform, gdf_utm)
    except RuntimeError as exc:
        print(f"\nFEHLER: {exc}", file=sys.stderr)
        return 1

    speichere_geotiff(ausgabe, transform, TIF_OUT)
    erzeuge_karte(ausgabe, transform, gdf_utm, PNG_OUT)

    print("\n--- Sichtprüfungs-Zusammenfassung ---")
    print(f"Quelle/Epoche: {CLMS_QUELLE_TEXT}")
    print(f"Epoche: {CLMS_EPOCHE}")
    print(
        f"Versiegelungsgrad über das Gemeindegebiet {GEMEINDE_NAME}: "
        f"Mittelwert {kennzahlen['mittelwert']:.1f} %, "
        f"Median {kennzahlen['median']:.1f} %, "
        f"Min {kennzahlen['min']:.0f} %, Max {kennzahlen['max']:.0f} %"
    )
    print(
        f"Flächenanteil mit > {SCHWELLE_STARK_VERSIEGELT:.0f} % Versiegelung: "
        f"{kennzahlen['flaechenanteil_ueber_schwelle']:.1f} % der Gemeindefläche "
        f"({kennzahlen['gueltige_pixelzahl']} von {kennzahlen['gemeinde_pixelzahl']} "
        "ausgewerteten Pixeln)"
    )
    print(
        "Hinweis: absolute Prozentkennzahl, KEINE Anomalie-Berechnung - "
        "wetterunabhängig und direkt interpretierbar."
    )
    print(
        "BEKANNTE LIMITATION: Epoche IMD 2018 (Referenzperiode 2017-2019) liegt zeitlich "
        "vor den Datengrundlagen von NDVI (Sentinel-2, Sommer 2025) und LST-Anomalie "
        "(Landsat, Sommer 2021-2025) - siehe README.md, Abschnitt Task 4, für Details "
        "und Begründung."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
