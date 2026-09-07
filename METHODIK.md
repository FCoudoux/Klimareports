# Methodik-Dokument: Klima-Check für Kommunen
## Satellitengestützte Ersteinschätzung der thermischen Ist-Lage

*Draft v0.1 · Stand: 04.09.2026 · Autor: F. Coudoux, methodische Prüfung mit Claude · noch nicht extern plausibilisiert*

---

## 1. Zweck und Geltungsbereich dieses Dokuments

Dieses Dokument beschreibt die fachliche Methodik hinter dem Klima-Check-Report und wird unverändert oder in gekürzter Form als Kapitel 2 ("Methodik und Datenquellen") Bestandteil jedes ausgelieferten Reports. Es dient zwei Zwecken: erstens der Transparenz gegenüber der auftraggebenden Kommune, zweitens der eigenen Absicherung gegenüber einem Fachbüro, das die Ergebnisse später nachrechnet.

**Was dieses Dokument nicht ist:** Es ersetzt keine Stadtklimaanalyse nach VDI 3787 und keine humanbiometeorologische Bewertung nach VDI 3787 Blatt 2. Es beschreibt eine satellitengestützte Ist-Darstellung mit regelbasierter, offengelegter Einordnung — kein planungsrechtlich verwertbares Gutachten.

### Was dieser Report leistet (Nutzenversprechen für die Kundenversion)

Die folgenden Abschnitte benennen bewusst und ausführlich die methodischen Grenzen des Verfahrens — das ist Voraussetzung für die fachliche Verteidigungsfähigkeit gegenüber einem prüfenden Fachbüro. Für die an die Kommune ausgelieferte Reportversion muss diesem Kapitel ein positiver Rahmen vorangestellt werden, der die Grenzen nicht verschweigt, aber den eigentlichen Nutzen zuerst benennt:

- Eine belastbare, aus offiziellen Satellitendaten abgeleitete **Ist-Darstellung** der thermischen und vegetationsbezogenen Situation der Gemeinde — Datengrundlage, die ohne dieses Produkt nur über ein mehrmonatiges, fünfstelliges Fachgutachten zu beschaffen wäre.
- Eine **innerhalb weniger Tage** statt Monate verfügbare, reproduzierbare Grundlage für die Ausgangslagenbeschreibung in einem Förderantrag.
- Eine **kleinräumige Differenzierung innerhalb der Gemeinde**, die öffentlich verfügbare Portale (Copernicus Urban Atlas, Landes-Klimaatlanten) für Gemeinden dieser Größenordnung nicht bieten — das ist der eigentliche Alleinstellungspunkt, siehe Businessplan A3.
- Eine Methodik, die vollständig offengelegt und mit anerkannter Fachliteratur unterlegt ist (siehe Abschnitt 4) — im Gegensatz zu einer Black-Box-Bewertung.

Diese Nutzenformulierung gehört in den Kunden-Report **vor** die Limitationen (Abschnitt 6), nicht anstelle davon.

---

## 2. Zentrales methodisches Prinzip: Relative Anomalie statt absoluter Schwellenwert

Alle drei Kennzahlen (Oberflächentemperatur, Vegetation, Versiegelung) werden **nicht** gegen feste, absolute Grenzwerte klassifiziert (z. B. "über 40 °C = kritisch"), sondern als **Abweichung vom Mittelwert des jeweiligen Gemeindegebiets** ausgedrückt.

**Warum, mit fachlicher Begründung:** Die absolute Oberflächentemperatur eines Ortes hängt von Faktoren ab, die mit der lokalen Klimaanpassungssituation nichts zu tun haben — Tag der Aufnahme, Jahreszeit, geografische Breite, Höhenlage, allgemeine Wetterlage. Ein fixer Schwellenwert wäre für eine Gemeinde in der Oberrheinebene systematisch anders zu kalibrieren als für eine Gemeinde im Schwarzwald, selbst wenn beide dieselbe *relative* Wärmeinsel-Struktur zeigen. Dieses Problem ist in der Fachliteratur dokumentiert: Shreevastava et al. (2019) begründen die Verwendung perzentilbasierter Schwellen für den städtischen Vergleich explizit damit, dass Städte unterschiedlicher Klimazonen unterschiedliche Referenztemperaturen haben und ein einheitlicher absoluter Schwellenwert die Ergebnisse zwischen Städten nicht vergleichbar machen würde<sup>[1]</sup>. Dieselbe Logik gilt für den Vergleich zwischen deutschen Kommunen unterschiedlicher Lage.

