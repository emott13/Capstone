from flask import render_template, url_for, redirect
# from sqlalchemy import create_engine, text, insert, Table, MetaData, update
from flask_login import logout_user, login_required, current_user
from extensions import *


@app.route("/test")
def test():
    return "test"

if __name__ == '__main__':
    app.run(debug=True)