# 🗄️ Database Setup Instructions

This directory contains the MySQL database schema definitions and setup queries for the BloodBridge application.

## 📁 Files:
- **`schema.sql`**: Contains the complete database structure:
  - Database Creation (`bloodbridge` with `utf8mb4` character set)
  - All Tables (`user`, `donor`, `blood_request`, `campaign`, `campaign_registration`, `contact_message`, `newsletter_subscriber`)
  - Foreign Keys, Constraints, and Indexes
  - Sample testing queries & JOIN operations

---

## 🚀 How to Setup the Database:

### Option 1: Run via MySQL CLI / Terminal
```bash
mysql -u root -p < database/schema.sql
```

### Option 2: Run via MySQL Workbench / phpMyAdmin
1. Open MySQL Workbench or phpMyAdmin.
2. Open the file `database/schema.sql`.
3. Click the **Execute** button to run the script.

### Option 3: Automatic Setup via Python / Flask
If you prefer not to run the SQL script manually, the Flask application can automatically create all required tables upon starting the app or by running `scripts/init_db.py`:
```bash
python scripts/init_db.py
```
*(Ensure that your `DATABASE_URL` is configured in your `.env` file).*
