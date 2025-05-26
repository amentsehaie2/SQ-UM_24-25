## Detailed Weekly Schedule for Assignment Completion (22 May 2025 – 16 June 2025)

*   **Team Size:** 3 Students
*   **Final Submission Deadline:** 20 June 2025
*   **Target Completion Date:** 16 June 2025 (4 days buffer for final fixes)

## Week 1 (26 May – 1 June): Setup & Core Components

*   **Goal:** Database setup, user authentication, and role-based access control.

### Student A: User Authentication & Authorization

*   **Tasks:**
    *   Implement the hard-coded Super Admin (`super_admin:Admin_123?`).
    *   Design user roles (Super Admin, System Admin, Service Engineer) with RBAC.
    *   Create password hashing using `bcrypt` or `hashlib` (SHA-256 with salt).
    *   Validate username/password rules (e.g., length, special characters).
    *   Implement login/logout functionality.
*   **GitHub Workflow:**
    *   Create `auth.py` module.
    *   Branch: `feature/auth`.

### Student B: Database Design & Encryption

*   **Tasks:**
    *   Design SQLite3 tables:
        *   `users` (`username`, `hashed_password`, `role`, `first_name`, `last_name`, `registration_date`).
        *   `travellers` (`customer_id`, `first_name`, `last_name`, encrypted fields like `zip_code`, `mobile_phone`).
        *   `scooters` (`serial_number`, `brand`, `model`, editable attributes per role).
        *   `logs` (encrypted activity logs with "suspicious" flag).
    *   Implement AES encryption for sensitive traveller/scooter data (e.g., zip code, phone).
*   **GitHub Workflow:**
    *   Create `database.py` and `models.py`.
    *   Branch: `feature/database`.

### Student C: Input Validation & Base Console Interface

*   **Tasks:**
    *   Create input validation functions:
        *   Validate formats (e.g., `DDDDXX` zip code, `+31-6-DDDDDDDDD` phone).
        *   Prevent SQL injection using parameterized queries.
    *   Design the console menu structure (role-specific menus).
    *   Implement helper functions for printing menus and handling user input.
*   **GitHub Workflow:**
    *   Create `validation.py` and `interface.py`.
    *   Branch: `feature/validation`.

## Week 2 (2 June – 8 June): Feature Implementation

*   **Goal:** Implement core functionalities for each user role.

### Student A: User Management & Backups

*   **Tasks:**
    *   Super Admin: Add/delete System Admins, generate restore codes.
    *   System Admin: Add/delete Service Engineers, reset passwords.
    *   Backup/restore logic (zip files with encrypted DB).
*   **GitHub Workflow:**
    *   Update `auth.py` and `database.py`.
    *   Branch: `feature/user-management`.

### Student B: Logging & Security

*   **Tasks:**
    *   Log all activities (e.g., login attempts, user creation).
    *   Flag suspicious activities (e.g., 3+ failed logins).
    *   Encrypt log files (AES) and ensure they’re unreadable externally.
*   **GitHub Workflow:**
    *   Create `logger.py`.
    *   Branch: `feature/logging`.

### Student C: Traveller/Scooter Management

*   **Tasks:**
    *   System Admin: CRUD operations for travellers/scooters.
    *   Service Engineer: Update scooter attributes (e.g., SoC, location).
    *   Search functionality with partial keys (e.g., "mik" for "Mike").
*   **GitHub Workflow:**
    *   Create `operations.py`.
    *   Branch: `feature/operations`.

## Week 3 (9 June – 15 June): Integration & Testing

*   **Goal:** Merge all components, test security, and fix bugs.

### All Students

*   **Tasks:**
    *   Merge branches into `main` and resolve conflicts.
    *   Test edge cases:
        *   SQL injection in search fields.
        *   Role escalation attempts (e.g., Service Engineer deleting scooters).
        *   Backup restoration with one-time codes.
    *   Ensure encrypted data cannot be read via external tools (e.g., DB Browser for SQLite).
*   **GitHub Workflow:**
    *   Create `test_cases.md` for manual testing.
    *   Use GitHub Issues to track bugs.

## Week 4 (16 June): Final Review & Presentation Prep

*   **Goal:** Dry-run presentation and final fixes.

### All Students

*   **Tasks:**
    *   Rehearse demonstrating:
        *   Super Admin creating a System Admin.
        *   Service Engineer updating scooter battery status.
        *   Logging of a suspicious login attempt.
    *   Verify all grading criteria (C1-C6) are met.
    *   Submit final zip file to GitHub.

