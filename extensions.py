import datetime
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from flask_login import LoginManager, UserMixin, current_user
from flask_bcrypt import Bcrypt

# USEFUL flask_login COMMANDS
# @app.route("/foo")
# @login_required # (requires the user to be logged in. Redirects to login if not logged in)
# def foo() ...
# current_user # (has current_user data like current_user.email or current_user.type)
# current_user.is_authenticated
# getCurrentType() # gets the current type. Is None if the user isn't signed in


# Initialize Flask app
# conn_str = "mysql://root:cset155@localhost/goods" <-- main database
conn_str = "mysql://root:cset155@localhost/goods" 
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = conn_str
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = b'\xdak\xd2\xf7\x80,8\x0f\xbdG\xb7\x87\xe4h\xcf\xae'

# Initialize bcrypt
bcrypt = Bcrypt(app)

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login.login"

# Initialize DB the way we did the other times
engine = create_engine(conn_str, echo=True)                                             
conn = engine.connect()                                                                 

# price formatter for jinja template. call like {{154|priceFormat}}
@app.template_filter()
def priceFormat(value):
    formatted = str(value)[:-2] + "." + str(value)[-2:]
    if int(value) < 10:
        formatted = formatted[:-1] + "0" + formatted[-1:]
    if int(value) < 100:
        formatted = "0" + formatted

    return formatted
    # return f"{ round( int(value)/100, 2):.2f }"

# date formatter for jinja template
@app.template_filter()
def dateFormat(value: datetime.datetime) -> str:
    # formats like "Dec 05, 2026 11:59 PM"
    return value.strftime("%b %d, %Y %I:%M %p")

# date formatter for jinja template
@app.template_filter()
def dateOnlyFormat(value: datetime.datetime) -> str:
    # formats like "Dec 05, 2026"
    return value.strftime("%b %d, %Y")

# date formatter for jinja template
@app.template_filter()
def timeOnlyFormat(value: datetime.datetime) -> str:
    # formats like "09:10:32 PM"
    return value.strftime("%I:%M:%S %p")

@app.template_filter()
def chatDateFormat(value: datetime.datetime) -> str:
    """Sets the date to Today or Yesterday if that's true"""
    currentTime = datetime.datetime.now()
    if value.date() == currentTime.date():
        # formats like "Today at 11:59 PM"
        return value.strftime("Today at %-I:%M %p")
    elif value.date() == currentTime.date() - datetime.timedelta(1):
        # formats like "Yesterday at 11:59 PM"
        return value.strftime("Yesterday at %-I:%M %p")
    # formats like "Sun, Dec 05, 2026 11:59 PM"
    return value.strftime("%a, %b %d, %Y %-I:%M %p")
