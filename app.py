from calendar import month
from crypt import methods
from datetime import datetime
import os
from random import randrange

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import *

# Configure application
app = Flask(__name__)

app.jinja_env.filters['jsonify'] = jsonify

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

# Allow users to Register for an Account
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        # Verify user inputs
        if username == "None":
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

# Displays Home page   
@app.route("/",)
@login_required
def home():
    username = db.execute("SELECT username FROM users WHERE id=?;", session["user_id"])[0]["username"]
    return render_template("home.html", name=username)

# Displays posts
@app.route("/feed", methods=["GET", "POST"])
@login_required
def feed():
    if request.method == "POST":
        post = request.form.get("like")
        try:
            db.execute("INSERT INTO liked (person_id,post_id) VALUES(?,?);", session["user_id"], post)
        except Exception:
            return "Already liked this post"
        # Increases lieks to specific post in database
        likes = db.execute("SELECT likes FROM posts WHERE id=?", post)[0]["likes"]
        likes += 1
        print(likes)
        db.execute("UPDATE posts SET likes=? WHERE id=?", likes, post)
        return redirect("/feed")
    else:
        # Displays posts
        posts = db.execute("SELECT posts.id as num,likes,post,time,username FROM posts,users WHERE posts.poster_id=users.id ORDER BY time DESC,likes;")
        return render_template("feed.html", posts=posts)

# Allows user to make a post   
@app.route("/make-post", methods=["GET", "POST"])
@login_required
def post():
    if request.method=="POST":
        # Adds post to database
        text = request.form.get("post")
        if text == "None":
            return "Please type a valid post" 
        db.execute("INSERT INTO posts (poster_id, post, time) VALUES(?,?,?);", session["user_id"], text, datetime.now())
        return redirect("/feed")
    else:
        # Gives space to input post
        return render_template("post.html")

# Display User's Finance History
@app.route("/finances")
@login_required
def finances():
    # Get persons finance history and format it then display on page
    log = db.execute("SELECT * FROM finance WHERE person_id=? ORDER BY time DESC;", session["user_id"])
    for entry in log:
        entry["amount"] = usd(entry["amount"])
    return render_template("finance.html",log=log)

# Delete an input from the table
@app.route("/delete", methods=["POST"])
@login_required
def delete():
    # Remove transaction from database
    transaction_id = request.form.get("transaction_id")
    db.execute("DELETE FROM finance WHERE transaction_id=?", transaction_id)
    return redirect("/finances")

# Display a Bar chart showing the person's financial progress over a month
@app.route("/analytics")
@login_required
def analytics():
    log = db.execute("SELECT * FROM finance WHERE person_id=? ORDER BY time;", session["user_id"])
    months = []
    years = [datetime.now().strftime("%Y")]
    data = {}
    for entry in log:
        # Get name of month and add it to a dictionary if new
        month = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S")
        year = month.strftime("%Y")
        month = month.strftime("%B")
        if entry["effect"] == "Spending":
            entry["amount"] *= -1
        if (month not in months) and (year in years):
            months.append(month)
            data[month] = 0
        # Calculate Earnings
        if (month in months) and (year in years):
            data[month] += int(entry["amount"])
    return render_template("analysis.html", months=months, data=data, time="Monthly")

# Display a Bar chart showing the person's financial progress over an year
@app.route("/yearly-analysis")
@login_required
def yearly_anaylysis():
    log = db.execute("SELECT * FROM finance WHERE person_id=? ORDER BY time;", session["user_id"])
    years = []
    data = {}

    for entry in log:
        # Get unique years and add to dictionary
        year = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S").strftime("%Y")
        if entry["effect"] == "Spending":
            entry["amount"] *= -1
        if year not in years:
            years.append(year)
            data[year] = 0
        # Calculate yearly profit/loss
        data[year] += entry["amount"]
    
    return render_template("analysis.html", months=years, data=data, time="Yearly")

@app.route("/weekly-analysis")
@login_required
# Display a Bar chart showing the person's financial progress over last 7 days of user's activity
def weekly_analysis():
    log = db.execute("SELECT * FROM finance WHERE person_id=? ORDER BY time;", session["user_id"])
    days = []
    data = {}

    for entry in log:
        # Get dates and add them to a dictionary
        day = datetime.strptime(entry["time"], "%Y-%m-%d %H:%M:%S").strftime("%d'th of %B")
        if entry["effect"] == "Spending":
            entry["amount"] *= -1
        if day not in days:
            days.append(day)
            data[day] = 0
        # Calculate profit/loss of that day
        data[day] += entry["amount"]
        # Ensure only 7 days are counted
        if len(days) == 8:
            days.pop
            break
    return render_template("analysis.html", months=days, data=data, time="7 Most Recent Day's")    

# Allow user to input their financial activity
@app.route("/add-entry", methods=["GET", "POST"])
@login_required
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

        if cause == "None":
            return "Please fill out cause field!"
        elif effect == "None":
            return "Please select one of the options!"
        elif int(amount) < 0:
            return "Please input a valid amount"
        
        # Add user input to database
        db.execute("INSERT INTO finance (person_id, cause, amount, time, effect) VALUES(?,?,?,?,?);",session["user_id"], cause, amount, time, effect)
        return redirect("/finances")
    else:
        return render_template("add-entry.html")

# Add Log out Functionality
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

@app.route("/stocks", methods=["GET", "POST"])
@login_required
def stcks():
    if request.method == "POST":
        name = request.form.get("name")
        try:
            price = usd(current_price(name))
        except:
            return("Stock not found")
        return render_template("stock-price.html", name=name, price=price)
    else:
        return render_template("stocks.html")
