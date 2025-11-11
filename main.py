from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import requests
import urllib3
import os

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

app = Flask(__name__)
CORS(app)

# ======================================================
# 🔹 PARTIE 1 : Ton IA (Gemma3 via Ollama)
# ======================================================

MODEL_NAME = "gemma3:270m"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    prompt = f"Contexte : {data['context']} Instructions : {data['instructions']}"
    result = subprocess.run(
        ["ollama", "run", MODEL_NAME, prompt],
        capture_output=True,
        text=True
    )
    response_text = result.stdout.strip() or result.stderr.strip()
    return jsonify({"response": response_text})


# ======================================================
# 🔹 PARTIE 2 : Proxy API véhicules / backend
# ======================================================

API_TOKEN = "TokenDemo2025A"
BACKEND_URL = "https://www.hopeful-northcutt.94-23-17-183.plesk.page:3000"

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "api-proxy", "backend_url": BACKEND_URL})

@app.route('/api/vehicle/<plaque>', methods=['GET'])
def get_vehicle_data(plaque):
    try:
        url = f"https://api.apiplaqueimmatriculation.com/plaque?immatriculation={plaque}&token={API_TOKEN}&pays=FR"
        response = requests.get(url, timeout=15)
        data = response.json()
        if data and data.get("data"):
            v = data["data"]
            return jsonify({
                "success": True,
                "plaque": plaque,
                "marque": v.get("marque", "Inconnu"),
                "modele": v.get("modele", ""),
                "energie": v.get("energieNGC", "Inconnu"),
                "co2PerKm": v.get("co2", None),
            })
        return jsonify({"success": False, "plaque": plaque})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/routes', methods=['GET'])
def get_routes():
    try:
        url = f"{BACKEND_URL}/route/get/all"
        response = requests.get(url, timeout=10, verify=False)
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ======================================================
# 🔹 Lancement Render
# ======================================================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # ⚠️ obligatoire pour Render
    app.run(host="0.0.0.0", port=port)
