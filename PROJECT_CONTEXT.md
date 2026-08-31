# Klima-Check für Kommunen
## Businessplan & Umsetzungsleitfaden

*Stand: 28.08.2026 · Portfolio-Projekt neben der KI-Agentur*

---

## Kurzfassung

**Produkt:** Ein automatisiert erzeugter Klimaanpassungs-Report für kleine und mittlere Gemeinden, basierend ausschließlich auf frei verfügbaren Satelliten- und Geodaten (Copernicus, Landsat, BKG, Zensus). Der Report zeigt die thermische Ist-Lage (Hitzeinseln, Versiegelung, Grünanteil), ordnet sie nach etablierten fachlichen Kriterien ein und liefert im zweiten Teil einen vorstrukturierten Entwurf für einen Förderantrag.

**Kernwertversprechen:** Nicht die Daten (die sind kostenlos), sondern *Zeitersparnis und Antragsfähigkeit*. Eine Gemeinde mit 8.000 Einwohnern hat kein GIS-Team. Sie bekommt in 48 Stunden für einen niedrigen vierstelligen Betrag das, wofür ein Ingenieurbüro drei Monate und 25.000 € braucht.

**Geschäftsmodell:** Einmal-Report (Einstieg) + jährliches Monitoring-Abo + Zusatzmodul Förderantrag.

**Realistische Einschätzung vorab:** Das ist kein schnelles Cashflow-Projekt. Der technische Aufbau ist in 4–6 Wochen machbar, der erste bezahlte Auftrag realistisch nach 3–6 Monaten. Was für die Idee spricht: nahezu null Grenzkosten pro zusätzlicher Gemeinde, ein politisch getriebener Bedarf und ein Zielsegment, das die etablierten Anbieter bewusst ignorieren. Was dagegen spricht: langsame Käufer, Vergaberecht und die Frage, ob dein Vertriebsplan (Massenversand) rechtlich so umsetzbar ist wie gedacht — dazu unten mehr.

---

# TEIL A — BUSINESSPLAN

## A1 · Problem und Lösung

### Das Problem der Zielgruppe

Kleine Kommunen stehen unter wachsendem Handlungsdruck bei der Klimaanpassung — durch Landes-Klimaanpassungsgesetze, durch Bürgerbeschwerden nach Hitzesommern, durch Anforderungen in Bauleitplanverfahren. Gleichzeitig gilt:

- Sie haben **kein Fachpersonal.** Ein Bauamt mit 3 Personen macht Baugenehmigungen, keine Fernerkundungsanalysen.
- Sie haben **kein Budget für Gutachten.** Eine vollwertige Stadtklimaanalyse nach VDI 3787 von einem Fachbüro kostet je nach Umfang einen mittleren bis hohen fünfstelligen Betrag.
- Sie sind von den bestehenden Angeboten **nicht abgedeckt.** Der Copernicus Urban Atlas deckt nur funktionale Stadtregionen ab einer bestimmten Größenordnung ab — kleine Gemeinden fallen durchs Raster. Forschungsprojekte wie KLIPS oder UrbanGreenEye laufen mit einzelnen Großstädten.
- Sie **wissen nicht, dass es Fördermittel gibt** — und wenn doch, ist der Antrag die eigentliche Hürde.

### Die Lösung

Ein standardisierter, automatisiert erzeugter Report, der genau die Lücke zwischen "gar nichts" und "50.000-€-Gutachten" füllt. Kein Beratungsprodukt, sondern ein **Informationsprodukt mit reproduzierbarer Methodik.**

### Die bewusste Abgrenzung (wichtig für Haftung)

Das Produkt liefert:
- ✅ Messwerte aus offiziellen Datenquellen
- ✅ Eine regelbasierte Einordnung nach offengelegten, aus der Fachliteratur abgeleiteten Kriterien
- ✅ Einen Vergleich mit einer Referenzgruppe
- ✅ Textbausteine für einen Förderantrag

Das Produkt liefert **nicht**:
- ❌ Eine Stadtklimaanalyse nach VDI 3787 (das ist ein geschützter fachlicher Standard mit anderen Anforderungen)
- ❌ Planungsrechtlich verwertbare Gutachten
- ❌ Individuelle Handlungsempfehlungen mit Verantwortungsübernahme

Diese Abgrenzung gehört wörtlich in jeden Report und in die AGB. Sie ist kein Nachteil, sondern der Grund, warum du das Produkt überhaupt ohne Ingenieurbüro-Zulassung skalieren kannst.

---

## A2 · Markt und Zielkunde

### Marktgröße bestimmen (nicht schätzen)

Deutschland hat rund 10.700 Gemeinden. Dein Zielsegment ist die Größenklasse, die groß genug für ein Problem und zu klein für eine eigene Lösung ist.

**Aufgabe für Phase 0:** Zieh dir das amtliche Gemeindeverzeichnis (Destatis GV-ISys, kostenlos) und filtere:

