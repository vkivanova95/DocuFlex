# 📄 DocuFlex – Document Automation Platform

**DocuFlex** is an internal Django-based web application designed for automating the full workflow of documents generation, review, signing and archiving. Built for financial institutions, the platform supports modular document processing, role-based user access, audit trails, and integration with external services (e.g., e-signature API).

---


## 🚀 Key Features

* 🔐 Role-based Access Control (business users, executors/makers, managers, and admin).

* 👤 Client & Contract Management with activation/deactivation and validation rules.

* 🧾 Requests Workflow – creation, assignment, processing.

* 📄 Annex Generator – dynamically generates `.docx` annexes from input data using reusable templates and conditional sections.

* ✅ E-signature integration (mock asynchronous API).

* 🗂️ Annex Archive – filtering, search, pagination, and Excel export.

* 📊 Reports/ Log – track user productivity, document signing history, and system activity.

* 🛠️ Nomenclatures – centralized reference data.

* 💬 News modules – internal communication

---
## 🧩 Tech Highlights
- **Backend**: Django 5+, PostgreSQL.

- **Frontend**: Bootstrap 5 with custom styles.

- **Asynchronous Views**: `async def` for non-blocking API calls.

- **REST API**: Mock integration for annex signing.

- **File Handling**: Word generation with `python-docx`; Excel export with `openpyxl`.

- **Security**: Custom login, first-login password change, role-based access.

- **Testing**: Unit tests for role access, API endpoints, export functionality.

---

## 🗂️ Project Structure

```
docuflex/
  |--- DocuFlex/		    # Django core settings and URLs
  |--- common/              # Shared mixins, utils, context processors
  |--- clients/          	# Manage corporate clients (with unique identifiers like company ID)
  |--- contracts/           # Manage loan contracts related to clients
  |--- loan_requests/       # Create and assign requests for drafting annexes tied to contracts
  |--- annexes/             # Generate annex files and track e-signature status
  |--- reports/             # Productivity analytics and document signing records
  |--- api/ 			    # REST endpoints for asynchronous communication and integration
  |--- logs/			    # System-wide logging of users actions
  |--- news/			    # Internal announcements and notifications
  |--- users/               # Custom user model, registration, roles, and permissions
  |--- nomenclatures/		# Reference tables (currencies, annex types, etc.)
  |--- templates/           # HTML templates (Bootstrap 5)
  |--- static/              # CSS 

```
---

## 🔗 Model Relationships

Below is a simplified diagram showing the most important relationships between models:


Client  ───▶  Contract (FK: client)  ───▶  Request (FK: contract)  ───▶  GeneratedAnnex (FK: request) ───▶ SignStatus (signed, failed, pending)


### 🧩 Entity-Relationship Overview

* A Client can have multiple Contracts.

* A Contract can have multiple Requests.

* Each Request is linked to one GeneratedAnnex.

* Each GeneratedAnnex has a signature status and associated file.

* Users with role executor can be assigned to requests.

---
## ✅ Validations & Business Logic

| Validation / Rule        | Description        |
|-----------------|-----------------|
| Unique CompanyEIK	   | Company ID (EIK) must be unique and match Bulgarian format   |
| Request creation        | Only possible if client and contract are active   |
| Cascading deactivation  | If a client is deactivated, all contracts, requests, and annexes are automatically deactivated   |
| One-time signature      | Annexes can be sent for signing only once unless previous attempt failed   |
| Group-based access      | Only users in proper groups (business, executor, manager) can access certain views   |
| Logging   | Every user action (create/edit/assign) is logged with time, user, model, and action   |



---

## 🛡️ User Roles & Access Control
- **Business User (Бизнес)** – Submit requests and track status.
- **Executor (Изпълнител)** – View and handle assigned requests, generate annexes.
- **Supervisor (Ръководител)** – Assign requests to executors, manage users, view all productivity data.
- **Superuser (admin)** – Full access to all data, users, logs, and configurations.

Access is managed via custom middleware and group-based permissions, enforced both in views and templates.

---

## 📄 Example Workflow
1. **Business User** creates an annex request for a specific contract.

2. **Manager** assigns the request to an **Executor**.

3. **Executor** completes specific fields and generates the annex.

4. All signed annexes go into the **Archive/ Register**, where they are filterable and exportable.

5. Annex is **sent to mock API for signing** – only once if successful.

6. **System Logs** track every action.

7. **Productivity Reports** summarize request/annex volume per executor.

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

---

## ⚙️ Deployment Instructions
### 🧬 Environment Setup
```
git clone https://github.com/vkivanova95/docuflex.git
cd docuflex
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
By default, the server runs on http://127.0.0.1:8000/


### 🔑 Configure Environment variables (.env)
Create a `.env` file in the root of the project and include the following variables:


**a. Security & Debug**

```
SECRET_KEY=your-django-secret-key
DEBUG=True # or False in production
ALLOWED_HOSTS=127.0.0.1, localhost
```

**b. Database Configuration**

```
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=localhost
DB_PORT=5432
```

---

## ⚖️ MIT License
Copyright (c) 2025 Veska Ivanova

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE. 