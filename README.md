# Warranty Claim Assistant

Ein agentenbasierter Assistent, der eingereichte Kfz-Garantiereklamationen automatisch analysiert, gegen hinterlegte markenspezifische Garantiebedingungen prüft und eine nachvollziehbare Empfehlung für Mitarbeiter erstellt.

## Überblick

Ein Mitarbeiter reicht einen Reklamationstext (z.B. eine Kundenbeschreibung) für ein bestimmtes Fahrzeug ein. Der Assistent extrahiert daraus strukturierte Daten (Bauteil, Fehlerbeschreibung, Kilometerstand), prüft diese deterministisch gegen die Garantiebedingungen der jeweiligen Marke und liefert eine verständlich formulierte Empfehlung. Die finale Entscheidung trifft weiterhin der Mitarbeiter — der Assistent unterstützt, ersetzt aber keine Entscheidung.

Dieses Projekt ist eine eigenständige Portfolio-Demo mit fiktiven Fahrzeug- und Garantiedaten, entstanden im Rahmen der Vorbereitung auf Bewerbungen im Bereich KI-Automatisierung/Prozessdigitalisierung.

## Architektur

Der Kern des Projekts ist eine bewusste Trennung von drei Verantwortlichkeiten, statt einer einzigen "LLM macht alles"-Logik:

```
Reklamationstext (Freitext)
        │
        ▼
  extraction.py   →  LLM mit Structured Outputs, liest unstrukturierten
        │              Text und extrahiert Bauteil, Fehlerbeschreibung,
        │              Kilometerstand als validiertes JSON
        ▼
    rules.py       →  Reine, deterministische Python-Logik. Prüft die
        │              extrahierten Daten gegen die WarrantyRule der
        │              Fahrzeugmarke (Laufzeit, Kilometerstand, Bauteil-
        │              Ausschlussliste). Kein LLM-Aufruf.
        ▼
recommendation.py  →  LLM formuliert aus dem Regel-Ergebnis eine
        │              verständliche Begründung für den Mitarbeiter.
        ▼
   Entscheidung wird gespeichert, Mitarbeiter trifft finale Entscheidung
```

**Warum diese Trennung:** Die eigentliche Garantie-Entscheidung basiert nicht auf LLM-Output, sondern auf nachvollziehbarer, testbarer Logik. Das LLM übernimmt nur zwei klar abgegrenzte Aufgaben — Sprache verstehen (Extraction) und Sprache erzeugen (Recommendation) — trifft aber selbst keine Entscheidung. Das reduziert das Risiko von Halluzinationen an der Stelle, an der es am meisten zählen würde.

## Datenmodell

| Tabelle | Zweck |
|---|---|
| `Vehicle` | Fahrzeugstammdaten (VIN, Marke, Modell, Erstzulassung) |
| `WarrantyRule` | Garantiebedingungen pro Marke (max. Laufzeit, max. Kilometerstand, ausgeschlossene Bauteile) |
| `Complaint` | Rohdaten der eingereichten Reklamation |
| `ComplaintExtraction` | Vom LLM extrahierte, strukturierte Reklamationsdaten |
| `ComplaintDecision` | Ergebnis der Regelprüfung + LLM-Empfehlungstext |

Rohdaten, Extraktion und Entscheidung sind bewusst in getrennten Tabellen abgelegt, um jeden Verarbeitungsschritt einzeln nachvollziehen zu können.

## Tech-Stack

- **Backend:** Python, Flask, Flask-SQLAlchemy
- **KI:** OpenAI API (GPT-4o-mini) mit Structured Outputs (JSON Schema, `strict: true`) für die Extraktion
- **Datenbank:** SQLite (lokal)
- **Frontend:** Serverseitig gerenderte Templates (Jinja2), HTML/CSS, minimales Vanilla JS — kein Frontend-Framework
- **Sonstiges:** python-dotenv für Konfiguration

## Projektstruktur