| Filter | Begründung |
|---|---|
| Einwohner 5.000–50.000 | Unter 5.000 kein Budget, über 50.000 meist eigene Klimaanpassungsstelle |
| Siedlungsdichte über Median | Ohne verdichtete Bebauung kein Hitzeinsel-Thema |
| Kein bestehendes Klimaanpassungskonzept | Recherchierbar über Fördermitteldatenbanken |
| Bundesland mit aktivem Landesförderprogramm | erhöht Abschlusswahrscheinlichkeit |

Erwartungswert: ein Zielmarkt in der Größenordnung **1.500–2.500 Gemeinden**. Verifiziere die Zahl selbst — arbeite nie mit einer geschätzten Marktgröße im eigenen Plan.

### Wer entscheidet in der Kommune?

Das ist die entscheidende Frage für den Vertrieb — nicht die Technik.

| Rolle | Rolle im Kauf | Ansprache |
|---|---|---|
| **Klimaanpassungsmanager\*in** | Bester Einstieg, wo vorhanden. Hat das Thema, sucht Argumente, kennt die Fördertöpfe. | Fachlich, kollegial |
| **Leitung Bauamt / Stadtplanung** | Häufigster faktischer Entscheider in kleinen Gemeinden | Zeitersparnis, Anlass Bauleitplanung |
| **Bürgermeister\*in** | Entscheidet bei kleinen Beträgen oft direkt | Politischer Nutzen, Fördermittel-Argument |
| **Kämmerei** | Vetorecht über Budget | Direktauftragsgrenze, Förderquote |

**Praktische Konsequenz:** Der erste Kontakt sollte immer die Fachebene sein (Klimaanpassungsmanagement oder Bauamtsleitung), nicht das Rathaus-Sekretariat.

### Der Kaufanlass

Kommunen kaufen nicht, weil ein Angebot gut ist. Sie kaufen, wenn ein **Anlass** vorliegt:

1. Ein anstehender Förderantrag mit Fristdruck
2. Ein laufendes Bauleitplanverfahren, in dem Klimabelange abgewogen werden müssen
3. Ein Ratsbeschluss oder Bürgerantrag zum Thema Hitze
4. Ein Hitzesommer im Rückspiegel

**Vertriebliche Konsequenz:** Timing ist wichtiger als Überzeugungskraft. Deine Ansprache muss so aufgebaut sein, dass sie bei den 5 % Gemeinden zündet, die gerade einen Anlass haben — und bei den anderen 95 % im Ordner landet, ohne zu nerven.

---

## A3 · Wettbewerb und Positionierung

### Wettbewerbsumfeld

| Anbietertyp | Beispiele | Stärke | Deine Chance |
|---|---|---|---|
| **Forschungsprojekte** | KLIPS, UrbanGreenEye (Leipzig) | Wissenschaftlich fundiert, für Kommune kostenlos | Nur einzelne Partnerstädte, nicht skalierend, oft mit Sensornetzwerk = teuer |
| **Raumfahrt-/Großanbieter** | OHB Urban View u. ä. | Technisch stark, Referenzen | Zielt auf Großstädte und öffentliche Auftraggeber, hohe Preise |
| **Spezialisierte Software** | z. B. Klimabilanz-Tools mit NDVI/Hitzeinsel-Modulen | Direkter Wettbewerber | Prüfen: Preis, Zielgruppe, ob Förderantrag enthalten |
| **Ingenieur-/Planungsbüros** | regional, viele | Vertrauen, Rechtssicherheit | Teuer, langsam, nicht skalierbar |
| **Öffentliche Portale** | GIS-ImmoRisk, Landes-Klimaatlanten, EO4CAM | Kostenlos | Rohdaten ohne Aufbereitung, Bedienung erfordert Fachwissen, kein Antragsbezug |
| **Nichts tun** | — | kostenlos | **Dein eigentlicher Hauptwettbewerber** |

### Dein Positionierungssatz

> "Die Datenlage, mit der Sie einen Förderantrag begründen können — in 48 Stunden statt in sechs Monaten, zum Preis eines Direktauftrags."

### Deine drei Differenzierungsmerkmale

1. **Preisklasse.** Bewusst unterhalb der kommunalen Direktauftragsgrenze. Kein Vergabeverfahren = kein Monatelanges Warten. (Die Grenze variiert je Bundesland und Kommune, meist 1.000–5.000 € netto. **Recherchiere die Grenzen der Bundesländer, die du zuerst angehst** — das ist deine wichtigste Preisleitplanke.)
2. **Anschlussfähigkeit an Förderung.** Du verkaufst nicht Daten, sondern die Vorstufe zu Geld für die Gemeinde.
3. **Zielgruppengröße.** Alle anderen gehen auf Großstädte. Du gehst auf die 8.000-Einwohner-Gemeinde, für die niemand ein Angebot baut, weil sich Einzelbetreuung nicht rechnet — was durch Automatisierung genau dein Vorteil ist.

---

## A4 · Produkt und Preise

### Produktstufen