**Konkrete Umsetzung (bereits implementiert für LST):**
```
Anomalie(Pixel) = Wert(Pixel) − Mittelwert(gesamtes Gemeindegebiet)
```
Positive Werte = wärmer/vegetationsärmer als der Gemeindedurchschnitt, negative Werte = kühler/vegetationsreicher. Für NDVI gilt dieselbe Grundregel implizit über die Farbskala, für den Versiegelungsgrad (Phase 3) wird sie analog angewendet.

**Grenze dieses Prinzips, transparent zu benennen:** Die Anomalie sagt nichts über die *absolute* thermische Situation der Gemeinde als Ganzes aus, nur über die *interne* Verteilung. Eine insgesamt sehr warme Gemeinde ohne interne Differenzierung zeigt trotzdem eine flache Anomalie-Karte nahe null. Das ist beabsichtigt (siehe Abbruchkriterium Phase 1), muss aber im Report explizit kommuniziert werden, damit es nicht als "hier ist alles unauffällig" missverstanden wird, wenn eigentlich die ganze Gemeinde strukturell betroffen ist.

---

## 3. Kritische Begriffsabgrenzung: Oberflächentemperatur ≠ Lufttemperatur ≠ Hitzestress

Dies ist die wichtigste Einzelaussage des gesamten Reports und muss in jeder Version prominent und wortgleich erscheinen.

**Fachliche Grundlage:** Die Unterscheidung zwischen der *Surface Urban Heat Island* (SUHI, aus Fernerkundung ableitbar) und der *(atmosphärischen) Urban Heat Island* (UHI, Lufttemperaturdifferenz) ist in der Stadtklimatologie seit über zwei Jahrzehnten etabliert. Voogt & Oke (2003) legen in ihrer vielzitierten Übersichtsarbeit dar, dass beide Phänomene unterschiedlichen physikalischen Mechanismen unterliegen, unterschiedliche zeitliche Muster zeigen (SUHI tagsüber am stärksten, UHI typischerweise nachts) und nicht ineinander umgerechnet werden können<sup>[2]</sup>. Der Deutsche Wetterdienst definiert die städtische Wärmeinsel entsprechend explizit über die **Lufttemperaturdifferenz** zwischen Stadt und Umland, mit Maximum bei windschwachen, wolkenfreien **Nächten**<sup>[3]</sup> — also zeitlich und physikalisch das Gegenteil dessen, was unsere satellitengestützte Messung (später Vormittag) erfasst.

Parlow (2021) geht in seiner methodenkritischen Arbeit noch weiter und benennt genau den Fehler, den dieses Projekt vermeiden muss: Ein großer Teil der Fernerkundungsliteratur suggeriere implizit, dass "warme Oberflächen" zu "hohen Lufttemperaturen" führten, und leite daraus unmittelbar Handlungsempfehlungen für die Stadtplanung ab — eine Schlussfolgerung, die die Datengrundlage nicht trägt<sup>[4]</sup>.

**Konsequenz für jeden Report:**
- Die Formulierungen "Oberflächentemperatur-Anomalie" bzw. "thermische Speicherung von Oberflächen" sind verpflichtend.
- Die Begriffe "Hitzebelastung", "Wärmeinsel" (ohne den Zusatz "Oberflächen-") und "thermischer Stress" sind für dieses Ergebnis **nicht zulässig**, auch nicht umgangssprachlich vereinfacht.
- Ein Absatz mit exakt dieser Abgrenzung gehört in jeden Report, nicht nur in dieses Methodik-Kapitel.

---

## 4. Fachliche Verankerung der Klassifizierungslogik

### 4.1 Normative Grundlage: VDI 3787