```
warranty-claim-assistant/
├── app.py                       # Flask-Routen (Formular, Übersicht, Detailansicht)
├── models.py                    # SQLAlchemy-Modelle (5 Tabellen)
├── extraction.py                 # LLM-Extraktion mit Structured Outputs
├── rules.py                       # Deterministische Garantie-Prüfung, kein LLM
├── recommendation.py               # LLM-generierter Empfehlungstext
├── config.py                        # App-Konfiguration, lädt .env
├── requirements.txt
├── .env                               # OPENAI_API_KEY (nicht versioniert)
├── .env.example
├── templates/
│   ├── submit_complaint.html          # Formular zum Einreichen
│   ├── review.html                     # Übersicht aller Reklamationen
│   └── complaint_detail.html            # Detailansicht mit Prüfergebnis
└── static/
    └── style.css
```

## API-Übersicht

| Methode | Route | Beschreibung |
|---|---|---|
| `GET` | `/` | Formular zum Einreichen einer Reklamation |
| `POST` | `/submit` | Verarbeitet eine Reklamation (Extraction → Rules → Recommendation → Speichern) |
| `GET` | `/complaints` | Übersicht aller Reklamationen |
| `GET` | `/complaints/<id>` | Detailansicht einer einzelnen Reklamation |

## Erste Schritte

**1. Repository klonen und virtuelle Umgebung einrichten**

```bash
git clone https://github.com/vincentkoenig/warranty-claim-assistant.git
cd warranty-claim-assistant
python -m venv venv
venv\Scripts\activate      # Windows
# source venv/bin/activate   # macOS/Linux
pip install -r requirements.txt
```

**2. `.env`-Datei anlegen**

```
OPENAI_API_KEY=dein_openai_api_key
```

> API-Key gibt es unter [platform.openai.com](https://platform.openai.com/api-keys)

**3. Datenbank anlegen und Testdaten einfügen**

```bash
flask shell
```

```python
from models import db
db.create_all()
# Beispiel-WarrantyRules und -Vehicles einfügen (siehe models.py für Feldnamen)
exit()
```

**4. Anwendung starten**

```bash
python app.py
```

**5. Im Browser öffnen**

```
http://127.0.0.1:5000
```

## Was fehlt bewusst

- **Bauteil-Abgleich per exaktem String-Vergleich:** Die Prüfung gegen die Ausschlussliste einer `WarrantyRule` matcht aktuell exakt. Formuliert das LLM ein Bauteil anders als in der Liste hinterlegt (z.B. "Bremsen" statt "Bremsbeläge"), greift der Ausschluss nicht. Bekannte Grenze, nächster Schritt wäre eine kontrollierte Werteliste im Extraction-Schema oder ein toleranteres Matching.
- **Kein Foto-/PDF-Input:** Nur Freitext wird verarbeitet. Bild-basierte Reklamationen (z.B. Fotos vom Schaden) sind nicht angebunden.
- **Keine Bestätigungs-/Korrekturschicht:** Der Mitarbeiter sieht die extrahierten Daten, kann sie aber vor der Regelprüfung nicht editieren.
- **Keine Nutzerauthentifizierung / Multi-User-Unterstützung.**
- **Keine automatisierte Test-Suite:** Testfälle wurden manuell durchgespielt, keine Unit-/Integrationstests.
- **Kein Cloud-Deployment:** Lokale Demo, für dieses MVP ausreichend.

## Datenschutz

Alle Fahrzeug-, Kunden- und Reklamationsdaten in diesem Projekt sind fiktiv. In einem echten Einsatz wären zusätzlich erforderlich: Zugriffskontrolle je nach Mitarbeiterrolle, ein Auftragsverarbeitungsvertrag mit dem LLM-Anbieter (oder der Einsatz eines lokal gehosteten Modells), sowie eine Prüfung, welche Kundendaten überhaupt an ein externes LLM übermittelt werden dürfen.