## Step-by-Step Tutorial for Each Week

### Week 1 Tutorial

*   **Student A:**
    *   Use `sqlite3` to create a `users` table.
    *   Hash passwords with `bcrypt.gensalt()` and `bcrypt.hashpw()`.
    *   **Example code:**

    ```python
    import bcrypt
    hashed_pw = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    ```

*   **Student B:**
    *   Use `sqlcipher3` for encrypted SQLite (or encrypt fields with Python’s `cryptography`).
    *   **Example AES encryption:**

    ```python
    from cryptography.fernet import Fernet
    cipher = Fernet.generate_key()
    encrypted_data = Fernet(cipher).encrypt(data.encode())
    ```

*   **Student C:**
    *   Use regex to validate inputs (e.g., `re.match(r"^\d{4}[A-Z]{2}$", zip_code)`).
    *   **Example menu:**

    ```python
    print("1. Register Traveller\n2. Update Scooter\n3. Exit")
    choice = input("Enter choice: ")
    ```

### Week 2 Tutorial

*   **Student A:**
    *   Implement backup using `shutil.make_archive()`.
    *   Restore code logic: Generate a UUID and link it to a backup file.

*   **Student B:**
    *   Log activities with timestamps:

    ```python
    log_entry = f"{datetime.now()}, {username}, {activity}, {suspicious_flag}"
    ```

*   **Student C:**
    *   Use SQL parameterization for search:

    ```python
    cursor.execute("SELECT * FROM travellers WHERE first_name LIKE ?", (f"%{partial}%",))
    ```

### Week 3 Tutorial

*   Test SQL injection by inputting `' OR 1=1;--` in login fields.
*   Verify password reset requires Super Admin privileges.

### Week 4 Tutorial

*   Prepare a script for the presentation:

    1.  Login as Super Admin → Create System Admin → Logout.
    2.  Login as System Admin → Add Traveller → Backup DB.
    3.  Login as Service Engineer → Update Scooter → Check logs.

## Final Notes:

*   Use GitHub Projects for task tracking.
*   Conduct daily standups to sync progress.
*   Test on both Windows and macOS to ensure compatibility.

## ----------------------------------------------------------------------------------------------------------------------

# Project Overview

This document outlines the tasks and responsibilities for each student in this project, spanning across four weeks.

## Student A: User Authentication & Authorization

**Tasks:**

*   **Implement Hard-Coded Super Admin**
    *   Create a Python file `auth.py`.
    *   Define the Super Admin credentials (username: `super_admin`, password: `Admin_123?`).

    ```python
    # auth.py
    SUPER_ADMIN = {"username": "super_admin", "password": "Admin_123?"}
    ```

*   **Design User Roles & Password Hashing**
    *   Use `bcrypt` for password hashing.

    ```python
    import bcrypt
    def hash_password(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt)
    ```
    *   Create a `users` table in SQLite3 with fields: `username`, `hashed_password`, `role`, `first_name`, `last_name`, `registration_date`.

*   **Login/Logout Functionality**
    *   Validate username/password rules (e.g., length, special characters).

**GitHub:**

*   **Branch:** `feature/auth`
*   **Files:** `auth.py`, `database.py` (shared with Student B).

## Student B: Database Design & Encryption

**Tasks:**

*   **Create SQLite Tables**
    *   Design tables for `users`, `travellers`, `scooters`, and `logs`.
    *   Example for `travellers`:

    ```sql
    CREATE TABLE travellers (
        customer_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        zip_code TEXT ENCRYPTED,  -- Encrypt using AES
        mobile_phone TEXT ENCRYPTED
    );
    ```

*   **Implement AES Encryption**
    *   Use `cryptography.fernet` for field-level encryption.

    ```python
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted_zip = cipher.encrypt(zip_code.encode())
    ```

**GitHub:**

*   **Branch:** `feature/database`
*   **Files:** `database.py`, `models.py` (shared with Student A).

## Student C: Input Validation & Base Interface

**Tasks:**

*   **Input Validation Functions**
    *   Create `validation.py` with regex checks for formats (e.g., zip code: `DDDDXX`).

    ```python
    import re
    def validate_zip(zip_code):
        return re.match(r"^\d{4}[A-Z]{2}$", zip_code)
    ```

*   **Console Menu Structure**
    *   Create `interface.py` with role-specific menus.

    ```python
    def super_admin_menu():
        print("1. Add System Admin\n2. Generate Restore Code\n3. Exit")
    ```

**GitHub:**

