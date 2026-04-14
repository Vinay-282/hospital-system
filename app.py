from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)
def get_db():
    return sqlite3.connect("database.db")

# Create table 
@app.route("/init")
def init():
    conn = get_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            gender TEXT,
            problem TEXT
        )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS doctors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        specialization TEXT,
        phone TEXT
    )
''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient_id INTEGER,
        doctor_id INTEGER,
        date TEXT,
        time TEXT
    )
''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        appointment_id INTEGER,
        medicines TEXT,
        notes TEXT
    )
''')
    conn.commit()
    conn.close()
    return "Database Initialized!"

# Home
@app.route("/")
def intro():
    return render_template("intro.html")
@app.route("/home")
def home():
    return render_template("index.html")

# Add Patient
@app.route("/add_patient", methods=["POST"])
def add_patient():
    name = request.form["name"]
    age = request.form["age"]
    gender = request.form["gender"]
    problem = request.form["problem"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO patients (name, age, gender, problem) VALUES (?, ?, ?, ?)",
                (name, age, gender, problem))
    conn.commit()
    conn.close()

    return redirect("/patients")

# View Patients
@app.route("/patients")
def patients():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM patients")
    data = cur.fetchall()
    conn.close()

    return render_template("patients.html", patients=data)

# Delete Patient
@app.route("/delete_patient/<int:id>")
def delete_patient(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM patients WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/patients")

#Add Doctor
@app.route("/add_doctor", methods=["POST"])
def add_doctor():
    name = request.form["name"]
    specialization = request.form["specialization"]
    phone = request.form["phone"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO doctors (name, specialization, phone) VALUES (?, ?, ?)",
                (name, specialization, phone))
    conn.commit()
    conn.close()

    return redirect("/doctors")

#View Doctors
@app.route("/doctors")
def doctors():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM doctors")
    data = cur.fetchall()
    conn.close()

    return render_template("doctors.html", doctors=data)

#Delete Doctor
@app.route("/delete_doctor/<int:id>")
def delete_doctor(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM doctors WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/doctors")

#Add Appointment
# Add Appointment
@app.route("/add_appointment", methods=["POST"])
def add_appointment():
    patient_id = request.form["patient_id"]
    doctor_id = request.form["doctor_id"]
    date = request.form["date"]
    time = request.form["time"]
    problem = request.form["problem"].lower()

    # Suggest doctor type
    if "heart" in problem:
        suggestion = "Cardiologist"
    elif "skin" in problem:
        suggestion = "Dermatologist"
    elif "eye" in problem:
        suggestion = "Ophthalmologist"
    elif "fever" in problem:
        suggestion = "General Physician"
    else:
        suggestion = "General Physician"

    conn = get_db()
    cur = conn.cursor()

    # Find doctor name
    cur.execute(
        "SELECT name, specialization FROM doctors WHERE specialization LIKE ?",
        ('%' + suggestion + '%',)
    )

    doc = cur.fetchone()

    if doc:
        doctor_name = doc[0]
        doctor_spec = doc[1]
        final_suggestion = f"{doctor_spec} - {doctor_name}"
    else:
        final_suggestion = "No matching doctor found"

    # Insert appointment
    cur.execute(
        "INSERT INTO appointments (patient_id, doctor_id, date, time) VALUES (?, ?, ?, ?)",
        (patient_id, doctor_id, date, time)
    )

    conn.commit()
    conn.close()
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        SELECT a.id, p.name, d.name, a.date, a.time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
    ''')

    data = cur.fetchall()
    conn.close()

    return render_template("appointments.html", appointments=data, suggestion=final_suggestion)
#View Appointments
@app.route("/appointments")
def appointments():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        SELECT a.id, p.name, d.name, a.date, a.time
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
    ''')

    data = cur.fetchall()
    conn.close()

    return render_template("appointments.html", appointments=data)

#Delete Appointment
@app.route("/delete_appointment/<int:id>")
def delete_appointment(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM appointments WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/appointments")

#Search Patients
@app.route("/search", methods=["GET", "POST"])
def search():
    result = []

    if request.method == "POST":
        query = request.form["query"]

        conn = get_db()
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM patients WHERE name LIKE ? OR id=?",
            ('%' + query + '%', query if query.isdigit() else -1)
        )

        result = cur.fetchall()
        conn.close()

    return render_template("search.html", result=result)

#Add Prescription
@app.route("/add_prescription", methods=["POST"])
def add_prescription():
    appointment_id = request.form["appointment_id"]
    medicines = request.form["medicines"]
    notes = request.form["notes"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO prescriptions (appointment_id, medicines, notes) VALUES (?, ?, ?)",
        (appointment_id, medicines, notes)
    )
    conn.commit()
    conn.close()

    return redirect("/prescriptions")

#View Prescriptions
@app.route("/prescriptions")
def prescriptions():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        SELECT pr.id, p.name, d.name, pr.medicines, pr.notes
        FROM prescriptions pr
        JOIN appointments a ON pr.appointment_id = a.id
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
    ''')

    data = cur.fetchall()
    conn.close()

    return render_template("prescriptions.html", prescriptions=data)

#Delete Prescription
@app.route("/delete_prescription/<int:id>")
def delete_prescription(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM prescriptions WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/prescriptions")

if __name__ == "__main__":
    app.run(debug=True)
