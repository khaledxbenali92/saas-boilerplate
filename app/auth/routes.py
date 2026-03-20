"""
Auth Routes — Register, Login, Logout, Password Reset, Email Verification
"""

from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models.user import User
from app.utils.email import send_verification_email, send_password_reset_email

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        data = request.get_json() or request.form
        email = data.get("email", "").strip().lower()
        name = data.get("name", "").strip()
        password = data.get("password", "")

        # Validate
        errors = _validate_registration(email, name, password)
        if errors:
            if request.is_json:
                return jsonify({"success": False, "errors": errors}), 400
            for error in errors:
                flash(error, "error")
            return render_template("auth/register.html")

        # Check duplicate
        if User.query.filter_by(email=email).first():
            msg = "Email already registered."
            if request.is_json:
                return jsonify({"success": False, "message": msg}), 400
            flash(msg, "error")
            return render_template("auth/register.html")

        # Create user
        user = User(email=email, name=name)
        user.set_password(password)
        token = user.generate_email_token()
        db.session.add(user)
        db.session.commit()

        # Send verification email
        try:
            send_verification_email(user, token)
        except Exception:
            pass

        if request.is_json:
            return jsonify({
                "success": True,
                "message": "Registration successful! Please verify your email.",
                "user": user.to_dict()
            })

        flash("Registration successful! Please check your email to verify your account.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        data = request.get_json() or request.form
        email = data.get("email", "").strip().lower()
        password = data.get("password", "")
        remember = data.get("remember", False)

        user = User.query.filter_by(email=email).first()

        if not user or not user.check_password(password):
            msg = "Invalid email or password."
            if request.is_json:
                return jsonify({"success": False, "message": msg}), 401
            flash(msg, "error")
            return render_template("auth/login.html")

        if not user.is_active:
            msg = "Account is deactivated. Contact support."
            if request.is_json:
                return jsonify({"success": False, "message": msg}), 403
            flash(msg, "error")
            return render_template("auth/login.html")

        login_user(user, remember=bool(remember))

        from datetime import datetime
        user.last_login_at = datetime.utcnow()
        db.session.commit()

        if request.is_json:
            return jsonify({"success": True, "redirect": url_for("dashboard.index")})

        next_page = request.args.get("next")
        return redirect(next_page or url_for("dashboard.index"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/verify-email/<token>")
def verify_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    if not user:
        flash("Invalid or expired verification link.", "error")
        return redirect(url_for("auth.login"))

    user.email_verified = True
    user.email_verification_token = None
    db.session.commit()

    flash("Email verified! You can now log in.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "POST":
        data = request.get_json() or request.form
        email = data.get("email", "").strip().lower()

        user = User.query.filter_by(email=email).first()
        if user:
            token = user.generate_password_reset_token()
            db.session.commit()
            try:
                send_password_reset_email(user, token)
            except Exception:
                pass

        # Always show success (security: don't reveal if email exists)
        msg = "If that email exists, we sent a reset link."
        if request.is_json:
            return jsonify({"success": True, "message": msg})
        flash(msg, "info")
        return redirect(url_for("auth.login"))

    return render_template("auth/forgot_password.html")


@auth_bp.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    from datetime import datetime
    user = User.query.filter_by(password_reset_token=token).first()

    if not user or not user.password_reset_expires or \
       user.password_reset_expires < datetime.utcnow():
        flash("Invalid or expired reset link.", "error")
        return redirect(url_for("auth.forgot_password"))

    if request.method == "POST":
        data = request.get_json() or request.form
        password = data.get("password", "")

        if len(password) < 8:
            msg = "Password must be at least 8 characters."
            if request.is_json:
                return jsonify({"success": False, "message": msg}), 400
            flash(msg, "error")
            return render_template("auth/reset_password.html", token=token)

        user.set_password(password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.session.commit()

        if request.is_json:
            return jsonify({"success": True, "message": "Password reset successful!"})
        flash("Password reset successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/reset_password.html", token=token)


def _validate_registration(email, name, password):
    errors = []
    if not email or "@" not in email:
        errors.append("Valid email is required.")
    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters.")
    if not password or len(password) < 8:
        errors.append("Password must be at least 8 characters.")
    return errors
