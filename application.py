from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///todo.db")


@app.route("/")
def index():
    """ Show main page """
    return render_template("index.html")


@app.route("/all", methods=["GET"])
@login_required
def all():
    """ Show all to-dos """
    return apology("TODO")


@app.route("/lists", methods=["GET"])
@login_required
def lists():
    """ Show lists of to-dos """
    return apology("TODO")


@app.route("/lists", methods=["GET"])
@login_required
def tags():
    """ Show tags of to-dos """
    return apology("TODO")


@app.route("/lists", methods=["GET"])
@login_required
def trash():
    """ Show trash """
    return apology("TODO")


@app.route("/lists", methods=["GET"])
@login_required
def change_password():
    """ Show change password """
    return apology("TODO")


@app.route("/lists", methods=["GET"])
@login_required
def logout():
    """ Show logout """
    return apology("TODO")


@app.route("/lists", methods=["GET"])
def register():
    """ Show register """
    return apology("TODO")


@app.route("/lists", methods=["GET"])
def login():
    """ Show login """
    return apology("TODO")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
