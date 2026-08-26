from datetime import date
from models import WarrantyRule


def check_warranty(vehicle, extraction, complaint_date=None):
    """
    Prüft, ob eine Reklamation nach den hinterlegten Garantiebedingungen
    der jeweiligen Marke gedeckt sein könnte.

    Gibt ein Dict mit 'result' ('covered' / 'not_covered' / 'unclear')
    und 'reason' (Begründung, welches Kriterium entscheidend war) zurück.

    Ein einzelnes nicht erfülltes Kriterium führt direkt zu 'not_covered' -
    kein Kriterium wird gegen ein anderes aufgewogen.
    """
    if complaint_date is None:
        complaint_date = date.today()

    # Passende Regel für die Marke des Fahrzeugs holen
    rule = WarrantyRule.query.filter_by(brand=vehicle.brand).first()

    if rule is None:
        return {
            "result": "unclear",
            "reason": f"Keine Garantieregel für Marke '{vehicle.brand}' hinterlegt."
        }

    # Kriterium 1: Laufzeit prüfen
    months_since_registration = _months_between(vehicle.first_registration, complaint_date)
    if months_since_registration > rule.max_months:
        return {
            "result": "not_covered",
            "reason": (
                f"Fahrzeug ist {months_since_registration} Monate alt, "
                f"Garantie gilt nur bis {rule.max_months} Monate."
            )
        }

    # Kriterium 2: Kilometerstand prüfen
    if extraction.reported_mileage_km > rule.max_mileage_km:
        return {
            "result": "not_covered",
            "reason": (
                f"Gemeldeter Kilometerstand ({extraction.reported_mileage_km} km) "
                f"überschreitet die Garantiegrenze von {rule.max_mileage_km} km."
            )
        }

    # Kriterium 3: Ausgeschlossene Bauteile prüfen
    excluded = _parse_excluded_components(rule.excluded_components)
    if extraction.reported_component.strip().lower() in excluded:
        return {
            "result": "not_covered",
            "reason": (
                f"Bauteil '{extraction.reported_component}' ist laut Garantiebedingungen "
                f"für {vehicle.brand} von der Deckung ausgeschlossen."
            )
        }

    # Alle Kriterien erfüllt
    return {
        "result": "covered",
        "reason": "Laufzeit, Kilometerstand und Bauteil liegen innerhalb der Garantiebedingungen."
    }


def _months_between(start_date, end_date):
    """Berechnet die Anzahl vollständiger Monate zwischen zwei Daten."""
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)


def _parse_excluded_components(excluded_components_str):
    """Wandelt die kommagetrennte Liste in eine Menge kleingeschriebener Begriffe um,
    damit der Vergleich case-insensitive und ohne Leerzeichen-Probleme funktioniert."""
    if not excluded_components_str:
        return set()
    return {item.strip().lower() for item in excluded_components_str.split(",")}