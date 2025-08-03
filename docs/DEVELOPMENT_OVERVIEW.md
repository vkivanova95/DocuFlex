# 💡 Development Overview

## 🧩 Tech Highlights
- **Backend**: Django 5+, PostgreSQL.
- **Frontend**: Bootstrap 5 with custom styles.
- **Asynchronous Views**: `async def` views for non-blocking processing.
- **Annex Signing Simulation**: Django REST mock API used for local testing; replaced by local function in production.
- **File Handling**: Word generation with `python-docx`; Excel export with `openpyxl`.
- **Security**: Custom login, first-login password change, role-based access.
- **Testing**: Unit tests for role access, mock signing, and export functionality.

---

## 📦 Key Dependencies
The project relies on the following core libraries and tools:

- **Django** – the primary web framework used to structure the project and handle routing, ORM, and templating.
- **Django REST Framework (DRF)** – used for building mock API endpoints during local development.
- **Whitenoise** – enables serving static files (CSS, JS, images) directly from the application server in production.
- **Gunicorn** – a production-grade WSGI server used to run the Django app on Azure.
- **Psycopg2** – PostgreSQL database adapter for Django.
- **Python-Decouple** – manages environment variables and sensitive settings outside the codebase.
- **dj-database-url** – allows database configuration using a single URL.
- **Bootstrap 5** – used via CDN in templates for responsive and styled UI.

These dependencies are listed in the requirements.txt file and should be installed with:

```pip install -r requirements.txt```

---

## 🔌 Annex Signing Logic
Due to connection limitations in Azure App Service, the project does not rely on REST API calls for annex signing in production.

**Production Approach:**

A local Python function (mock_sign_annex) is used to simulate signing (success/failure).

This approach ensures compatibility with Azure, which may drop internal requests to mock REST endpoints.

**Local Development:**

Django REST Framework can still be used to expose a /api/mock-sign/ endpoint for testing async integration and client behavior.

---
## 🧪 Testing

Tests are located in each app’s `tests/` directory. To run the tests:

```python manage.py test```

The project includes a mix of **unit and integration tests**, covering:

- **Role-based access control** – verifies that users in different groups can or cannot access specific views (e.g. restricted nomenclature pages result in redirect).
- **Model validation** – checks behavior with edge cases such as inactive clients or invalid data inputs.
- **Annex generation logic** – simulates full annex creation via form wizard steps and ensures that annexes and logs are correctly created.
- **Mock signing workflow** – tests the internal mock function (mock_sign_annex) used in production instead of an external REST API.
- **View permissions and redirects** – confirms correct behavior when unauthorized users are redirected (HTTP 302) or denied access.
- **Export functionality** – validates Excel/Word file generation and download behavior.
