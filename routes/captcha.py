import requests
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash

register_bp = Blueprint("register", __name__)

# Your Google reCAPTCHA Secret Key (Keep this secure)
RECAPTCHA_SECRET_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

def verify_recaptcha(response):
    """Verify the reCAPTCHA response token with Google."""
    url = "https://www.google.com/recaptcha/api/siteverify"
    data = {
        "secret": RECAPTCHA_SECRET_KEY,
        "response": response
    }
    result = requests.post(url, data=data).json()
    return result.get("success", False)  # Returns True if valid

@register_bp.route("/register", methods=["GET", "POST"])
def register():
    """Handle user registration with reCAPTCHA validation."""
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        recaptcha_response = request.form.get("g-recaptcha-response")

        # Check if reCAPTCHA token exists
        if not recaptcha_response:
            flash("CAPTCHA validation failed. Please complete the CAPTCHA.", "danger")
            return redirect(url_for("register.register"))

        # Validate reCAPTCHA with Google
        if not verify_recaptcha(recaptcha_response):
            flash("CAPTCHA verification failed. Try again.", "danger")
            return redirect(url_for("register.register"))

        # If CAPTCHA is valid, proceed with user registration logic
        flash("Registration successful!", "success")
        return redirect(url_for("login.login"))

    return render_template("register.html")