# BloodBridge — Technology Stack & Tooling Architecture

---

## 1. Overview & Stack Summary

| Dimension | Primary Technology | Version / Standard | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Core** | Python / Flask | Python 3.10+ / Flask 3.0+ | Server-side Application Engine & Routing |
| **Database Engine** | MySQL Server / MariaDB | MySQL 8.0.x / MariaDB 10.4+ | Relational Data Storage & ACID Transactions |
| **Database Driver & ORM**| PyMySQL & Flask-SQLAlchemy | PyMySQL 1.1+ / SQLAlchemy 2.0+ | Python-to-MySQL Connectivity & Object Mapping |
| **Authentication & Auth**| Flask-Login & Werkzeug | Flask-Login 0.6+ / Werkzeug 3.0+ | Session Management, PBKDF2 Password Hashing |
| **Administration Portal**| Flask-Admin | Flask-Admin 1.6+ | Declarative CRUD Management Interface |
| **Frontend Framework** | Bootstrap | Bootstrap 5.3.2 | Responsive Grid, UI Modals, Glassmorphism Cards |
| **Iconography** | FontAwesome | FontAwesome 6.4.0 (CDN) | Medical, User, Status & Navigational Icons |
| **Typography** | Google Fonts (Inter) | Inter (300, 400, 500, 600, 700, 800) | Enterprise-grade Crisp Typography |
| **Form & Input Validation**| Python `re` / HTML5 Pattern | RFC 5322 & E.164 Standards | Zero-Bypass Server-Side & Client-Side Regex |

---

## 2. Frontend Technologies & Languages

### Languages & Markup
- **HTML5 (Jinja2 Template Engine):**
  - Modular template inheritance (`base.html`, `welcome.html`, `index.html`, etc.).
  - Dynamic template context injection for session user, flash alerts, and query datasets.
- **CSS3 / Modern Styling:**
  - Custom Design System implemented in `static/css/style.css`.
  - CSS Custom Properties (Variables) for consistent thematic blood-red gradients, glassmorphism (`backdrop-filter: blur()`), glowing borders, and floating emergency cards.
  - Media queries for 100% responsiveness across mobile (360px+), tablet, and 4K desktop screens.
- **Vanilla JavaScript (ES6+):**
  - Minimalistic, progressive-enhancement scripts for interactive live filtering, client-side pre-submit regex checks, and dynamic form helper toggles.
  - Zero heavy frontend framework dependencies (e.g., React/Vue) to ensure instantaneous server-side page loads and optimal SEO.

### Libraries & CDNs
- **Bootstrap 5.3.2 (CSS & Bundle JS):** Responsive layout grid, navbar collapse, modal dialogs, and alert dismissal.
- **FontAwesome 6.4.0:** Comprehensive visual icon set for medical indicators, blood bags, status badges, and action buttons.

---

## 3. Backend Technologies & Frameworks

### Language & Runtime
- **Python 3.10+ / 3.11+ / 3.12+**
  - High-performance, clean Python code adhering to PEP 8 standards.

### Core Frameworks & Python Libraries
- **Flask (v3.0.x):** Micro-framework providing the routing engine, request handling, error interception, template rendering, and HTTP request context.
- **Flask-SQLAlchemy (v3.1.x):** High-level ORM translating Python class models directly into optimized MySQL SQL queries.
- **Flask-Login (v0.6.x):** Manages user session state, `current_user` context, login/logout lifecycles, and `@login_required` decorators.
- **Flask-Admin (v1.6.x):** Provides out-of-the-box administrative views with model inspection, search filtering, and record management for administrators.
- **Werkzeug Security:** Secure password hashing utilizing PBKDF2/Scrypt algorithms with random cryptographic salts to prevent rainbow-table exploits.
- **PyMySQL (v1.1.x):** Pure-Python MySQL client library allowing asynchronous connection pooling and seamless dialect translation for SQLAlchemy.

---

## 4. Database & Storage Architecture

### Database Engine
- **MySQL Community Server 8.0+**
  - **Storage Engine:** `InnoDB` (ACID compliance, Row-level locking, Foreign Key constraints with `ON DELETE SET NULL / CASCADE`).
  - **Character Set:** `utf8mb4` (Full Unicode support including multilingual text and emojis).
  - **Collation:** `utf8mb4_unicode_ci` (Case-insensitive, accent-accurate comparisons).

### Connection Configuration
- Connected via SQLAlchemy connection string:
  ```
  mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>?charset=utf8mb4
  ```
- Handles URL-encoded special characters (e.g. `@` mapped to `%40`) securely within `app.py`.

---

## 5. Security, Regex & Validation Suite

### Regex Specifications
1. **Email Validation:**
   ```regex
   ^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$
   ```
   Ensures strict adherence to RFC standard email syntax.
2. **Phone Number Validation (Indian Mobile Format):**
   ```regex
   ^[6-9]\d{9}$
   ```
   Validates standard 10-digit mobile numbers starting with 6, 7, 8, or 9.
3. **Password Security Policy:**
   ```regex
   ^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$
   ```
   Requires minimum 8 characters, at least 1 uppercase letter, 1 lowercase letter, 1 number, and 1 special symbol.

---

## 6. Development Tools & Runtime Environment

| Tool / Service | Application |
| :--- | :--- |
| **IDE / Editor** | Antigravity AI IDE / VS Code |
| **Command Shell** | Windows PowerShell / Bash |
| **Database Management** | MySQL Workbench / phpMyAdmin / CLI |
| **Version Control** | Git & GitHub |
| **HTTP Client Testing** | Postman / cURL / Browser DevTools |
| **Process Management** | Python `app.py` / Gunicorn (Production Ready) |

---

## 7. Python Dependencies (`requirements.txt`)

```txt
Flask>=3.0.0
Flask-SQLAlchemy>=3.1.1
Flask-Login>=0.6.3
Flask-Admin>=1.6.1
PyMySQL>=1.1.0
cryptography>=41.0.0
Werkzeug>=3.0.1
```
