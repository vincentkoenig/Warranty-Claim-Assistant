import os
from openai import OpenAI

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "Du bist ein Assistent, der Mitarbeitern eines Autohauses hilft, "
    "Garantiefälle nachvollziehbar einzuschätzen. "
    "Du erhältst die Reklamationsdaten und das Ergebnis einer automatisierten "
    "Regelprüfung. Formuliere daraus eine kurze, sachliche Empfehlung in 2-3 Sätzen "
    "für den Mitarbeiter. Mach klar, dass es sich um eine Empfehlung handelt, "
    "keine endgültige Entscheidung - der Mitarbeiter trifft die finale Entscheidung. "
    "Sei präzise, nicht blumig."
)


def generate_recommendation(vehicle, extraction, rule_result: dict) -> str:
    """
    Erzeugt einen verständlichen Empfehlungstext für den Mitarbeiter,
    basierend auf den extrahierten Reklamationsdaten und dem Ergebnis
    der deterministischen Regelprüfung (rules.py).

    Trifft selbst keine Entscheidung - gibt nur das Ergebnis aus rules.py
    in verständlicher Sprache wieder.
    """
    context = (
        f"Fahrzeug: {vehicle.brand} {vehicle.model}, "
        f"Erstzulassung: {vehicle.first_registration}\n"
        f"Gemeldetes Bauteil: {extraction.reported_component}\n"
        f"Fehlerbeschreibung: {extraction.reported_issue}\n"
        f"Gemeldeter Kilometerstand: {extraction.reported_mileage_km} km\n"
        f"Regelprüfung ergab: {rule_result['result']}\n"
        f"Begründung der Regelprüfung: {rule_result['reason']}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
    )

    return response.choices[0].message.content