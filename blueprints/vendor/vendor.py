from flask import Blueprint, render_template
from extensions import conn
from sqlalchemy import text
from extensions import db

vendor_bp = Blueprint("vendor", __name__, static_folder="static_vendor",
                  template_folder="templates_vendor")

@vendor_bp.route("/vendor", methods=["GET"])
def vendor():
    return render_template(
        "vendor.html",
    )
