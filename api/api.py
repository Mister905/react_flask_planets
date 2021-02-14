import time
from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/')
def hello_world():
    return jsonify(message='Hello from React Flask Planets'), 200


@app.route('/time')
def get_current_time():
    return {'time': time.time()}


@app.route('/parameters')
def parameters():
    name = request.args.get('name')
    age = int(request.args.get('age'))
    return jsonify(message = f"Hello, {name}. You are {age}.")


@app.route('/url_vars/<string:name>/<int:age>')
def url_vars(name: str, age: int):
    return jsonify(message = f"Hello, {name}. You are {age}.")
