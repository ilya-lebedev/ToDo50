from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

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


@app.route("/tags", methods=["GET"])
@login_required
def tags():
    """ Show tags of to-dos """
    return apology("TODO")


@app.route("/trash", methods=["GET"])
@login_required
def trash():
    """ Show trash """
    return apology("TODO")


@app.route("/change-password", methods=["GET"])
@login_required
def change_password():
    """ Show change password """
    return apology("TODO")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """ Show logout """
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """ Register user """

    # User reached route via POST (as by submiting a form via POST)
    if request.method == "POST":

        # Ensure email was submited
        if not request.form.get("email"):
            return apology("must provide e-mail", 400)

        # Ensure username was submitted
        elif not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("must provide confirmation of password", 400)

        # Ensure password and confirmations equals
        elif not request.form.get("password") == request.form.get("confirmation"):
            return apology("password doesn't match", 400)

        # Query database for username
        users = db.execute("SELECT id FROM users WHERE username = :username",
                           username = request.form.get("username"))

        # Ensure username is available
        if len(users) > 0:
            return apology("username alredy exist", 400)

        # Generate password hash
        hash = generate_password_hash(request.form.get("password"))

        # Save new user into database
        user_id = db.execute("INSERT INTO users(username, hash, email) VALUES (:username, :hash, :email)",
                             username = request.form.get("username"), hash = hash, email = request.form.get("email"))

        # Remember which user has registered and logged in
        session["user_id"] = user_id

        # Redirect user to all to-dos page
        return redirect("/all")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/login", methods=["GET"])
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
