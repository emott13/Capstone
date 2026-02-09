from flask import Blueprint, render_template, request, url_for, redirect
from flask_login import login_user
from extensions import Users, Roles, bcrypt, db
register_bp = Blueprint("register", __name__, static_folder="static",
                  template_folder="templates")


@register_bp.route("/register", methods=["GET", "POST"])
def register():
    error = request.args.get("error", None)
    if request.method == "POST":
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        confPassword = request.form.get('conf-password')
        firstName = request.form.get('first_name')
        lastName = request.form.get('last_name')
        type = request.form.get('type')



        if not email or not password:
            return render_template("register.html", error="Invalid input")

    # roles = db.session.execute(text('SELECT * FROM roles ORDER BY role_id DESC'))
    roles = Roles.query.order_by(Roles.role_id.desc())

    return render_template("register.html", error=error,
                           roles=roles)
