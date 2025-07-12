from flask import render_template, Blueprint, redirect, url_for

user = Blueprint('user', __name__)

@user.route("/profile")
def renderProfile():
    return render_template("user/profile.html")