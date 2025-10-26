
# Grade report — Urban Mobility backend (security focus)

Grade: 6 / 10

Summary
-------
Security posture: partially implemented with serious weaknesses and a number of missing defensive controls. The code demonstrates awareness of encryption, password hashing, and use of restore codes, but there are practical faults that weaken confidentiality, integrity, and availability. Several fixes are straightforward and high-impact.

Key high-severity issues
-----------------------
- Backup/restore flow allows dangerous state transitions if not validated before replacing live data. (Observed and patched in `src/backup.py`, but original behavior allowed restoring an archive that could remove the currently-acting admin.)
- `logger.py`/`interface.py` duplication and imports create circular-import risk and likely broken module responsibility — `logger.py` contains interface code and imports itself.
- Validators often call parsing routines (e.g., `datetime.date.fromisoformat`) without exception handling; invalid inputs will raise and may crash callers. Several validators do not check argument types.
- Some input validation enforces ASCII-only characters or overly-strict patterns (names, cities, serials) and will reject legitimate input; lack of explicit normalization and type checks is a security/robustness issue.
- ID generation appears to use predictable integers in places (assignment requirement warns against predictable IDs). The codebase should use non-predictable UUIDs for external IDs.
- Error handling is inconsistent: many broad excepts and silent continues; some user-facing messages leak state (e.g., logs that reveal whether a username exists). Authentication flow partially fixed but needs a centralized strike/lockout, rate-limiting and consistent logging.

Grading per assignment criteria (security-critical items)
-----------------------------------------------------
1) Sensitive data encrypted in DB (weight: high)
	 - Status: Partial / Needs verification
	 - Evidence: `database.py` and `encryption.py` exist; `_initialize_keys()` invoked. However, not all code paths show that all traveller/user fields are encrypted before DB insertion. Search for direct INSERT of plaintext fields in `database.py` and `traveller.py` and `admin.py`.
	 - Risk: cleartext PII in DB if encryption calls are missed.
	 - Fix: Enforce an application-level contract: write wrapper functions in `database.py` that accept plaintext objects and always perform encryption centrally before any INSERT/UPDATE. Add tests asserting stored DB bytes are not equal to plaintext.

2) Predictable IDs (weight: high)
	 - Status: Fail (observed or likely)
	 - Evidence: assignment requires unique customer IDs and warns against predictable IDs. Search shows no use of uuid4 for traveller/customer ids. Some `id` values are read/written directly in DB code.
	 - Risk: enumeration and account takeover risk.
	 - Fix: switch to UUIDv4 for all public identifiers (traveller/customer IDs, backup tokens). Use internal autoincrement only for internal DB keys if truly needed but do not expose them externally.

3) Backup / restore integrity & broken session attack (weight: high)
	 - Status: Partial: original code replaced live DB first; patched to validate before swap, but additional controls required.
	 - Evidence: `backup.py` previously unpacked archive directly into live output directory. Attack scenario: create a backup, create a temp admin, attempt to restore a backup that does not include the current user, resulting in the actor being deleted or state inconsistencies.
	 - Risk: self-deletion, privilege escalation, and denial-of-service.
	 - Fix (required):
		 - Always extract to a temporary directory and validate the presence/consistency of the requesting admin (done in patch).
		 - Additionally: invalidate the current session before performing a destructive restore OR require a two-person approval (two distinct admin accounts, or a super-admin + system-admin), or require physical presence (out-of-band code). Implement atomic swap with pre-restore snapshot and rollback on failure.
		 - Bind restore codes cryptographically to the target backup (HMAC of backup contents) and to the target sysadmin username, and make them single-use and time-limited.

4) Validation placement and database checks (weight: medium)
	 - Status: Partially incorrect design
	 - Evidence: `auth.py` originally mixed format validation and DB lookup; guidance and code indicate DB membership check should be separate from pure format validation.
	 - Risk: inefficient double validation, possible timing differences that can be abused for username enumeration.
	 - Fix: Keep `validate_*` functions pure (type & format checks only, no DB access). Perform DB lookups only after format passes. Centralize error messages and keep them generic. Implement consistent rate-limiting and lockouts.

5) Search fields and irrelevance of last-maintenance/in-service in search (weight: low)
	 - Status: Observed: code exposes last maintenance and in-service date; interface uses them in search options.
	 - Recommendation: remove last maintenance and in-service date from default search filters. Keep them available in detail views only.

6) Error handling and logging (weight: medium)
	 - Status: Inconsistent
	 - Evidence: Many `except Exception:` blocks and multiple log messages that vary in format. Some sensitive details are logged (including decrypted usernames); some logs are written before input sanitization.
	 - Risk: noisy logs, leaked PII, missed root-cause information.
	 - Fix: adopt a small logging contract: use `log_activity(username, description, additional_info=None, suspicious=False)` consistently. Catch specific exceptions (ValueError, sqlite3.Error). Never log raw secrets (passwords, private keys). Sanitize user-controlled strings before writing logs.

7) Authentication hardening (weight: high)
	 - Status: Partially implemented
	 - Evidence: `auth.py` now enforces per-field strike counts but needs central lockout policy, consistent messages, and backoff.
	 - Fix: Implement per-account lockout (persist lockout counters in DB with expiry), global rate limiting, exponential backoff, CAPTCHA after repeated failures in UI contexts, and maintain generic error messages to avoid username enumeration.

