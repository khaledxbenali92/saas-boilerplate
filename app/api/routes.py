"""
REST API Routes — JWT Auth + Rate Limiting
"""

from functools import wraps
from flask import Blueprint, jsonify, request, current_app
from flask_login import current_user, login_required
from app import db
from app.models.user import User, APIKey

api_bp = Blueprint("api", __name__)


# ── API Key Auth Decorator ─────────────────────────────────
def api_key_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get("X-API-Key") or request.args.get("api_key")
        if not api_key:
            return jsonify({"error": "API key required", "code": "MISSING_API_KEY"}), 401

        key_obj = APIKey.query.filter_by(key=api_key, is_active=True).first()
        if not key_obj:
            return jsonify({"error": "Invalid API key", "code": "INVALID_API_KEY"}), 401

        from datetime import datetime
        key_obj.last_used_at = datetime.utcnow()
        key_obj.calls_count += 1
        db.session.commit()

        request.api_user = key_obj.user
        return f(*args, **kwargs)
    return decorated


# ── Auth Endpoints ─────────────────────────────────────────
@api_bp.route("/auth/register", methods=["POST"])
def api_register():
    from app.auth.routes import register
    return register()


@api_bp.route("/auth/login", methods=["POST"])
def api_login():
    from app.auth.routes import login
    return login()


# ── User Endpoints ─────────────────────────────────────────
@api_bp.route("/me", methods=["GET"])
@api_key_required
def get_me():
    return jsonify({"success": True, "user": request.api_user.to_dict()})


@api_bp.route("/me", methods=["PATCH"])
@api_key_required
def update_me():
    data = request.get_json()
    user = request.api_user

    if "name" in data:
        user.name = data["name"].strip()

    db.session.commit()
    return jsonify({"success": True, "user": user.to_dict()})


# ── API Keys Endpoints ─────────────────────────────────────
@api_bp.route("/keys", methods=["GET"])
@login_required
def list_keys():
    keys = APIKey.query.filter_by(user_id=current_user.id).all()
    return jsonify({
        "success": True,
        "keys": [{
            "id": k.id,
            "name": k.name,
            "key": k.key[:8] + "..." + k.key[-4:],
            "is_active": k.is_active,
            "calls_count": k.calls_count,
            "last_used": k.last_used_at.isoformat() if k.last_used_at else None,
            "created_at": k.created_at.isoformat()
        } for k in keys]
    })


@api_bp.route("/keys", methods=["POST"])
@login_required
def create_key():
    data = request.get_json() or {}
    name = data.get("name", "API Key")

    key = APIKey.generate(user_id=current_user.id, name=name)
    db.session.add(key)
    db.session.commit()

    return jsonify({
        "success": True,
        "key": key.key,
        "name": key.name,
        "message": "Save this key — it won't be shown again!"
    }), 201


@api_bp.route("/keys/<int:key_id>", methods=["DELETE"])
@login_required
def delete_key(key_id):
    key = APIKey.query.filter_by(id=key_id, user_id=current_user.id).first_or_404()
    db.session.delete(key)
    db.session.commit()
    return jsonify({"success": True, "message": "API key deleted"})


# ── Health Check ───────────────────────────────────────────
@api_bp.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0",
        "app": current_app.config["APP_NAME"]
    })


# ── Subscription Status ────────────────────────────────────
@api_bp.route("/subscription", methods=["GET"])
@api_key_required
def get_subscription():
    user = request.api_user
    return jsonify({
        "success": True,
        "plan": user.plan,
        "status": user.subscription_status,
        "is_subscribed": user.is_subscribed,
    })
