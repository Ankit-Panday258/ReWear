from flask import render_template, Blueprint, redirect, url_for, request, flash, session, jsonify


auth = Blueprint('auth', __name__)

@auth.route("/register")
def register():
    return render_template("user/register.html")

@auth.route("/login")
def login():
    return render_template("user/login.html")
