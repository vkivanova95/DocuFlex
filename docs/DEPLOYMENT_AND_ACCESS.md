# ⚙️ Deployment & Local Setup

## 🧬 Local Development Setup

### **Environment Setup**
```
git clone https://github.com/vkivanova95/docuflex.git
cd docuflex
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```
By default, the server runs on http://127.0.0.1:8000/


### **Configure Environment variables (.env)**

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

## ☁️ Azure Deployment (Production)

This application is deployed on Azure App Service and includes pre-created test accounts for demonstration.

The following information applies to the deployed version of the application hosted on Azure App Service.

### **User Roles and Access**

The application uses role-based access control via Django Groups:

| Role (Group)    | Access Permissions                                                             |
|-----------------|--------------------------------------------------------------------------------|
| Business        | Create and manage clients, contracts, and loan requests                        |
| Executor        | Process assigned loan requests and generate annex documents                    |
| Supervisor      | Assign requests, access reports and logs, manage the internal Admin Module (users, nomenclatures, logs, news) — *no access to Django Admin*                          |
| Director  | Full access to all application modules (combines Business, Executor, Supervisor) — *no access to Django Admin*              |
| Admin (superuser) | Full access, including Django Admin for managing users, master data, and configuration |



### **Test User Credentials**

| Role        | Username     | Password    |
|-------------|--------------|-------------|
| Business    | `business1`  | `zz123456`  |
| Executor    | `maker1`     | `zz123456`  |
| Supervisor  | `manager1`   | `zz123456`  |
| Director    | `admin`      | `zz123456`  |


### **Application URL**

[https://docuflex-a5c5ejdcgzhtgzht.italynorth-01.azurewebsites.net](https://docuflex-a5c5ejdcgzhtgzht.italynorth-01.azurewebsites.net)

The home page `/` is public and displays a brief system description and recent news.

All other modules (clients, contracts, requests, etc.) require login with an appropriate role-based user. 

 > 💡 **Navigation Tip:** The **“DocuFlex”** text next to the bank logo in the top-left corner is clickable and will take you back to the homepage at any time.
 > 