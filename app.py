from flask import Flask
from flask_cors import CORS
from vehicle_proxy import app as proxy_app
from server import app as ia_app

# Créer une app principale
app = Flask(__name__)
CORS(app)

# Monter les deux sous-apps Flask
app.register_blueprint(proxy_app.blueprint, url_prefix="/")
app.register_blueprint(ia_app.blueprint, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
