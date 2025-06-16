# test_all.py

from database import (
    add_user, get_user_by_username, update_user_password, delete_user_by_username,
    create_backup, restore_backup_by_name,
    generate_restore_code_db, use_restore_code_db, get_users_by_role
)
from auth import verify_password, validate_password
from logger import log_activity, read_logs, get_suspicious_logs

import os

print("=== TEST: USER CRUD ===")
test_username = "JaydenTest"
test_pw = "SterkWachtwoord!123"
test_role = "system_admin"

print("> Valideer wachtwoord:", test_pw)
print("Wachtwoord validatie resultaat:", validate_password(test_pw))

print("> Probeer gebruiker toe te voegen...")

try:
    print(f"DEBUG: add_user() called met username={test_username}, password={test_pw}, role={test_role}")
    add_user(test_username, test_pw, test_role)
    print("DEBUG: add_user() uitgevoerd zonder exceptie.")
except Exception as e:
    print(f"DEBUG: Exception tijdens add_user: {e}")

user = get_user_by_username(test_username)
print("Gebruiker opgehaald uit database:", user)
assert user is not None, "User toevoegen mislukt!"

print("> Wachtwoord controleren...")
print("DEBUG: user['password'] =", user["password"])
try:
    pw_result = verify_password(test_pw, user["password"])
    print("Wachtwoordcontrole:", pw_result)
    assert pw_result, "Wachtwoordcontrole mislukt!"
except Exception as e:
    print(f"DEBUG: Exception tijdens verify_password: {e}")
    assert False, "Wachtwoordcontrole gooide een exceptie!"

print("> Wachtwoord updaten...")
try:
    update_user_password(test_username, "NieuwWachtwoord!456")
    print("DEBUG: Wachtwoord geüpdatet.")
except Exception as e:
    print(f"DEBUG: Exception tijdens update_user_password: {e}")

user = get_user_by_username(test_username)
try:
    pw_update_result = verify_password("NieuwWachtwoord!456", user["password"])
    print("DEBUG: Password update check:", pw_update_result)
    assert pw_update_result, "Wachtwoord reset mislukt!"
except Exception as e:
    print(f"DEBUG: Exception tijdens verify_password na update: {e}")
    assert False, "Wachtwoord reset verificatie faalde!"

print("> Gebruikers met rol ophalen...")
admins = get_users_by_role("system_admin")
print("System Admins:", admins)
assert any(u["username"] == test_username for u in admins), "Gebruiker niet gevonden bij rol!"

print("> Gebruiker verwijderen...")
try:
    delete_user_by_username(test_username)
    print("DEBUG: delete_user_by_username uitgevoerd.")
except Exception as e:
    print(f"DEBUG: Exception tijdens delete_user_by_username: {e}")

user = get_user_by_username(test_username)
print("DEBUG: User na delete:", user)
assert user is None, "User verwijderen mislukt!"
print("Gebruiker verwijderd.")

print("\n=== TEST: BACKUP & RESTORE ===")
backup_name = create_backup()
backup_path = os.path.join(os.path.dirname(__file__), "output", "backups", backup_name)
print("DEBUG: backup_path =", backup_path)
assert os.path.exists(backup_path), "Backup niet gevonden!"
print("Backup gemaakt:", backup_name)

print("> Restore uitvoeren...")
restore_backup_by_name(backup_name)
print("Restore uitgevoerd (controleer output directory voor effect).")

print("\n=== TEST: RESTORE-CODE FUNCTIONALITEIT ===")
test_admin = "SysAdminTestRestore"
restore_pw = "ComplexWachtwoord!789"
print("> Valideer restore-password:", restore_pw)
print("Wachtwoord validatie resultaat:", validate_password(restore_pw))
add_user(test_admin, restore_pw, "system_admin")
code = generate_restore_code_db(test_admin, backup_name)
print("Genereerde restore-code:", code)
ok, backup = use_restore_code_db(test_admin, code)
print("Resultaat use_restore_code_db:", ok, backup)
assert ok and backup == backup_name, "Restore-code gebruik mislukt!"
ok2, backup2 = use_restore_code_db(test_admin, code)
print("Tweede keer use_restore_code_db (moet False zijn):", ok2, backup2)
assert not ok2, "Restore-code kan maar 1x gebruikt worden!"
delete_user_by_username(test_admin)

print("\n=== TEST: LOGGING FUNCTIONALITEIT ===")
log_activity("TestLogger", "Normale actie", "Info", False)
log_activity("TestLogger", "SQL injectie poging", "DROP TABLE users;", True)
logs = read_logs()
assert any(l["username"] == "TestLogger" for l in logs), "Log niet opgeslagen!"
print("Log entries:")
for log in logs:
    print(log)
suspicious = get_suspicious_logs()
assert any(l["suspicious"] for l in suspicious), "Suspicious logs niet gevonden!"
print("Suspicious log entries:")
for log in suspicious:
    print(log)

print("\n=== ALLES SUCCESVOL GETEST ===")
