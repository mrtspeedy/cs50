# Taken from CS50 Finance Problem

from flask import redirect, render_template, session
from functools import wraps

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