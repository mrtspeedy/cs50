# Taken from CS50 Finance Problem

from flask import redirect, render_template, session
from functools import wraps
import requests

CURRENCIES = {
    "GBP": "£",
    "USD": "$",
    "EUR": "€",
}

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

# To change the date and times to human readable time, with help of AI
def datetimefmt(value, fmt="%d %b %Y, %H:%M"):
    if value is None:
        return ""
    return value.strftime(fmt)

# Define currency converter (with help of AI)
def convert(amount, base, target):

    # If the base currency is equal to the target currency
    if base == target:
        return {"result": amount, "rate": float("1"), "date": None}

    try:
        # Contact free Frankfurter API to get latest currency conversion from base to target, timeout of 5 seconds
        response = requests.get(
            "https://api.frankfurter.dev/v1/latest",
            params={"from": base, "to": target},
            timeout=5
        )
        response.raise_for_status()
        # Get the JSON from the API
        data = response.json()

        # Get rate as float, convert to str first to avoid binary noise
        rate = float(str(data["rates"][target]))

    # If any errors occured during lookup
    except (requests.RequestException, KeyError, ValueError):
        return None

    # Return the results of the API
    return {
        "result": round((amount * rate), 2),
        "rate": rate,
        "date": data.get("date"),
    }

# Define a loan calculator
def loan_cost(principal, annual_rate, months):
    # principal is the amount borrowed as a float
    # annual_rate is the yearly interest rate as a percentage
    # months is the number of monthly payments as an integer

    monthly_rate = annual_rate / 100 / 12

    if monthly_rate == 0:
        # Interest-free loan: just split the principal evenly
        payment = principal / months
    else:
        # Standard amortisation formula
        payment = principal * monthly_rate / (1 - (1 + monthly_rate) ** -months)

    # Round all values to the nearest 2 decimal places, as it is a currency
    payment = round(payment, 2)
    total = round(payment * months, 2)
    interest = round(total - principal, 2)

    # Return all 
    return {
        "payment": payment,
        "total": total,
        "interest": interest,
        "months": months,
    }