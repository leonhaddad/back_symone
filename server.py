from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

from flask import Blueprint
app = Blueprint('vehicle_proxy', __name__)

CORS(app)  # autorise toutes les origines ; restreins si besoin

MODEL_NAME = "gemma3:270m"  # Modèle léger

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    prompt = f"Contexte : {data['context']} Instructions : {data['instructions']}"

    # Exécuter Ollama avec le modèle Gemma3
    result = subprocess.run(
        ["ollama", "run", MODEL_NAME, prompt],
        capture_output=True,
        text=True
    )

    response_text = result.stdout.strip() or result.stderr.strip()
    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(port=5001)
