"""
Berechnet die Oberflächentemperatur-Anomalie (LST-Anomalie) für Baden-Baden
(AGS 08211000) aus Landsat 8/9 Collection 2 Level-2-Daten (Band ST), Zugriff
über den Microsoft Planetary Computer STAC-Katalog (kein Login für Lesezugriff
nötig).

WICHTIG (siehe PROJECT_CONTEXT.md, Methodik-Regel 2): Das hier berechnete
Ergebnis ist ausschließlich die Oberflächentemperatur (Landoberfläche, aus dem
thermalen Landsat-Band), NICHT die Lufttemperatur und NICHT die thermische
Belastung von Menschen. Diese Begriffe dürfen für dieses Ergebnis nirgends
verwendet werden.

BEKANNTE LIMITIERUNG: Landsat überfliegt Baden-Baden vormittags (Ortszeit ca.
10:30) - das Nachmittagsmaximum der Aufheizung wird dadurch nicht erfasst,
die Anomalie unterschätzt tendenziell die maximale Tagesamplitude.

BESONDERHEIT BADEN-BADEN (siehe scripts/01_load_geometry_badenbaden.py):
Stadtkreis, VG250-Geometrie ist ein MultiPolygon mit 4 Teilflächen. Das
Zielraster wird aus der Bounding Box ALLER Teilflächen aufgespannt
(gdf.total_bounds), die Gemeindemaske (rasterio.features.geometry_mask)
berücksichtigt jede Teilfläche einzeln.

Datenquelle: Landsat 8/9 Collection 2 Level-2 (Collection "landsat-c2-l2"),
Microsoft Planetary Computer STAC (planetarycomputer.microsoft.com/api/stac/v1).
Sentinel-2 hat keinen Thermalkanal - LST kommt ausschließlich aus Landsat.

Ablauf:
    1. Gemeindegeometrie aus data/badenbaden_boundary.geojson laden
       (erzeugt von scripts/01_load_geometry_badenbaden.py), Geometrietyp prüfen.
    2. Über pystac-client den Planetary-Computer-STAC-Katalog nach Landsat
       8/9 Collection 2 Level-2-Szenen über dem Gemeindegebiet durchsuchen,
       für mehrere Sommer (Juni-August, 2021-2025), gefiltert nach
       Szenen-Wolkenbedeckung (eo:cloud_cover) UND Tier-1-Qualität.
    3. Je Szene das ST-Band (Surface Temperature) und das QA_PIXEL-Band laden,
       pixelgenau Wolken/Wolkenschatten/Cirrus über dem Gemeindegebiet
       ausmaskieren (nicht nur szenenweise filtern), auf EPSG:25832
       reprojizieren und auf die exakte Gemeindegeometrie zuschneiden. Szenen,
       bei denen danach zu wenig Gemeindefläche wolkenfrei übrig bleibt,
       werden verworfen, auch wenn ihre Szenen-Wolkenbedeckung unauffällig war.
    4. Mittelwert je Pixel hierarchisch bilden: zuerst je Sommer mitteln, dann
       über die Sommermittel mitteln (jeder Sommer gleich gewichtet,
       unabhängig von seiner Terminanzahl). Daraus die Anomalie berechnen
       (Pixelwert minus Mittelwert des gesamten Gemeindegebiets - keine
       absoluten Temperaturschwellen).
    5. Ergebnis als GeoTIFF und PNG-Karte speichern, Sichtprüfungs-
       Zusammenfassung mit getrennt ausgewiesenen Anomalie- und Absolutwerten
       ausgeben.

Nutzung:
    python scripts/03_lst_badenbaden.py
    python scripts/03_lst_badenbaden.py --max-cloud-cover 30

Benötigt keine Zugangsdaten (Planetary-Computer-Lesezugriff ist öffentlich).
"""

from __future__ import annotations

import argparse
import sys
import warnings
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import planetary_computer
import pystac_client
import rasterio
import rioxarray  # noqa: F401 - registriert den .rio-Accessor auf xarray
from matplotlib.colors import TwoSlopeNorm
from rasterio.enums import Resampling
from rasterio.features import geometry_mask
from rasterio.transform import Affine, from_origin

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUTS_DIR = REPO_ROOT / "outputs"

