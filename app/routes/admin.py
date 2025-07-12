from flask import render_template, Blueprint, redirect, url_for

admin = Blueprint('admin', __name__)

@admin.route("/")
def renderAdmin():
    return render_template("admin/admin.html")