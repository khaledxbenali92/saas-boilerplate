"""
Configuration — Development, Testing, Production
"""

import os
from datetime import timedelta


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Mail
    MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER", "noreply@yoursaas.com")

    # App Settings
    APP_NAME = os.getenv("APP_NAME", "SaaS Starter")
    APP_URL = os.getenv("APP_URL", "http://localhost:5000")

    # Stripe
    STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
    STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
    STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

    # Stripe Plans
    STRIPE_PLANS = {
        "starter": {
            "name": "Starter",
            "price_id": os.getenv("STRIPE_STARTER_PRICE_ID", ""),
            "price": 9,
            "features": ["5 projects", "10GB storage", "Email support"],
        },
        "pro": {
            "name": "Pro",
            "price_id": os.getenv("STRIPE_PRO_PRICE_ID", ""),
            "price": 29,
            "features": ["Unlimited projects", "100GB storage", "Priority support", "API access"],
        },
        "enterprise": {
            "name": "Enterprise",
            "price_id": os.getenv("STRIPE_ENTERPRISE_PRICE_ID", ""),
            "price": 99,
            "features": ["Everything in Pro", "Custom domain", "SSO", "Dedicated support"],
        },
    }

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-change-me")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Rate Limiting
    RATELIMIT_DEFAULT = "100 per hour"
    RATELIMIT_STORAGE_URL = "memory://"

    # Uploads
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = "uploads"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "sqlite:///saas_dev.db"
    )


class TestingConfig(BaseConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    MAIL_SUPPRESS_SEND = True
    STRIPE_SECRET_KEY = "sk_test_fake"


class ProductionConfig(BaseConfig):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///saas.db")


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
