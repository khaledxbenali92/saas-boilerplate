"""
Billing Routes — Stripe Checkout, Webhooks, Subscription Management
"""

import json
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db
from app.models.user import User

billing_bp = Blueprint("billing", __name__)


@billing_bp.route("/plans")
def plans():
    """Public pricing page."""
    return render_template("billing/plans.html",
                           plans=current_app.config["STRIPE_PLANS"],
                           stripe_public_key=current_app.config["STRIPE_PUBLIC_KEY"])


@billing_bp.route("/checkout/<plan_name>", methods=["POST"])
@login_required
def checkout(plan_name):
    """Create Stripe checkout session."""
    plans = current_app.config["STRIPE_PLANS"]
    if plan_name not in plans:
        return jsonify({"error": "Invalid plan"}), 400

    plan = plans[plan_name]
    if not plan.get("price_id"):
        flash("Stripe not configured. Please set up your Stripe keys.", "error")
        return redirect(url_for("billing.plans"))

    try:
        import stripe
        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

        # Get or create Stripe customer
        if not current_user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=current_user.name,
                metadata={"user_id": current_user.id}
            )
            current_user.stripe_customer_id = customer.id
            db.session.commit()

        session = stripe.checkout.Session.create(
            customer=current_user.stripe_customer_id,
            payment_method_types=["card"],
            line_items=[{"price": plan["price_id"], "quantity": 1}],
            mode="subscription",
            success_url=url_for("billing.success", _external=True) + "?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=url_for("billing.plans", _external=True),
            metadata={"user_id": current_user.id, "plan": plan_name}
        )
        return jsonify({"checkout_url": session.url})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@billing_bp.route("/success")
@login_required
def success():
    flash("🎉 Subscription activated successfully!", "success")
    return redirect(url_for("dashboard.index"))


@billing_bp.route("/portal", methods=["POST"])
@login_required
def customer_portal():
    """Stripe customer portal for managing subscription."""
    if not current_user.stripe_customer_id:
        flash("No active subscription found.", "error")
        return redirect(url_for("billing.plans"))

    try:
        import stripe
        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]
        session = stripe.billing_portal.Session.create(
            customer=current_user.stripe_customer_id,
            return_url=url_for("dashboard.settings", _external=True)
        )
        return redirect(session.url)
    except Exception as e:
        flash(f"Error: {str(e)}", "error")
        return redirect(url_for("dashboard.index"))


@billing_bp.route("/webhook", methods=["POST"])
def webhook():
    """Handle Stripe webhooks."""
    payload = request.data
    sig_header = request.headers.get("Stripe-Signature")
    webhook_secret = current_app.config.get("STRIPE_WEBHOOK_SECRET")

    try:
        import stripe
        stripe.api_key = current_app.config["STRIPE_SECRET_KEY"]

        if webhook_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            event = json.loads(payload)

        _handle_webhook_event(event)
        return jsonify({"status": "ok"})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


def _handle_webhook_event(event):
    """Process Stripe webhook events."""
    from datetime import datetime

    event_type = event.get("type")
    data = event.get("data", {}).get("object", {})

    if event_type == "checkout.session.completed":
        user_id = data.get("metadata", {}).get("user_id")
        plan_name = data.get("metadata", {}).get("plan")
        if user_id:
            user = User.query.get(user_id)
            if user:
                user.plan = plan_name
                user.stripe_subscription_id = data.get("subscription")
                user.subscription_status = "active"
                db.session.commit()

    elif event_type == "customer.subscription.deleted":
        sub_id = data.get("id")
        user = User.query.filter_by(stripe_subscription_id=sub_id).first()
        if user:
            user.subscription_status = "cancelled"
            user.plan = "free"
            db.session.commit()

    elif event_type == "invoice.payment_failed":
        customer_id = data.get("customer")
        user = User.query.filter_by(stripe_customer_id=customer_id).first()
        if user:
            user.subscription_status = "past_due"
            db.session.commit()
