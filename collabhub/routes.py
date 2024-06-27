from collabhub import app
from flask import render_template


@app.route("/")
def home_page():
    return render_template("index.html")