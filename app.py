import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import pandas as pd
import joblib
import subprocess
from datetime import datetime
from employees_db import employees, file_access

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"

# Load AI Models
rf_model = joblib.load("models/rf_model.pkl")
device_encoder = joblib.load("models/device_encoder.pkl")
decision_encoder = joblib.load("models/decision_encoder.pkl")

# Log File Path
LOG_FILE_PATH = "IAM_logs/logs.csv"

# AI Risk Calculation Function
def calculate_risk(username, new_device, new_location):
    last_behavior = employees.get(username, {"device": "Laptop", "location": "New York"})
    risk_score = 0.1  # Base risk

    if new_device != last_behavior["device"]:
        risk_score += 0.4
    if new_location != last_behavior["location"]:
        risk_score += 0.3

    return min(1, risk_score)

# Logging Function
def log_activity(username, event_type, details):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = [timestamp, username, event_type, details]

    # Ensure logs.csv exists
    os.makedirs("IAM_logs", exist_ok=True)
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Username", "Event Type", "Details"])

    # Append new log entry
    with open(LOG_FILE_PATH, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(log_entry)

    push_logs_to_github()

# Function to Push Logs to GitHub
def push_logs_to_github():
    try:
        subprocess.run(["git", "add", LOG_FILE_PATH], check=True)
        subprocess.run(["git", "commit", "-m", "Updated logs"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
    except Exception as e:
        print("Git push failed:", str(e))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in employees and employees[username]["password"] == password:
            session["username"] = username
            log_activity(username, "Login", "Successful login")
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid Credentials. Please try again."
            log_activity(username, "Login", "Failed login attempt")

    return render_template("login.html", error=error)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_role = employees[username]["role"]
    access_levels = employees[username]["access_level"]
    allowed_files = [file_access[level] for level in access_levels]

    return render_template("dashboard.html", username=username, role=user_role, allowed_files=allowed_files)

@app.route("/log_file_access", methods=["POST"])
def log_file():
    data = request.get_json()
    log_activity(data["username"], "File Access", data["file_name"])
    return jsonify({"message": "File access logged successfully"})

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
