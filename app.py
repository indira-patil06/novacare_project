from fpdf import FPDF
from flask import send_file
from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask('__name__')

# Path to the user "database"
USER_DB = "users.json"

# ---------- Helper Functions ----------
def load_users():
    if not os.path.exists(USER_DB):
        return {}
    with open(USER_DB, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_DB, "w") as f:
        json.dump(users, f, indent=4)

# ---------- Routes ----------

# Home Page
@app.route('/')
def home():
    return render_template('mainpage.html')

# Doctors Page
@app.route('/doctors')
def doctors():
    return render_template('doctors.html')

# Login Form Page
@app.route('/role_login')
def role_login():
    return render_template('role_login.html')

# Registration Form Page
@app.route('/form')
def form():
    return render_template('form.html')

# Registration Submission
@app.route('/submit', methods=['POST'])
def submit():
    users = load_users()
    user_id = request.form['name'].lower().replace(" ", "")

    user_data = {
        "id": user_id,
        "name": request.form['name'],
        "dob": request.form['dob'],
        "gender": request.form['gender'],
        "blood_group": request.form['blood_group'],
        "allergies": request.form['allergies'],
        "conditions": request.form['conditions'],
        "emergency_name": request.form['emergency_name'],
        "emergency_phone": request.form['emergency_phone'],
        "emergency_relation": request.form['emergency_relation']
    }

    users[user_id] = user_data
    save_users(users)

    return redirect(url_for('role_login'))

# Dashboard Page
@app.route('/dashboard')
def dashboard():
    user_id = request.args.get('user_id', '').lower().replace(" ", "")
    role = request.args.get('role')

    users = load_users()
    user = users.get(user_id)

    if user:
        return render_template('dashboard.html', user=user, role=role)
    else:
        return "❌ User not found. Please register first.", 404

@app.route('/dashboard')
def doctor_dashboard():
    role = request.args.get('role')
    user_id = request.args.get('user_id')

    if role.lower() == 'doctor':
        patients = load_all_patients_from_database()  # your database function
        return render_template('doctor_dashboard.html', patients=patients)
    else:
        # For patients, maybe redirect to a patient-specific dashboard
        return redirect(url_for('patient_dashboard', user_id=user_id))


# Optional: Dummy Endpoints for QR and PDF
import qrcode

@app.route('/generate_qr/<user_id>')
def generate_qr(user_id):
    users = load_users()
    user = users.get(user_id)

    if not user:
        return "❌ User not found", 404

    # Data to encode in the QR code
    qr_data = f"Name: {user['name']}\nDOB: {user['dob']}\nBlood Group: {user['blood_group']}\nEmergency: {user['emergency_name']} - {user['emergency_phone']}"

    # Generate QR Code
    qr = qrcode.make(qr_data)

    # Save it into static/qr/ folder
    qr_path = f"static/qr/{user_id}_qr.png"
    qr.save(qr_path)

    # Display the image on a simple page
    return f"""
    <h3>✅ QR Code for {user['name']}</h3>
    <img src="/{qr_path}" alt="QR Code for {user['name']}" style="margin-top:20px;">
    <br><br>
    <a href="/dashboard?user_id={user_id}&role=patient">⬅ Back to Dashboard</a>
    """


@app.route('/export_pdf/<user_id>')
def export_pdf(user_id):
    users = load_users()
    user = users.get(user_id)

    if not user:
        return "❌ User not found", 404

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"Health Card for {user['name']}", ln=True, align="C")
    pdf.ln(10)

    for key, label in [
        ("dob", "Date of Birth"),
        ("gender", "Gender"),
        ("blood_group", "Blood Group"),
        ("allergies", "Allergies"),
        ("conditions", "Conditions"),
        ("emergency_name", "Emergency Contact Name"),
        ("emergency_phone", "Emergency Phone"),
        ("emergency_relation", "Emergency Relation"),
    ]:
        value = user.get(key, "N/A")
        pdf.cell(200, 10, txt=f"{label}: {value}", ln=True)

    filepath = f"{user_id}_healthcard.pdf"
    pdf.output(filepath)

    return send_file(filepath, as_attachment=True)
def export_pdf(user_id):
    return f"PDF Export for {user_id} (placeholder)"

# ---------- Run App ----------
if __name__ == '_main_':
    app.run(debug=True)