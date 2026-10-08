import os
from flask import Flask, redirect, render_template, request, session
from sqlalchemy import func
from werkzeug.security import check_password_hash, generate_password_hash
from database import db, Users, Expenses
from dotenv import load_dotenv
from helpers import login_required

# Load .env file
load_dotenv()

# Configure application
app = Flask(__name__)

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
    return render_template("index.html")

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

