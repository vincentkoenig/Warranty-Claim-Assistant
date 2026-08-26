from flask import Flask, render_template, request, redirect, url_for
from config import Config
from models import db, Vehicle, Complaint, ComplaintExtraction, ComplaintDecision
from extraction import extract_complaint_data
from rules import check_warranty
from recommendation import generate_recommendation

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)


@app.route("/")
def index():
    vehicles = Vehicle.query.all()
    return render_template("submit_complaint.html", vehicles=vehicles)


@app.route("/submit", methods=["POST"])
def submit_complaint():
    vehicle_id = request.form["vehicle_id"]
    raw_text = request.form["complaint_text"]

    vehicle = Vehicle.query.get_or_404(vehicle_id)

    # 1. Complaint anlegen (Rohdaten)
    complaint = Complaint(
        vehicle_id=vehicle.id,
        raw_text=raw_text,
        source_type="text",
        status="pending"
    )
    db.session.add(complaint)
    db.session.commit()  # commit, damit complaint.id existiert

    # 2. Extraction
    extracted_data = extract_complaint_data(raw_text)
    extraction = ComplaintExtraction(
        complaint_id=complaint.id,
        reported_component=extracted_data["reported_component"],
        reported_issue=extracted_data["reported_issue"],
        reported_mileage_km=extracted_data["reported_mileage_km"]
    )
    db.session.add(extraction)
    db.session.commit()

    # 3. Regelprüfung
    rule_result = check_warranty(vehicle, extraction)

    # 4. Empfehlung formulieren
    recommendation_text = generate_recommendation(vehicle, extraction, rule_result)

    # 5. Decision speichern
    decision = ComplaintDecision(
        complaint_id=complaint.id,
        rule_result=rule_result["result"],
        rule_reason=rule_result["reason"],
        llm_recommendation=recommendation_text
    )
    db.session.add(decision)

    complaint.status = "reviewed"
    db.session.commit()

    return redirect(url_for("view_complaint", complaint_id=complaint.id))


@app.route("/complaints")
def list_complaints():
    complaints = Complaint.query.order_by(Complaint.submitted_at.desc()).all()
    return render_template("review.html", complaints=complaints)


@app.route("/complaints/<int:complaint_id>")
def view_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    return render_template("complaint_detail.html", complaint=complaint)


if __name__ == "__main__":
    app.run(debug=True)