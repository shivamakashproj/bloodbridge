# 🩸 BloodBridge — Healthcare & Blood Logistics Management System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0%2B-red.svg?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-orange.svg?logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**BloodBridge** is a modern, enterprise-ready blood donation and emergency matching platform. It bridges the critical time gap between emergency patients, voluntary donors, hospitals, and community camp organizers through strict role-based access control, real-time donor discovery, and verified administrative moderation.

---

## 📑 Table of Contents
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Role-Based Access Control (RBAC)](#-role-based-access-control-rbac)
- [Directory Structure](#-directory-structure)
- [Installation & Quickstart Guide](#-installation--quickstart-guide)
- [Database Setup & Admin Seeding](#-database-setup--admin-seeding)
- [Security & Validation Standards](#-security--validation-standards)
- [Application Endpoints & Routes](#-application-endpoints--routes)
- [System Documentation](#-system-documentation)
- [License](#-license)

---

## 🌟 Key Features

### 1. 🚪 3-Way Role Gateway
- **Donor / Citizen Portal (Customer):** Search verified donors, post emergency blood requirements, track requisition status, and sign up for local blood drives.
- **Camp Organizer Portal (Hoster):** Designed for universities, hospitals, corporate entities, and NGOs to register blood donation camps and track live attendee rosters.
- **Admin Control Center:** Super-admin dashboard to inspect, approve, reject, or fulfill blood requests and verify upcoming community camps.

### 2. ⚡ Real-Time Donor Discovery Engine
- Search verified voluntary donors filtered by **Blood Group** and **City**.
- Direct communication via **Click-to-Call** and **1-Click WhatsApp Chat**.
- Pure voluntary network with zero commercial intermediary charges.

### 3. 🚨 Emergency Blood Requisition Lifecycle
- Structured patient intake with hospital, units required, and attendant contact info.
- Full transparent state tracking: `Pending` 🟡 $\rightarrow$ `Approved` 🟢 $\rightarrow$ `Fulfilled` 🔵 / `Rejected` 🔴.

### 4. 🏥 Community Blood Drives & Attendee Rostering
- Organizations can schedule blood drives with full venue details and operating hours.
- Verified citizens can RSVP to drives with medical details.
- Hosts can monitor live attendance sheets to organize medical staff and collection kits.

### 5. 🏥 24x7 National Blood Bank Directory
- Curated directory of premier healthcare centers across India (AIIMS New Delhi, Red Cross Society, Tata Memorial Mumbai, Apollo Hospitals, Narayana Health, SMS Jaipur).
- Blood component inventory indicators (RBC, Platelets, Plasma, Cryoprecipitate) and direct Google Maps navigation.

---

## 🏗 System Architecture

The application is built on the **Model-View-Controller (MVC)** architectural pattern:

```
[ Client Browser / Mobile ]
            │ (HTTP Requests)
            ▼
┌──────────────────────────────────────┐
│       Flask Application Router       │
│      (Flask-Login, Session RBAC)     │
├──────────────────────────────────────┤
│           Business Logic             │
│ (Donor Engine, Campaigns, Emergency) │
├──────────────────────────────────────┤
│       SQLAlchemy ORM + PyMySQL       │
└──────────────────┬───────────────────┘
                   │ (Parameterized Queries)
                   ▼
┌──────────────────────────────────────┐
│          MySQL 8.0+ Database         │
└──────────────────────────────────────┘
```

---

## 👥 Role-Based Access Control (RBAC)

| Capability / Resource | Public / Guest | Customer (Donor / Recipient) | Hoster (Camp Organizer) | Administrator |
|:---|:---:|:---:|:---:|:---:|
| **Welcome Gateway & Directory** | ✅ | ✅ | ✅ | ✅ |
| **Search Donors & Blood Banks** | ✅ | ✅ | ✅ | ✅ |
| **Register as a Voluntary Donor** | ❌ (Login req.) | ✅ | ❌ | ✅ |
| **Submit Emergency Blood Request**| ❌ (Login req.) | ✅ | ❌ | ✅ |
| **Track Own Blood Requests** | ❌ | ✅ | ❌ | ✅ |
| **Host a Blood Donation Drive** | ❌ (Login req.) | ❌ | ✅ | ✅ |
| **View Drive Donor Roster** | ❌ | ❌ | ✅ (Own drives) | ✅ (All drives) |
| **Moderate Requests & Drives** | ❌ | ❌ | ❌ | ✅ |
| **Admin Control Center (`/admin`)**| ❌ | ❌ | ❌ | ✅ |

---

## 📁 Directory Structure

```
BloodBridge/
│
├── database/
│   └── schema.sql              # Clean DDL database blueprint (No seed passwords)
│
├── docs/
│   ├── project_documentation.md# Enterprise SRS & architecture specification
│   ├── tech_stack.md           # Technology stack & libraries reference
│   └── forgot_password.md      # Authentication recovery workflows
│
├── scripts/
│   ├── init_db.py              # Automated database table creation & admin seed
│   └── reset_db.py             # Database reset utility (uses .env credentials)
│
├── static/
│   ├── css/                    # Custom stylesheets and admin themes
│   └── js/                     # Client-side scripts and UX interactions
│
├── templates/
│   ├── admin/                  # Administrative moderation templates
│   ├── index.html              # Main showcase landing page
│   ├── login.html              # Role-aware authentication portal
│   └── ...                     # Feature-specific Jinja2 views
│
├── .env.example                # Clean environment variables blueprint (Safe for Git)
├── .gitignore                  # Production gitignore rules (Excludes .env & cache)
├── app.py                      # Application controller, routes & business logic
├── config.py                   # Environment configuration classes
├── models.py                   # SQLAlchemy data models & relationships
├── requirements.txt            # Python dependencies
├── schema.db                   # Backup SQL DDL schema
└── wsgi.py                     # Production WSGI entry point
```

---

## 🚀 Installation & Quickstart Guide

### Prerequisites
- **Python 3.11+** installed on your system
- **MySQL 8.0+** running locally or on a cloud provider (e.g. AWS RDS, Google Cloud SQL, XAMPP)
- **Git**

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/BloodBridge.git
cd BloodBridge
```

### 2. Create a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Required Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.example` to create your own local `.env` file:
```bash
# Windows (PowerShell)
Copy-Item .env.example .env

# Linux / macOS
cp .env.example .env
```

Open `.env` and set your local database connection and admin credentials:
```env
FLASK_ENV=development
SECRET_KEY=change-this-to-a-secure-random-key

# Database Connection URL (MySQL)
DATABASE_URL=mysql+pymysql://<db_user>:<db_password>@localhost:3306/bloodbridge

# Admin Setup (Optional - Used when running init_db.py)
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=your_secure_password
```

---

## 🗄 Database Setup & Admin Seeding

You can initialize the database tables and admin user in two ways:

### Option A: Using the Automated Python Script (Recommended)
Make sure your MySQL server is running and the database specified in `DATABASE_URL` exists, then run:
```bash
python scripts/init_db.py
```
This script will automatically create all tables and create an admin user using the credentials from your `.env` file.

### Option B: Using the SQL Schema File
You can import the clean table structure directly using MySQL CLI or MySQL Workbench:
```bash
mysql -u root -p < database/schema.sql
```

---

## 🏃 Running the Application

### Development Mode
```bash
python app.py
```
Open your browser and navigate to: **`http://127.0.0.1:5000`**

### Production WSGI Mode
```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

---

## 🛡 Security & Validation Standards

- **Zero Hardcoded Secrets:** No database passwords or administrative keys exist in the repository code or SQL files.
- **Password Protection:** Passwords are never stored in plaintext; hashed securely using `werkzeug.security` (`scrypt` / `pbkdf2:sha256`).
- **SQL Injection Prevention:** 100% parameterized queries via SQLAlchemy ORM.
- **Cross-Site Scripting (XSS) Mitigation:** Jinja2 auto-escapes all dynamic content.
- **Strict Server-Side Validation:** Validates email format (RFC 5322), 10-digit Indian phone numbers, and strong password constraints on every submission.

---

## 🌐 Application Endpoints & Routes

| Endpoint | Method | Access Level | Description |
|:---|:---:|:---:|:---|
| `/` or `/welcome` | `GET` | Public | 3-Way Role Entry Gateway |
| `/home` | `GET` | Public | Main landing page showcase |
| `/login` | `GET, POST` | Public | Unified role-specific login |
| `/register` | `GET, POST` | Public | Account creation (Customer or Hoster) |
| `/logout` | `GET` | Authenticated | Terminate user session |
| `/find_donor` | `GET, POST` | Public | Search donors by blood group & city |
| `/become_donor` | `GET, POST` | Customer | Register as a voluntary blood donor |
| `/request_blood`| `GET, POST` | Customer | Submit emergency blood requisition |
| `/my_requests` | `GET` | Customer | Track real-time status of blood requests |
| `/host_drive` | `GET, POST` | Hoster | Propose a new blood donation camp |
| `/my_campaigns`| `GET` | Hoster | Manage submitted camps & view registrations |
| `/campaign/<id>/registrations` | `GET` | Host / Admin | View attendee roster for a camp |
| `/blood_banks` | `GET` | Public | National directory of certified blood centers |
| `/profile` | `GET` | Authenticated | User account dashboard & donor pass |
| `/admin` | `GET` | Admin | Administrative moderation control center |

---

## 📄 License
This project is open-source and distributed under the [MIT License](LICENSE).