**Stufe 0 — Teaser-Report (kostenlos, automatisiert)**
2–3 Seiten. Übersichtskarte der Gemeinde mit Hitzeinsel-Anomalie, eine Gesamt-Ampel, ein anonymisierter Hinweis auf die Position im Vergleich zur Referenzgruppe. Konkrete Kennzahlen, Detailkarten und Förderteil bleiben verdeckt.
→ *Zweck: Aufmerksamkeit erzeugen, Relevanz beweisen.*

**Stufe 1 — Klima-Check Basis** · Richtwert **1.400–2.400 €** netto
12–16 Seiten PDF + Kartenmaterial als GeoTIFF/PNG zur Weiterverwendung.
Kapitel:
1. Zusammenfassung mit Ampel-Übersicht (1 Seite, für den Rat)
2. Methodik und Datenquellen (Transparenz + Haftungsabgrenzung)
3. Thermische Belastung — Karte der Oberflächentemperatur-Anomalie, Hotspots benannt (Straßenzüge/Quartiere)
4. Versiegelungsgrad — Karte + Kennzahl gesamt und je Ortsteil
5. Grün- und Vegetationsausstattung (NDVI-basiert) + Entwicklung über die letzten ~5 Jahre
6. Betroffenheit: Überlagerung der Hotspots mit Bevölkerungsdichte (Zensus-Gitter) und sensiblen Einrichtungen (Kitas, Schulen, Pflegeheime — via OpenStreetMap)
7. Vergleich mit Referenzgruppe (Gemeinden gleicher Größenklasse und Naturraum)
8. Datenblatt-Anhang mit allen Rohkennzahlen

**Stufe 2 — Modul Förderfähigkeit** · Richtwert **+900–1.500 €**
Aufbereitung der Ergebnisse als Textbausteine entlang der Gliederung einer konkreten Förderrichtlinie: Ausgangslage, Betroffenheitsanalyse, Handlungsbedarf, Indikatoren für die spätere Wirkungskontrolle. Plus Kurzübersicht der aktuell offenen Förderfenster für diese Gemeinde.

**Stufe 3 — Monitoring-Abo** · Richtwert **900–1.800 € / Jahr**
Jährliche Aktualisierung, Veränderungsanalyse gegenüber dem Vorjahr, Wirkungsnachweis für umgesetzte Maßnahmen. **Das ist der eigentlich interessante Teil des Geschäftsmodells** — denn die Wirkungskontrolle ist bei fast allen Förderprogrammen eine Auflage, und niemand liefert sie einfach.

### Preislogik

| Prinzip | Umsetzung |
|---|---|
| Unter der Direktauftragsgrenze bleiben | Basis + Modul zusammen sollten in den relevanten Bundesländern ohne Vergabeverfahren beauftragbar sein — ggf. als zwei getrennte Aufträge kalkulieren |
| Kein Stundensatz | Festpreis pro Gemeinde. Du verkaufst ein Produkt, keine Dienstleistung |
| Gegenrechnung sichtbar machen | "Ihr Eigenanteil bei 65 % Förderquote: ca. 500 €" wirkt stärker als jeder Rabatt |
| Kein Dumping | Unter 1.000 € wirkt es für eine Verwaltung unseriös, nicht günstig |

---

## A5 · Vertrieb — mit einer wichtigen Korrektur

### ⚠️ Zum Plan "Teaser-Reports per Mail an hunderte Gemeinden"

Die Idee ist strategisch richtig, aber der Kanal ist rechtlich problematisch. **E-Mail-Werbung ohne vorherige ausdrückliche Einwilligung ist nach § 7 UWG unzulässig — und das gilt nicht nur gegenüber Verbrauchern, sondern auch im B2B- und Behördenkontext.** Ein Massenversand an 500 Rathäuser ist damit angreifbar, und im kommunalen Umfeld ist Reputation dein einziges Vertriebskapital. Eine einzige Beschwerde bei einem Kommunalverband kostet dich mehr als 500 Mails einbringen.

**Der Umbau, der die Idee rettet:** Der eigentliche Hebel deiner Idee ist nicht der Kanal, sondern die *Personalisierung im Maßstab* — dass jede Gemeinde etwas über sich selbst sieht. Diesen Hebel bekommst du auch legal:

| Kanal | Zulässigkeit | Einsatz |
|---|---|---|
| **Postbrief** | Zulässig, auch als Kaltakquise | **Hauptkanal.** Personalisierter 2-Seiten-Teaser mit der Karte der Gemeinde. Kosten ca. 1,20–1,80 € inkl. Druck. 300 Briefe ≈ 500 € |
| **Telefon** | Im B2B/Behördenkontext bei mutmaßlichem Interesse zulässig (§ 7 Abs. 2 Nr. 1 UWG) | Follow-up 5–8 Tage nach dem Brief. **Hier entstehen die Abschlüsse** |
| **Öffentliches Portal** | Uneingeschränkt | Landingpage, auf der jede Gemeinde ihren Teaser selbst abrufen kann → aus Kaltakquise wird Inbound, und der Abruf ist zugleich die Einwilligung für weitere Mails |
| **E-Mail** | Nur nach Einwilligung oder auf Anfrage | Nach Portalabruf oder Telefonkontakt |
| **Fachverbände / Multiplikatoren** | — | Städte- und Gemeindebund der Länder, kommunale Klimaschutzagenturen, Zentrum KlimaAnpassung. **Höchster Hebel überhaupt** — ein Fachartikel oder Webinar dort erreicht mehr als 1.000 Briefe |

