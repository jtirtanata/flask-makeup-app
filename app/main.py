import flask
import numpy as np
import pandas as pd
import json
import pickle
import os
from libs import rec_app
from flask import url_for, render_template, redirect
from werkzeug import secure_filename
from PIL import Image

image_profile_data = {"filename": "img/selfie.png",
                        "skin_color":"rgba(255,255,255,0)",
                        "age": '',
                        "eye": ""}
rec = rec_app.Recommender()
# Initialize the app
app = flask.Flask(__name__, static_url_path='')
UPDIR = 'app/static/img/upload/'
def fetch_attr(data, key, default, datatype=""):
    if key in data:
        if datatype == "int":
            return int(data[key])
        if datatype == "intlist":
            return [int(x) for x in json.loads(data[key])]
        if datatype == "rgb":
            val = data[key].replace("rgb", '')
            val = val.replace("(", '')
            val = val.replace(")", '')
            return [int(x) for x in val.split(",")]
        return data[key]
    else:
        return default
#
@app.route("/")
def home():
    return redirect("/start")

@app.route("/start")
def viz_page():
    """
    Homepage: serve our visualization page, awesome.html
    """
    return render_template("start.html")

@app.route("/popular", methods=["POST"])
def popular():
    data = flask.request.json
    pop = rec.fetch_popular(12, int(data["offset"]))
    return pop

@app.route("/inputphoto", methods=["POST"])
def inputphoto():
    files = flask.request.files
    f = files['file']
    filename = secure_filename(f.filename)
    save_name = filename
    name, ext = filename.rsplit('.', 1)
    save_path = os.path.join(UPDIR, save_name)
    i = 1
    while os.path.isfile(save_path):
        print(save_path)
        save_name = '{}-{}.{}'.format(name, i, ext)
        save_path = os.path.join(UPDIR, save_name)
        i += 1
    f.save(save_path)
    skin_color = rec.get_skin_color(Image.open(save_path))
    skin_color = [str(int(x)) for x in skin_color]
    skin_color = 'rgb({})'.format(','.join(skin_color))
    return flask.jsonify({"filename": "img/upload/" + save_name, "skin-color": skin_color})

@app.route("/profile")
def profile():
    return render_template("profile.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/recommendations", methods=["POST"])
def recommendations():
    data = flask.request.json
    cat = data["category"]
    likes = fetch_attr(data, "likes", [], "intlist")
    dislikes = fetch_attr(data, "dislikes", [], "intlist")
    age = fetch_attr(data, "age", None, "int")
    skin_color = fetch_attr(data, "skin_color", None, "rgb")
    eye_color = fetch_attr(data, "eye_color", None)
    recs = rec.recommend(cat, likes=likes, eye_color=eye_color,\
        age=age, dislikes=dislikes, skin_color=skin_color, topn=8)
    return recs.to_json()

@app.route("/allproducts", methods=["GET"])
def allproducts():
    prds = rec.fetch_all_products()
    return prds

@app.route("/product", methods=["POST"])
def product():
    data = flask.request.json
    prod = rec.fetch_product(data["pid"])
    return prod

#--------- RUN WEB APP SERVER ------------#
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
