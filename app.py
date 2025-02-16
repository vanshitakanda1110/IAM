import os
from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import joblib
import random  # For simulated login attempts

app = Flask(__name__, template_folder="templates")
app.secret_key = "your_secret_key"

# Load ML Models
rf_model = joblib.load("models/rf_model.pkl")
device_encoder = joblib.load("models/device_encoder.pkl")
decision_encoder = joblib.load("models/decision_encoder.pkl")

# Employee Roles & Access Levels
employee_roles = {
    "alice": {"password": "password123", "role": "Customer Service", "access_level": [1, 2]},
    "bob": {"password": "securepass", "role": "Loan Officer", "access_level": [1, 2, 3]},
    "charlie": {"password": "accountpass", "role": "Accountant", "access_level": [1, 3]},
    "dave": {"password": "financepass", "role": "Financial Analyst", "access_level": [1, 3, 4]},
    "eve": {"password": "managerpass", "role": "Senior Manager", "access_level": [1, 2, 3, 4]},
    "frank": {"password": "executivepass", "role": "Executive", "access_level": [1, 2, 3, 4, 5]},
}

# Simulated user behavior database
user_behavior = {
    "alice": {"device": "Laptop", "location": "New York"},
    "bob": {"device": "Mobile", "location": "San Francisco"},
}

# Function to Calculate Risk Score
def calculate_risk(username, new_device, new_location):
    last_behavior = user_behavior.get(username, {"device": "Laptop", "location": "New York"})
    risk_score = 0.1  # Base risk score

    if new_device != last_behavior["device"]:
        risk_score += 0.4
    if new_location != last_behavior["location"]:
        risk_score += 0.3

    return min(1, risk_score)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if username in employee_roles and employee_roles[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Invalid Credentials. Please try again."

    return render_template("login.html", error=error)

@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    user_role = employee_roles[username]["role"]
    access_levels = employee_roles[username]["access_level"]
    decision = None
    risk_score = None

    if request.method == "POST":
        new_device = request.form.get("device")
        new_location = request.form.get("location")

        risk_score = calculate_risk(username, new_device, new_location)

        if risk_score <= 0.5:
            decision = "Access Granted"
        elif 0.5 < risk_score <= 0.8:
            session["mfa_required"] = True
            return redirect(url_for("mfa"))
        else:
            return render_template("denied.html")

    return render_template("dashboard.html", username=username, role=user_role, access_levels=access_levels, decision=decision, risk_score=risk_score)

@app.route("/mfa", methods=["GET", "POST"])
def mfa():
    if "username" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        entered_otp = request.form.get("otp")
        if entered_otp == session.get("otp"):
            session.pop("otp", None)
            return redirect(url_for("dashboard"))

    session["otp"] = str(random.randint(100000, 999999))
    print(f"Your OTP is: {session['otp']}")  # In real-world, send via SMS or Email

    return render_template("mfa.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
