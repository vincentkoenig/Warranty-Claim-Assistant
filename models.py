from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

# Wird in app.py mit db.init_app(app) an die Flask-App gebunden
db = SQLAlchemy()


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vin = db.Column(db.String(17), unique=True, nullable=False)  # Fahrgestellnummer
    brand = db.Column(db.String(50), nullable=False)  # "Toyota", "Lexus", "VW Nutzfahrzeuge"
    model = db.Column(db.String(100))
    first_registration = db.Column(db.Date)  # Erstzulassung
    purchase_mileage_km = db.Column(db.Integer)  # Kilometerstand bei Kauf

    # Beziehung zu Complaints, damit man vehicle.complaints aufrufen kann
    complaints = db.relationship("Complaint", backref="vehicle", lazy=True)


class WarrantyRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    brand = db.Column(db.String(50), nullable=False)
    max_months = db.Column(db.Integer, nullable=False)
    max_mileage_km = db.Column(db.Integer, nullable=False)
    excluded_components = db.Column(db.Text)  # Kommagetrennte Liste, z.B. "Verschleißteile,Reifen,Bremsbeläge"


class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicle.id"), nullable=False)
    raw_text = db.Column(db.Text)  # Freitext oder extrahierter PDF-Inhalt
    source_type = db.Column(db.String(20))  # "text" oder "pdf"
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="pending")  # pending, reviewed, closed

    # Beziehungen, damit man complaint.extraction und complaint.decision aufrufen kann
    extraction = db.relationship("ComplaintExtraction", backref="complaint", uselist=False, lazy=True)
    decision = db.relationship("ComplaintDecision", backref="complaint", uselist=False, lazy=True)


class ComplaintExtraction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaint.id"), nullable=False)
    reported_component = db.Column(db.String(100))  # genanntes Bauteil
    reported_issue = db.Column(db.Text)  # Fehlerbeschreibung
    reported_mileage_km = db.Column(db.Integer)  # vom Kunden genannter km-Stand
    extracted_at = db.Column(db.DateTime, default=datetime.utcnow)


class ComplaintDecision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey("complaint.id"), nullable=False)
    rule_result = db.Column(db.String(20))  # "covered", "not_covered", "unclear"
    rule_reason = db.Column(db.Text)  # welche Regel gegriffen hat (aus rules.py, reine Logik)
    llm_recommendation = db.Column(db.Text)  # ausformulierte Begründung fürs Mitarbeiter-Review
    decided_at = db.Column(db.DateTime, default=datetime.utcnow)