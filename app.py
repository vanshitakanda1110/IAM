import os
from flask import Flask, render_template, request  # Added 'request' import
import joblib
import pandas as pd

template_path = os.path.join(os.getcwd(), "templates")
print("Template path:", template_path)

app = Flask(__name__, template_folder=template_path)

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

            # Convert timestamp to numerical format
            timestamp = pd.to_datetime(timestamp_str).timestamp()
            device_val = device_encoder.transform([device_str])[0]

            # Create dataframe for prediction
            new_event = pd.DataFrame({
                "Timestamp": [timestamp],
                "Device": [device_val],
                "Risk Score": [risk_score]
            })

            # Predict decision
            decision = decision_encoder.inverse_transform(rf_model.predict(new_event))[0]

        except Exception as e:
            print("Error:", str(e))

    return render_template("index.html", decision=decision)

if __name__ == "__main__":
    app.run(debug=True)
