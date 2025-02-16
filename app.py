from flask import Flask, request, render_template
import pandas as pd
import joblib

app = Flask(__name__, template_folder='templates')

# Load your model and encoders
rf_model = joblib.load('rf_model.pkl')
device_encoder = joblib.load('device_encoder.pkl')
decision_encoder = joblib.load('decision_encoder.pkl')

def adaptive_iam_decision(new_event_df):
    # Get prediction from your model
    prediction = rf_model.predict(new_event_df)
    # Convert numeric prediction back to original label
    decision = decision_encoder.inverse_transform(prediction)
    return decision[0]

@app.route('/', methods=['GET', 'POST'])
def index():
    decision = None

    if request.method == 'POST':
        # Get form data
        timestamp_str = request.form.get('timestamp')
        device_str = request.form.get('device')
        risk_score = float(request.form.get('risk_score'))
        
        # Convert timestamp to numeric (seconds since epoch)
        timestamp = pd.to_datetime(timestamp_str).timestamp()
        
        # Transform the device string to numeric value using device_encoder
        try:
            device_val = device_encoder.transform([device_str])[0]
        except ValueError:
            # Handle case where device is not recognized
            device_val = 0  # default or show error message
        
        # Create new event DataFrame
        new_event = pd.DataFrame({
            "Timestamp": [timestamp],
            "Device": [device_val],
            "Risk Score": [risk_score]
        })
        
        # Get model decision
        decision = adaptive_iam_decision(new_event)
    
    return render_template('index.html', decision=decision)

if __name__ == '__main__':
    app.run(debug=True)