BOUNDARY_GEOJSON = DATA_DIR / "badenbaden_boundary.geojson"
TIF_OUT = OUTPUTS_DIR / "badenbaden_lst_anomaly.tif"
PNG_OUT = OUTPUTS_DIR / "badenbaden_lst_anomaly.png"

PC_STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"
LANDSAT_COLLECTION_ID = "landsat-c2-l2"
ST_ASSET_KEY = "lwir11"  # Surface-Temperature-Band (ST_B10) im PC-STAC-Item
QA_ASSET_KEY = "qa_pixel"

ZIEL_CRS_EPSG = 25832  # ETRS89/UTM32N - Vorgabe für alle Flächen-/Rasterberechnungen (Westdeutschland)
AUFLOESUNG_M = 30.0  # native Auflösung des thermalen ST-Bands (TIRS)
PUFFER_M = 90.0  # Sicherheitsabstand ums Zielraster (3 Pixel) für sauberes Resampling am Rand

SOMMER_JAHRE = list(range(2021, 2026))  # 2021-2025
SOMMER_START_MMTT = "06-01"
SOMMER_ENDE_EXKLUSIV_MMTT = "09-01"

MIN_TERMINE_GESAMT = 3  # Methodik-Vorgabe: mind. 3 Sommertermine, wenn verfügbar
MIN_TERMINE_PRO_SOMMER = 3
MIN_ANTEIL_GUELTIGE_FLAECHE = 0.5  # Szene wird verworfen, wenn nach QA_PIXEL-
# Filterung weniger als 50% der Gemeindefläche wolken-/schattenfrei sind -
# auch wenn die Szenen-Wolkenbedeckung (eo:cloud_cover) unter der Schwelle lag.

# USGS Landsat Collection 2 Level-2 Surface Temperature: DN -> Kelvin.
ST_SKALIERUNGSFAKTOR = 0.00341802
ST_OFFSET_KELVIN = 149.0
KELVIN_NULLPUNKT_CELSIUS = 273.15

# QA_PIXEL-Bitpositionen (Landsat Collection 2, CFMask-Algorithmus).
QA_BIT_DILATED_CLOUD = 1
QA_BIT_CIRRUS = 2
QA_BIT_CLOUD = 3
QA_BIT_CLOUD_SHADOW = 4


def lade_gemeindegeometrie() -> gpd.GeoDataFrame:
    if not BOUNDARY_GEOJSON.exists():
        raise FileNotFoundError(
            f"Gemeindegeometrie nicht gefunden: {BOUNDARY_GEOJSON}. "
            "Bitte zuerst scripts/01_load_geometry_badenbaden.py ausführen."
        )
    gdf = gpd.read_file(BOUNDARY_GEOJSON)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)

    geometrie = gdf.geometry.iloc[0]
    if geometrie.geom_type == "MultiPolygon":
        print(
            f"Geometrietyp: MultiPolygon mit {len(geometrie.geoms)} Teilflächen "
            "(Baden-Baden-Fragmente) - Zielraster, Gemeindemaske und "
            "Kartendarstellung berücksichtigen im Folgenden alle Teilflächen."
        )
    elif geometrie.geom_type != "Polygon":
        raise TypeError(
            f"Unerwarteter Geometrietyp '{geometrie.geom_type}' für Baden-Baden - "
            "erwartet wurde Polygon oder MultiPolygon. Abbruch, keine "
            "stillschweigende Weiterverarbeitung."
        )
    return gdf


def baue_zielraster(gdf_utm: gpd.GeoDataFrame) -> tuple[Affine, tuple[int, int]]:
    """Legt ein gemeinsames EPSG:25832-Raster (Transform + Shape) fest, auf das
    jede Szene reprojiziert wird - notwendig, damit alle Termine pixelgenau
    deckungsgleich sind und ein Pixel-für-Pixel-Mittelwert überhaupt sinnvoll ist.

    gdf_utm.total_bounds deckt bei einem MultiPolygon automatisch die Bounding
    Box über ALLE Teilflächen ab.
    """
    minx, miny, maxx, maxy = gdf_utm.total_bounds
    minx -= PUFFER_M
    miny -= PUFFER_M
    maxx += PUFFER_M
    maxy += PUFFER_M
    minx = np.floor(minx / AUFLOESUNG_M) * AUFLOESUNG_M
    maxy = np.ceil(maxy / AUFLOESUNG_M) * AUFLOESUNG_M
    breite = int(np.ceil((maxx - minx) / AUFLOESUNG_M))
    hoehe = int(np.ceil((maxy - miny) / AUFLOESUNG_M))
    transform = from_origin(minx, maxy, AUFLOESUNG_M, AUFLOESUNG_M)
    return transform, (hoehe, breite)


