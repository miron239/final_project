import os

import sqlite3
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask import g

from helpers import apology, login_required, lookup, usd, sql_data_to_list_of_dicts

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
path_to_db = 'orders.db'


# Configure CS50 Library to use SQLite database


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


connect = sqlite3.connect('database.db')


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    if request.method == "POST":
        if not request.form.get("username"):
            return apology("must provide username", 403)
        if not request.form.get("password"):
            return apology("must provide password", 403)
        query = ("SELECT * FROM users WHERE username = " + "'" + request.form.get("username")) + "'"
        rows = sql_data_to_list_of_dicts(path_to_db, query)
        print(rows)
        if len(rows) != 1 or not (check_password_hash(rows[0]["hash"], (request.form.get("password")))):
            return apology("invalid username or password", 403)

        session["user_id"] = rows[0]["id"]
        session["user_role"] = rows[0]["role"]
        session["user_rights"] = rows[0]["rights"]
        return redirect("/")

    if request.method == "GET":
        return render_template("login.html")
    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username

        connect = sqlite3.connect('database.db')
        cursor = connect.cursor()
        cursor.execute("SELECT * FROM users WHERE username = (?)", request.get.form("username"))

        rows = cursor.fetchall()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        print(rows)
        session["user_id"] = rows[0]["id"]
        session["user_role"] = rows[0]["role"]
        session["user_rights"] = rows[0]["rights"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    return apology("TODO")


@app.route("/new_dish", methods=["GET", "POST"])
@login_required
def new_dish():
    if request.method == "POST":
        if session["user_role"] == "admin":
            name = request.form.get('name')
            price = request.form.get('price')
            livetime = request.form.get('livetime')

            if not name:
                return apology("Name can not be empty")
            if not price:
                return apology("Price can not be empty")
            if not livetime:
                return apology("Price can not be livetime")

            with sqlite3.connect("orders.db") as users:
                cursor = users.cursor()
                try:
                    cursor.execute("INSERT INTO dishes (name, dish_price, livetime) VALUES (?, ?, ?)",
                                   (name, price, livetime))
                except:
                    return apology("Name is already in use")
            users.commit()
        else:
            return apology("You are not the manager")
    else:
        return render_template("new_dish.html")
    """Get stock quote."""
    return apology("TODO")


@app.route("/all_orders")
@login_required
def orders():
    if session["user_role"] == "admin":
        user_id = session["user_id"]
        connect = sqlite3.connect('orders.db')
        cursor = connect.cursor()
        query = """
                SELECT
                    o.id AS order_id,
                    GROUP_CONCAT(d.name) AS ordered_dishes,
                    SUM(d.dish_price) AS total_price,
                    u.username AS user_username
                FROM
                    orders o
                JOIN
                    ordered_items oi ON o.id = oi.order_id
                JOIN
                    dishes d ON oi.dish_id = d.id
                JOIN
                    users u ON o.user_id = u.id
                GROUP BY
                    o.id, u.username;
                """
        result = cursor.execute(query)
        return render_template("all_orders.html", orders=result)


@app.route("/new_order_admin", methods=["GET", "POST"])
def new_order_admin():
    if request.method == "POST":
        user_id = request.form.get('user_id')
        user_select = request.form.get('user_select')

        try:
            with sqlite3.connect("orders.db") as connection:
                cursor = connection.cursor()

                if user_id:
                    cursor.execute("INSERT INTO orders (user_id) VALUES (?)", (user_id,))
                elif user_select:
                    cursor.execute("INSERT INTO orders (user_id) VALUES (?)", (user_select,))

                connection.commit()
        except sqlite3.Error:
            return apology("Error while creating order")


        return redirect("/")
    else:
        connect = sqlite3.connect('orders.db')
        cursor = connect.cursor()
        result = cursor.execute("SELECT username FROM users")
        return render_template("new_order_admin.html", users=result)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        confirmation = request.form.get('confirmation')

        if not username:
            return apology("Please enter the username")
        if not password:
            return apology("Please enter the password")
        if not confirmation:
            return apology("Please enter the password confirmation")
        if password != confirmation:
            return apology("Password is not the same with password confirmation")

        hash = generate_password_hash(password)
        with sqlite3.connect("orders.db") as users:
            cursor = users.cursor()
            try:
                cursor.execute("INSERT INTO users (role, rights, username, hash) VALUES (?, ?, ?, ?)",
                               ('admin', 'all', username, hash))
            except:
                return apology("Username is already in use")
            users.commit()
        return redirect("/")
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    return apology("TODO")
