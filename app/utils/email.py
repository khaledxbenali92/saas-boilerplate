"""
Email Utility
"""

from flask import render_template_string, current_app, url_for
from flask_mail import Message
from app import mail


def send_verification_email(user, token):
    verify_url = url_for("auth.verify_email", token=token, _external=True)
    msg = Message(
        subject=f"Verify your {current_app.config['APP_NAME']} account",
        recipients=[user.email],
        html=f"""
        <h2>Welcome to {current_app.config['APP_NAME']}!</h2>
        <p>Please verify your email by clicking the link below:</p>
        <a href="{verify_url}" style="background:#0d7377;color:white;padding:12px 24px;
           border-radius:8px;text-decoration:none;display:inline-block">
           ✅ Verify Email
        </a>
        <p>This link expires in 24 hours.</p>
        """
    )
    mail.send(msg)


def send_password_reset_email(user, token):
    reset_url = url_for("auth.reset_password", token=token, _external=True)
    msg = Message(
        subject=f"Reset your {current_app.config['APP_NAME']} password",
        recipients=[user.email],
        html=f"""
        <h2>Password Reset Request</h2>
        <p>Click the link below to reset your password:</p>
        <a href="{reset_url}" style="background:#0d7377;color:white;padding:12px 24px;
           border-radius:8px;text-decoration:none;display:inline-block">
           🔐 Reset Password
        </a>
        <p>This link expires in 2 hours. If you didn't request this, ignore this email.</p>
        """
    )
    mail.send(msg)
