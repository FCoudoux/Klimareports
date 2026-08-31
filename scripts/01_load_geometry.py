"""
Lädt die amtliche Gemeindegeometrie für Gernsbach (AGS 08216017) aus den
BKG VG250-Verwaltungsgebieten und bereitet sie für die weitere Pipeline auf.

Datenquelle: BKG VG250 (Verwaltungsgebiete 1:250.000), Open Data,
Lizenz dl-de/by-2-0. Kein Login/API-Key nötig - siehe README.md für den
bekannten Netzwerk-Einschränkungshinweis in dieser Cloud-Umgebung.

Nutzung:
    python scripts/01_load_geometry.py
    python scripts/01_load_geometry.py --local-shapefile data/raw/vg250_gem.shp
    python scripts/01_load_geometry.py --url https://.../vg250_ebenen.zip
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt

AGS_GERNSBACH = "08216017"
REFERENZ_FLAECHE_KM2 = 82.03
FLAECHEN_TOLERANZ_PROZENT = 5.0

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUTS_DIR = REPO_ROOT / "outputs"

GEOJSON_OUT = DATA_DIR / "gernsbach_boundary.geojson"
PNG_OUT = OUTPUTS_DIR / "gernsbach_boundary.png"

# Bekannte VG250-Downloadquellen des BKG (Open Data, dl-de/by-2-0).
# Die konkrete Zip-URL ändert sich mit jedem Datenstand; siehe
# https://gdz.bkg.bund.de/index.php/default/verwaltungsgebiete-1-250-000-stand-01-01-vg250.html
VG250_CANDIDATE_URLS = [
    "https://daten.gdz.bkg.bund.de/produkte/vg/vg250_ebenen_0101/aktuell/vg250_01-01.utm32s.shape.ebenen.zip",
]

# Innerhalb des VG250-Shape-Pakets liegt die Gemeindeebene typischerweise hier:
VG250_GEMEINDE_LAYER_HINT = "VG250_GEM.shp"


def lade_vg250_gemeinden(url: str | None, local_path: str | None) -> gpd.GeoDataFrame:
    """Lädt die VG250-Gemeindeebene entweder von einer lokalen Kopie oder per Download.

    geopandas/pyogrio können sowohl lokale Shapefiles/GeoPackages als auch
    (bei bestehender Netzwerkverbindung) direkt eine ZIP-URL via vsizip/vsicurl
    öffnen, z.B. "zip+https://.../vg250_ebenen.zip!vg250_ebenen_0101/DE_VG250.gpkg".
    """
    if local_path:
        pfad = Path(local_path)
        if not pfad.exists():
            raise FileNotFoundError(
                f"Lokale VG250-Datei nicht gefunden: {pfad}. "
                "Bitte VG250-Gemeindeebene manuell unter diesem Pfad ablegen."
            )
        print(f"Lade VG250-Gemeinden aus lokaler Datei: {pfad}")
        return gpd.read_file(pfad)

    kandidaten = [url] if url else VG250_CANDIDATE_URLS
    letzter_fehler: Exception | None = None
    for kandidat in kandidaten:
        try:
            print(f"Versuche VG250-Download von: {kandidat}")
            zip_url = f"zip+{kandidat}" if not kandidat.startswith("zip+") else kandidat
            return gpd.read_file(zip_url, layer=VG250_GEMEINDE_LAYER_HINT.replace(".shp", ""))
        except Exception as exc:  # noqa: BLE001 - wir wollen jede Downloadmethode versuchen
            print(f"  Fehlgeschlagen: {exc}")
            letzter_fehler = exc

    raise RuntimeError(
        "Konnte die VG250-Gemeindegrenzen weder herunterladen noch lokal finden.\n"
        "Bekannte Einschränkung: In dieser Cloud-Sandbox ist der ausgehende "
        "Netzwerkzugriff auf daten.gdz.bkg.bund.de durch die Umgebungs-Policy "
        "gesperrt (siehe README.md, Abschnitt 'Bekannte Einschränkungen').\n"
        "Abhilfe: VG250-Paket lokal (z.B. auf einem Rechner mit Internetzugang) "
        "von https://gdz.bkg.bund.de/index.php/default/verwaltungsgebiete-1-250-000-stand-01-01-vg250.html "
        "herunterladen, entpacken und den Pfad zur Gemeinde-Shapefile/GeoPackage-Ebene "
        "über --local-shapefile übergeben.\n"
        f"Letzter Fehler: {letzter_fehler}"
    )


def filtere_gemeinde(gdf: gpd.GeoDataFrame, ags: str) -> gpd.GeoDataFrame:
    """Filtert die VG250-Gemeindeebene nach amtlichem Gemeindeschlüssel (AGS)."""
    ags_spalte = None
    for kandidat in ("AGS", "ags", "AGS_0"):
        if kandidat in gdf.columns:
            ags_spalte = kandidat
            break
    if ags_spalte is None:
        raise KeyError(
            f"Keine AGS-Spalte in den Daten gefunden. Vorhandene Spalten: {list(gdf.columns)}"
        )

    treffer = gdf[gdf[ags_spalte].astype(str) == ags]
    if treffer.empty:
        raise ValueError(f"Keine Gemeinde mit AGS {ags} in den VG250-Daten gefunden.")
    if len(treffer) > 1:
        print(f"Warnung: {len(treffer)} Treffer für AGS {ags}, verwende den ersten.")
    return treffer.iloc[[0]]


def berechne_flaeche_km2(gdf_utm: gpd.GeoDataFrame) -> float:
    """Berechnet die Fläche in km² aus einer bereits in EPSG:25832 projizierten Geometrie."""
    return float(gdf_utm.geometry.area.iloc[0] / 1_000_000)


def plausibilisiere_flaeche(berechnete_flaeche_km2: float) -> None:
    abweichung_prozent = (
        abs(berechnete_flaeche_km2 - REFERENZ_FLAECHE_KM2) / REFERENZ_FLAECHE_KM2 * 100
    )
    print(
        f"Berechnete Fläche: {berechnete_flaeche_km2:.2f} km² "
        f"(Referenz: {REFERENZ_FLAECHE_KM2:.2f} km², Abweichung: {abweichung_prozent:.2f}%)"
    )
    if abweichung_prozent > FLAECHEN_TOLERANZ_PROZENT:
        print(
            f"WARNUNG: Abweichung über der Toleranzschwelle von "
            f"{FLAECHEN_TOLERANZ_PROZENT}% - Geometrie/AGS-Filter prüfen!"
        )
    else:
        print("Plausibilitätsprüfung bestanden.")


def speichere_geojson(gdf_utm: gpd.GeoDataFrame, pfad: Path) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    # GeoJSON ist per Spezifikation WGS84 (EPSG:4326) - für die Weitergabe/Anzeige
    # reprojizieren wir zurück, die Flächenberechnung selbst bleibt in EPSG:25832.
    gdf_wgs84 = gdf_utm.to_crs(epsg=4326)
    gdf_wgs84.to_file(pfad, driver="GeoJSON")
    print(f"Geometrie gespeichert: {pfad}")


def erzeuge_uebersichtskarte(gdf_utm: gpd.GeoDataFrame, pfad: Path) -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 6))
    gdf_utm.boundary.plot(ax=ax, color="black", linewidth=1.5)
    gdf_utm.plot(ax=ax, color="#c6dbef", edgecolor="black", alpha=0.6)
    ax.set_title(f"Gemeindegrenze Gernsbach (AGS {AGS_GERNSBACH})")
    ax.set_xlabel("Rechtswert [m, EPSG:25832]")
    ax.set_ylabel("Hochwert [m, EPSG:25832]")
    ax.set_aspect("equal")
    fig.tight_layout()
    fig.savefig(pfad, dpi=150)
    plt.close(fig)
    print(f"Übersichtskarte gespeichert: {pfad}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--url",
        help="Alternative VG250-Download-URL (Zip-Paket des BKG-Geodatendienstes).",
        default=None,
    )
    parser.add_argument(
        "--local-shapefile",
        help="Pfad zu einer bereits lokal abgelegten VG250-Gemeindeebene "
        "(.shp oder .gpkg), falls kein Netzwerkzugriff möglich ist.",
        default=None,
    )
    args = parser.parse_args()

    try:
        vg250_gemeinden = lade_vg250_gemeinden(args.url, args.local_shapefile)
    except (RuntimeError, FileNotFoundError) as exc:
        print(f"\nFEHLER: {exc}", file=sys.stderr)
        return 1

    gernsbach = filtere_gemeinde(vg250_gemeinden, AGS_GERNSBACH)
    gernsbach_utm = gernsbach.to_crs(epsg=25832)

    flaeche_km2 = berechne_flaeche_km2(gernsbach_utm)
    plausibilisiere_flaeche(flaeche_km2)

    speichere_geojson(gernsbach_utm, GEOJSON_OUT)
    erzeuge_uebersichtskarte(gernsbach_utm, PNG_OUT)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
