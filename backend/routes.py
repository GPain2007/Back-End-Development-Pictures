from . import app
import os
import json
from flask import jsonify, request, make_response, abort, url_for  # noqa; F401

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "data", "pictures.json")
data: list = json.load(open(json_url))

######################################################################
# RETURN HEALTH OF THE APP
######################################################################


@app.route("/health")
def health():
    return jsonify(dict(status="OK")), 200

######################################################################
# COUNT THE NUMBER OF PICTURES
######################################################################


@app.route("/count")
def count():
    """return length of data"""
    if data:
        return jsonify(length=len(data)), 200

    return {"message": "Internal server error"}, 500


######################################################################
# GET ALL PICTURES
######################################################################
@app.route("/picture", methods=["GET"])
def get_pictures():
    return jsonify(data)

######################################################################
# GET A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["GET"])
def get_picture_by_id(id):
    picture = next((item for item in data if item["id"] == id), None)
    if picture:
        return jsonify(picture)
    else:
        abort(404)


######################################################################
# CREATE A PICTURE
######################################################################
@app.route("/picture", methods=["POST"])
def create_picture():
    picture_data = request.json

    # Check if picture with given id already exists
    existing_picture = next((item for item in data if item["id"] == picture_data["id"]), None)
    if existing_picture:
        return jsonify({"Message": f"picture with id {picture_data['id']} already present"}), 302

    # Append the new picture data to the list
    data.append(picture_data)
    with open(json_url, 'w') as f:
        json.dump(data, f, indent=4)
    
    return jsonify(picture_data), 201

######################################################################
# UPDATE A PICTURE
######################################################################


@app.route("/picture/<int:id>", methods=["PUT"])
def update_picture(id):
    picture_data = request.json

    # Find the picture with the given id
    picture_index = next((i for i, item in enumerate(data) if item["id"] == id), None)
    
    if picture_index is not None:
        # Update the picture with the new data
        data[picture_index].update(picture_data)
        with open(json_url, 'w') as f:
            json.dump(data, f, indent=4)
        return jsonify(data[picture_index]), 200
    else:
        # If picture with given id is not found, return 404 error
        return jsonify({"Message": "picture not found"}), 404

######################################################################
# DELETE A PICTURE
######################################################################
@app.route("/picture/<int:id>", methods=["DELETE"])
def delete_picture(id):
    # Traverse the data list to find the picture by id
    picture_index = None
    for i, picture in enumerate(data):
        if picture["id"] == id:
            picture_index = i
            break
    
    if picture_index is not None:
        # If picture exists, delete it from the list
        del data[picture_index]
        with open(json_url, 'w') as f:
            json.dump(data, f, indent=4)
        return '', 204  # Return empty body with 204 status code
    else:
        # If picture with given id is not found, return 404 error
        abort(404, description={"message": "picture not found"})