- **VDI 3787 Blatt 1** — "Umweltmeteorologie: Klima- und Lufthygienekarten für Städte und Regionen" — beschreibt, wie stadtklimatische Sachverhalte kartografisch dargestellt und für die Planung nutzbar gemacht werden<sup>[5]</sup>. Unser Kartenformat (Anomalie-Karte mit Referenz aufs Gemeindemittel) orientiert sich konzeptionell an diesem Ansatz, erreicht aber nicht dessen methodische Tiefe (u. a. keine Modellierung, keine Windfeldsimulation).
- **VDI 3787 Blatt 2** — "Methoden zur human-biometeorologischen Bewertung der thermischen Komponente des Klimas"<sup>[6]</sup> — ist explizit **nicht** Grundlage unserer LST-Kennzahl, da diese Richtlinie die menschliche thermische Belastung behandelt, die wir laut Abgrenzung in Abschnitt 3 gerade nicht berechnen. Wird im Report als Negativabgrenzung zitiert ("nicht Gegenstand dieser Analyse").
- **VDI 3787 Blatt 5** — "Lokale Kaltluft"<sup>[7]</sup> — für dieses Projekt aktuell nicht einschlägig (keine Kaltluftmodellierung), aber relevant als Vormerkung für ein mögliches Zusatzmodul in Phase 5.

### 4.2 Deutscher Wetterdienst

Der DWD stellt mit dem **UHI-MAP-Klimadienst** ein deutschlandweites Monitoring der (atmosphärischen) städtischen Wärmeinsel bereit, basierend auf Copernicus-Landbedeckungsdaten, mit 1 km² Auflösung<sup>[8]</sup>. Dieser Dienst ist konzeptionell verwandt, aber **nicht deckungsgleich** mit unserer Kennzahl und darf nicht mit ihr zusammengeführt oder gegen sie ausgetauscht werden — aus zwei Gründen:

1. **Physikalisch:** Er modelliert die Lufttemperaturdifferenz Stadt–Umland, wir messen die Oberflächentemperatur direkt (siehe Abschnitt 3). Eine gemeinsame Darstellung beider Werte in einer Tabelle würde beim Leser genau die Verwechslung nahelegen, die Parlow (2021) als Kernproblem der UHI-Literatur beschreibt<sup>[4]</sup>.
2. **Räumlich, für uns der wichtigere Punkt:** 1 km² Auflösung kann die kleinräumige Binnendifferenzierung innerhalb einer Gemeinde wie Gernsbach (82 km², wenige Dutzend Rasterzellen) nicht auflösen — genau die Auflösung, die den Kern unseres Wertversprechens ausmacht (siehe "Was dieser Report leistet", Abschnitt 1). Der DWD-Dienst kann unsere Kernfrage für kleine und mittlere Gemeinden methodisch nicht beantworten.

**Konsequenz für den Report:** Der UHI-MAP-Dienst wird nicht als zusätzliche Datenquelle eingebunden oder zitiert, um Ergebnisse zu untermauern, sondern höchstens als Kontexthinweis erwähnt — etwa: *"Ergänzend bietet der Deutsche Wetterdienst mit dem UHI-MAP-Klimadienst ein bundesweites, lufttemperaturbasiertes Monitoring der städtischen Wärmeinsel (1 km² Auflösung). Für die hier relevante kleinräumige Differenzierung innerhalb der Gemeinde ist diese Auflösung nicht geeignet — das schließt die vorliegende Analyse."* Diese Formulierung wertet das eigene Produkt auf, statt es zu verwässern, weil sie die Lücke benennt, die wir füllen.

### 4.3 Umweltbundesamt und Zentrum KlimaAnpassung

Für die Einordnung in den kommunalen Klimaanpassungsprozess orientiert sich das Produkt am Aufbau der UBA-Publikation *"Klimarisikoanalysen auf kommunaler Ebene"* (Porst, Voß, Kahlenborn & Schauser, 2022), die in Anlehnung an ISO 14091 zwischen Exposition, Sensitivität und Anpassungskapazität unterscheidet<sup>[9]</sup>. Unser Report liefert primär die **Expositions**-Komponente (wo ist die Gemeinde thermisch/vegetationsseitig auffällig); die im Zusatzmodul "Förderfähigkeit" vorgesehene Verknüpfung mit Bevölkerungsdichte und sensiblen Einrichtungen (Kitas, Pflegeheime) bewegt sich Richtung Sensitivität, ersetzt aber keine vollständige Vulnerabilitätsanalyse.

Das **Zentrum KlimaAnpassung** (gegründet 2021, getragen von Difu und adelphi im Auftrag des BMUV) dient als Referenzstelle für die Einordnung in bestehende kommunale Beratungsstrukturen und als möglicher Multiplikator (siehe Businessplan A5), nicht als methodische Quelle für die Kennzahlenberechnung selbst<sup>[10]</sup>.

