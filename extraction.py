import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# JSON Schema für die Structured Output-Antwort
# Muss exakt zu den Feldern von ComplaintExtraction (models.py) passen
EXTRACTION_SCHEMA = {
    "type": "json_schema",
    "json_schema": {
        "name": "complaint_extraction",
        "schema": {
            "type": "object",
            "properties": {
                "reported_component": {
                    "type": "string",
                    "description": "Das vom Kunden genannte betroffene Bauteil, z.B. 'Motor', 'Getriebe', 'Bremsen'"
                },
                "reported_issue": {
                    "type": "string",
                    "description": "Kurze, sachliche Zusammenfassung der Fehlerbeschreibung"
                },
                "reported_mileage_km": {
                    "type": "integer",
                    "description": "Der vom Kunden genannte Kilometerstand. 0, falls nicht erwähnt."
                }
            },
            "required": ["reported_component", "reported_issue", "reported_mileage_km"],
            "additionalProperties": False
        },
        "strict": True
    }
}

SYSTEM_PROMPT = (
    "Du bist ein Assistent, der Kundenreklamationen für ein Autohaus analysiert. "
    "Extrahiere aus dem folgenden Text die relevanten Informationen. "
    "Sei sachlich und übernimm keine wertenden Aussagen des Kunden. "
    "Falls ein Wert nicht im Text steht, nutze einen sinnvollen Platzhalter "
    "(bei Zahlen: 0, bei Text: 'nicht angegeben')."
)


def extract_complaint_data(raw_text: str) -> dict:
    """
    Nimmt den Rohtext einer Reklamation entgegen und gibt ein Dict mit
    reported_component, reported_issue und reported_mileage_km zurück.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": raw_text}
        ],
        response_format=EXTRACTION_SCHEMA
    )

    # Bei strict=True garantiert die API, dass hier valides JSON steht,
    # das exakt dem Schema entspricht - kein try/except für Parsing-Fehler nötig
    import json
    result = json.loads(response.choices[0].message.content)
    return result