# 🏗 Project Architecture

## 🗂️ Project Structure

```
docuflex/
  |--- DocuFlex/        # Django core settings and URLs
  |--- common/          # Shared mixins, utils, context processors
  |--- clients/         # Manage corporate clients (with unique identifiers like company ID)
  |--- contracts/       # Manage loan contracts related to clients
  |--- loan_requests/   # Create and assign requests for drafting annexes tied to contracts
  |--- annexes/         # Generate annex files and track e-signature status
  |--- reports/         # Productivity analytics and document signing records
  |--- api/             # REST endpoints for asynchronous communication and integration
  |--- logs/            # System-wide logging of users actions
  |--- news/            # Internal announcements and notifications
  |--- users/           # Custom user model, registration, roles, and permissions
  |--- nomenclatures/	# Reference tables (currencies, annex types, etc.)
  |--- templates/       # HTML templates (Bootstrap 5)
  |--- static/          # CSS 

```
---



## 🔗 Model Relationships

Below is a simplified diagram showing the most important relationships between models:


Client  --->  Contract (FK: client)  --->   Request (FK: contract)  --->   GeneratedAnnex (FK: request) --->  SignStatus (signed, failed, pending)


### Entity-Relationship Overview

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

