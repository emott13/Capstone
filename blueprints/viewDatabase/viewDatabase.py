from flask import Blueprint, render_template, request
from sqlalchemy import text, inspect
from extensions import db

view_database_bp = Blueprint(
    "viewDatabase",
    __name__,
    template_folder="templates"
)

@view_database_bp.route("/view/database", methods=["GET", "POST"])
def view_database():
    results = []
    error = None
    table_name = None
    columns = []

    # Dynamically get all table names
    inspector = inspect(db.engine)
    allowed_tables = inspector.get_table_names()

    # Determine table from POST or GET
    if request.method == "POST":
        table_name = request.form.get("table_name")
    elif request.method == "GET":
        table_name = request.args.get("table")
        if not table_name:
            table_name = "users"  # default table

    if table_name:
        if table_name not in allowed_tables:
            error = f"Table '{table_name}' does not exist or is not allowed."
        else:
            try:
                stmt = text(f"SELECT * FROM {table_name} LIMIT 100")
                result_proxy = db.session.execute(stmt).mappings()
                results = result_proxy.all()
                if results:
                    columns = results[0].keys()
            except Exception as e:
                error = str(e)

    return render_template(
        "view_database.html",
        results=results,
        columns=columns,
        table_name=table_name,
        error=error,
        allowed_tables=allowed_tables
    )
