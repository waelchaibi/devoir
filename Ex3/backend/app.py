import flask
from flask import jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = flask.Flask(__name__)
CORS(app)

TOR_PROXY = os.getenv("TOR_PROXY")
USER_API = os.getenv("USER_API")

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
        proxies=proxies
    )
    return jsonify(r.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
