import flask as flask
import flask_cors
app = flask.Flask(__name__)
@app.route('/api/hello', methods=['GET'])
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    flask_cors.CORS(app)
    app.run(host='0.0.0.0', port = 5000, debug=True)