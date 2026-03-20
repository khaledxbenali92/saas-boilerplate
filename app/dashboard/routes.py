"""
Dashboard Routes
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    return render_template("dashboard/index.html", user=current_user)


@dashboard_bp.route("/settings", methods=["GET", "POST"])
@login_required
def settings():
    if request.method == "POST":
        data = request.form
        current_user.name = data.get("name", current_user.name).strip()
        db.session.commit()
        flash("Settings updated!", "success")
        return redirect(url_for("dashboard.settings"))

    return render_template("dashboard/settings.html", user=current_user)


@dashboard_bp.route("/api-keys")
@login_required
def api_keys():
    from app.models.user import APIKey
    keys = APIKey.query.filter_by(user_id=current_user.id).all()
    return render_template("dashboard/api_keys.html",
                           user=current_user, api_keys=keys)


@dashboard_bp.route("/billing")
@login_required
def billing():
    plans = current_app.config["STRIPE_PLANS"]
    return render_template("dashboard/billing.html",
                           user=current_user, plans=plans)
