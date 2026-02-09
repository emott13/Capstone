from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_user
from extensions import Users, bcrypt
register_bp = Blueprint("register", __name__, static_folder="static",
                  template_folder="templates")


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    error = request.args.get("error", None)
    # if request.method == "POST":
        # email = request.form.get("username")
        # password = request.form.get("password")

        # if not email or not password:
        #     return render_template("register.html", error="Invalid input")


    return render_template("register.html", error=error)