**Empfohlene Reihenfolge:** Portal live → Teaser für alle Zielgemeinden vorgenerieren → Brief an 200–300 priorisierte Gemeinden → Telefon-Follow-up → parallel Multiplikatoren ansprechen.

### Der Brief (Struktur)

Eine Seite Text, eine Seite Karte. Nicht mehr.

1. Betreff: Konkret und ortsbezogen — "Thermische Belastung im Gemeindegebiet [Name]: Auswertung aktueller Satellitendaten"
2. Ein Satz Anlass ("Nach den Sommern der letzten Jahre …")
3. **Die Karte der eigenen Gemeinde** — das ist der gesamte Effekt des Briefs
4. Zwei bis drei Sätze Ergebnis, davon einer mit einer verdeckten Zahl
5. Der Fördermittel-Hinweis
6. Ein einziger Call-to-Action: Link zum Portal oder Rückruf-Angebot
7. Quellen- und Methodikhinweis in der Fußzeile (schafft Seriosität)

### Vergaberechtlicher Hinweis

Unterhalb der Wertgrenzen für Direktaufträge kann eine Kommune formlos beauftragen. Die Grenzen unterscheiden sich je Bundesland und teils je Kommune. **Nimm diese Information aktiv in dein Angebot auf** ("Der Auftragswert liegt unterhalb der Direktauftragsgrenze in [Bundesland]") — das nimmt dem Bauamt die größte gedankliche Hürde ab. Prüfe die Grenzen selbst und lass dir das ggf. einmalig anwaltlich bestätigen.

---

## A6 · Wirtschaftlichkeit

### Kostenstruktur

| Position | Aufbau (einmalig) | Laufend |
|---|---|---|
| Deine Zeit | 120–200 h | ~10–20 h / Monat |
| Datenzugang (Copernicus, Landsat, BKG, Zensus, OSM) | 0 € | 0 € |
| Rechenzeit / Server | — | 20–60 € / Monat |
| Domain, Portal, Mailversand | ~100 € | ~30 € / Monat |
| Rechtsberatung (AGB, Haftungsausschluss, UWG-Check) | 800–1.500 € | — |
| Fachliche Plausibilisierung (siehe Phase 2) | 500–1.500 € | gelegentlich |
| Briefkampagne | — | ~1,50 € / Kontakt |

**Grenzkosten pro zusätzlichem Report: praktisch null.** Das ist der ökonomische Kern des Modells und der Grund, warum es sich trotz langsamer Kunden rechnen kann.

### Break-Even

Bei ca. 2.500 € Auftragswert (Basis + Modul) und einem Aufbauaufwand von rund 3.000–4.000 € an Fremdkosten liegt der finanzielle Break-Even bei **2 verkauften Reports.** Der Break-Even auf deine eigene Zeit gerechnet (150 h) liegt je nach angesetztem Stundensatz bei **4–6 Reports.**

### Szenarien Jahr 1

| Szenario | Verkaufte Reports | Abos | Umsatz |
|---|---|---|---|
| Pessimistisch | 3 | 1 | ~8.000 € |
| Realistisch | 8 | 4 | ~25.000 € |
| Optimistisch (mit Multiplikator-Effekt) | 20 | 12 | ~65.000 € |

Ansetzen solltest du das pessimistische Szenario. Die Idee trägt sich, wenn sie nebenher läuft — nicht, wenn sie tragen muss.

### Die eigentliche Skalierungsfrage

Ab ca. 30 Bestandskunden wird das Monitoring-Abo zum tragenden Umsatz, und der Vertriebsaufwand pro Neukunde sinkt durch Referenzen deutlich. **Ab da wird es interessant.** Bis dahin ist es ein Portfolio-Projekt mit moderatem Rückfluss.

---

## A7 · Risiken und Abbruchkriterien

| Risiko | Schwere | Gegenmaßnahme |
|---|---|---|
| Fachliche Angreifbarkeit der Methodik | hoch | Methodik offenlegen, an anerkannten Referenzen orientieren, einmalig extern plausibilisieren lassen (Phase 2) |
| Haftung bei Fehlentscheidung der Kommune | mittel | Strikte Beschränkung auf Ist-Darstellung, expliziter Ausschluss in AGB und Report |
| Öffentlicher Anbieter macht es kostenlos | hoch | Nicht verhinderbar. Deshalb: Wert liegt im Förderteil und im Monitoring, nicht in den Daten |
| Verkaufszyklus länger als geplant | hoch | Erwartung von Anfang an auf 6–12 Monate stellen. Nicht auf Cashflow angewiesen sein |
| Rechtliches Problem bei Kaltakquise | mittel | Postweg statt Mail (siehe A5) |
| Datenqualität für kleine Gemeinden unzureichend | mittel | In Phase 1 zwingend an 3 realen Gemeinden prüfen, **bevor** irgendetwas gebaut wird |

