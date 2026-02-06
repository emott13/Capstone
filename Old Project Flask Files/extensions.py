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

# User model (required for flask-login)
# Create database
# with app.app_context():
#     db.create_all()

# class Products(UserMixin, db.Model):
#     product_id = db.Column(db.Integer, primary_key=True)
#     vendor_id = db.Column(db.String(255), ForeignKey("users.email"), nullable=False)
#     product_title = db.Column(db.String(255), nullable=False)
#     product_description = db.Column(db.String(500), nullable=False)
#     warranty_months = db.Column(db.Integer, nullable=False)

class Users(UserMixin, db.Model):
    email = db.Column(db.String(255), primary_key=True)
    username = db.Column(db.String(255), unique=False, nullable=False)
    hashed_pswd = db.Column(db.String(300), nullable=False)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    type = db.Column(db.Enum('vendor', 'admin', 'customer'), nullable=False)

    def get_id(self):
        return self.email

    def get_email(self):
        return self.email

def getCurrentType():
    """Returns the current_user type. Returns None if the user isn't logged in"""
    return None if not current_user.is_authenticated else current_user.type

def dict_db_data(table, extra="", select=""):
    """
    Converts a table's data from an array of arrays to an array of dictionaries
    with the columns as the key for easy usage like "data['username']"
    variable 'extra' gets passed to the sql query for WHERE statements etc.
    """
    keys = [ key[0] for key in conn.execute(text(f"DESC {table}")).all() ]
    for key in select.replace(",", "").split():
        keys.append(key)

    data = conn.execute(text("SELECT " + str(keys)[1:-1].replace("\'", "") + f" FROM {table} {extra}")).all()

    dataDict = []
    for row in data:
        dictRow = {}
        for key, value in zip(keys, row):
            dictRow[key] = value
        dataDict.append(dictRow)

    return dataDict

def sql_enum_list(enum: str) -> list:
    arr = []
    for item in enum[5:-1].split(','):
        arr.append(item.replace("'", ""))
    return arr

def defaultDBPassword():
    """
    Sets the default user's password to the hashed password, 'password'.
    'password' default hash value is invalid so the user can't allow their
    password to be changed by this function
    """
    conn.execute(text(
        "UPDATE users SET hashed_pswd = :pswdHash WHERE hashed_pswd = 'password'"),
        {'pswdHash': bcrypt.generate_password_hash('password')})
    conn.commit()

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

# Load user for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)
