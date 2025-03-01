import re
import requests
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models.user import User
from extensions import db

register_bp = Blueprint("register", __name__)

# Google reCAPTCHA Secret Key (Test key for development)
RECAPTCHA_SECRET_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

def verify_recaptcha(response_token):
    """Verify the reCAPTCHA response token with Google."""
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": RECAPTCHA_SECRET_KEY,
        "response": response_token
    }
    result = requests.post(url, data=data).json()
    return result.get("success", False)

def is_valid_password(password):
    """Check if the password meets security requirements."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one number."
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "Password must contain at least one special character."
    return True, ""

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        recaptcha_response = request.form.get("g-recaptcha-response")

        # Validate reCAPTCHA
        if not recaptcha_response or not verify_recaptcha(recaptcha_response):
            flash("CAPTCHA verification failed. Please complete the reCAPTCHA.", "error")
            return redirect(url_for("register.register"))

        # Validate username uniqueness
        if User.query.filter_by(username=username).first():
            flash("Username already exists. Please choose a different one.", "error")
            return redirect(url_for("register.register"))

        # Validate password complexity
        valid, error_message = is_valid_password(password)
        if not valid:
            flash(error_message, "error")
            return redirect(url_for("register.register"))

        # Create new user with hashed password
        new_user = User(username=username)
        new_user.set_password(password)  # Assuming this method hashes the password
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful! You can now log in.", "success")
        return redirect(url_for("login.login"))

    return render_template("register.html")