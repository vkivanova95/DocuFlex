# 💡 Development Overview

## 🧩 Tech Highlights
- **Backend**: Django 5+, PostgreSQL.

- **Frontend**: Bootstrap 5 with custom styles.

- **Asynchronous Views**: `async def` for non-blocking API calls.

- **REST API**: Mock integration for annex signing.

- **File Handling**: Word generation with `python-docx`; Excel export with `openpyxl`.

- **Security**: Custom login, first-login password change, role-based access.

- **Testing**: Unit tests for role access, API endpoints, export functionality.

---

## 📦 Key Dependencies
The project relies on the following core libraries and tools:

- **Django** – the primary web framework used to structure the project and handle routing, ORM, and templating.

- **Django REST Framework (DRF)** – used for building RESTful API endpoints for integration with external systems.

- **Whitenoise** – enables serving static files (CSS, JS, images) directly from the application server in production.

- **Gunicorn** – a production-grade WSGI server used to run the Django app on Azure.

- **Psycopg2** – PostgreSQL database adapter for Django.

- **Python-Decouple** – manages environment variables and sensitive settings outside the codebase.

- **dj-database-url** – allows database configuration using a single URL.

- **Bootstrap 5** – used via CDN in templates for responsive and styled UI.

These dependencies are listed in the requirements.txt file and should be installed with:

```pip install -r requirements.txt```

---

## 🔌 REST & Asynchronous API Integration
`POST /api/send-annex/<id>/` – sends the annex to the signature API.

Simulated async result using Celery-style mock view.

Once signed, annex cannot be sent again.

---
## 🧪 Testing

Tests are located in each app’s `tests/` directory. To run the tests:

```python manage.py test```

The project includes **unit and integration tests**:

- Role-based access testing

- Model validation (e.g. inactive clients)

- API endpoint response

- Export functionality

- View permissions