def baue_gemeinde_maske(
    gdf_utm: gpd.GeoDataFrame, transform: Affine, shape: tuple[int, int]
) -> np.ndarray:
    """Boolesches Raster auf dem Zielraster: True = Pixelmittelpunkt liegt
    innerhalb der Gemeindegeometrie. rasterio.features.geometry_mask
    unterstützt MultiPolygon nativ."""
    return geometry_mask(gdf_utm.geometry, out_shape=shape, transform=transform, invert=True)


def berechne_wolken_maske(qa_werte: np.ndarray) -> np.ndarray:
    """True = Pixel ist laut QA_PIXEL Wolke, Wolkenschatten oder Cirrus
    (inkl. Wolken-Dilatation) und muss aus der ST-Auswertung ausgeschlossen
    werden."""
    qa = np.nan_to_num(qa_werte, nan=0).astype("uint16")
    maske = np.zeros(qa.shape, dtype=bool)
    for bit in (QA_BIT_DILATED_CLOUD, QA_BIT_CIRRUS, QA_BIT_CLOUD, QA_BIT_CLOUD_SHADOW):
        maske |= ((qa >> bit) & 1).astype(bool)
    return maske


def verarbeite_szene(
    item, gdf_wgs84: gpd.GeoDataFrame, ziel_transform: Affine, ziel_shape: tuple[int, int]
) -> tuple[np.ndarray | None, str | None]:
    """Lädt ST- und QA_PIXEL-Band einer Landsat-Szene, maskiert Wolken/Schatten/
    Cirrus pixelgenau über dem Gemeindegebiet, rechnet das ST-Band in Grad
    Celsius um und reprojiziert das Ergebnis auf das gemeinsame Zielraster.

    Gibt (Array, None) bei Erfolg zurück, sonst (None, Fehlertext) - eine
    einzelne fehlerhafte Szene bricht den Gesamtlauf nicht ab.
    """
    try:
        st_da = rioxarray.open_rasterio(item.assets[ST_ASSET_KEY].href, masked=True)
        st_da = st_da.squeeze("band", drop=True)
        qa_da = rioxarray.open_rasterio(item.assets[QA_ASSET_KEY].href, masked=True)
        qa_da = qa_da.squeeze("band", drop=True)

        # Nur das Gemeindegebiet (+Puffer) aus der ~185 km breiten Szene laden.
        aoi_native = gdf_wgs84.to_crs(st_da.rio.crs)
        minx, miny, maxx, maxy = aoi_native.total_bounds
        st_da = st_da.rio.clip_box(minx - PUFFER_M, miny - PUFFER_M, maxx + PUFFER_M, maxy + PUFFER_M)
        qa_da = qa_da.rio.clip_box(minx - PUFFER_M, miny - PUFFER_M, maxx + PUFFER_M, maxy + PUFFER_M)

        wolken_maske = berechne_wolken_maske(qa_da.values)

        st_celsius = (
            st_da.values.astype("float64") * ST_SKALIERUNGSFAKTOR
            + ST_OFFSET_KELVIN
            - KELVIN_NULLPUNKT_CELSIUS
        )
        st_celsius[wolken_maske] = np.nan

        st_maskiert = st_da.copy(data=st_celsius)
        st_maskiert = st_maskiert.rio.write_nodata(np.nan)

        st_reproj = st_maskiert.rio.reproject(
            f"EPSG:{ZIEL_CRS_EPSG}",
            shape=ziel_shape,
            transform=ziel_transform,
            resampling=Resampling.bilinear,
            nodata=np.nan,
        )
        return st_reproj.values, None
    except Exception as exc:  # noqa: BLE001 - jede Szene robust einzeln behandeln, Fehlergrund wird gemeldet
        return None, f"Lese-/Verarbeitungsfehler: {exc}"


