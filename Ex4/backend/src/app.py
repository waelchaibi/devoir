import flask
from flask import jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv
from db import init_db, get_all_users, get_user_by_id, create_user, update_user, delete_user, check_db_connection

load_dotenv()

app = flask.Flask(__name__)
CORS(app)

# Configuration depuis les variables d'environnement
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8080))
TOR_PROXY = os.getenv("TOR_PROXY")
USER_API = os.getenv("USER_API")

# Configuration proxy Tor pour toutes les requêtes externes
proxies = {
    "http": TOR_PROXY,
    "https": TOR_PROXY,
}


@app.route("/random-user")
def random_user():
    r = requests.get(USER_API, proxies=proxies, timeout=30)
    return jsonify(r.json())

@app.route("/ip")
def check_ip():
    r = requests.get(
        "https://api.ipify.org?format=json",
        proxies=proxies,
        timeout=30
    )
    return jsonify(r.json())

@app.route("/users", methods=["GET", "POST"])
def users():
    if flask.request.method == "GET":
        try:
            users = get_all_users()
            return jsonify(users)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif flask.request.method == "POST":
        try:
            data = flask.request.get_json()
            if not data or "name" not in data or "email" not in data:
                return jsonify({"error": "name and email are required"}), 400
            
            user_id = create_user(data["name"], data["email"])
            user = get_user_by_id(user_id)
            return jsonify(user), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

@app.route("/users/<int:user_id>", methods=["GET", "PUT", "DELETE"])
def user(user_id):
    if flask.request.method == "GET":
        try:
            user = get_user_by_id(user_id)
            if user:
                return jsonify(user)
            return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif flask.request.method == "PUT":
        try:
            data = flask.request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            success = update_user(user_id, data.get("name"), data.get("email"))
            if success:
                user = get_user_by_id(user_id)
                return jsonify(user)
            return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    
    elif flask.request.method == "DELETE":
        try:
            success = delete_user(user_id)
            if success:
                return jsonify({"message": "User deleted successfully"}), 200
            return jsonify({"error": "User not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

# Initialisation de la base de données au démarrage
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=BACKEND_PORT)
