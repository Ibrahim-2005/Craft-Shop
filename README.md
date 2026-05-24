# Curated by Afza

A premium full-stack Flask website for a handmade gifting studio: customized bouquets, gift hampers, pipe cleaner florals, keychains, surprise gifts, testimonials, custom order inquiries, admin management, PostgreSQL storage, and profit analytics.

## Features

- Public pages: home, shop, product detail, about, contact, custom order request, testimonials
- Admin pages: dashboard, products, categories, orders, testimonials, settings, analytics
- Secure admin login with hashed passwords and Flask-Login
- CSRF-protected forms with Flask-WTF validation
- UUID media uploads to `app/static/uploads`
- PostgreSQL via Flask-SQLAlchemy
- Profit tracking per order using raw material cost rows
- Revenue, expense, profit, cancelled-order exclusion, monthly chart, and category analytics
- Responsive premium UI with glassmorphism, animations, floating WhatsApp button, and Chart.js

## Local Setup

The default local setup uses SQLite so you can run the project immediately.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python seed.py
python run.py
```

Open `http://127.0.0.1:5000`.


## Optional PostgreSQL Setup

For a local PostgreSQL setup, install PostgreSQL first, then create a database named `gift_studio`.

If you use pgAdmin, create a new database:

```text
gift_studio
```

If you use `psql`, run:

```sql
CREATE DATABASE gift_studio;
```

Then update `.env` and replace `your_password` with your local PostgreSQL password:

```text
DATABASE_URL=postgresql+psycopg2://postgres:your_password@localhost:5432/gift_studio
```

## Deployment On Render

This folder is ready for Render Blueprint deployment through `render.yaml`.

1. Push the project to GitHub.
2. In Render, choose **New > Blueprint** and select the repository.
3. Render will create the Python web service and PostgreSQL database.
4. On every deploy/start, `python seed.py && gunicorn wsgi:app` creates missing tables and upserts the owner account plus starter content.
5. After the first login, change the demo admin password from **Admin > Accounts**.

## Architecture

```text
app/
  routes/       Public, auth, and admin blueprints
  models/       SQLAlchemy models for products, media, orders, categories, admins, reviews, settings
  services/     Analytics, uploads, and profit calculations
  forms/        Flask-WTF forms
  templates/    Jinja public/admin/auth templates
  static/       CSS, JavaScript, uploads, images
  utils/        Small helpers such as slug generation
```

## Profit Tracking

For each order, the admin can enter raw material rows such as:

- Rose flowers: Rs. 300
- Wrapper paper: Rs. 80
- Ribbon: Rs. 40
- Lights: Rs. 100

The system calculates total expense, selling price, profit, and margin automatically. Cancelled orders remain in history but do not count toward revenue, expense, profit, or monthly performance charts.
