from flask import session, redirect
from functools import wraps
import yfinance as yf

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

def usd(value):
    return f"${value:,.2f}"


def current_price(instrument):
    data = yf.Ticker(instrument).history(period="1d", interval="5m")
    return data["Close"].iloc[-1]
