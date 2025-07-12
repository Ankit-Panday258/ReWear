from flask import render_template, Blueprint, redirect, url_for


home = Blueprint('home', __name__)

@home.route('/')
def index():
    return render_template("listing/landing.html")
