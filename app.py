from crypt import methods
from datetime import datetime
import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import *

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///database.db")


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Allow user to Login
@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            rows = db.execute(
                "SELECT * FROM users WHERE username = ?", request.form.get("username")
            )
        except Exception:
            return "Incorrect Username"
        # Verify that the username is valid
        if len(rows) == 0:
            return "Incorrect Username"
        hash = rows[0]["hash"]

        # Verify that the password is correct
        if check_password_hash(hash, password) == False:
            return "Incorrect Password"
        # Log person in and get id in session["user_id"]            
        else:
            session["user_id"] = rows[0]["id"]
            return redirect("/")
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Verify user inputs
        if username == "":
            return "Please enter a username"
        elif len(password) < 8:
            return "Password must be atleast 8 characters long"
        elif password != request.form.get("check_password"):
            return "The two passwords do not match!"
        elif len(db.execute("SELECT username FROM users WHERE username=?;", username)) > 0:
            return "Username already exists"
        # Add user information to Database
        else:
            password = generate_password_hash(password)
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?);", username, password)
            return redirect("/")
    else:
        return render_template("register.html")
    
@app.route("/",)
@login_required
def home():
    username = db.execute("SELECT username FROM users WHERE id=?;", session["user_id"])[0]["username"]
    return render_template("home.html", name=username)

@app.route("/feed")
def feed():
    pass

@app.route("/finances")
def finances():
    # Get persons finance history and format it then display on page
    log = db.execute("SELECT * FROM finance WHERE person_id=?;", session["user_id"])
    for entry in log:
        entry["amount"] = usd(entry["amount"])
    return render_template("finance.html",log=log)

@app.route("/delete", methods=["POST"])
def delete():
    # Remove transaction from database
    transaction_id = request.form.get("transaction_id")
    db.execute("DELETE FROM finance WHERE transaction_id=?", transaction_id)
    return redirect("/finances")

@app.route("/add-entry", methods=["GET", "POST"])
def add_entry():
    if request.method == "POST":
        methods = ["Earning", "Spending"]
        cause = request.form.get("cause")
        effect = request.form.get("effect")
        # Verify user inputs
        if effect not in methods:
            return "Please select a valid option"
        try:
            amount = int(request.form.get("amount"))
        except TypeError:
            return "Please enter a valid amount"
        time = datetime.now()

        if cause == "":
            return "Please fill out cause field!"
        elif effect == "":
            return "Please select one of the options!"
        elif int(amount) < 0:
            return "Please input a valid amount"
        
        # Add user input to database
        db.execute("INSERT INTO finance (person_id, cause, amount, time, effect) VALUES(?,?,?,?,?);",session["user_id"], cause, amount, time, effect)
        return redirect("/finances")
    else:
        return render_template("add-entry.html")

@app.route("/link_email")
def link_email():
    pass

# Add Log out Functionality
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