### 4.4 Fernerkundungsmethodik im engeren Sinn

- Voogt & Oke (2003) — s. Abschnitt 3 — Grundlage für die SUHI/UHI-Unterscheidung.
- Parlow (2021) — s. Abschnitt 3 — Grundlage für die Vorsicht bei Kausalaussagen.
- Shreevastava et al. (2019) — s. Abschnitt 2 — Grundlage für die relative statt absolute Klassifizierung.
- Die Landsat-Collection-2-Level-2-ST-Verarbeitungskette selbst (Skalierungsformel, Emissivitätskorrektur) folgt der offiziellen USGS-Produktdokumentation<sup>[11]</sup>. **Aktiv verfolgter Vormerkpunkt, nicht nur dokumentiert:** Der USGS bereitet aktuell eine Collection-3-Neuprozessierung mit überarbeitetem Emissivitäts- und Atmosphärenkorrekturverfahren vor (geplant für die späten 2020er-Jahre)<sup>[12]</sup>. Das ist kein rein passiver Hinweis: Sobald Collection 3 veröffentlicht wird, muss geprüft werden, ob die bereits berechneten LST-Referenzwerte der drei Pilotgemeinden neu berechnet werden müssen, um über die Zeit konsistent zu bleiben — relevant spätestens für das Monitoring-Abo (Businessplan A4, Stufe 3), das auf Jahr-zu-Jahr-Vergleichbarkeit angewiesen ist. Dieser Punkt wird eigenständig nachverfolgt (nicht nur in diesem Dokument vermerkt) und bei jeder Aktualisierung der Pipeline oder des Monitoring-Abos erneut geprüft.

---

## 5. Referenzgruppenvergleich

**Geplantes Vorgehen (Umsetzung in Phase 3):** Jede Gemeinde wird nicht nur intern (Anomalie gegen eigenen Mittelwert), sondern auch extern gegen eine Referenzgruppe vergleichbarer Gemeinden eingeordnet — Kriterien: Einwohnergrößenklasse (5.000–50.000, siehe Businessplan A2) und Naturraum (z. B. Rheinebene/Oberrheingraben vs. Schwarzwald-Randlagen vs. norddeutsches Tiefland). Die Einordnung erfolgt als **Perzentilrang** innerhalb der Referenzgruppe, nicht als weitere absolute Zahl — konsistent mit dem Grundprinzip aus Abschnitt 2.

**Offener Punkt, noch zu klären, bevor das operativ wird:** Mit aktuell drei Pilotgemeinden (alle im selben Naturraum, Landkreis Rastatt/Baden-Baden) existiert noch keine belastbare Referenzgruppe. Eine Perzentilangabe wäre bei einer Stichprobe von n=3 methodisch nicht vertretbar. Für den ersten produktiven Report muss entweder (a) auf eine öffentlich verfügbare Vergleichsstatistik zurückgegriffen werden (zu prüfen: ob DWD-, UBA- oder Forschungsprojekt-Datensätze mit vergleichbarer Methodik existieren) oder (b) der Referenzgruppenvergleich für die ersten Reports offen als "vorläufig, Stichprobe wird erweitert" gekennzeichnet werden.

**Zeitliche Einordnung eines größer angelegten Referenzlaufs (explizit festgehalten, um Vorgriffe zu vermeiden):** Ein Durchlauf über eine größere Zahl von Gemeinden (im Bereich mehrerer Hundert) zum Aufbau einer belastbaren Referenzstatistik ist ausdrücklich **erst nach** zwei Voraussetzungen sinnvoll: (1) abgeschlossene externe Plausibilisierung der Methodik (Businessplan Phase 2, Punkt 5) und (2) eine in Phase 3 gebaute, fehlertolerante Pipeline-Funktion, die für beliebige Gemeinden entweder ein valides Ergebnis oder eine klare, protokollierte Fehlermeldung liefert — nicht die drei aktuell handgebauten Einzelskripte. Vor Erfüllung beider Punkte fehlt die Möglichkeit, Fehler in der Breite zu erkennen (bei den drei Pilotgemeinden durch Ortskenntnis abgesichert, bei einer großen unbekannten Menge nicht). Wenn der Referenzlauf dann stattfindet, sollte er zudem **stratifiziert** nach Naturraum und Größenklasse gezogen werden, nicht als unstrukturierte Masse — das ist für die Repräsentativität der Referenzgruppe wichtiger als die reine Fallzahl.

