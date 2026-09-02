"""
Berechnet NDVI (Vegetationsindex) für Gernsbach (AGS 08216017) aus Sentinel-2
L2A-Daten des Copernicus Data Space Ecosystem (CDSE), Zugriff über openEO.

Datenquelle: Sentinel-2 L2A, CDSE (openeo.dataspace.copernicus.eu), Login
über OAuth2 Client-Credentials-Flow erforderlich (siehe .env). Räumliche
Auflösung 10 m (Bänder B04/B08).

Ablauf:
    1. Gemeindegeometrie aus data/gernsbach_boundary.geojson laden
       (erzeugt von scripts/01_load_geometry.py).
    2. Bei CDSE per openEO authentifizieren (Client-Credentials, aus .env).
    3. Verfügbare wolkenarme Sentinel-2-L2A-Termine für Sommer 2025 über dem
       Gemeindegebiet ermitteln (Sichtprüfung, ob genug Termine vorhanden sind).
    4. NDVI = (B08-B04)/(B08+B04) serverseitig berechnen, auf die exakte
       Gemeindegrenze maskieren, Median-Komposit über die Zeit bilden.
    5. Ergebnis als GeoTIFF speichern, PNG-Karte erzeugen, Kennzahlen ausgeben.

Nutzung:
    python scripts/02_ndvi_gernsbach.py
    python scripts/02_ndvi_gernsbach.py --max-cloud-cover 30

Benötigte Umgebungsvariablen (aus .env, siehe README.md):
    CDSE_CLIENT_ID, CDSE_CLIENT_SECRET
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import openeo
import pystac_client
import rioxarray  # noqa: F401 - registriert den .rio-Accessor auf xarray
from dotenv import load_dotenv
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm

# Braun (wenig/keine Vegetation) -> helles Grau/Beige -> Grün (viel Vegetation).
# Bewusst kein Standard-Colorbrewer-"BrBG", da dessen Grün-Ende ins Blaugrüne
# geht - hier ausschließlich Braun/Grau vs. reines Grün wie gefordert.
NDVI_CMAP = LinearSegmentedColormap.from_list(
    "braun_grau_gruen",
    ["#7b4a24", "#c9a26a", "#eee8dc", "#8fbf5f", "#1b7a3d"],
)

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUTS_DIR = REPO_ROOT / "outputs"

BOUNDARY_GEOJSON = DATA_DIR / "gernsbach_boundary.geojson"
TIF_OUT = OUTPUTS_DIR / "gernsbach_ndvi.tif"
PNG_OUT = OUTPUTS_DIR / "gernsbach_ndvi.png"

OPENEO_BACKEND_URL = "https://openeo.dataspace.copernicus.eu"
OPENEO_OIDC_PROVIDER_ID = "CDSE"  # Issuer: https://identity.dataspace.copernicus.eu/auth/realms/CDSE
STAC_CATALOG_URL = "https://catalogue.dataspace.copernicus.eu/stac"
STAC_COLLECTION_ID = "sentinel-2-l2a"
OPENEO_COLLECTION_ID = "SENTINEL2_L2A"

ZIEL_CRS_EPSG = 25832  # ETRS89/UTM32N - Vorgabe für alle Flächen-/Rasterberechnungen (Westdeutschland)

SOMMER_START = "2025-06-01"
SOMMER_ENDE_EXKLUSIV = "2025-09-01"  # openEO-Zeitintervalle sind oben exklusiv
MIN_WOLKENFREIE_TERMINE = 3


def lade_zugangsdaten() -> tuple[str, str]:
    """Lädt CDSE-Zugangsdaten ausschließlich aus Umgebungsvariablen (via .env).

    Kein Platzhalterwert, kein stiller Fallback: Fehlen die Variablen, wird
    mit einer klaren Fehlermeldung abgebrochen.
    """
    load_dotenv(REPO_ROOT / ".env")
    client_id = os.environ.get("CDSE_CLIENT_ID")
    client_secret = os.environ.get("CDSE_CLIENT_SECRET")
    fehlend = [
        name
        for name, wert in (("CDSE_CLIENT_ID", client_id), ("CDSE_CLIENT_SECRET", client_secret))
        if not wert
    ]
    if fehlend:
        raise RuntimeError(
            "Fehlende Umgebungsvariable(n): " + ", ".join(fehlend) + ". "
            "Bitte in der .env-Datei im Projektordner setzen (CDSE Sentinel-Hub-"
            "OAuth-Client, Client-Credentials-Flow). Kein Platzhalter- oder "
            "Fallback-Zugang möglich."
        )
    return client_id, client_secret


def verbinde_openeo(client_id: str, client_secret: str) -> openeo.Connection:
    """Verbindet mit dem CDSE-openEO-Backend und authentifiziert per Client-Credentials.

    Schlägt die Authentifizierung fehl, wird der Fehler unverändert weitergereicht
    (kein alternativer Zugang, kein automatischer Retry mit anderen Zugangsdaten).
    """
    connection = openeo.connect(OPENEO_BACKEND_URL)
    connection.authenticate_oidc_client_credentials(
        client_id=client_id,
        client_secret=client_secret,
        provider_id=OPENEO_OIDC_PROVIDER_ID,
    )
    print(f"Authentifiziert bei {OPENEO_BACKEND_URL} (Provider {OPENEO_OIDC_PROVIDER_ID}).")
    return connection


def lade_gemeindegeometrie() -> gpd.GeoDataFrame:
    if not BOUNDARY_GEOJSON.exists():
        raise FileNotFoundError(
            f"Gemeindegeometrie nicht gefunden: {BOUNDARY_GEOJSON}. "
            "Bitte zuerst scripts/01_load_geometry.py ausführen."
        )
    gdf = gpd.read_file(BOUNDARY_GEOJSON)
    if gdf.crs is None or gdf.crs.to_epsg() != 4326:
        gdf = gdf.to_crs(epsg=4326)
    return gdf


def ermittle_wolkenfreie_termine(bbox: tuple[float, float, float, float], max_cloud_cover: float) -> list:
    """Fragt den CDSE-STAC-Katalog nach Sentinel-2-L2A-Szenen über der Bounding-Box
    ab (gleiche Datenquelle wie die openEO-Verarbeitung), nur zur Sichtprüfung der
    tatsächlich verfügbaren Aufnahmetermine - kein Datenzugriff, kein Login nötig.

    Gibt eine sortierte Liste eindeutiger Aufnahmedaten zurück (mehrere UTM-Kacheln
    am selben Tag zählen als ein Termin).
    """
    katalog = pystac_client.Client.open(STAC_CATALOG_URL)
    suche = katalog.search(
        collections=[STAC_COLLECTION_ID],
        bbox=list(bbox),
        datetime=f"{SOMMER_START}/{SOMMER_ENDE_EXKLUSIV}",
        query={"eo:cloud_cover": {"lt": max_cloud_cover}},
    )
    termine = sorted({item.datetime.date() for item in suche.items()})
    return termine


def baue_ndvi_datacube(
    connection: openeo.Connection,
    bbox: tuple[float, float, float, float],
    geometrie,
    max_cloud_cover: float,
) -> openeo.DataCube:
    spatial_extent = {
        "west": bbox[0],
        "south": bbox[1],
        "east": bbox[2],
        "north": bbox[3],
        "crs": "EPSG:4326",
    }
    cube = connection.load_collection(
        OPENEO_COLLECTION_ID,
        spatial_extent=spatial_extent,
        temporal_extent=[SOMMER_START, SOMMER_ENDE_EXKLUSIV],
        bands=["B04", "B08"],
        max_cloud_cover=max_cloud_cover,
    )
    # Auf die exakte Gemeindegrenze maskieren (nicht nur die Bounding-Box) -
    # Pixel außerhalb werden zu No-Data.
    cube = cube.mask_polygon(geometrie)  # srs default: EPSG:4326 (lon-lat), passt zur Geometrie
    # Sentinel-2 liefert nativ EPSG:326xx (WGS84/UTM). Projektvorgabe (PROJECT_CONTEXT.md):
    # immer in ETRS89/UTM rechnen, nie in WGS84 - daher hier auf EPSG:25832 umprojizieren.
    cube = cube.resample_spatial(resolution=10, projection=ZIEL_CRS_EPSG, method="bilinear")
    cube = cube.ndvi(nir="B08", red="B04", target_band=None)
    cube = cube.reduce_dimension(dimension="t", reducer="median")
    return cube.save_result(format="GTiff")


def fuehre_batch_job_aus(cube: openeo.DataCube, ziel: Path) -> None:
    ziel.parent.mkdir(parents=True, exist_ok=True)
    print("Starte openEO-Batch-Job (NDVI-Median-Komposit)...")
    cube.execute_batch(outputfile=ziel, title="Gernsbach NDVI Sommer 2025")
    print(f"NDVI-GeoTIFF gespeichert: {ziel}")


def berechne_statistik(tif_pfad: Path) -> tuple[float, float, float]:
    da = rioxarray.open_rasterio(tif_pfad, masked=True)
    if isinstance(da, list):
        da = da[0]
    werte = da.values.astype("float64")
    werte = werte[np.isfinite(werte)]
    if werte.size == 0:
        raise RuntimeError(
            "NDVI-Raster enthält keine gültigen (Nicht-No-Data-)Pixel über dem "
            "Gemeindegebiet - Ergebnis nicht plausibel, keine Kennzahlen berechnet."
        )
    return float(np.nanmin(werte)), float(np.nanmax(werte)), float(np.nanmedian(werte))


def erzeuge_karte(tif_pfad: Path, gdf_wgs84: gpd.GeoDataFrame, png_pfad: Path) -> None:
    da = rioxarray.open_rasterio(tif_pfad, masked=True)
    if isinstance(da, list):
        da = da[0]
    if da.rio.crs is not None:
        gdf_plot = gdf_wgs84.to_crs(da.rio.crs)
    else:
        gdf_plot = gdf_wgs84

    png_pfad.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(7, 7))
    norm = TwoSlopeNorm(vmin=-0.2, vcenter=0.3, vmax=0.8)
    bild = da.squeeze().plot.imshow(
        ax=ax, cmap=NDVI_CMAP, norm=norm, add_colorbar=False, add_labels=False
    )
    gdf_plot.boundary.plot(ax=ax, color="black", linewidth=1.2)
    cbar = fig.colorbar(bild, ax=ax, shrink=0.75)
    cbar.set_label("NDVI")
    ax.set_title("NDVI-Median-Komposit Gernsbach, Sommer 2025 (Sentinel-2 L2A)")
    ax.set_xlabel(f"Rechtswert [{da.rio.crs}]" if da.rio.crs else "x")
    ax.set_ylabel(f"Hochwert [{da.rio.crs}]" if da.rio.crs else "y")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(png_pfad, dpi=150)
    plt.close(fig)
    print(f"NDVI-Karte gespeichert: {png_pfad}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--max-cloud-cover",
        type=float,
        default=20.0,
        help="Maximale Wolkenbedeckung der Szene in Prozent (Startwert: 20).",
    )
    args = parser.parse_args()

    try:
        client_id, client_secret = lade_zugangsdaten()
    except RuntimeError as exc:
        print(f"\nFEHLER: {exc}", file=sys.stderr)
        return 1

    try:
        connection = verbinde_openeo(client_id, client_secret)
    except Exception as exc:  # noqa: BLE001 - Authentifizierungsfehler klar melden, kein Fallback
        print(f"\nFEHLER bei der openEO-Authentifizierung: {exc}", file=sys.stderr)
        return 1

    gdf = lade_gemeindegeometrie()
    bbox = tuple(gdf.total_bounds)
    geometrie = gdf.geometry.iloc[0]

    print(
        f"Suche Sentinel-2 L2A-Termine für Gernsbach, {SOMMER_START} bis "
        f"{SOMMER_ENDE_EXKLUSIV} (exklusiv), max. {args.max_cloud_cover:.0f}% Wolken..."
    )
    termine = ermittle_wolkenfreie_termine(bbox, args.max_cloud_cover)
    if len(termine) == 0:
        print(
            "\nFEHLER: Keine wolkenfreien Sentinel-2-Termine im angegebenen Zeitraum "
            "gefunden - NDVI kann nicht berechnet werden.",
            file=sys.stderr,
        )
        return 1
    if len(termine) < MIN_WOLKENFREIE_TERMINE:
        print(
            f"\nWARNUNG: Nur {len(termine)} wolkenfreie(r) Termin(e) verfügbar "
            f"(Minimum lt. Methodik: {MIN_WOLKENFREIE_TERMINE}). Ergebnis basiert auf "
            "einer dünnen Datengrundlage und ist entsprechend vorsichtig zu "
            "interpretieren."
        )

    cube = baue_ndvi_datacube(connection, bbox, geometrie, args.max_cloud_cover)
    fuehre_batch_job_aus(cube, TIF_OUT)

    ndvi_min, ndvi_max, ndvi_median = berechne_statistik(TIF_OUT)
    erzeuge_karte(TIF_OUT, gdf, PNG_OUT)

    print("\n--- Sichtprüfungs-Zusammenfassung ---")
    print(f"Verwendete Szenen (eindeutige Aufnahmetermine): {len(termine)}")
    print(f"Zeitraum der genutzten Termine: {termine[0].isoformat()} bis {termine[-1].isoformat()}")
    print(f"NDVI min / median / max über dem Gemeindegebiet: {ndvi_min:.3f} / {ndvi_median:.3f} / {ndvi_max:.3f}")
    if len(termine) < MIN_WOLKENFREIE_TERMINE:
        print(f"WARNUNG: weniger als {MIN_WOLKENFREIE_TERMINE} wolkenfreie Termine verfügbar (s.o.).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
