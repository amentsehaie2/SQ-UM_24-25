import os
import sqlite3
from encryption import _initialize_keys

# Initialiseer encryptie/keys direct voor consistentie
_initialize_keys()
print("DEBUG: Encryptie-keys geïnitialiseerd.")

# Bepaal project root
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(project_root, "output", "urban_mobility.db")
os.makedirs(os.path.join(project_root, "output"), exist_ok=True)

# # Tabel legen (voor betrouwbare tests)
# conn = sqlite3.connect(db_path)
# cursor = conn.cursor()
# cursor.execute("DELETE FROM users")  # Leegt de users-tabel
# conn.commit()
# conn.close()

from database import (
    add_user, get_user_by_username, update_user_password, delete_user_by_username,
    get_users_by_role
)
from auth import verify_password, validate_password, login, logout
from operations import (
    make_backup, restore_backup_by_name,
    generate_restore_code_db, use_restore_code_db
)

print("=== TEST: USER CRUD ===")
test_username = "JaydenTest"
test_pw = "Leukewachtwoord123!"
test_role = "system_admin"  # Rol voor de testgebruiker
test_name = "Jayden"
test_lname = "Doe"

print("> Valideer wachtwoord:", test_pw)
print("Wachtwoord validatie resultaat:", validate_password(test_pw))

print("> Probeer gebruiker toe te voegen...")
add_user(test_username, test_pw, test_role)
print("Gebruiker toegevoegd!")

user = get_user_by_username(test_username)
print("Gebruiker opgehaald uit database:", user)
assert user is not None, "User toevoegen mislukt!"

print("> Wachtwoord controleren...")
pw_result = verify_password(test_pw, user["password"])
print("Wachtwoordcontrole:", pw_result)
assert pw_result, "Wachtwoordcontrole mislukt!"

# print("> Wachtwoord updaten...")
# update_user_password(test_username, "NieuwWachtwoord!456")
# print("Wachtwoord geüpdatet.")

# user = get_user_by_username(test_username)
# pw_update_result = verify_password("NieuwWachtwoord!456", user["password"])
# print("Password update check:", pw_update_result)
# assert pw_update_result, "Wachtwoord reset mislukt!"

# print("> Gebruikers met rol ophalen...")
# admins = get_users_by_role("system_admin")
# print("System Admins:", admins)
# assert any(u["username"] == test_username for u in admins), "Gebruiker niet gevonden bij rol!"

# print("> Gebruiker verwijderen...")
# delete_user_by_username(test_username)
# print("Gebruiker verwijderd.")

# user = get_user_by_username(test_username)
# print("User na delete:", user)
# assert user is None, "User verwijderen mislukt!"

# # ===== TEST: LOGIN/LOGOUT =====
# print("\n=== TEST: LOGIN/LOGOUT ===")
# # Voeg gebruiker opnieuw toe voor login test
# add_user(test_username, test_pw, test_role)

# # Login simuleren zonder echte input (patch input())
# def mock_input(prompt):
#     if "Username" in prompt:
#         return test_username
#     elif "Password" in prompt:
#         return test_pw
#     return ""

# import builtins
# orig_input = builtins.input
# builtins.input = mock_input

# user_obj = login()
# assert user_obj is not None, "Login met juiste gegevens mislukt!"
# print("Login succesvol!")

# # Fout wachtwoord
# def wrong_input(prompt):
#     if "Username" in prompt:
#         return test_username
#     elif "Password" in prompt:
#         return "FoutWachtwoord123"
#     return ""

# builtins.input = wrong_input
# user_obj_fail = login()
# assert user_obj_fail is None, "Login met verkeerde wachtwoord zou moeten falen!"
# print("Login met fout wachtwoord correct afgewezen.")

# builtins.input = orig_input  # Herstel input

# # Logout testen
# logout(user_obj)
# print("Logout succesvol.")

# # ===== TEST: BACKUP/RESTORE ZIP FILE FUNCTIONS =====
# print("\n=== TEST: BACKUP/RESTORE ZIP FILE FUNCTIONS ===")
# backup_name = make_backup(user_obj)
# print("Backup gemaakt:", backup_name)

# # Simuleer een 'restore' met code functionaliteit
# code = generate_restore_code_db(test_username, backup_name, user_obj)
# print("Restore-code gegenereerd:", code)

# ok, backup = use_restore_code_db(test_username, code, user_obj)
# assert ok and backup == backup_name, "Restore-code niet bruikbaar!"
# print("Restore-code correct gebruikt.")

# # Tweede keer proberen (moet mislukken)
# ok2, backup2 = use_restore_code_db(test_username, code, user_obj)
# assert not ok2, "Restore-code kan niet twee keer gebruikt worden!"
# print("Restore-code is correct ongeldig na gebruik.")

# # Restore daadwerkelijk uitvoeren (simuleer system_admin context)
# restore_backup_by_name(test_username, backup_name)
# print("Backup succesvol hersteld.")

# # Cleanup
# delete_user_by_username(test_username)
# print("\n=== ALLES SUCCESVOL GETEST ===")
