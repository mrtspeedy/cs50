# This code I wrote myself, however I got AI to help understand exactly how SQLAlchemy works and how to use it

from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

# Initialise Database
db = SQLAlchemy()

# Define SQLAlchemy tables in classes
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    hash = db.Column(db.String, nullable=False)
    # Define relationship between tables
    # Backref means the relationship can be referenced both ways, from the users table and from the expenses table
    # Lazy loading here means the expenses of this user aren't loaded until explicitly asked
    # Cascase allows for automatic deletion of orphaned expenses
    expenses = db.relationship("Expenses",
                               backref="user",
                               lazy=True,
                               cascade="all, delete-orphan"
                               )

class Expenses(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    amount = db.Column(db.Numeric, nullable=False)
    category = db.Column(db.String, nullable=False)
    desc = db.Column(db.String)
    # Get the time of the transaction using the current date that is pulled from datetime.now from timezone utc
    time = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))