---

## 6. Bekannte Limitationen (Fallstricke)

Diese Liste ist bewusst vollständig und ungeschönt — sie ist die Grundlage für den entsprechenden Abschnitt in jedem Report und für das Gespräch mit der externen Plausibilisierung.

| # | Limitation | Auswirkung | Umgang im Projekt |
|---|---|---|---|
| 1 | **Landsat-Überflugzeit vormittags** (ca. 10:30 Ortszeit) | Erfasst nicht das Nachmittagsmaximum der Aufheizung; SUHI-Intensität tagsüber generell variabel, unser Zeitpunkt ist nur eine Stichprobe des Tagesverlaufs | Explizit im Report benannt (bereits in Task-3-README dokumentiert) |
| 2 | **Landsat-Wiederholrate** (16 Tage je Satellit, 8 Tage kombiniert L8+L9) | Wenige nutzbare Termine pro Sommer bei zusätzlicher Bewölkung | Aggregation über 5 Sommer, hierarchische Mittelung (bereits implementiert) |
| 3 | **Räumliche Auflösung LST** (~100 m nativ, 30 m geliefert) vs. NDVI (10 m) | Gröbere Auflösung kann kleinräumige Hotspots verwässern, besonders bei kleinen/flächigen Gemeinden | Als Phase-1-Erfolgskriterium geprüft und für alle drei Pilotgemeinden bestanden; bleibt Restrisiko für untypische Gemeinden |
| 4 | **Mischpixel an Gemeinderändern** | Randpixel können Werte der Nachbargemeinde enthalten | Bisher nicht gesondert behandelt — **offener Punkt für Phase 3**, insbesondere bei den Sinzheim-Exklaven relevant, wo der Rand-zu-Fläche-Anteil besonders hoch ist |
| 5 | **Wolkenfilterung uneinheitlich zwischen Pilotgemeinden** | Gernsbachs NDVI-Skript filtert nur auf Szenenebene (max. Gesamtwolkenbedeckung), Sinzheim und Baden-Baden nutzen pixelgenaue SCL-Maskierung | **Muss vor Phase 3 behoben werden**: Gernsbach-NDVI-Skript nachziehen, sonst sind die drei Pilot-NDVI-Werte nicht direkt vergleichbar — das unterläuft den in Abschnitt 5 beschriebenen Referenzgruppenvergleich, sobald er live geht |
| 6 | **Koordinatensystem** | Falsche Flächen-/Rasterberechnung bei Vermischung von WGS84 und UTM | Durchgängig EPSG:25832, technisch bereits sichergestellt und stichprobenartig verifiziert |
| 7 | **SUHI ungleich UHI** (siehe Abschnitt 3) | Fachliche Angreifbarkeit bei unpräziser Sprache | Verpflichtende Begriffsregel, s. o. |
| 8 | **Fehlende Bodenvalidierung** | Keine Kalibrierung gegen tatsächliche Messstationen vor Ort | Parlow (2021) nennt begrenzte Bodenvalidierung als generisches Problem der UHI-Fernerkundungsliteratur<sup>[4]</sup>; für dieses Produkt bewusst nicht vorgesehen (Kostenrahmen), aber im Report als Limitation zu nennen, nicht zu verschweigen |
| 9 | **Sentinel-2-Wiederholrate und Wolkenfilterung** | Bei ungünstiger Wetterlage (z. B. verregneter Sommer) ggf. zu wenige Termine für einen belastbaren Median-Komposit | Mindestanzahl von 3 Terminen als Warnschwelle implementiert, kein stiller Fallback |
| 10 | **Bevorstehende Landsat-Collection-3-Neuprozessierung** | Künftige LST-Werte ggf. nicht direkt mit heutigen vergleichbar | Vormerken für Monitoring-Abo (Businessplan A4, Stufe 3) — Versionswechsel muss dokumentiert werden, sobald er eintritt |

---

## 7. Umgang mit Datenqualitätsproblemen — Grundprinzip

