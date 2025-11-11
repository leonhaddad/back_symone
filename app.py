from flask import Flask
from flask_cors import CORS
from vehicle_proxy import app as proxy_app
from server import app as ia_app

app = Flask(__name__)
CORS(app)

# 🔹 On enregistre les Blueprints
app.register_blueprint(proxy_app, url_prefix="/")
app.register_blueprint(ia_app, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
