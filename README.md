<div align="center">

# 🚀 SaaS Boilerplate Starter

### Production-ready SaaS foundation — Auth + Billing + Dashboard + REST API

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-000000?style=for-the-badge&logo=flask&logoColor=white)](https://flask.palletsprojects.com)
[![Stripe](https://img.shields.io/badge/Stripe-Ready-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://stripe.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Stars](https://img.shields.io/github/stars/khaledxbenali92/saas-boilerplate?style=for-the-badge&color=yellow)](https://github.com/khaledxbenali92/saas-boilerplate/stargazers)
[![CI](https://img.shields.io/github/actions/workflow/status/khaledxbenali92/saas-boilerplate/ci.yml?style=for-the-badge&label=CI)](https://github.com/khaledxbenali92/saas-boilerplate/actions)

[Features](#-features) • [Quick Start](#-quick-start) • [Structure](#-structure) • [Deploy](#-deploy) • [Contributing](#-contributing)

</div>

---

## ⏱️ Save Weeks of Setup Time

Every SaaS product needs the same foundation:
- User registration & authentication
- Email verification & password reset
- Subscription billing with Stripe
- REST API with key management
- Admin dashboard

**SaaS Boilerplate Starter** gives you all of this, production-ready, in minutes.

---

## ✨ Features

| Module | Features |
|--------|---------|
| 🔐 **Authentication** | Register, Login, Logout, OAuth-ready |
| 📧 **Email** | Verification, Password Reset, HTML templates |
| 💳 **Billing** | Stripe Checkout, Webhooks, Customer Portal |
| 📊 **Dashboard** | User dashboard, Settings, Billing management |
| 🔌 **REST API** | API key auth, Rate limiting, CRUD endpoints |
| 🗄️ **Database** | SQLAlchemy ORM, Migrations with Flask-Migrate |
| 🛡️ **Security** | CSRF, Password hashing, Token-based auth |
| 🎨 **UI** | Clean dashboard interface |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/khaledxbenali92/saas-boilerplate.git
cd saas-boilerplate
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Run

```bash
python run.py
```

Open: **http://localhost:5000** 🎉

---

## 📁 Structure

```
saas-boilerplate/
├── run.py                        # Entry point
├── app/
│   ├── __init__.py               # App factory
│   ├── config.py                 # Config (dev/test/prod)
│   ├── main.py                   # Landing page
│   ├── auth/
│   │   └── routes.py             # Register, Login, Reset
│   ├── billing/
│   │   └── routes.py             # Stripe Checkout + Webhooks
│   ├── dashboard/
│   │   └── routes.py             # User dashboard
│   ├── api/
│   │   └── routes.py             # REST API + API Keys
│   ├── models/
│   │   └── user.py               # User + APIKey models
│   └── utils/
│       └── email.py              # Email utilities
├── frontend/
│   └── pages/                    # HTML templates
├── tests/
│   └── test_app.py               # 12 tests
├── .github/workflows/ci.yml
├── requirements.txt
├── .env.example
└── LICENSE
```

---

## 🔌 REST API

```bash
# Health check
curl http://localhost:5000/api/v1/health

# Register
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","name":"John","password":"pass1234"}'

# Get current user
curl http://localhost:5000/api/v1/me \
  -H "X-API-Key: your-api-key"

# Create API key
curl -X POST http://localhost:5000/api/v1/keys \
  -H "Content-Type: application/json" \
  -d '{"name":"Production Key"}'
```

---

## 💳 Stripe Setup

1. Create a Stripe account at [stripe.com](https://stripe.com)
2. Create products and prices in Stripe Dashboard
3. Add price IDs to `.env`:

```env
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_STARTER_PRICE_ID=price_...
STRIPE_PRO_PRICE_ID=price_...
```

4. Set up webhook endpoint: `https://yourdomain.com/billing/webhook`

---

## 🚀 Deploy

### Railway (Recommended)

```bash
npm install -g @railway/cli
railway login && railway init && railway up
```

### Heroku

```bash
heroku create my-saas
heroku config:set SECRET_KEY=xxx APP_NAME="My SaaS"
git push heroku main
```

### Docker

```bash
docker build -t saas-boilerplate .
docker run -p 5000:5000 --env-file .env saas-boilerplate
```

---

## 🗺️ Roadmap

- [x] User authentication (register/login/logout)
- [x] Email verification & password reset
- [x] Stripe billing integration
- [x] REST API with API key auth
- [x] User dashboard
- [x] Database migrations
- [ ] OAuth (Google, GitHub)
- [ ] Admin panel
- [ ] Team/Organization support
- [ ] Usage-based billing
- [ ] Next.js frontend version
- [ ] Docker compose setup

---

## 🤝 Contributing

```bash
git clone https://github.com/YOUR-USERNAME/saas-boilerplate.git
cd saas-boilerplate
git checkout -b feat/your-feature
pytest tests/ -v
git commit -m "feat: your feature"
git push origin feat/your-feature
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Khaled Ben Ali**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/benalikhaled)
[![Twitter](https://img.shields.io/badge/Twitter-Follow-1DA1F2?style=flat&logo=twitter)](https://twitter.com/khaledbali92)
[![GitHub](https://img.shields.io/badge/GitHub-Follow-333?style=flat&logo=github)](https://github.com/khaledxbenali92)

---

<div align="center">

⭐ **Star this to save weeks on your next SaaS project!** ⭐

</div>