Kein stiller Fallback, keine Interpolation über fehlende Daten hinweg, kein Platzhalterwert. Wenn eine Gemeinde nicht mit ausreichender Datenqualität berechnet werden kann, liefert die Pipeline eine explizite Fehlermeldung statt eines optisch plausiblen, aber methodisch nicht abgesicherten Ergebnisses. Das ist in der bisherigen Implementierung (Tasks 1–3) durchgehend so umgesetzt und bleibt verbindliche Vorgabe für Phase 3.

---

## 8. Attribution (verpflichtender Quellenblock für jeden Report)

> Enthält modifizierte Copernicus-Sentinel-Daten [Jahr], verarbeitet durch FCX.
> Enthält Landsat-Daten des U.S. Geological Survey.
> Verwaltungsgeometrien: © GeoBasis-DE / BKG [Jahr] (dl-de/by-2-0).

---

## 9. Offene Punkte vor Abschluss von Phase 2

1. Klassifizierungslogik für Versiegelungsgrad (CLMS-Daten, noch nicht implementiert) analog zu NDVI/LST festlegen.
2. Wolkenfilterungs-Inkonsistenz zwischen Gernsbach und den beiden anderen Pilotgemeinden beheben (siehe Tabelle Punkt 5).
3. Referenzgruppen-Frage klären (Abschnitt 5) — realistischerweise erst mit mehr Pilotgemeinden oder externer Vergleichsstatistik lösbar.
4. **Externe Plausibilisierung einholen** (Businessplan Phase 2, Punkt 5) — dieses Dokument ist die Diskussionsgrundlage dafür, nicht der Ersatz dafür.

---

## Literaturverzeichnis

[1] Shreevastava, A., Bhalachandran, S., McGrath, G. S., Huber, M., & Rao, P. S. C. (2019). Paradoxical impact of sprawling intra-Urban Heat Islets: Reducing mean surface temperatures while enhancing local extremes. *Scientific Reports*, 9, 19681. https://doi.org/10.1038/s41598-019-56091-w

[2] Voogt, J. A., & Oke, T. R. (2003). Thermal remote sensing of urban climates. *Remote Sensing of Environment*, 86(3), 370–384. https://doi.org/10.1016/S0034-4257(03)00079-8

[3] Deutscher Wetterdienst. Glossar: Städtische Wärmeinsel. Abgerufen 2026, von https://www.dwd.de/DE/service/lexikon/Functions/glossar.html?lv3=744502

[4] Parlow, E. (2021). Regarding Some Pitfalls in Urban Heat Island Studies Using Remote Sensing Technology. *Remote Sensing*, 13(18), 3598. https://doi.org/10.3390/rs13183598

[5] VDI 3787 Blatt 1 (2015). Umweltmeteorologie — Klima- und Lufthygienekarten für Städte und Regionen. Verein Deutscher Ingenieure.

[6] VDI 3787 Blatt 2 (2008). Umweltmeteorologie — Methoden zur human-biometeorologischen Bewertung der thermischen Komponente des Klimas. Verein Deutscher Ingenieure.

[7] VDI 3787 Blatt 5 (2003). Umweltmeteorologie — Lokale Kaltluft. Verein Deutscher Ingenieure.

[8] Deutscher Wetterdienst. UHI-MAP Klimadienst. https://www.dwd.de/DE/klimaumwelt/ku_beratung/stadt-regionalplanung/

[9] Porst, L., Voß, M., Kahlenborn, W., & Schauser, I. (2022). *Klimarisikoanalysen auf kommunaler Ebene*. Umweltbundesamt.

[10] Zentrum KlimaAnpassung. Difu / adelphi, im Auftrag des Bundesministeriums für Umwelt, Naturschutz, nukleare Sicherheit und Verbraucherschutz (BMUV). https://zentrum-klimaanpassung.de

[11] U.S. Geological Survey (2024). *Landsat 8-9 Collection 2 Level-2 Science Product Guide* (LSDS-1619, Version 6.0).

[12] U.S. Geological Survey. Enhancements to the USGS Landsat Level 2 surface temperature and emissivity product for Collection 3 reprocessing. https://www.usgs.gov/publications/enhancements-usgs-landsat-level-2-surface-temperature-and-emissivity-product

---

*Dieses Dokument ist ein Entwurf (v0.1) zur internen Diskussion und externen Plausibilisierung. Es ersetzt nicht die in Businessplan Phase 2 vorgesehene fachliche Prüfung durch ein Fachbüro, eine Hochschule oder eine Stadtklimatologin/einen Stadtklimatologen.*
