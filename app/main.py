"""
Main Routes — Landing page
"""

from flask import Blueprint, render_template, current_app

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    plans = current_app.config["STRIPE_PLANS"]
    return render_template("main/index.html", plans=plans,
                           app_name=current_app.config["APP_NAME"])
