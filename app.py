from flask import Flask, request, render_template
import pandas as pd
import joblib

# Ensure Flask knows where the templates folder is
app = Flask(__name__, template_folder="templates")

# Load models
rf_model = joblib.load("rf_model.pkl")
device_encoder = joblib.load("device_encoder.pkl")
decision_encoder = joblib.load("decision_encoder.pkl")

@app.route("/", methods=["GET", "POST"])
def index():
    decision = None

    if request.method == "POST":
        try:
            timestamp_str = request.form.get("timestamp")
            device_str = request.form.get("device")
            risk_score = float(request.form.get("risk_score"))
            
            timestamp = pd.to_datetime(timestamp_str).timestamp()
            device_val = device_encoder.transform([device_str])[0]
            
            new_event = pd.DataFrame({
                "Timestamp": [timestamp],
                "Device": [device_val],
                "Risk Score": [risk_score]
            })

            decision = decision_encoder.inverse_transform(rf_model.predict(new_event))[0]

        except Exception as e:
            print("Error:", str(e))

    return render_template("index.html", decision=decision)

if __name__ == "__main__":
    app.run(debug=True)