### Abbruchkriterien — vorher festlegen

Definiere jetzt, wann du aufhörst. Vorschlag:

- **Nach Phase 1 (Woche 2):** Wenn die Auflösung der Thermaldaten für eine 10.000-Einwohner-Gemeinde keine erkennbare Binnendifferenzierung zeigt → das Produkt trägt nicht. Abbruch oder Neuausrichtung auf größere Gemeinden.
- **Nach Phase 4 (Monat 3):** Wenn von 200 kontaktierten Gemeinden weniger als 5 in ein Gespräch gehen → Kanal oder Angebot falsch. Eine Nachjustierung, dann Abbruch.
- **Nach Monat 9:** Wenn kein zahlender Kunde → Abbruch. Der Code und die Pipeline bleiben als wiederverwendbare Bausteine für die Agentur.

---

# TEIL B — UMSETZUNG IN PHASEN

## Phase 0 · Fundament (Woche 1, ca. 8–12 h)

**Ziel:** Entscheidungsgrundlage schaffen, bevor Aufwand entsteht.

1. **Zielgemeinden-Liste bauen.** Gemeindeverzeichnis von Destatis ziehen, nach den Kriterien aus A2 filtern, als CSV ablegen. Ergebnis: konkrete Zahl statt Schätzung.
2. **Drei Pilotgemeinden auswählen.** Unterschiedliche Charakteristika: eine verdichtete Kleinstadt, eine flächige Gemeinde, eine im Umland einer Großstadt. Am besten Gemeinden, die du kennst — dann kannst du die Ergebnisse gegen deine eigene Ortskenntnis prüfen.
3. **Wettbewerb konkret prüfen.** Bestehende kommerzielle Anbieter anschreiben oder Preislisten recherchieren. Du musst wissen, gegen welchen Preis du antrittst.
4. **Direktauftragsgrenzen** der 3–4 Bundesländer recherchieren, die du zuerst angehen willst.
5. **Aktuelle Förderfenster prüfen** (BMUKN/ZUG, Landesprogramme, kommunale Digitalisierungsförderung). Diese Fenster öffnen und schließen — arbeite nie mit veralteten Informationen im Angebot.

**Ergebnis Phase 0:** Zielliste, 3 Pilotgemeinden, Preiskorridor, Förderlage.

---

## Phase 1 · Technischer Durchstich (Woche 1–2, ca. 30–40 h)

**Ziel:** Für **eine** Gemeinde manuell alle drei Kernkennzahlen erzeugen. Noch kein Report, noch keine Automatisierung. Nur: funktionieren die Daten?

**Das ist die kritischste Phase.** Wenn hier die Datenqualität nicht reicht, ist alles Weitere gegenstandslos.

**Schritte:**
1. Zugänge einrichten (CDSE-Konto, Planetary Computer, BKG-Download) — Details in Teil C
2. Gemeindegrenze als Geometrie laden
3. Vegetationsindex (NDVI) aus Sentinel-2 für einen Sommer berechnen
4. Versiegelungsgrad aus dem Copernicus-Layer ausschneiden
5. Oberflächentemperatur aus Landsat für 3–5 wolkenfreie Sommertermine berechnen und mitteln
6. Alle drei Layer auf ein gemeinsames Raster bringen und übereinanderlegen
7. **Sichtprüfung:** Liegen die Hotspots dort, wo du sie erwartest? Gewerbegebiet, Ortskern, große Parkplätze warm — Wald, Wiesen, Bachläufe kühl?

**Erfolgskriterium:** Die Karte muss innerhalb der Gemeinde erkennbar differenzieren und mit deiner Ortskenntnis übereinstimmen. Wenn die ganze Gemeinde einfarbig ist, reicht die Auflösung nicht.

---

## Phase 2 · Methodik festzurren (Woche 3, ca. 20–25 h)

**Ziel:** Aus Rohwerten wird eine verteidigbare Einordnung.

