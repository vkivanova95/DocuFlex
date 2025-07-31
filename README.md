# 📄 DocuFlex – Document Automation Platform

**DocuFlex** is an internal Django-based web application designed for automating the full workflow of documents generation, review, signing and archiving. Built for financial institutions, the platform supports modular document processing, role-based user access, audit trails, and integration with external services (e.g., e-signature API).

> This project was developed as part of a course final exam and is intended for demonstration and evaluation purposes.

 🔗 **Live Demo**: [https://docuflex-a5c5ejdcgzhtgzht.italynorth-01.azurewebsites.net](https://docuflex-a5c5ejdcgzhtgzht.italynorth-01.azurewebsites.net)

🔐 **Test users** are available – see [Deployment & Local Setup](docs/DEPLOYMENT_AND_ACCESS.md#test-users) for credentials and roles.

---


## 🚀 Key Features

* **Role-based Access Control** (business users, executors/makers, managers, and admin).

* **Client & Contract Management** with activation/deactivation and validation rules.

* **Requests Workflow** – creation, assignment, processing.

* **Annex Generator** – dynamically generates `.docx` annexes from input data using reusable templates and conditional sections.

* **E-signature integration** (mock asynchronous API).

* **Annex Archive** – filtering, search, pagination, and Excel export.

* **Reports/ Log** – track user productivity, document signing history, and system activity.

* **Nomenclatures** – centralized reference data.

* **News modules** – internal communication
---

## 🧾 Additional Documentation

🏗 [Project Architecture](docs/ARCHITECTURE.md)  
  Folder structure, data models, relationships, and validation logic.

👥 [User Journey](docs/USER_FLOW.md)  
  Role-based access and example usage scenarios.

💡 [Development Overview](docs/DEVELOPMENT_OVERVIEW.md)  
Frameworks used, key dependencies, API integrations, and testing instructions.

 🌐 [Deployment & Local Setup](docs/DEPLOYMENT_AND_ACCESS.md)  
  Setup instructions for local development and Azure deployment, plus available test users.

⚖️ Licence

This project is licensed under the MIT License. See the [Licence](docs/LICENSE.md) file for details.

---