def suche_szenen(katalog, bbox_wgs84: tuple[float, float, float, float], jahr: int, max_cloud_cover: float) -> list:
    zeitraum = f"{jahr}-{SOMMER_START_MMTT}/{jahr}-{SOMMER_ENDE_EXKLUSIV_MMTT}"
    suche = katalog.search(
        collections=[LANDSAT_COLLECTION_ID],
        bbox=list(bbox_wgs84),
        datetime=zeitraum,
        query={
            "eo:cloud_cover": {"lt": max_cloud_cover},
            "platform": {"in": ["landsat-8", "landsat-9"]},
        },
    )
    items = list(suche.items())
    # Nur Tier 1 (radiometrisch/geometrisch höchste Präzisionsstufe) verwenden -
    # Tier 2/RT sind für pixelgenaue Auswertung nicht geeignet. Fehlt das Feld,
    # wird die Szene nicht ausgeschlossen (Default "T1").
    return [it for it in items if it.properties.get("landsat:collection_category", "T1") == "T1"]


def speichere_geotiff(array: np.ndarray, transform: Affine, pfad: Path) -> None:
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
        dst.write(array.astype("float32"), 1)
    print(f"Anomalie-GeoTIFF gespeichert: {pfad}")


def erzeuge_karte(
    anomalie: np.ndarray, transform: Affine, gdf_utm: gpd.GeoDataFrame, sommer_text: str, png_pfad: Path
) -> None:
    hoehe, breite = anomalie.shape
    xmin = transform.c
    ymax = transform.f
    xmax = xmin + breite * transform.a
    ymin = ymax + hoehe * transform.e  # transform.e ist negativ
    extent = (xmin, xmax, ymin, ymax)

    vmax = float(np.nanmax(np.abs(anomalie)))
    norm = TwoSlopeNorm(vmin=-vmax, vcenter=0.0, vmax=vmax)

    png_pfad.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 7))
    bild = ax.imshow(anomalie, extent=extent, origin="upper", cmap="RdBu_r", norm=norm)
    gdf_utm.boundary.plot(ax=ax, color="black", linewidth=1.2)
    cbar = fig.colorbar(bild, ax=ax, shrink=0.75)
    cbar.set_label("Oberflächentemperatur-Anomalie [°C] ggü. Gemeindemittel")
    ax.set_title(f"Oberflächentemperatur-Anomalie Baden-Baden\n(Landsat 8/9 C2 L2, Sommer {sommer_text})")
    ax.set_xlabel(f"Rechtswert [EPSG:{ZIEL_CRS_EPSG}]")
    ax.set_ylabel(f"Hochwert [EPSG:{ZIEL_CRS_EPSG}]")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(png_pfad, dpi=150)
    plt.close(fig)
    print(f"Anomalie-Karte gespeichert: {png_pfad}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--max-cloud-cover",
        type=float,
        default=20.0,
        help="Maximale Szenen-Wolkenbedeckung (eo:cloud_cover) in Prozent (Startwert: 20).",
    )
    parser.add_argument(
        "--min-flaechenanteil",
        type=float,
        default=MIN_ANTEIL_GUELTIGE_FLAECHE * 100,
        help="Mindestanteil (%%) der Gemeindefläche, der nach pixelgenauer "
        "QA_PIXEL-Filterung je Szene noch wolken-/schattenfrei sein muss "
        f"(Startwert: {MIN_ANTEIL_GUELTIGE_FLAECHE * 100:.0f}).",
    )
    args = parser.parse_args()
    min_anteil = args.min_flaechenanteil / 100.0

    gdf_wgs84 = lade_gemeindegeometrie()
    gdf_utm = gdf_wgs84.to_crs(epsg=ZIEL_CRS_EPSG)
    bbox_wgs84 = tuple(gdf_wgs84.total_bounds)

    ziel_transform, ziel_shape = baue_zielraster(gdf_utm)
    gemeinde_maske = baue_gemeinde_maske(gdf_utm, ziel_transform, ziel_shape)
    gemeinde_pixelzahl = int(gemeinde_maske.sum())
    if gemeinde_pixelzahl == 0:
        print("\nFEHLER: Gemeindegeometrie deckt auf dem Zielraster keine Pixel ab.", file=sys.stderr)
        return 1

    katalog = pystac_client.Client.open(PC_STAC_URL, modifier=planetary_computer.sign_inplace)

    ergebnisse_je_sommer: dict[int, dict[str, int]] = {}
    alle_verwendet: list[tuple[str, int, np.ndarray]] = []
    jahres_mittelwerte: dict[int, np.ndarray] = {}

    for jahr in SOMMER_JAHRE:
        print(f"\nSommer {jahr}: suche Landsat 8/9 C2 L2-Szenen (max. {args.max_cloud_cover:.0f}% Szenen-Wolken)...")
        items = suche_szenen(katalog, bbox_wgs84, jahr, args.max_cloud_cover)
        print(f"  {len(items)} Szene(n) gefunden (nach Wolken- und Tier-1-Filter auf Szenen-Ebene).")

        verwendet_jahr: list[tuple[str, np.ndarray]] = []
        verworfen_jahr: list[tuple[str, str]] = []

        for item in items:
            datum = item.datetime.date().isoformat()
            array, fehler = verarbeite_szene(item, gdf_wgs84, ziel_transform, ziel_shape)
            if array is None:
                verworfen_jahr.append((datum, fehler or "unbekannter Fehler"))
                continue

            array = array.copy()
            array[~gemeinde_maske] = np.nan
            gueltige_pixel = int(np.sum(~np.isnan(array) & gemeinde_maske))
            anteil = gueltige_pixel / gemeinde_pixelzahl
            if anteil < min_anteil:
                verworfen_jahr.append(
                    (datum, f"nur {anteil:.0%} wolken-/schattenfreie Gemeindefläche nach QA_PIXEL-Filterung")
                )
                continue

            verwendet_jahr.append((datum, array))

        for datum, grund in verworfen_jahr:
            print(f"    verworfen ({datum}): {grund}")
        for datum, _ in verwendet_jahr:
            print(f"    verwendet  ({datum})")

        if len(verwendet_jahr) == 0:
            print(f"  WARNUNG: kein nutzbarer Termin in Sommer {jahr}.")
        elif len(verwendet_jahr) < MIN_TERMINE_PRO_SOMMER:
            print(
                f"  WARNUNG: nur {len(verwendet_jahr)} nutzbare(r) Termin(e) in Sommer {jahr} "
                f"(Minimum lt. Methodik: {MIN_TERMINE_PRO_SOMMER})."
            )

        ergebnisse_je_sommer[jahr] = {
            "gefunden": len(items),
            "verwendet": len(verwendet_jahr),
            "verworfen": len(verworfen_jahr),
        }
        alle_verwendet.extend((datum, jahr, array) for datum, array in verwendet_jahr)
        if verwendet_jahr:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", category=RuntimeWarning)
                jahres_mittelwerte[jahr] = np.nanmean(
                    np.stack([array for _, array in verwendet_jahr], axis=0), axis=0
                )

    sommer_mit_daten = sorted({jahr for _, jahr, _ in alle_verwendet})

    if len(alle_verwendet) == 0:
        print(
            "\nFEHLER: Über alle Sommer 2021-2025 kein einziger nutzbarer Termin nach "
            "Wolken-/QA_PIXEL-Filterung - Oberflächentemperatur-Anomalie kann nicht berechnet werden.",
            file=sys.stderr,
        )
        return 1

    if len(sommer_mit_daten) < 2:
        print(
            f"\nFEHLER: Nutzbare Termine liegen nur in einem Sommer ({sommer_mit_daten[0]}) vor "
            f"({len(alle_verwendet)} Termin(e)). Eine Aggregation über mehrere Sommer (Pflicht laut "
            "Methodik wegen Bewölkungsproblem Mitteleuropa) ist damit nicht möglich. Kein Fallback "
            "auf einen einzelnen Sommer/Termin - Abbruch.",
            file=sys.stderr,
        )
        return 1

    if len(alle_verwendet) < MIN_TERMINE_GESAMT:
        print(
            f"\nWARNUNG: Insgesamt nur {len(alle_verwendet)} nutzbare Termine über "
            f"{len(sommer_mit_daten)} Sommer (Minimum lt. Methodik: {MIN_TERMINE_GESAMT}). "
            "Ergebnis basiert auf dünner Datengrundlage und ist entsprechend vorsichtig zu interpretieren."
        )

    stack = np.stack([array for _, _, array in alle_verwendet], axis=0)

    # Hierarchische Mittelung: zuerst je Sommer mitteln, dann über die Sommermittel
    # mitteln - jeder Sommer geht unabhängig von seiner Terminanzahl gleich stark
    # ein.
    stack_sommer = np.stack([jahres_mittelwerte[jahr] for jahr in sommer_mit_daten], axis=0)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)  # "Mean of empty slice" für nie beobachtete Pixel
        mittel = np.nanmean(stack_sommer, axis=0)

    beobachtungen_je_pixel = np.sum(~np.isnan(stack), axis=0)
    nie_beobachtet = int(np.sum(gemeinde_maske & (beobachtungen_je_pixel == 0)))
    if nie_beobachtet > 0:
        print(
            f"\nHinweis: {nie_beobachtet} von {gemeinde_pixelzahl} Gemeindepixeln wurden an keinem "
            "nutzbaren Termin wolkenfrei beobachtet und bleiben No-Data."
        )

    gemeinde_mittelwert = float(np.nanmean(mittel[gemeinde_maske]))
    anomalie = mittel - gemeinde_mittelwert
    anomalie[~gemeinde_maske] = np.nan

    gueltige_anomalie = anomalie[np.isfinite(anomalie)]
    if gueltige_anomalie.size == 0:
        print(
            "\nFEHLER: Nach Mittelung über alle nutzbaren Termine sind keine gültigen "
            "(Nicht-No-Data-)Pixel im Gemeindegebiet übrig - Ergebnis nicht plausibel.",
            file=sys.stderr,
        )
        return 1

    speichere_geotiff(anomalie, ziel_transform, TIF_OUT)
    sommer_text = ", ".join(str(j) for j in sommer_mit_daten)
    erzeuge_karte(anomalie, ziel_transform, gdf_utm, sommer_text, PNG_OUT)

    gesamt_verworfen = sum(v["verworfen"] for v in ergebnisse_je_sommer.values())
    print("\n--- Sichtprüfungs-Zusammenfassung ---")
    print(f"Verwendete Szenen gesamt: {len(alle_verwendet)}, über Sommer: {sommer_text}")
    for jahr, werte in ergebnisse_je_sommer.items():
        print(f"  Sommer {jahr}: {werte['verwendet']} verwendet, {werte['verworfen']} verworfen (von {werte['gefunden']} gefundenen Szenen)")
    print(f"Verworfene Szenen gesamt (Wolken/Schatten/Cirrus oder Lesefehler): {gesamt_verworfen}")
    absolut_gemeinde = mittel[gemeinde_maske]
    print(
        f"Absolute Oberflächentemperatur, hierarchisch gemittelt über {len(sommer_mit_daten)} Sommer "
        f"(je Sommer gleich gewichtet, {len(alle_verwendet)} Termine gesamt) "
        f"(zwei unabhängige Kennzahlen, NICHT durch Subtraktion ineinander umrechenbar):"
    )
    print(f"  Gemeindemittel (Bezugsgröße der Anomalie): {gemeinde_mittelwert:.2f} °C")
    print(
        f"  Spanne einzelner Pixel im Gemeindegebiet: {np.nanmin(absolut_gemeinde):.2f} °C "
        f"bis {np.nanmax(absolut_gemeinde):.2f} °C"
    )
    print(
        f"Oberflächentemperatur-Anomalie (= Pixelwert minus Gemeindemittel) über dem Gemeindegebiet: "
        f"{np.nanmin(anomalie):.2f} °C bis {np.nanmax(anomalie):.2f} °C"
    )
    print(
        "Hinweis: Es handelt sich ausschließlich um die Oberflächentemperatur (Landoberfläche) "
        "aus Landsat, nicht um Lufttemperatur und nicht um thermische Belastung von Menschen."
    )
    print(
        "Bekannte Limitierung: Landsat überfliegt Baden-Baden vormittags (Ortszeit ca. 10:30) - "
        "das Nachmittagsmaximum der Aufheizung wird dadurch nicht erfasst, die Anomalie "
        "unterschätzt tendenziell die maximale Tagesamplitude."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
