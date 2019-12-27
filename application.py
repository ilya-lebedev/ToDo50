from cs50 import SQL
from flask import Flask, jsonify, redirect, render_template, request, session
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


@app.route("/active", methods=["GET"])
@login_required
def active():
    """ Show active todos to user """

    # Query database for active todos of user
    todos = db.execute("SELECT todos.id, todos.title, todos.description, complete, trash, list_id, lists.title AS list_title FROM todos LEFT JOIN lists ON list_id = lists.id WHERE todos.user_id = :user_id AND complete = 0 AND trash = 0",
                       user_id = session["user_id"])

    # Query database for tags of each todo
    for todo in todos:
        tags = db.execute("SELECT tags.id, tags.tag_name FROM todos_tags JOIN tags ON todos_tags.tag_id = tags.id WHERE todos_tags.todo_id = :todo_id",
                          todo_id = todo["id"])
        todo["tags"] = tags

    return render_template("all-todos.html", todos = todos)


@app.route("/add-list", methods=["GET", "POST"])
@login_required
def add_list():
    """ Add new list """

    # User reached route via PODT (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure title was submitted
        if not request.form.get("title"):
            return apology("must provide title", 400)

        # Add new list into the database
        list_id = db.execute("INSERT INTO lists(title, description, user_id) VALUES (:title, :description, :user_id)",
                    title = request.form.get("title"), description = request.form.get("description"), user_id = session["user_id"])

        # Redirect user to lists page
        return redirect("/lists")

    # User reached route via GET (as by clicking a ling or via redirect)
    else:
        return render_template("add-list.html")


@app.route("/add-tag", methods=["GET", "POST"])
@login_required
def add_tag():
    """ Add new tag """

    # User reached route via POST (as by submittihg a form via POST)
    if request.method == "POST":

        # Ensure tag name was submitted
        if not request.form.get("tag_name"):
            return apology("must provide tag name", 400)

        # Ensure tag name length is less than 255 symbols
        if not len(request.form.get("tag_name")) < 255:
            return apology("too long tag name", 400)

        # Query database for tag name
        tags = db.execute("SELECT id FROM tags WHERE user_id = :user_id AND tag_name = :tag_name",
                          user_id = session["user_id"], tag_name = request.form.get("tag_name"))

        # Ensure there is no such tag name
        if len(tags) == 1:
            return apology("tag alredy exist", 400)

        # Add new tag into the database
        db.execute("INSERT INTO tags(tag_name, user_id) VALUES (:tag_name, :user_id)",
                   tag_name = request.form.get("tag_name"), user_id = session["user_id"])

        # Redirect user to tags page
        return redirect("/tags")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("add-tag.html")


@app.route("/add-todo", methods=["GET", "POST"])
@login_required
def add_todo():
    """ Add new to-do """

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure title was submitted
        if not request.form.get("title"):
            return apology("must provide title", 400)

        # Get list of tags from form
        tags = request.form.getlist("tags")

        # Add new todo into the database
        todo_id = db.execute("INSERT INTO todos(title, description, user_id, list_id) VALUES (:title, :description, :user_id, :list_id)",
                    title = request.form.get("title"), description = request.form.get("description"), user_id = session["user_id"], list_id = request.form.get("list_id"))

        # Add tags for new todo into the database
        for tag_id in tags:
            db.execute("INSERT INTO todos_tags(todo_id, tag_id) VALUES (:todo_id, :tag_id)",
                       todo_id = todo_id, tag_id = tag_id)

        # Redirect user to all todos page
        return redirect("/active")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Query database for user tags
        tags = db.execute("SELECT id, tag_name FROM tags WHERE user_id = :user_id",
                          user_id = session["user_id"])

        # Query database for user lists
        lists = db.execute("SELECT id, title FROM lists WHERE user_id = :user_id",
                           user_id = session["user_id"])

        return render_template("add-todo.html", tags = tags, lists = lists)


@app.route("/all", methods=["GET"])
@login_required
def all():
    """ Show all to-dos """

    # Query database for user todos
    todos = db.execute("SELECT todos.id, todos.title, todos.description, complete, trash, list_id, lists.title AS list_title FROM todos LEFT JOIN lists ON list_id = lists.id WHERE todos.user_id = :user_id",
                       user_id = session["user_id"])

    # Query database for tags of each todo
    for todo in todos:
        tags = db.execute("SELECT tags.id, tags.tag_name FROM todos_tags JOIN tags ON todos_tags.tag_id = tags.id WHERE todos_tags.todo_id = :todo_id",
                          todo_id = todo["id"])
        todo["tags"] = tags

    return render_template("all-todos.html", todos = todos)


