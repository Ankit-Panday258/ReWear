from flask import render_template, Blueprint, redirect, url_for


listing = Blueprint('listing', __name__)

#Index route
@listing.route('/')
def index():
    return render_template("listing/index.html")

#Show Route
@listing.route('/id')
def showListing():
    return render_template("listing/show.html")

#Edit Route
@listing.route("/id/edit")
def renderEditPage():
    return render_template("listing/edit.html")

#Update route
@listing.route("/id")
def updateListing():
    return redirect("listing/show.html")