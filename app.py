import os
import csv
import sqlite3
import random
import joblib
import subprocess
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from datetime import datetime
from employees_db import employees, file_access

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"

LOG_FILE_PATH = "IAM_logs/logs.csv"
DB_PATH = "iam_database.db"

rf_model = joblib.load("models/rf_model.pkl")
device_encoder = joblib.load("models/device_encoder.pkl")
decision_encoder = joblib.load("models/decision_encoder.pkl")

os.makedirs("IAM_logs", exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def log_activity(username, action, risk_score=0, access_result="N/A"):
    """Logs user activity into SQLite and CSV."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Store in SQLite
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (timestamp, username, action, risk_score, access_result) VALUES (?, ?, ?, ?, ?)",
        (timestamp, username, action, risk_score, access_result)
    )
    conn.commit()
    conn.close()

    # Store in CSV logs
    log_exists = os.path.exists(LOG_FILE_PATH)
    with open(LOG_FILE_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        if not log_exists:
            writer.writerow(["Timestamp", "Username", "Action", "Risk Score", "Access Result"])
        writer.writerow([timestamp, username, action, risk_score, access_result])

    print(f"Activity logged: {username} - {action} - Risk Score: {risk_score} - Access: {access_result}")

def get_recent_activities(username):
    """Fetch recent activities of a user from the logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, action FROM logs WHERE username = ? ORDER BY timestamp DESC LIMIT 5", (username,))
    logs = cursor.fetchall()
    conn.close()
    return [f"{log['timestamp']} - {log['action']}" for log in logs]

@app.route("/", methods=["GET", "POST"])
def login():
    """Handles user login, assigns risk scores, and determines access."""
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            risk_score = round(random.uniform(0, 1), 2)  # Simulated Risk Score
            access_result = "Allowed" if risk_score < 0.5 else "MFA Required" if risk_score < 0.8 else "Denied"

            log_activity(username, "Login Attempt", risk_score, access_result)

            if access_result == "Allowed":
                session["username"] = username
                return redirect(url_for("dashboard"))
            elif access_result == "MFA Required":
                return render_template("mfa.html", username=username)
            else:
                return render_template("denied.html", username=username)

        error = "Invalid credentials. Try again."

    return render_template("login.html", error=error)

@app.route("/dashboard")
def dashboard():
    """Loads the user-specific dashboard with logs and file access details."""
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_data = employees.get(username, {})
    role = user_data.get("role", "User")
    location = user_data.get("location", "Unknown")
    working_hours = user_data.get("working_hours", "Not specified")
    files = user_data.get("files", [])

    last_login = get_recent_activities(username)[0] if get_recent_activities(username) else "First Login"
    activities = get_recent_activities(username)

    return render_template(
        "dashboard.html",
        username=username,
        role=role,
        location=location,
        working_hours=working_hours,
        files=files,
        last_login=last_login,
        activities=activities
    )

@app.route("/access_file/<filename>")
def access_file(filename):
    """Logs file access and allows users to open their assigned files."""
    if "username" in session:
        username = session["username"]
        log_activity(username, f"Accessed {filename}", 0, "Allowed")
        return f"Opening {filename}..."
    
    return redirect(url_for("login"))

@app.route("/log_file_access", methods=["POST"])
def log_file():
    """API to log file access events."""
    data = request.get_json()
    log_activity(data["username"], "File Access", 0, "Allowed")
    return jsonify({"message": "File access logged successfully"})

@app.route("/logs")
def get_logs():
    """Fetches recent logs as JSON for real-time monitoring."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, username, action, risk_score, access_result FROM logs ORDER BY timestamp DESC LIMIT 10")
    logs = cursor.fetchall()
    conn.close()

    logs_list = [{"timestamp": row["timestamp"], "username": row["username"], "action": row["action"], "risk_score": row["risk_score"], "access_result": row["access_result"]} for row in logs]

    return jsonify(logs_list)

@app.route("/logout")
def logout():
    """Logs the user out."""
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)