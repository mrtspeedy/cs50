import os
from flask import Flask, redirect, render_template, request, session
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone
from database import db, Users, Expenses
from dotenv import load_dotenv
from helpers import login_required, datetimefmt

# Load .env file
load_dotenv()

# Configure application
app = Flask(__name__)

# Register Jinja filters
app.add_template_filter(datetimefmt, "datetimefmt")

# Get secret key from environment variables file
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY")

# Configure database address
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///budget.db"

# Initialise database
db.init_app(app)

# Create database tables if they don't exist
with app.app_context():
    db.create_all()

# Define routes
@app.route("/")
@login_required
def index():

    user = db.session.get(Users, session["user_id"])

    return render_template("index.html", expenses=user.expenses)

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":
        # Check field inputs
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # If any input is missing
        if not username or not password or not confirmation:
            return "Missing Required Input(s)", 400

        # If passwords do not match
        if password != confirmation:
            return "Passwords Do Not Match", 400

        # Check if the username already exists in the database
        existing_user = db.session.execute(db.select(Users).filter_by(username=username)).scalar_one_or_none()
        if existing_user is not None:
            return "Username Exists", 400

        # Hash password
        hash = generate_password_hash(password)

        # Create new user
        user = Users(username=username, hash=hash)

        # Push changes to database
        db.session.add(user)
        db.session.commit()

        # Log user in
        session["user_id"] = user.id

        # Redirect user to homepage
        return redirect("/")

    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    # Clear any existing user_id
    session.clear()

    if request.method == "POST":
        # Check field inputs
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if all fields are populated
        if not username or not password:
            return "Missing Required Input(s)", 400

        # Find user in database
        user = db.session.execute(db.select(Users).filter_by(username=username)).scalar_one_or_none()

        # Check if user exists or if the password matches
        if user is None or not check_password_hash(user.hash, password):
            return "Invalid Username and/or Password", 403

        # Remember logged in user in session
        session["user_id"] = user.id

        # Redirect to homepage
        return redirect("/")

    # If user got here through redirect or any other GET method
    else:
        return render_template("login.html")

@app.route("/logout")
@login_required
def logout():

    # Clear current user_id
    session.clear()

    # Redirect user to login
    return redirect("/login")

@app.route("/add", methods=["POST", "GET"])
@login_required
def add():

    if request.method == "POST":
        # Store fields from form
        amount = request.form.get("amount")
        category = request.form.get("category")
        desc = request.form.get("desc")

        # Check all required fields are populated
        if not amount or not category:
            return "Missing Required Input(s)", 400

        # Convert amount to a float with 2 decimal points
        try:
            amount = round(float(amount), 2)
        except ValueError:
            return "Amount must be a number", 400

        # Check whether the number entered is a valid positive numeric number
        if amount <= 0:
            return "Amount must be positive", 400

        # Populate values into database, desc or None means that if the value is null, then don't put anything there
        expense = Expenses(user_id=session["user_id"], amount=amount, category=category, desc=desc or None)
        db.session.add(expense)
        db.session.commit()

        return redirect("/")

    else:
        return render_template("add.html")

# Define which expense id to edit, or instead get a selection of expenses that can be edited
@app.route("/edit", defaults={"expense_id": None})
@app.route("/edit/<int:expense_id>", methods=["POST", "GET"])
@login_required
def edit(expense_id):

    # Get all of the current user's expenses that can be edited
    expenses = db.session.execute(db.select(Expenses).filter_by(user_id=session["user_id"]).order_by(Expenses.time.desc())).scalars().all()

    expense = None
    # Check if an expense id was given and matches any ids in the database, else return none
    if expense_id is not None:
        expense = next((e for e in expenses if e.id == expense_id), None)
        if expense is None:
            return "Expense not found", 404
    
    if request.method == "POST":
        amount = request.form.get("amount")
        category = request.form.get("category")
        desc = request.form.get("desc")
        time = request.form.get("time")

        # Check if any inputs were given
        if not amount or not category or not desc or not time:
            return "No inputs given.", 400

        # Only round and validate the amount if it was given as an input
        if amount:
            try:
                amount = round(float(amount), 2)
            except ValueError:
                return "Amount must be a number", 400

            if amount <= 0:
                return "Amount must be a positive number", 400

        # Convert time into time in database, only if it was given as an input
        if time:
            try:
                dbtime = datetime.strptime(time, "%Y-%m-%dT%H:%M").replace(tzinfo=timezone.utc)
            except ValueError:
                return "Invalid date/time", 400

        # Update fields in database, if they were given as inputs
        if amount:
            expense.amount = amount
        if category:
            expense.category = category
        if desc:
            expense.desc = desc
        if time:
            expense.time = dbtime
        db.session.commit()

        return redirect("/")

    else:
        return render_template("edit.html", expenses=expenses, expense=expense, current_time=expense.time.strftime("%Y-%m-%dT%H:%M") if expense else None)

@app.route("/remove", defaults={"expense_id": None})
@app.route("/remove/<int:expense_id>", methods=["GET", "POST"])
@login_required
def remove(expense_id):
    # Get all of the current users expenses from the database
    expenses = db.session.execute(
        db.select(Expenses)
        .filter_by(user_id=session["user_id"])
        .order_by(Expenses.time.desc())
    ).scalars().all()

    # Check if the expense exists for the current user
    expense = None
    if expense_id is not None:
        expense = next((e for e in expenses if e.id == expense_id), None)
        if expense is None:
            return "Expense not found", 404

    if request.method == "POST":
        db.session.delete(expense)
        db.session.commit()
        return redirect("/")

    return render_template("remove.html", expenses=expenses, expense=expense)
    
@app.route("/credits")
def credits():

    return render_template("credits.html")
