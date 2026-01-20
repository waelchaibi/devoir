import flask
import flask_cors
from db import init_db, create_user, get_user, get_all_users, update_user, delete_user

app = flask.Flask(__name__)
flask_cors.CORS(app)

# Initialize database on startup
init_db()

@app.route("/")
def hello():
    return "Hello from User Management API!"

# GET all users
@app.route("/api/users", methods=["GET"])
def get_users():
    users = get_all_users()
    return flask.jsonify({"users": users}), 200

# GET a specific user
@app.route("/api/users/<int:user_id>", methods=["GET"])
def get_user_endpoint(user_id):
    user = get_user(user_id)
    if user:
        return flask.jsonify(user), 200
    return flask.jsonify({"error": "User not found"}), 404

# CREATE a new user
@app.route("/api/users", methods=["POST"])
def create_user_endpoint():
    data = flask.request.get_json()
    
    if not data or "username" not in data or "password" not in data:
        return flask.jsonify({"error": "Missing username or password"}), 400
    
    try:
        user = create_user(data["username"], data["password"])
        return flask.jsonify(user), 201
    except ValueError as e:
        return flask.jsonify({"error": str(e)}), 409

# UPDATE a user
@app.route("/api/users/<int:user_id>", methods=["PUT"])
def update_user_endpoint(user_id):
    data = flask.request.get_json()
    
    if not data:
        return flask.jsonify({"error": "No data provided"}), 400
    
    try:
        user = update_user(
            user_id,
            username=data.get("username"),
            password=data.get("password")
        )
        
        if user:
            return flask.jsonify(user), 200
        return flask.jsonify({"error": "User not found"}), 404
    except ValueError as e:
        return flask.jsonify({"error": str(e)}), 409

# DELETE a user
@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def delete_user_endpoint(user_id):
    if delete_user(user_id):
        return flask.jsonify({"message": "User deleted successfully"}), 200
    return flask.jsonify({"error": "User not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
