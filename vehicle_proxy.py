"""
API Proxy pour contourner les restrictions CORS
Endpoints:
- Plaques d'immatriculation
- Backend routes/orders/users
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib3

# Désactiver les avertissements SSL (pour certificats auto-signés)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from flask import Blueprint
app = Blueprint('vehicle_proxy', __name__)
CORS(app)  # Permettre les requêtes depuis le front

# Configuration
API_TOKEN = "TokenDemo2025A"
DEFAULT_CO2_PER_KM = 120
BACKEND_URL = "https://www.hopeful-northcutt.94-23-17-183.plesk.page:3000"

# ============================================
# HEALTH CHECK
# ============================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "service": "api-proxy",
        "backend_url": BACKEND_URL
    })

# ============================================
# VÉHICULES
# ============================================

@app.route('/api/vehicle/<plaque>', methods=['GET'])
def get_vehicle_data(plaque):
    """Récupérer les données d'un véhicule via sa plaque"""
    if not plaque or plaque.strip() == "":
        return jsonify({
            "success": False,
            "plaque": "",
            "marque": "Inconnu",
            "modele": "",
            "energie": "Inconnu",
            "co2PerKm": None
        })
    
    try:
        url = f"https://api.apiplaqueimmatriculation.com/plaque?immatriculation={plaque}&token={API_TOKEN}&pays=FR"
        print(f"📡 Appel API: {url}")
        response = requests.get(url, timeout=15)
        print(f"📥 Status: {response.status_code}")
        
        data = response.json()
        
        if data and data.get("data"):
            vehicle_data = data.get("data", {})
            
            # Nettoyer la cylindrée
            cylindree_str = vehicle_data.get("ccm", "")
            cylindree = None
            if cylindree_str:
                try:
                    cylindree = int(''.join(filter(str.isdigit, str(cylindree_str))))
                except:
                    cylindree = None
            
            # Gérer le CO2
            co2_value = vehicle_data.get("co2", "")
            co2_per_km = float(co2_value) if co2_value and str(co2_value).strip() else None
            
            return jsonify({
                "success": True,
                "plaque": plaque,
                "marque": vehicle_data.get("marque", "Inconnu"),
                "modele": vehicle_data.get("modele", ""),
                "energie": vehicle_data.get("energieNGC", "Inconnu"),
                "co2PerKm": co2_per_km,
                "puissance": int(vehicle_data.get("puisFisc", 0)) if vehicle_data.get("puisFisc") else None,
                "cylindree": cylindree
            })
        
        return jsonify({
            "success": False,
            "plaque": plaque,
            "marque": "Non trouvé",
            "modele": "",
            "energie": "Inconnu",
            "co2PerKm": None
        })
        
    except Exception as e:
        print(f"❌ Erreur API plaque {plaque}: {e}")
        return jsonify({
            "success": False,
            "plaque": plaque,
            "marque": "Erreur",
            "modele": "",
            "energie": "Inconnu",
            "co2PerKm": None,
            "error": str(e)
        }), 500

@app.route('/api/vehicles/batch', methods=['POST'])
def get_multiple_vehicles():
    """Récupérer les données de plusieurs véhicules"""
    try:
        data = request.get_json()
        plaques = data.get('plaques', [])
        
        if not plaques:
            return jsonify({"error": "Liste de plaques vide"}), 400
        
        results = []
        for plaque in plaques:
            try:
                url = f"https://api.apiplaqueimmatriculation.com/plaque?immatriculation={plaque}&token={API_TOKEN}&pays=FR"
                response = requests.get(url, timeout=15)
                vehicle_data_response = response.json()
                
                if vehicle_data_response and vehicle_data_response.get("data"):
                    vehicle_data = vehicle_data_response.get("data", {})
                    
                    # Nettoyer la cylindrée
                    cylindree_str = vehicle_data.get("ccm", "")
                    cylindree = None
                    if cylindree_str:
                        try:
                            cylindree = int(''.join(filter(str.isdigit, str(cylindree_str))))
                        except:
                            cylindree = None
                    
                    # Gérer le CO2
                    co2_value = vehicle_data.get("co2", "")
                    co2_per_km = float(co2_value) if co2_value and str(co2_value).strip() else None
                    
                    results.append({
                        "success": True,
                        "plaque": plaque,
                        "marque": vehicle_data.get("marque", "Inconnu"),
                        "modele": vehicle_data.get("modele", ""),
                        "energie": vehicle_data.get("energieNGC", "Inconnu"),
                        "co2PerKm": co2_per_km,
                        "puissance": int(vehicle_data.get("puisFisc", 0)) if vehicle_data.get("puisFisc") else None,
                        "cylindree": cylindree
                    })
                else:
                    results.append({
                        "success": False,
                        "plaque": plaque,
                        "marque": "Non trouvé",
                        "modele": "",
                        "energie": "Inconnu",
                        "co2PerKm": None
                    })
            except Exception as e:
                print(f"❌ Erreur pour {plaque}: {e}")
                results.append({
                    "success": False,
                    "plaque": plaque,
                    "marque": "Erreur",
                    "modele": "",
                    "energie": "Inconnu",
                    "co2PerKm": None
                })
        
        return jsonify({"vehicles": results})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ============================================