**Schritte:**
1. **Klassifizierungslogik definieren und schriftlich fixieren.** Empfehlung: keine absoluten Temperaturschwellen verwenden, sondern eine **relative Anomalie** — Abweichung jedes Rasterpunkts vom Mittelwert des Gemeindegebiets bzw. vom umgebenden Freiland. Das ist methodisch deutlich robuster und weniger angreifbar als eine absolute Grenze, die es so nicht gibt.
2. **Fachliche Verankerung recherchieren.** Orientiere dich an anerkannten Referenzen (u. a. VDI 3787 für Stadtklimaanalysen, DWD-Publikationen zu städtischen Wärmeinseln, Handreichungen des Umweltbundesamts und des Zentrums KlimaAnpassung). Jede Schwelle, die du setzt, braucht eine benennbare Herleitung.
3. **Die zentrale Einschränkung sauber formulieren:** Satellitengestützte Oberflächentemperatur ist **nicht** Lufttemperatur und **nicht** thermische Belastung des Menschen. Sie ist ein Indikator für Wärmespeicherung von Oberflächen. Dieser Satz gehört prominent in jeden Report. Er schützt dich und macht dich gleichzeitig glaubwürdiger als ein Anbieter, der ihn weglässt.
4. **Referenzgruppen-Vergleich vorbereiten:** Definieren, welche Gemeinden vergleichbar sind (Größenklasse, Naturraum, Siedlungsdichte).
5. **Externe Plausibilisierung einholen.** Ein Fachbüro, ein Hochschulinstitut oder ein\*e Stadtklimatolog\*in schaut einmalig auf deine Methodik und die Ergebnisse für die drei Pilotgemeinden. Kosten: wenige hundert bis ~1.500 €.

   **Warum das trotz allem sinnvoll ist:** Nicht weil das Fachwissen nicht beschaffbar wäre — es ist dokumentiert und erarbeitbar. Sondern aus zwei anderen Gründen: erstens findet ein erfahrener Blick systematische Fehler, die man bei selbst gebauter Methodik strukturell nicht sieht. Zweitens — und praktisch wichtiger — ist "die Methodik wurde von [Institution] geprüft" im Verkaufsgespräch mit einer Verwaltung ein deutlich stärkeres Argument als jede Selbstauskunft. Das ist eine Vertriebsinvestition, nicht nur eine fachliche.

**Ergebnis:** Ein Methodik-Dokument von 3–5 Seiten, das als Kapitel 2 in jeden Report wandert.

---

## Phase 3 · Automatisierung (Woche 4–5, ca. 40–50 h)

**Ziel:** Von "eine Gemeinde manuell" zu "beliebige Gemeinde per Knopfdruck".

**Schritte:**
1. **Pipeline kapseln:** Eine Funktion, die als Eingabe einen amtlichen Gemeindeschlüssel nimmt und als Ausgabe ein strukturiertes Ergebnisobjekt liefert (alle Kennzahlen + Kartenbilder).
2. **Fehlerbehandlung:** Was passiert bei zu wenig wolkenfreien Aufnahmen? Bei fehlenden Daten? Jede Gemeinde muss entweder ein valides Ergebnis oder eine klare Fehlermeldung liefern — niemals ein stilles Falschergebnis.
3. **Report-Vorlage bauen:** HTML-Template mit Platzhaltern → PDF. Design ist hier kein Nebenaspekt: Eine Verwaltung beurteilt Seriosität zuerst über die Optik. Ordentliches Layout, klare Legenden, Quellenangaben, Seitenzahlen, Impressum.
4. **Textgenerierung:** Die beschreibenden Passagen aus den Kennzahlen erzeugen. Empfehlung: **regelbasierte Textbausteine als Grundgerüst**, KI nur zur sprachlichen Glättung. Vollständig frei generierte Fließtexte über Messwerte sind ein Fehlerrisiko, das du in einem Verwaltungsdokument nicht brauchst.
5. **Teaser-Variante:** Dieselbe Pipeline, reduzierter Umfang, gezielt verdeckte Kennzahlen.
6. **Batch-Lauf:** Alle Zielgemeinden eines Bundeslands durchrechnen. Rechenzeit und Kosten messen.

**Ergebnis:** Ein Befehl erzeugt Vollreport und Teaser für jede beliebige Gemeinde.

---

## Phase 4 · Markttest (Woche 6–12, laufend)

**Ziel:** Herausfinden, ob jemand dafür zahlt — bevor weiter gebaut wird.

**Schritte:**
1. **Landingpage** mit Produktbeschreibung, Beispielreport (eine Gemeinde vollständig, öffentlich), Methodik, Preisen, Impressum, AGB.
2. **Rechtliches finalisieren:** AGB, Haftungsausschluss, Copernicus- und Landsat-Attribution, Datenschutzerklärung. Einmalig anwaltlich prüfen lassen.
3. **Erste Briefkampagne:** 100 Gemeinden, ein Bundesland, priorisiert nach Anlass-Wahrscheinlichkeit.
4. **Telefon-Follow-up** nach 5–8 Tagen. Kein Verkaufsgespräch — eine Frage: "Ist das Thema bei Ihnen gerade relevant?" Die Antworten sind wertvoller als die Abschlüsse.
5. **Parallel Multiplikatoren:** Kommunale Spitzenverbände, Klimaschutzagenturen der Länder, Fachzeitschriften für kommunale Verwaltung. Angebot: Fachbeitrag oder kostenloses Webinar. Das ist der Kanal mit dem besten Verhältnis von Aufwand zu Reichweite.
6. **Erster Referenzkunde:** Einer Gemeinde den Vollreport kostenlos oder stark reduziert geben — gegen ein schriftliches Statement und die Erlaubnis, sie als Referenz zu nennen. **Ohne erste Referenz verkaufst du in diesem Markt praktisch nichts.**

