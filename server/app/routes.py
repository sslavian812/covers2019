import tempfile
import base64
import os
import util
import json
import flask
import re

from app import app
from flask import request
from api import google_query


@app.route('/')
@app.route('/index')
def index():
    return "Test"


@app.route('/detection', methods=['POST'])
def get_boxes():
    with tempfile.TemporaryDirectory("box-session") as tmpdir:
        if request.mimetype == "image/jpeg":
            image_path = os.path.join(tmpdir, "image.jpeg")
            data = request.get_data()
        elif request.mimetype == "application/json":
            json_data = json.loads(request.get_data())
            data = base64.decodebytes(json_data["data"].encode())
            extension = json_data["type"]
            image_path = os.path.join(tmpdir, "image.png")
        else:
            return "Unsupported MIME type: `{}`".format(request.mimetype)
        
        util.save_image(image_path, data)
        return flask.jsonify(google_query.get_boxes(image_path))


# TODO: refactor processing
@app.route('/crop-gcloud', methods=['POST'])
def get_crops():
    with tempfile.TemporaryDirectory("crop-session") as tmpdir:
        aspect_ratio = 3/4
        if request.mimetype == "image/jpeg":
            image_path = os.path.join(tmpdir, "image.jpeg")
            data = request.get_data()
        elif request.mimetype == "application/json":
            json_data = json.loads(request.get_data())
            data = base64.b64decode(json_data["data"])
            extension = json_data["type"]
            image_path = os.path.join(tmpdir, "image.png")
            if "aspect_ratio" in json_data:
                aspect_ratio_str = json_data["aspect_ratio"]
                try:
                    match = re.match(r"(\d+)/(\d+)", aspect_ratio_str)
                    if match:
                        aspect_ratio = float(match.group(1)) / float(match.group(2))
                    else:
                        aspect_ratio = float(aspect_ratio_str)
                except ValueError:
                    return "Cannot parse aspect_ratio value: `{}`".format(aspect_ratio_str)
        else:
            return "Unsupported MIME type: `{}`".format(request.mimetype)
        
        util.save_image(image_path, data)
        return flask.jsonify(google_query.get_crops(image_path, aspect_ratio))


# @app.route('/bgrm', methods=['POST'])
# def get_boxes():
#     if request.mimetype != "image/jpeg":
#         return "Error: expected image/jpeg, got `{}`".format(request.mimetype)

#     with tempfile.TemporaryDirectory("box-session") as tmpdir:
#         imgpath = os.path.join(tmpdir, "data.jpeg")
#         with open(imgpath, "wb") as imgfile:
#             imgfile.write(request.get_data())
#         return google_query.get_boxes(imgpath)
