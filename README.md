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

This plan ensures all components are built incrementally, security is prioritized, and the team finishes ahead of the deadline.