*   **Branch:** `feature/validation`
*   **Files:** `validation.py`, `interface.py`.

## Week 2 (2 June – 8 June): Feature Implementation

**Goal:** User management, logging, and traveller/scooter operations.

### Student A: User Management & Backups

**Tasks:**

*   **Super Admin Functions**
    *   Add/delete System Admins (store in `users` table).
    *   Generate one-time restore codes (use UUID).

*   **Backup Logic**
    *   Use `shutil` to zip the encrypted database.

    ```python
    import shutil
    shutil.make_archive("backup_20250602", "zip", "database/")
    ```

**GitHub:**

*   **Branch:** `feature/user-management`
*   **Files:** Update `auth.py` and `database.py`.

### Student B: Logging & Security

**Tasks:**

*   **Activity Logging**
    *   Create `logger.py` to log actions (e.g., logins, user creation).
    *   Flag suspicious activities (e.g., 3+ failed logins).

*   **Encrypt Log Files**
    *   Use AES to encrypt logs. Ensure they’re unreadable externally.

**GitHub:**

*   **Branch:** `feature/logging`
*   **Files:** `logger.py`, update `database.py`.

### Student C: Traveller/Scooter Management

**Tasks:**

*   **CRUD Operations**
    *   System Admin: Add/delete travellers/scooters.
    *   Service Engineer: Update scooter attributes (e.g., State of Charge).

*   **Search Functionality**
    *   Allow partial search keys using SQL `LIKE`.

    ```python
    cursor.execute("SELECT * FROM travellers WHERE first_name LIKE ?", (f"%{key}%",))
    ```

**GitHub:**

*   **Branch:** `feature/operations`
*   **Files:** `operations.py`.

## Week 3 (9 June – 15 June): Integration & Testing

**Goal:** Merge components, test security, and fix bugs.

### All Students

**Tasks:**

*   **Merge GitHub Branches**
    *   Resolve conflicts in `main` branch.

*   **Test edge cases:**
    *   SQL injection in search fields (e.g., `' OR 1=1;--`).
    *   Role escalation (e.g., Service Engineer deleting scooters).

*   **Verify Encryption**
    *   Ensure encrypted data is unreadable via tools like DB Browser for SQLite.

**GitHub:**

*   Create `test_cases.md` for manual testing.
*   Use GitHub Issues to track bugs.

## Week 4 (16 June): Final Review & Presentation Prep

**Goal:** Rehearse presentation and final checks.

### All Students

**Tasks:**

*   **Presentation Script**
    *   Demo flow:

        1.  Login as Super Admin → Create System Admin → Logout.
        2.  Login as System Admin → Add Traveller → Backup DB.
        3.  Login as Service Engineer → Update Scooter → Check logs.

*   **Verify Grading Criteria**
    *   C1 (Authentication): Ensure all roles have correct access.
    *   C2 (Input Validation): Test invalid formats (e.g., wrong zip code).
    *   C3 (SQL Injection): Confirm parameterized queries are used everywhere.

**GitHub:**

*   Final commit: `main` branch.
*   Create submission zip: `studentnumber1_studentnumber2_studentnumber3.zip`.

## Key Success Tips

*   **Daily Standups:** Sync progress daily (e.g., 15-minute calls).

## GitHub Best Practices

*   Use descriptive commit messages (e.g., "Fix: Password hashing bug").
*   Review each other’s pull requests.

## Security Focus

*   Never store plaintext passwords.
*   Encrypt all sensitive fields (e.g., phone numbers, logs).

## Template
*    Structure

    ```python
    src/  
├── um_members.py          # Main entry point to run the system  
├── auth.py                # User authentication and authorization logic  
├── database.py            # Database connection and table creation  
├── models.py              # Data schemas (e.g., User, Traveller, Scooter)  
├── validation.py          # Input validation functions  
├── interface.py           # Console-based user interface menus  
├── operations.py          # CRUD operations for travellers/scooters  
├── logger.py              # Activity logging and encryption  
├── encryption.py          # Symmetric encryption (AES) for sensitive data  
└── config.py              # Constants (e.g., encryption key, predefined cities)  

data/                      # Folder for SQLite database and backups  
├── urban_mobility.db      # Encrypted SQLite3 database  
└── backups/               # Backup zip files  

docs/  
└── test_cases.md          # Manual test cases for grading criteria  

.gitignore                 # Ignore temporary files, keys, etc.  
requirements.txt           # Dependencies (e.g., bcrypt, cryptography)  
README.md                  # Setup instructions for teachers  
    ```