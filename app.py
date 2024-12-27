from flask import Flask, request, jsonify
import requests
import nltk
from nltk.tokenize import word_tokenize

nltk.download('punkt')

# Initialize Flask app
app = Flask(__name__)

# Mock availability and doctors
mock_availability = {
    "Dr. Alpha": ["10:00", "14:00", "16:00"],
    "Dr. Beta": ["09:00", "13:00", "15:00"]
}
mock_doctors = [
    {"name": "Dr. Alpha", "specialization": "Cardiologist"},
    {"name": "Dr. Beta", "specialization": "Dermatologist"}
]

# Calendly API settings
CALENDLY_API_KEY = "UWVMPKPJD4MOXCGSBICI42Y3ZW6JM7G6"
CALENDLY_URL = "https://calendly.com/kothollavishwateja"

# Helper function for intent recognition
def parse_user_message(message):
    tokens = word_tokenize(message.lower())
    intents = {
        'check_availability': ['availability', 'available', 'open'],
        'book_appointment': ['book', 'appointment', 'schedule'],
        'reschedule': ['reschedule', 'change']
    }
    detected_intent = None
    for intent, keywords in intents.items():
        if any(token in tokens for token in keywords):
            detected_intent = intent
            break
    return detected_intent

# Function to match doctors
def match_doctor(preferences):
    for doctor in mock_doctors:
        if doctor['specialization'].lower() == preferences.get('specialization', '').lower():
            return doctor
    return None

# Function to book an appointment
def book_appointment_with_calendly(doctor_name, patient_name, time_slot):
    headers = {"Authorization": f"Bearer {CALENDLY_API_KEY}"}
    data = {"doctor_name": doctor_name, "patient_name": patient_name, "time_slot": time_slot}
    response = requests.post(CALENDLY_URL, headers=headers, json=data)
    if response.status_code == 201:
        return response.json()
    else:
        return {"error": "Failed to book appointment"}

# Function to reschedule an appointment
def reschedule_appointment(appointment_id, new_time_slot):
    url = f"{CALENDLY_URL}/{appointment_id}/reschedule"
    headers = {"Authorization": f"Bearer {CALENDLY_API_KEY}"}
    data = {"new_time_slot": new_time_slot}
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to reschedule"}

# API route for chatbot interaction
@app.route('/chat', methods=['POST'])
def chatbot():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({"error": "Message not provided"}), 400

    intent = parse_user_message(user_message)

    if intent == 'check_availability':
        return jsonify({"reply": f"Available times: {mock_availability}"})
    elif intent == 'book_appointment':
        return jsonify({"reply": "Which doctor and time slot do you prefer?"})
    elif intent == 'reschedule':
        return jsonify({"reply": "Please provide the appointment ID and the new time slot."})
    else:
        return jsonify({"reply": "I'm here to assist you. Can you clarify your request?"})

# API route for booking an appointment
@app.route('/book', methods=['POST'])
def book():
    data = request.json
    doctor_name = data.get('doctor_name')
    patient_name = data.get('patient_name')
    time_slot = data.get('time_slot')

    if not all([doctor_name, patient_name, time_slot]):
        return jsonify({"error": "Missing required fields"}), 400

    response = book_appointment_with_calendly(doctor_name, patient_name, time_slot)
    return jsonify(response)

# API route for rescheduling an appointment
@app.route('/reschedule', methods=['POST'])
def reschedule():
    data = request.json
    appointment_id = data.get('appointment_id')
    new_time_slot = data.get('new_time_slot')

    if not all([appointment_id, new_time_slot]):
        return jsonify({"error": "Missing required fields"}), 400

    response = reschedule_appointment(appointment_id, new_time_slot)
    return jsonify(response)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
