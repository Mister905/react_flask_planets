import time
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Float
import os
from flask_marshmallow import Marshmallow
from flask_jwt_extended import JWTManager, jwt_required, create_access_token, get_jwt_identity, get_jwt
from flask_mail import Mail, Message


app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))
# os.path.join offers a platform agnositc path handling
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(basedir, "app.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]  = False
app.config['JWT_SECRET_KEY'] = 'jamesmsecret'
app.config['MAIL_SERVER']='smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = 'f32dfb06bf6667'
app.config['MAIL_PASSWORD'] = '1ee268d5b9fb81'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False


db = SQLAlchemy(app)
ma = Marshmallow(app)
jwt = JWTManager(app)
mail = Mail(app)

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

@app.route('/api/register', methods=['POST'])
def register():
    email = request.json["email"]
    test = User.query.filter_by(email=email).first()
    if test:
        return jsonify(message='That email already exists.'), 409
    else:
        first_name = request.json['first_name']
        last_name = request.json['last_name']
        password = request.json['password']
        user = User(first_name=first_name, last_name=last_name, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return jsonify(message="User created successfully."), 201
    
@app.route('/api/login', methods=['POST'])
def login():
    email = request.json["email"]
    password = request.json["password"]
    user = User.query.filter_by(email=email, password=password).first()
    if user:
        additional_claims = {"user_id": user.id, "foo": "bar"}
        access_token = create_access_token(identity=email, additional_claims=additional_claims)
        return jsonify(message="Login successful", access_token=access_token), 200
    else:
        return jsonify(message="Login failed"), 401
    
@app.route('/api/send_email/<string:email_address>', methods=['GET'])
def send_email(email_address: str):
    user = User.query.filter_by(email=email_address).first()
    if user:
       message = Message("Test Email",
                      sender="jamesm@admin.com",
                      recipients=[email_address])
       
       
       mail.send(message)
       return jsonify(message="Password sent to " + email_address)
    else:
        return jsonify(message="Email not found")
    
@app.route('/api/planets/<int:id>', methods=['GET'])
def get_planet(id: int):
    planet = Planet.query.filter_by(id=id).first()
    if planet:
        result = planet_schema.dump(planet)
        return jsonify(result)
    else:
        return jsonify(message="Planet not found."), 404
    
@app.route('/api/planets', methods=['POST'])
@jwt_required()
def create_planet():
    name = request.json['name']
    test = Planet.query.filter_by(name=name).first()
    if test:
        return jsonify("There is already a planet by that name"), 409
    else:
        # return jsonify(message="DERP"), 200
        type = request.json['type']
        home_star = request.json['home_star']
        mass = float(request.json['mass'])
        radius = float(request.json['radius'])
        distance = float(request.json['distance'])

        new_planet = Planet(name=name,
                            type=type,
                            home_star=home_star,
                            mass=mass,
                            radius=radius,
                            distance=distance)

        db.session.add(new_planet)
        db.session.commit()
        return jsonify(message="You created a planet"), 201
    
    
@app.route('/api/planets', methods=['PUT'])
@jwt_required()
def update_planet():
    id = int(request.json['id'])
    planet = Planet.query.filter_by(id=id).first()
    if planet:
        planet.name = request.json['name']
        planet.type = request.json['type']
        planet.home_star = request.json['home_star']
        planet.mass = float(request.json['mass'])
        planet.radius = float(request.json['radius'])
        planet.distance = float(request.json['distance'])
        db.session.commit()
        return jsonify(message="Planet successfully updated"), 202
    else:
        return jsonify(message="Planet update failed"), 404
    
    
@app.route('/api/planets/<int:id>', methods=['DELETE'])
@jwt_required()
def remove_planet(id: int):
    planet = Planet.query.filter_by(id=id).first()
    if planet:
        db.session.delete(planet)
        db.session.commit()
        return jsonify(message="You deleted a planet"), 202
    else:
        return jsonify(message="That planet does not exist"), 404

# Protect a route with jwt_required, which will kick out requests
# without a valid JWT present.
@app.route("/api/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    # current_user = get_jwt_identity()
    # return jsonify(logged_in_as=current_user), 200
    claims = get_jwt()
    return jsonify(claims)

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
