from flask import Flask
from flask_bootstrap import Bootstrap
from sqlalchemy import text
from extensions import *
from blueprints.viewDatabase.viewDatabase import view_database_bp
from blueprints.login.login import login_bp
from blueprints.register.register import register_bp
from blueprints.home.home import home_bp
from blueprints.search.search import search_bp

# register blueprints
app.register_blueprint(login_bp)
app.register_blueprint(register_bp)
app.register_blueprint(view_database_bp)
app.register_blueprint(home_bp)
app.register_blueprint(search_bp)

# quick route to see all routes
@app.route("/routes")
def routes():
    return (f"<a href=\"{r}\">{r}</a><br>" for r in app.url_map.iter_rules())

# simple route to check database connection
@app.route("/db-check")
def db_check():
    try:
        db.session.execute(text("SELECT 1"))
        return "Database connection OK"
    except Exception as e:
        return f"Database error: {e}"
    
# simple route to list all tables in the database
@app.route("/db-tables")
def db_tables():
    inspector = db.inspect(db.engine)
    return "<br>".join(inspector.get_table_names())

# simple route to show current database and schema
@app.route("/db-info")
def db_info():
    result = db.session.execute(text("SELECT current_database(), current_schema()"))
    return str(result.fetchone())



if __name__ == "__main__":
    app.run(debug=True)
