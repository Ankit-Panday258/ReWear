from flask import render_template, Blueprint, redirect, url_for


home = Blueprint('home', __name__)

@home.route('/')
def index():
    return "I am home route"
