import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS

# Load dataset
def load_dataset():
    dataset_path = os.path.join(os.path.dirname(__file__), 'dataset.json')
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return []

DISEASE_DATASET = load_dataset()

# ✅ NEW: Manual Symptom Extraction (NO AI NEEDED)
def extract_symptoms(user_text):
    user_text = user_text.lower()
    detected = set()

    for disease in DISEASE_DATASET:
        for symptom in disease.get("symptoms", []):
            symptom_lower = symptom.lower()

            # Exact phrase match
            if symptom_lower in user_text:
                detected.add(symptom_lower)

            # Word-level match (important)
            for word in symptom_lower.split():
                if word in user_text:
                    detected.add(symptom_lower)

    return list(detected)

# ✅ IMPROVED MATCHING
def match_disease(extracted_symptoms):
    best_match = None
    max_score = 0

    for disease in DISEASE_DATASET:
        disease_symptoms = [s.lower().strip() for s in disease.get("symptoms", [])]

        # Score = number of matching symptoms
        score = len(set(extracted_symptoms) & set(disease_symptoms))

        if score > max_score:
            max_score = score
            best_match = disease

    return best_match

# Flask App
app = Flask(__name__)
CORS(app)

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.json
    user_text = data.get("message", "")

    if not user_text:
        return jsonify({"error": "No message provided"}), 400

    # ✅ Step 1: Extract symptoms
    extracted_symptoms = extract_symptoms(user_text)

    if not extracted_symptoms:
        return jsonify({
            "message": "❌ No symptoms matched. Try words like fever, cough, headache, etc.",
            "symptoms_identified": [],
            "matched_disease": None
        })

    # ✅ Step 2: Match disease
    matched_disease_info = match_disease(extracted_symptoms)

    if matched_disease_info:
        return jsonify({
            "symptoms_identified": extracted_symptoms,
            "matched_disease": matched_disease_info
        })
    else:
        return jsonify({
            "message": "⚠️ Symptoms found but no exact disease match. Please consult a doctor.",
            "symptoms_identified": extracted_symptoms,
            "matched_disease": None
        })

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        "status": "Backend running successfully",
        "dataset_size": len(DISEASE_DATASET)
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)