File-by-file prioritized feedback and fixes
----------------------------------------
`src/backup.py` (critical)
	- Finding: original extraction replaced live directory; patched to use temp dir but still needs cryptographic binding for restore codes and session handling.
	- Fix (code): keep the validation; add HMAC-of-backup when generating restore code: compute HMAC over the archive bytes with server-side key and store both code and HMAC; on `use_restore_code_db` verify HMAC matches file to prevent attackers from reusing codes for different archives.
	- Fix (policy): require restore to be executed by a session that is not the target admin (force different approver) or require session invalidation.

`src/auth.py` (high)
	- Finding: improved but still leaves user enumeration risk if logs contain different messages. Super-admin bypass logic must be explicit and protected.
	- Fix: Keep `validate_username` pure and ensure super-admin bypass happens before any DB lookup but after type-check. Implement persistent failed-attempt counters per username and per IP (if possible). Move strike counters into DB so crashes can't reset them.

`src/validation.py` (high/medium)
	- Finding: many validators call parsing functions directly (`fromisoformat`) without try/except and without type checks. `validate_location` has a logic bug: returns True if instance of str BEFORE applying regex.
	- Fixes (examples):
		- `validate_birth_date`: wrap parse in try/except and return False on error.
			```py
			try:
					parsed = datetime.date.fromisoformat(birth_date)
			except (TypeError, ValueError):
					return False
			return parsed < datetime.date.today()
			```
		- `validate_last_maint`: same pattern.
		- `validate_location`: evaluate regex first and ensure both conditions are correct; remove the stray "if isinstance(location, str): return True".
		- Add explicit `isinstance(..., str)` at top of every string validator.

`src/logger.py` and `src/interface.py` (high)
	- Finding: `logger.py` contains UI code (duplicate of `interface.py`) and imports itself. This is a major separation-of-concerns and circular import bug.
	- Fix: Restore `logger.py` to only logging responsibilities: implement `log_activity`, `print_logs`, `show_suspicious_alert`, etc. Move menu/UI code back into `interface.py`. Avoid `from logger import ...` inside `logger.py`.

`src/database.py` (high)
	- Finding: encryption initialization present. Need to confirm every sensitive field is encrypted before write. Also check whether usernames/roles are stored encrypted and whether `get_user_by_username` handles encryption correctly (should accept plaintext username, encrypt it deterministically for lookup or perform decryption of stored values to compare safely).
	- Fix: centralize DB write functions and force encryption there. Use deterministic but authenticated encryption for lookup fields if necessary (AEAD with nonce fixed per field is risky); instead, consider storing searchable hash (HMAC) for username lookups and keep ciphertext for display.

`src/encryption.py` (high)
	- Finding: keys exist in `output/.key` etc. Ensure private keys are never checked into VCS and are file-permission protected. Current repo shows .private-key in `output/` — check `.gitignore`.
	- Fix: move keys out of repo, use environment-controlled key location, or generate per-deployment keys. Add key-rotation and backup procedures.

Testing and CI
--------------
- Add unit tests that confirm all `validate_*` functions return False for invalid types and reject malicious inputs. A tests file was added for `validate_birth_date` — expand tests to cover all validators.
- Add an integration test for backup/restore: create a backup, create a temp admin, attempt the attack pattern and assert the system blocks the restore or does not delete the acting admin.

Prioritized action list (highest to lowest)
-----------------------------------------
1. Fix `logger.py` duplication and remove circular imports. (Critical)
2. Harden backup/restore: temp extraction, HMAC tie, session invalidation or two-person approval, atomic swap with rollback. (Critical)
3. Centralize DB encryption and enforce it for all writes. (Critical)
4. Replace public IDs with UUIDv4 for all externally visible IDs. (High)
5. Harden authentication: persistent lockouts, generic messages, rate-limiting. (High)
6. Add exception handling to all validators; fix `validate_location` logic. (Medium)
7. Standardize error handling and log format; never log secrets. (Medium)
8. Add tests and CI pipelines that run them, keep pytest as a dev-only dependency. (Medium)

Scoring rationale
-----------------
- Confidentiality (encryption of fields): 5/10 — encryption present but not consistently enforced before writes.
- Integrity (backup/restore, ID predictability): 4/10 — original restore flow dangerous; IDs likely predictable.
- Availability (restore could delete actor / lack of atomic swap): 6/10 after patch, but policy changes required.
- Authentication & authorization: 6/10 — password hashing present, strike logic implemented, but lockout persistence and enumeration risks remain.
- Error handling & logging: 6/10 — present, but inconsistent and leaks potential.

Deliverables / checks to make before resubmission
------------------------------------------------
- Ensure `logger.py` contains only logging code and `interface.py` contains the UI. Run lint and import checks.
- Confirm every DB INSERT/UPDATE passes through a single encryption wrapper in `database.py`.
- Replace any exposeable integer IDs with UUID strings.
- Implement HMAC-binding for restore codes and require either session invalidation or multi-approver restore.
- Add tests for validators (already started) and expand to other validators, plus integration tests for backup/restore.

References / Notes
-----------------
- Follow OWASP guidance for authentication: generic error messages, persistent lockout, rate limiting.
- Use UUIDv4 for non-predictable IDs. Use deterministic HMAC for lookups where necessary, not raw ciphertext.

