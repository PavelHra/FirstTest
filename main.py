from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random

app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)


def to_dict(self):
    # Method 1.
    dictionary = {}
    # Loop through each column in the data record
    for column in self.__table__.columns:
        # Create a new dictionary entry;
        # where the key is the name of the column
        # and the value is the value of the column
        dictionary[column.name] = getattr(self, column.name)
    return dictionary

    # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
    # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")


# Route to return all cafes in database
@app.route("/all")
def all_cafes():
    cafes = db.session.query(Cafe).all()
    cafes_json = {}
    for cafe in cafes:
        cafes_json.update({cafe.id: to_dict(cafe)})
    return cafes_json
    # Alternatively is possible to use a List Comprehension
    # return jsonify(cafes=[cafe.to_dict() for cafe in cafes])


# Route to search a coffe by its location
@app.route("/search")
def get_cafe_at_location():
    query_location = request.args.get("loc")
    cafe = db.session.query(Cafe).filter_by(location=query_location).first()
    if cafe:
        return jsonify(cafe=to_dict(cafe))
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route("/random", methods=['GET'])
def random_cafe():
    cafes = db.session.query(Cafe).all()
    random_cafe = random.choice(cafes)
    random_cafe_json = to_dict(random.choice(cafes))
    print(random_cafe)
    print(random_cafe_json)
    # Return serialize object - better way is to create function like to_dict, to transfer every object into dict
    # And then simply return random_cafe_json
    return jsonify(cafe={
        # Omit the id from the response
        # "id": random_cafe.id,
        "name": random_cafe.name,
        "map_url": random_cafe.map_url,
        "img_url": random_cafe.img_url,
        "location": random_cafe.location,

        # Put some properties in a sub-category
        "amenities": {
            "seats": random_cafe.seats,
            "has_toilet": random_cafe.has_toilet,
            "has_wifi": random_cafe.has_wifi,
            "has_sockets": random_cafe.has_sockets,
            "can_take_calls": random_cafe.can_take_calls,
            "coffee_price": random_cafe.coffee_price,
        }
    })


## HTTP POST - Create Record
@app.route("/add", methods=['POST'])
def add_cafe():
    new_cafe = Cafe(
        name=request.args.get("name"),
        map_url=request.args.get("map_url"),
        img_url=request.args.get("img_url"),
        location=request.args.get("location"),
        seats=request.args.get("seats"),
        has_toilet=bool(request.args.get("has_toilet")),
        has_wifi=bool(request.args.get("has_wifi")),
        has_sockets=bool(request.args.get("has_sockets")),
        can_take_calls=bool(request.args.get("can_take_calls")),
        coffee_price=bool(request.args.get("coffee_price"))
    )
    db.session.add(new_cafe)
    try:
        db.session.commit()
        response = {"Response": {"Success": "Successfully added new record"}}
    except:
        response = {"Response": {"Fail": "Something went wrong"}}
    return jsonify(response)


## HTTP GET - Read Record


## HTTP PUT/PATCH - Update Record
@app.route("/update-price/<cafe_id>", methods=['PATCH'])
def update_price(cafe_id):
    # Just test - load and show headers
    test_header = request.headers
    print(test_header)
    # When id not found, return info to client
    try:
        updated_cafe = Cafe.query.filter_by(id=cafe_id).first()
        updated_cafe.coffee_price = request.args.get("new_price")
    except:
        return jsonify({"Response": {"Fail": "ID was not found in DB"}}), 404  # 404 = Response code

    try:
        db.session.commit()
        response = {"Response": {"Success": "Price has been successfully updated"}}
    except:
        response = {"Response": {"Fail": "Something went wrong"}}
    return jsonify(response)


## HTTP DELETE - Delete Record
@app.route("/caffe-closed/<cafe_id>", methods=['DELETE'])
def delete_caffe(cafe_id):
    # First, check API Key
    if request.args.get("api-key") != "TopSecretAPIKey":
        return jsonify({"Response": {"Fail": "Not allowed. Wrong API Key"}}), 403

    # Try to load caffe by id from DB, if not found, return info to client
    caffe_for_delete = Cafe.query.filter_by(id=cafe_id).first()
    if not caffe_for_delete:
        return jsonify({"Response": {"Fail": "ID was not found in DB"}}), 404  # 404 = Response code

    # Finally delete record from DB
    try:
        db.session.delete(caffe_for_delete)
        db.session.commit()
        return jsonify({"Response": {"Success": "Caffe has been successfully deleted"}}), 200
    except:
        return jsonify({"Response": {"Fail": "Something went wrong"}}), 500


if __name__ == '__main__':
    app.run(debug=True)
