"""
Lädt die amtliche Gemeindegeometrie für Sinzheim (AGS 08216049) aus den
BKG VG250-Verwaltungsgebieten und bereitet sie für die weitere Pipeline auf.

BESONDERHEIT SINZHEIM (siehe PROJECT_CONTEXT.md, Pilotgemeinden-Tabelle):
Sinzheim besteht aus 9 Ortsteilen, von denen 3 als Exklaven vollständig
innerhalb der Gemarkung der Stadt Baden-Baden liegen. Die VG250-Geometrie ist
deshalb sehr wahrscheinlich ein MultiPolygon, kein einzelnes zusammenhängendes
Polygon wie bei Gernsbach. Dieses Skript prüft das explizit (geometry.geom_type)
und stellt sicher, dass Flächenberechnung, Speicherung und Kartendarstellung
alle Teilflächen erfassen - shapely/geopandas summieren Flächen und zeichnen
Geometrien für MultiPolygon bereits korrekt über alle Teilflächen, das wird
hier durch den expliziten Log-Hinweis nachvollziehbar gemacht statt stillschweigend
vorausgesetzt.

Datenquelle: BKG VG250 (Verwaltungsgebiete 1:250.000), Open Data,
Lizenz dl-de/by-2-0. Kein Login/API-Key nötig.

Nutzung:
    python scripts/01_load_geometry_sinzheim.py
    python scripts/01_load_geometry_sinzheim.py --local-shapefile data/raw/vg250_gem.shp
    python scripts/01_load_geometry_sinzheim.py --url https://.../vg250_ebenen.zip
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt

AGS_SINZHEIM = "08216049"
# Amtliche Gemeindefläche verifiziert gegen das Gemeindeverzeichnis-Informationssystem
# (gemeinsames Portal von Destatis und den Statistischen Ämtern der Länder),
# https://www.statistikportal.de/de/gemeindeverzeichnis/08216049 : 28,50 km²
# (intern konsistent mit dort ausgewiesener Bevölkerungsdichte 405 Einwohner/km²
# bei 11.547 Einwohnern). Deckungsgleich mit sinzheim.de (Zahlen-Daten-Fakten)
# und Wikipedia-Infobox. Stand Recherche 2026 - nicht geraten.
REFERENZ_FLAECHE_KM2 = 28.5
FLAECHEN_TOLERANZ_PROZENT = 5.0

REPO_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = REPO_ROOT / "data"
OUTPUTS_DIR = REPO_ROOT / "outputs"

GEOJSON_OUT = DATA_DIR / "sinzheim_boundary.geojson"
PNG_OUT = OUTPUTS_DIR / "sinzheim_boundary.png"

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
        "Abhilfe: VG250-Paket lokal (z.B. auf einem Rechner mit Internetzugang) "
        "von https://gdz.bkg.bund.de/index.php/default/verwaltungsgebiete-1-250-000-stand-01-01-vg250.html "
        "herunterladen, entpacken und den Pfad zur Gemeinde-Shapefile/GeoPackage-Ebene "
        "über --local-shapefile übergeben.\n"
        f"Letzter Fehler: {letzter_fehler}"
    )


def filtere_gemeinde(gdf: gpd.GeoDataFrame, ags: str) -> gpd.GeoDataFrame:
    """Filtert die VG250-Gemeindeebene nach amtlichem Gemeindeschlüssel (AGS).

    Trifft der Filter auf mehrere Datensätze zu, werden diese zu EINER
    Gemeindegeometrie vereinigt (z.B. falls Exklaven als separate Features
    statt als ein MultiPolygon-Feature abgelegt sind) - es wird NIE
    stillschweigend nur der erste Treffer verwendet, das würde Teilflächen
    (z.B. Exklaven) unbemerkt verlieren.
    """
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

    if len(treffer) == 1:
        return treffer.iloc[[0]]

    print(
        f"Hinweis: {len(treffer)} Datensätze für AGS {ags} gefunden - werden zu EINER "
        "Gemeindegeometrie vereinigt (union), damit keine Teilfläche/Exklave "
        "stillschweigend verworfen wird."
    )
    vereinigte_geometrie = treffer.geometry.union_all()
    vereinigt = gpd.GeoDataFrame({ags_spalte: [ags]}, geometry=[vereinigte_geometrie], crs=gdf.crs)
    return vereinigt


def pruefe_geometrietyp(gdf: gpd.GeoDataFrame) -> None:
    """Gibt den Geometrietyp explizit aus - Pflicht laut Aufgabenstellung, damit
    MultiPolygon-Fälle (Exklaven) nicht stillschweigend wie ein einzelnes
    Polygon behandelt werden."""
    geometrie = gdf.geometry.iloc[0]
    geom_type = geometrie.geom_type
    if geom_type == "MultiPolygon":
        anzahl_teilflaechen = len(geometrie.geoms)
        print(
            f"Geometrietyp: MultiPolygon mit {anzahl_teilflaechen} Teilflächen "
            "(erwartet bei Sinzheim wegen der 3 Exklaven in der Gemarkung Baden-Baden)."
        )
    elif geom_type == "Polygon":
        print(
            "Geometrietyp: Polygon (einzelne zusammenhängende Fläche) - "
            "KEIN MultiPolygon gefunden, obwohl laut PROJECT_CONTEXT.md wegen der "
            "3 Exklaven eines erwartet wurde. Bitte VG250-Datenstand/AGS-Filter prüfen, "
            "bevor mit dieser Geometrie weitergearbeitet wird."
        )
    else:
        raise TypeError(
            f"Unerwarteter Geometrietyp '{geom_type}' für Sinzheim - erwartet wurde "
            "Polygon oder MultiPolygon. Abbruch, keine stillschweigende Weiterverarbeitung."
        )


def berechne_flaeche_km2(gdf_utm: gpd.GeoDataFrame) -> float:
    """Berechnet die Fläche in km² aus einer bereits in EPSG:25832 projizierten
    Geometrie. shapely.MultiPolygon.area summiert automatisch über alle
    Teilflächen (Exklaven) - hier zusätzlich explizit über .geoms verifiziert,
    damit sich niemand auf dieses shapely-interne Verhalten "blind" verlassen muss.
    """
    geometrie = gdf_utm.geometry.iloc[0]
    flaeche_m2 = geometrie.area
    if geometrie.geom_type == "MultiPolygon":
        flaeche_teilflaechen_summe = sum(teil.area for teil in geometrie.geoms)
        if abs(flaeche_teilflaechen_summe - flaeche_m2) > 1.0:  # 1 m² Toleranz für Fließkomma
            raise RuntimeError(
                "Flächensumme der Teilflächen weicht von geometrie.area ab "
                f"({flaeche_teilflaechen_summe:.1f} m² vs. {flaeche_m2:.1f} m²) - "
                "Flächenberechnung nicht plausibel, Abbruch statt stillschweigend "
                "falschem Ergebnis."
            )
    return float(flaeche_m2 / 1_000_000)


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
    """Zeichnet die Gemeindegrenze. geopandas.GeoSeries.plot()/.boundary.plot()
    zeichnen MultiPolygon-Geometrien bereits nativ vollständig (alle Teilflächen,
    auch disjunkte) - keine Sonderbehandlung nötig, hier zusätzlich per
    Flächenanzahl im Titel sichtbar gemacht."""
    pfad.parent.mkdir(parents=True, exist_ok=True)
    geometrie = gdf_utm.geometry.iloc[0]
    teilflaechen_hinweis = (
        f" ({len(geometrie.geoms)} Teilflächen)" if geometrie.geom_type == "MultiPolygon" else ""
    )
    fig, ax = plt.subplots(figsize=(7, 7))
    gdf_utm.boundary.plot(ax=ax, color="black", linewidth=1.5)
    gdf_utm.plot(ax=ax, color="#c6dbef", edgecolor="black", alpha=0.6)
    ax.set_title(f"Gemeindegrenze Sinzheim (AGS {AGS_SINZHEIM}){teilflaechen_hinweis}")
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

    sinzheim = filtere_gemeinde(vg250_gemeinden, AGS_SINZHEIM)
    sinzheim_utm = sinzheim.to_crs(epsg=25832)

    pruefe_geometrietyp(sinzheim_utm)

    flaeche_km2 = berechne_flaeche_km2(sinzheim_utm)
    plausibilisiere_flaeche(flaeche_km2)

    speichere_geojson(sinzheim_utm, GEOJSON_OUT)
    erzeuge_uebersichtskarte(sinzheim_utm, PNG_OUT)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
