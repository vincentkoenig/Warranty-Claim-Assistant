import os
from dotenv import load_dotenv

# Lädt die Werte aus der .env-Datei in die Umgebungsvariablen
load_dotenv()


class Config:
    # Wird von Flask-SQLAlchemy benötigt, um DB-Verbindung aufzubauen
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///warranty_assistant.db"
    )
    # Deaktiviert ein Feature, das wir nicht brauchen und nur Overhead erzeugt
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OpenAI API Key, wird in extraction.py verwendet
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")