**Messgrößen:** Rücklaufquote Brief, Gesprächsquote Telefon, Angebotsquote, Abschlussquote. Diese vier Zahlen entscheiden über Phase 5.

---

## Phase 5 · Ausbau (ab Monat 4, nur bei positivem Markttest)

Erst starten, wenn Phase 4 zahlende Kunden gebracht hat.

1. **Modul Förderfähigkeit** vollständig ausbauen — inkl. Abgleich mit der Gliederung konkreter Richtlinien
2. **Monitoring-Abo** aufsetzen: jährlicher Wiederholungslauf, Veränderungsanalyse, Wirkungsnachweis
3. **Selbstbedienungs-Portal** mit Login, falls Kunden wiederkehrend zugreifen wollen
4. **Auflösung verbessern** (siehe Teil C: ECOSTRESS, ggf. kommunale Geodaten wie ALKIS oder Baumkataster einbinden)
5. **Angrenzende Produkte** aus derselben Pipeline: Starkregen-/Abflussbetrachtung, Dachbegrünungspotenzial, Photovoltaik-Eignung, Baumstandort-Priorisierung. Die Datenbasis ist identisch — jedes Zusatzmodul kostet wenig und erhöht den Auftragswert deutlich.

---

# TEIL C — TECHNISCHER ANHANG

## C1 · Datenquellen

| Layer | Quelle | Auflösung | Zugang | Bemerkung |
|---|---|---|---|---|
| **Oberflächentemperatur (LST)** | Landsat 8/9 Collection 2 Level-2 (Band ST) | ~100 m, auf 30 m geliefert | Microsoft Planetary Computer (STAC) oder USGS EarthExplorer | **Wichtig:** Sentinel-2 hat *keinen* Thermalkanal. Sentinel-3 hat einen, aber mit ~1 km zu grob für kleine Gemeinden |
| **Vegetation (NDVI)** | Sentinel-2 L2A | 10 m | Copernicus Data Space Ecosystem | Sehr gute Auflösung, ideal für Grünflächen |
| **Versiegelungsgrad** | Copernicus Land Monitoring Service, HRL Imperviousness Density | 10 m / 100 m | land.copernicus.eu (Registrierung, kostenlos) | Fertiges Produkt, kein Eigenmodell nötig |
| **Landbedeckung** | CORINE Land Cover / HRL | 100 m | CLMS | Für Kontext und Referenzgruppenbildung |
| **Gemeindegrenzen** | BKG Verwaltungsgebiete (VG250/VG25) | — | Open Data (dl-de/by-2-0) | Amtliche Geometrien, kostenlos |
| **Bevölkerungsverteilung** | Zensus-Gitterdaten | 100 m | Destatis, kostenlos | Für die Betroffenheitsanalyse — **das ist dein Differenzierungsmerkmal** |
| **Sensible Einrichtungen** | OpenStreetMap | Punkte | Overpass API | Kitas, Schulen, Pflegeheime, Krankenhäuser |
| **Höhenmodell** | Copernicus DEM / BKG DGM | 10–30 m | kostenlos | Optional, für Kaltluftbahnen |
| **Klimareferenz** | DWD Open Data | Stationen | opendata.dwd.de | Zur Plausibilisierung |
| **Upgrade-Option LST** | ECOSTRESS (NASA) | 70 m | LP DAAC / AppEEARS | Bessere Auflösung, tageszeitlich variabel, aufwendiger. Für Phase 5 |

## C2 · Zugang zu Copernicus einrichten

**Copernicus Data Space Ecosystem (CDSE)** — der zentrale Zugang seit Ablösung des alten Open Access Hub:

1. Kostenloses Konto auf `dataspace.copernicus.eu` anlegen
2. Zugriffswege:
   - **openEO** — der einfachste Weg für Zeitreihen und Aggregationen, rechnet serverseitig
   - **Sentinel Hub Process API** — komfortabel, mit kostenlosem Kontingent
   - **STAC / OData** — für direkten Dateizugriff und eigene Verarbeitung
3. **Copernicus Land Monitoring Service** (`land.copernicus.eu`) separat registrieren — dort liegen Imperviousness und CORINE als fertige Downloads.

**Landsat über Microsoft Planetary Computer:** STAC-Katalog, kein Konto zwingend erforderlich für den lesenden Zugriff, Zugriff über `pystac-client`.

## C3 · Technologie-Stack

```
Python 3.11+
├── Datenzugriff:    openeo, pystac-client, planetary-computer, requests
├── Raster:          rioxarray, xarray, rasterio, odc-stac
├── Vektor:          geopandas, shapely, pyproj
├── Analyse:         numpy, pandas, scipy
├── Karten:          matplotlib, contextily, cartopy
├── Report:          Jinja2 → HTML → WeasyPrint (PDF)
└── Orchestrierung:  einfache CLI + Cron/GitHub Actions; Prefect erst bei Bedarf
```

