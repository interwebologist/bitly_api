import logging
import flask
import os
from flask import jsonify, request
import json
from bitly import Bitly
from helper import Helper
from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

jwt_username = os.environ.get('JWTUSER')
jwt_password = os.environ.get('JWTPASS')
jwt_secret_key  = os.environ.get('JWT_SECRET_KEY')
token = os.environ.get('BITLYTOKEN')

app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config["JWT_SECRET_KEY"] = jwt_secret_key  # Change this!

bitly_object = Bitly(token)
helper_object = Helper(token)

jwt = JWTManager(app)
@app.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != jwt_username or password != jwt_password:
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route('/', methods=['GET'])
@jwt_required()
def home():
    group = bitly_object.group_getter() 
    if 'FORBIDDEN' in group.values():
        return jsonify({'message':'Bitly token is bad, broken or expired.'})
    else:
        group_links = bitly_object.bitlink_getter(group['default_group_guid'])
        links = helper_object.json_snippet_builder(group_links)
        data = helper_object.avg_calculator(links)
        
        return jsonify(data)
def main():    
    # Security warnings for default credentials
    if jwt_username == "test" and jwt_password == "test":
        logger.warning('JWT username and password are default. Change this for production!')

    if app.config['JWT_SECRET_KEY'] == "changethis":
        logger.warning('JWT Secret is set to default. Change this for production!')

    if not bitly_token:
        logger.error('Bitly API token missing. Exiting.')
        exit(1)
    else:
        group = bitly_object.group_getter()
        if 'FORBIDDEN' in group.values():
            logger.error("Bitly doesn't like your token. Replace or check it. Exiting.")
            exit(1)
        else:
            # For production, consider using waitress or gunicorn
            app.run(host="0.0.0.0", port=8080)

if __name__ == "__main__":
    main()
