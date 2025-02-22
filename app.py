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

# Paths
LOG_FILE_PATH = "IAM_logs/logs.csv"
DB_PATH = "iam_database.db"

# Load AI Models
rf_model = joblib.load("models/rf_model.pkl")
device_encoder = joblib.load("models/device_encoder.pkl")
decision_encoder = joblib.load("models/decision_encoder.pkl")

# Ensure Logs Directory Exists
os.makedirs("IAM_logs", exist_ok=True)

# Initialize Database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )""")
    
    # Create logs table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        username TEXT NOT NULL,
        action TEXT NOT NULL,
        risk_score REAL NOT NULL,
        access_result TEXT NOT NULL
    )""")
    
    conn.commit()
    conn.close()

# Function to log activities (Both CSV & SQLite)
def log_activity(username, action, risk_score, access_result):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Log to SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO logs (timestamp, username, action, risk_score, access_result) VALUES (?, ?, ?, ?, ?)",
        (timestamp, username, action, risk_score, access_result),
    )
    conn.commit()
    conn.close()

    # Log to CSV
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Username", "Action", "Risk Score", "Access Result"])
    
    with open(LOG_FILE_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, username, action, risk_score, access_result])

    push_logs_to_github()

# Function to Push Logs to GitHub
def push_logs_to_github():
    """Push the updated logs to the GitHub repository."""
    try:
        subprocess.run(["git", "add", LOG_FILE_PATH], check=True)
        subprocess.run(["git", "commit", "-m", "Updated logs"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except Exception as e:
        print("Git push failed:", str(e))

# AI Risk Calculation Function
def calculate_risk(username, new_device, new_location):
    last_behavior = employees.get(username, {"device": "Laptop", "location": "New York"})
    risk_score = 0.1  # Base risk

    if new_device != last_behavior.get("device", "Laptop"):
        risk_score += 0.4
    if new_location != last_behavior.get("location", "New York"):
        risk_score += 0.3

    return min(1, risk_score)

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB_PATH)
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
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_role = employees.get(username, {}).get("role", "User")
    access_levels = employees.get(username, {}).get("access_level", [])

    # Ensure file_access keys exist
    allowed_files = [file_access.get(level, []) for level in access_levels]

    return render_template("dashboard.html", username=username, role=user_role, allowed_files=allowed_files)

@app.route("/access_file/<filename>")
def access_file(filename):
    if "username" in session:
        username = session["username"]
        log_activity(username, f"Accessed {filename}", 0, "Allowed")
        return f"Opening {filename}..."
    
    return redirect(url_for("login"))

@app.route("/log_file_access", methods=["POST"])
def log_file():
    data = request.get_json()
    log_activity(data["username"], "File Access", 0, "Allowed")
    return jsonify({"message": "File access logged successfully"})

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    init_db()  # Initialize database tables if not exist
    app.run(host="0.0.0.0", port=5000, debug=True)
