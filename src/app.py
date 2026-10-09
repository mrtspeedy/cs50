import os
from flask import Flask, redirect, render_template, request, session
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timezone
from database import db, Users, Expenses
from dotenv import load_dotenv
import math
from helpers import login_required, datetimefmt, convert, CURRENCIES, loan_cost

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

@app.route("/insights")
@login_required
def insights():

    # Get all of the expenses from the current logged in user, group by category, and order by most amount spent on a category first
    rows = db.session.execute(
        db.select(
            Expenses.category,
            func.sum(Expenses.amount).label("total"),
            func.count(Expenses.id).label("count"),
        )
        .where(Expenses.user_id == session["user_id"])
        .group_by(Expenses.category)
        .order_by(func.sum(Expenses.amount).desc())
    ).all()

    grand_total = sum(float(total) for _, total, _ in rows)

    # Put all expenses per category and their total and percentage into a list of dictionaries
    categories = [
        {
            "name": category,
            "total": total,
            "count": count,
            "percentage": float(total) / grand_total * 100 if grand_total else 0
        }
        for category, total, count in rows
    ]

    return render_template("insights.html", categories=categories, grand_total=grand_total)

# Manage account, such as changing your password or deleting your account
@app.route("/manage", methods=["GET", "POST"])
@login_required
def manage():

    # Get user info from database
    user = db.session.get(Users, session["user_id"])

    # If user got here by clicking any of the actions
    if request.method == "POST":
        action = request.form.get("action")

        # If user wants to change their password, get form information about password
        if action == "password":
            current = request.form.get("current")
            new = request.form.get("new")
            confirmation = request.form.get("confirmation")

            # If any inputs aren't given
            if not current or not new or not confirmation:
                return "Missing Required Input(s)", 400

            # If new passwords do not match
            if new != confirmation:
                return "Passwords Do Not Match", 400

            # If old password doesn't match the stored one
            if not check_password_hash(user.hash, current):
                return "Incorrect Current Password", 403

            # Make sure the new password isn't equal to the old one
            if check_password_hash(user.hash, new):
                return "New Password Must Be Different", 400

            # Generate a new password hash to store and store it in the database
            user.hash = generate_password_hash(new)
            db.session.commit()
            return redirect("/manage")

        # Otherwise if the user selected to delete their account, get the password to confirm deletion
        elif action == "delete":
            password = request.form.get("password")

            # If the password is missing missing
            if not password:
                return "Missing Required Input(s)", 400

            # Or if the password does not match the stored one
            if not check_password_hash(user.hash, password):
                return "Incorrect Password", 403

            # If all is well, delete the user from the database, clear their session in the browser and redirect them to register a new account
            db.session.delete(user)
            db.session.commit()
            session.clear()
            return redirect("/register")

        # If action doesn't match any of the above, then return invalid action
        return "Invalid Action", 400

    # If no action is given, pass None to show menu to select an action
    action = request.args.get("action")
    if action not in ("password", "delete"):
        action = None

    # Render the manage account page based on the action selected
    return render_template("manage.html", action=action)

@app.route("/converter", methods=["GET", "POST"])
@login_required
def converter():

    if request.method == "POST":
        # Get all form fields from the page
        amount = request.form.get("amount")
        base = request.form.get("base")
        target = request.form.get("target")

        # If any inputs are missing
        if not amount or not base or not target:
            return "Missing Required Input(s)", 400

        # Only accept currencies that have been listed
        if base not in CURRENCIES or target not in CURRENCIES:
            return "Unsupported Currency", 400

        # Try to round the amount, and if it throws an error then it's not a number
        try:
            amount = round(float(amount), 2)
        except ValueError:
            return "Amount must be a number", 400

        # Make sure value is positive
        if amount <= 0:
            return "Amount must be a positive number", 400

        # Convert the currencies, and if it doesn't return anything, return an error
        conversion = convert(amount, base, target)
        if conversion is None:
            return "Exchange rates are unavailable right now, please try again", 502

        # Send all fields to page to display the conversion
        return render_template(
            "converter.html",
            currencies=CURRENCIES,
            conversion=conversion,
            amount=amount,
            base=base,
            target=target,
        )

    # Makes sure the currencies shown are only the ones we have listed
    # Makes sure not to show any conversions since none have been selected
    # The default pre-populated values for the base and target when first reaching the page
    return render_template(
        "converter.html",
        currencies=CURRENCIES,
        conversion=None,
        base="GBP",
        target="USD",
    )

@app.route("/calculator", methods=["GET", "POST"])
@login_required
def calculator():

    if request.method == "POST":
        # Get field inputs from page
        principal = request.form.get("principal")
        rate = request.form.get("rate")
        term = request.form.get("term")
        unit = request.form.get("unit")

        if not principal or not rate or not term or not unit:
            return "Missing Required Input(s)", 400

        # If unit is not months or years
        if unit not in ("years", "months"):
            return "Invalid Term Unit", 400

        # princial is the amount to be paid
        # rate is the interest rate
        # term is how long, in years or months, that loan will be paid by
        try:
            principal = round(float(principal), 2)
            rate = float(rate)
            term = int(term)
        except ValueError:
            return "Amount, rate and term must be numbers", 400

        # Check if all inputs are valid numbers
        if not math.isfinite(principal) or principal <= 0:
            return "Amount must be a positive number", 400

        if not math.isfinite(rate) or rate < 0 or rate > 100:
            return "Rate must be between 0 and 100", 400

        months = term * 12 if unit == "years" else term
        if months < 1 or months > 600:
            return "Term must be between 1 month and 50 years", 400

        # Calculate the loan cost from helpers.py
        result = loan_cost(principal, rate, months)

        # Return all the loan values to the page
        return render_template(
            "calculator.html",
            result=result,
            principal=principal,
            rate=rate,
            term=term,
            unit=unit,
        )

    # If the user has just gotten here via GET method, show nothing except the form
    return render_template("calculator.html", result=None, principal=None, rate=None, term=None, unit="years")
    
@app.route("/credits")
def credits():

    return render_template("credits.html")
