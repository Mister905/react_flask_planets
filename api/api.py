import time
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow

app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
# os.path.join offers a platform agnositc path handling
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]  = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

@app.cli.command("db_create")
def db_create():
    db.create_all()
    print("Database Created!")
    
@app.cli.command("db_seed")
def db_seed():
    mercury = Planet(name = "Mercury", 
                     type = "Class D",
                     home_star = "Sol",
                     mass = 3.258e23,
                     radius = 1516,
                     distance = 35.98e6)
    venus = Planet(name = "Venus", 
                     type = "Class K",
                     home_star = "Sol",
                     mass = 4.867e24,
                     radius = 3760,
                     distance = 67.24e6)
    earth = Planet(name = "Earth", 
                     type = "Class M",
                     home_star = "Sol",
                     mass = 5.972e2,
                     radius = 3959,
                     distance = 92.96e6)
    db.session.add(mercury)
    db.session.add(venus)
    db.session.add(earth)
    
    test_user = User(first_name = "John",
                     last_name = "Doe",
                     email = "jdoe@gmail.com",
                     password = "password123")
    db.session.add(test_user)
    
    db.session.commit()
    print("Database Seeded!")

@app.cli.command("db_drop")
def db_drop():
    db.drop_all()
    print("Database dropped!")

# database models
class User(db.Model):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, unique=True)
    password = Column(String)

class Planet(db.Model):
    __tablename__ = "planets"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    type = Column(String)
    home_star = Column(String)
    mass = Column(Float)
    radius = Column(Float)
    distance = Column(Float)

class UserSchema(ma.Schema):
    class Meta:
        fields = ("id", "first_name", "last_name", "email", "password")
        
class PlanetSchema(ma.Schema):
    class Meta:
        fields = ("id", "name", "type", "home_star", "mass", "radius", "distance")
        
user_schema = UserSchema()
users_schema = UserSchema(many=True)

planet_schema = PlanetSchema()
planets_schema = PlanetSchema(many=True)

@app.route("/api/planets", methods=["GET"])
def planets():
    planets_list = Planet.query.all()
    result = planets_schema.dump(planets_list)
    return jsonify(result)


@app.route("/")
def hello_world():
    return jsonify(message="Hello from React Flask Planets"), 200


@app.route("/time")
def get_current_time():
    return {"time": time.time()}


@app.route("/parameters")
def parameters():
    name = request.args.get("name")
    age = int(request.args.get("age"))
    return jsonify(message = f"Hello, {name}. You are {age}.")


@app.route("/url_vars/<string:name>/<int:age>")
def url_vars(name: str, age: int):
    return jsonify(message = f"Hello, {name}. You are {age}.")