Bewusst schlicht gehalten. Keine Datenbank, kein Kubernetes, kein Frontend-Framework in Phase 1–3. Das Produkt ist ein PDF.

## C4 · Ablauf der Pipeline (Struktur)

```
gemeindeschlüssel (AGS)
  │
  ├─► Geometrie laden (BKG VG250, nach AGS filtern)
  │     └─► Bounding Box + Puffer für Umlandvergleich
  │
  ├─► Sentinel-2: Sommeraufnahmen, wolkenfrei gefiltert
  │     └─► NDVI je Termin → Median-Komposit → Grünanteil, Vegetationsvitalität
  │
  ├─► Landsat: Sommertermine, wolkenfrei, Mittagsüberflug
  │     └─► Oberflächentemperatur → Mittel über Termine
  │           └─► Anomalie = Wert − Median(Gemeindegebiet)
  │
  ├─► CLMS Imperviousness: auf Gemeindegebiet zuschneiden
  │     └─► Versiegelungsgrad gesamt + je Ortsteil
  │
  ├─► Zensus-Gitter + OSM-Einrichtungen
  │     └─► Überlagerung mit Hitze-Hotspots → Betroffenheitskennzahl
  │
  ├─► Alle Layer auf gemeinsames Raster (empfohlen: 30 m, EPSG:25832/25833)
  │
  ├─► Klassifizierung nach Methodik-Dokument → Ampelwerte
  │
  ├─► Referenzgruppen-Vergleich (Perzentilrang in der Größenklasse)
  │
  ├─► Kartenbilder rendern (PNG + GeoTIFF)
  │
  └─► Jinja2-Template befüllen → HTML → PDF
        ├─► Vollreport
        └─► Teaser (reduziert)
```

## C5 · Fallstricke

| Problem | Auswirkung | Lösung |
|---|---|---|
| **Bewölkung in Deutschland** | Wenige verwertbare Thermalaufnahmen | Über mehrere Sommer aggregieren (z. B. 5 Jahre), nicht über einen |
| **Landsat-Wiederholrate 16 Tage** | Pro Sommer evtl. nur 2–4 brauchbare Szenen | Landsat 8 und 9 kombinieren → effektiv 8 Tage |
| **Überflugzeit vormittags** | Erfasst nicht das Nachmittagsmaximum | Transparent benennen. Für Aufheizungsmuster trotzdem aussagekräftig. ECOSTRESS als Upgrade |
| **Auflösung 100 m bei LST** | In sehr kleinen Gemeinden zu grob | Erfolgskriterium in Phase 1. Notfalls Zielgruppe nach oben verschieben |
| **Mischpixel an Ortsrändern** | Verfälschte Randwerte | Randpuffer definieren, Grenzpixel gesondert behandeln |
| **Koordinatensysteme** | Falsche Flächenberechnung | Konsequent in UTM (EPSG:25832 West / 25833 Ost) rechnen, nie in WGS84 |
| **Oberflächen- vs. Lufttemperatur** | Fachliche Angreifbarkeit | Explizit im Report klarstellen |

## C6 · Lizenz und Attribution

Copernicus-Daten sind kostenfrei, vollständig und offen nutzbar — auch kommerziell. Voraussetzung ist die korrekte Attribution.

**In jeden Report gehört ein Quellenblock**, z. B.:

> Enthält modifizierte Copernicus-Sentinel-Daten [Jahr], verarbeitet durch [Firma].
> Enthält Daten des Copernicus Land Monitoring Service.
> Enthält Landsat-Daten des U.S. Geological Survey.
> Verwaltungsgeometrien: © GeoBasis-DE / BKG [Jahr] (dl-de/by-2-0).
> Bevölkerungsdaten: Statistische Ämter des Bundes und der Länder, Zensus.
> Punktdaten: © OpenStreetMap-Mitwirkende (ODbL).

**Prüfe die aktuellen Nutzungsbedingungen jeder Quelle vor dem ersten kommerziellen Einsatz selbst.** Insbesondere OpenStreetMap unter ODbL hat eigene Anforderungen an abgeleitete Datenbanken — bei reiner Darstellung im PDF unproblematisch, bei Weitergabe von Datensätzen ist es zu prüfen.

---

## Zusammenfassung: die nächsten drei Schritte

1. **Diese Woche:** Zielgemeinden-Liste erstellen, drei Pilotgemeinden auswählen, Zugänge zu CDSE und CLMS einrichten.
2. **Nächste Woche:** Technischer Durchstich für eine Gemeinde. Danach die ehrliche Entscheidung: differenzieren die Daten ausreichend oder nicht?
3. **Erst danach:** Methodik, Automatisierung, Vertrieb.

Die Reihenfolge ist bewusst so gewählt: Die teuerste Variante des Scheiterns wäre, sechs Wochen zu bauen und dann festzustellen, dass die Auflösung für 8.000-Einwohner-Gemeinden nicht reicht. Das weißt du nach Woche 2 für unter 40 Stunden Aufwand.