@app.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    """ Change user password """

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure old password was submitted
        if not request.form.get("old-password"):
            return apology("must provide old password", 400)

        # Query database for old user password
        users = db.execute("SELECT hash FROM users WHERE id = :id",
                           id = session["user_id"])

        # Ensure old password is correct
        if not check_password_hash(users[0]["hash"], request.form.get("old-password")):
            return apology("invalid old password", 400)

        # Ensure new password was submitted
        if not request.form.get("new-password"):
            return apology("must provide new password", 400)

        # Ensure confirmation was submitted
        if not request.form.get("confirmation"):
            return apology("must provide confirmation", 400)

        # Ensure new password and confirmation equal
        if not request.form.get("new-password") == request.form.get("confirmation"):
            return apology("password doesn't match", 400)

        # Query database for update hash
        db.execute("UPDATE users SET hash = :hash WHERE id = :id",
                   hash = generate_password_hash(request.form.get("new-password")), id = session["user_id"])

        # Redirect user
        return redirect("/change-password")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("change-password.html")


@app.route("/check-username", methods=["GET"])
def check():
    """ Check username """
    """ Return true if username available, else false, in JSON format """

    # Get username
    username = request.args.get("username").strip()

    # Ensure username not empty
    if len(username) < 1:
        return jsonify(False)

    # Query database for username
    users = db.execute("SELECT id FROM users WHERE username = :username",
                       username = username)

    if len(users) > 0:
        return jsonify(False)
    else:
        return jsonify(True)


@app.route("/complete", methods=["POST"])
@login_required
def complete():
    """ Complete todo """

    db.execute("UPDATE todos SET complete=1 WHERE id = :id AND user_id = :user_id",
               id = request.form.get("todo-id"), user_id = session["user_id"])

    return redirect("active")


@app.route("/")
def index():
    """ Show main page """
    return render_template("index.html")


@app.route("/lists", methods=["GET"])
@login_required
def lists():
    """ Show lists of to-dos """

    lists = db.execute("SELECT id, title, description FROM lists WHERE user_id = :user_id",
                       user_id = session["user_id"])

    return render_template("lists.html", lists = lists)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log user in """

    # Foget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for user
        user = db.execute("SELECT id, username, hash FROM users WHERE username = :username",
                          username = request.form.get("username"))

        # Ensure username is exist and password is correct
        if not (len(user) == 1 and check_password_hash(user[0]["hash"], request.form.get("password"))):
            return apology("invalid username and/or password", 403)

        # Remember which user has loggedin
        session["user_id"] = user[0]["id"]
        session["user_name"] = user[0]["username"]

        # Redirect user to all to-dos page
        return redirect("/active")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """ Log user out """

    # Forget any user id
    session.clear()

    # Redirect user to the main page
    return redirect("/")


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
        session["user_name"] = request.form.get("username")

        # Redirect user to all to-dos page
        return redirect("/active")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/tags", methods=["GET"])
@login_required
def tags():
    """ Show tags of to-dos """

    # Query database for user tags
    tags = db.execute("SELECT id, tag_name FROM tags WHERE user_id = :user_id",
                      user_id = session["user_id"])

    return render_template("tags.html", tags = tags)


@app.route("/trash", methods=["GET", "POST"])
@login_required
def trash():
    """ Todos trash """

    # User reached route via POST (as by submitting a form via POST)
    if (request.method == "POST"):
        # Put todo to the trash

        # Query database for putting todo into trash
        db.execute("UPDATE todos SET trash = 1 WHERE id = :id AND user_id = :user_id",
                   id = request.form.get("todo-id"), user_id = session["user_id"])

        # Redirect user to all to-dos page
        return redirect("/active")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        # Show all todos in trash for user

        # Query database for user todos
        todos = db.execute("SELECT id, title, description, complete, trash FROM todos WHERE user_id = :user_id AND trash = 1",
                           user_id = session["user_id"])

        return render_template("all-todos.html", todos = todos)


@app.route("/todos/tag/<tag_id>", methods=["GET"])
@login_required
def todos_by_tag(tag_id):
    """ Show todos by tag """

    # Query database for todos by tag
    todos = db.execute("SELECT todos.id, todos.title, todos.description, todos.complete, todos.trash FROM todos JOIN todos_tags ON todos.id = todos_tags.todo_id WHERE todos.user_id = :user_id AND todos_tags.tag_id = :tag_id",
                       user_id = session["user_id"], tag_id = tag_id)

    # Query database for tags of each todo
    for todo in todos:
        tags = db.execute("SELECT tags.id, tags.tag_name FROM todos_tags JOIN tags ON todos_tags.tag_id = tags.id WHERE todos_tags.todo_id = :todo_id",
                          todo_id = todo["id"])
        todo["tags"] = tags

    return render_template("all-todos.html", todos = todos)


@app.route("/todos/list/<list_id>", methods=["GET"])
@login_required
def todos_from_list(list_id):
    """ Show todos from list """

    # Query database for todos from list
    todos = db.execute("SELECT todos.id, todos.title, todos.description, complete, trash, list_id, lists.title AS list_title FROM todos LEFT JOIN lists ON list_id = lists.id WHERE todos.user_id = :user_id AND list_id = :list_id",
                       user_id = session["user_id"], list_id = list_id)

    # Query database for tags of each todo
    for todo in todos:
        tags = db.execute("SELECT tags.id, tags.tag_name FROM todos_tags JOIN tags ON todos_tags.tag_id = tags.id WHERE todos_tags.todo_id = :todo_id",
                          todo_id = todo["id"])
        todo["tags"] = tags

    return render_template("all-todos.html", todos = todos)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