# ROUTES
# ============================================

@app.route('/api/routes', methods=['GET'])
def get_routes():
    """Proxy pour récupérer toutes les routes"""
    try:
        url = f"{BACKEND_URL}/route/get/all"
        print(f"🔍 Calling: {url}")
        # ✅ DÉSACTIVER LA VÉRIFICATION SSL
        response = requests.get(url, timeout=10, verify=False)
        print(f"✅ Response: {response.status_code}, Items: {len(response.json())}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"❌ Error fetching routes: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/routes/<route_id>', methods=['GET'])
def get_route_by_id(route_id):
    """Proxy pour récupérer une route par ID"""
    try:
        url = f"{BACKEND_URL}/route/get/all"
        # ✅ DÉSACTIVER LA VÉRIFICATION SSL
        response = requests.get(url, timeout=10, verify=False)
        routes = response.json()
        
        route = next((r for r in routes if str(r.get('id')) == str(route_id)), None)
        
        if route:
            return jsonify(route), 200
        else:
            return jsonify({"error": "Route not found"}), 404
    except Exception as e:
        print(f"❌ Error fetching route {route_id}: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# COMMANDES (ORDERS)
# ============================================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    """Proxy pour récupérer toutes les commandes"""
    try:
        url = f"{BACKEND_URL}/order/get/all"
        print(f"🔍 Calling: {url}")
        # ✅ DÉSACTIVER LA VÉRIFICATION SSL
        response = requests.get(url, timeout=10, verify=False)
        print(f"✅ Response: {response.status_code}, Items: {len(response.json())}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"❌ Error fetching orders: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/orders/<order_id>', methods=['GET'])
def get_order_by_id(order_id):
    """Proxy pour récupérer une commande par ID"""
    try:
        url = f"{BACKEND_URL}/order/get/all"
        # ✅ DÉSACTIVER LA VÉRIFICATION SSL
        response = requests.get(url, timeout=10, verify=False)
        orders = response.json()
        
        order = next((o for o in orders if str(o.get('id')) == str(order_id)), None)
        
        if order:
            return jsonify(order), 200
        else:
            return jsonify({"error": "Order not found"}), 404
    except Exception as e:
        print(f"❌ Error fetching order {order_id}: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# UTILISATEURS (USERS)
# ============================================

@app.route('/api/users', methods=['GET'])
def get_users():
    """Proxy pour récupérer tous les utilisateurs"""
    try:
        url = f"{BACKEND_URL}/user/get/all"
        print(f"🔍 Calling: {url}")
        # ✅ DÉSACTIVER LA VÉRIFICATION SSL
        response = requests.get(url, timeout=10, verify=False)
        print(f"✅ Response: {response.status_code}, Items: {len(response.json())}")
        return jsonify(response.json()), response.status_code
    except Exception as e:
        print(f"❌ Error fetching users: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/drivers', methods=['GET'])
def get_drivers():
    """Proxy pour récupérer uniquement les chauffeurs (type=5)"""
    try:
        url = f"{BACKEND_URL}/user/get/all"
        # ✅ DÉSACTIVER LA VÉRIFICATION SSL
        response = requests.get(url, timeout=10, verify=False)
        users = response.json()
        
        drivers = [u for u in users if u.get('type') == 5]
        print(f"✅ Found {len(drivers)} drivers out of {len(users)} users")
        
        return jsonify(drivers), 200
    except Exception as e:
        print(f"❌ Error fetching drivers: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/users/<user_id>', methods=['GET'])
def get_user_by_id(user_id):
    """Proxy pour récupérer un utilisateur par ID"""
    try:
        url = f"{BACKEND_URL}/user/get/all"
        # ✅ DÉSACTIVER LA VÉRIFICATION SSL
        response = requests.get(url, timeout=10, verify=False)
        users = response.json()
        
        user = next((u for u in users if str(u.get('id')) == str(user_id)), None)
        
        if user:
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        print(f"❌ Error fetching user {user_id}: {e}")
        return jsonify({"error": str(e)}), 500

# ============================================
# DÉMARRAGE
# ============================================

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 API Proxy démarré sur http://localhost:5000")
    print(f"📡 Redirection vers: {BACKEND_URL}")
    print("⚠️  SSL verification disabled (certificat auto-signé)")
    print("=" * 60)
    print("\n📋 Endpoints disponibles:\n")
    print("   🚗 Véhicules:")
    print("      GET  /api/vehicle/<plaque>")
    print("      POST /api/vehicles/batch")
    print("\n   🛣️  Routes:")
    print("      GET  /api/routes")
    print("      GET  /api/routes/<id>")
    print("\n   📦 Commandes:")
    print("      GET  /api/orders")
    print("      GET  /api/orders/<id>")
    print("\n   👥 Utilisateurs:")
    print("      GET  /api/users")
    print("      GET  /api/users/<id>")
    print("      GET  /api/users/drivers")
    print("\n   ✅ Health:")
    print("      GET  /health")
    print("\n" + "=" * 60)
    print("✨ Prêt à recevoir des requêtes!")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
