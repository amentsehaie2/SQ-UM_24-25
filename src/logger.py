import os
import json
from datetime import datetime
from encryption import encrypt_data, decrypt_data

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)
_OUTPUT_DIR = os.path.join(_PROJECT_ROOT, "output")
LOG_FILE_PATH = os.path.join(_OUTPUT_DIR, "activities.log")

def _get_next_log_id():
    """Determines the next available log ID."""
    logs = read_logs()
    return max(log["log_id"] for log in logs) + 1 if logs else 1

def log_activity(username, description, additional_info="", suspicious=False):
    """Logs an activity to the encrypted log file using JSON format."""
    log_id = _get_next_log_id()
    timestamp = datetime.now().isoformat()
    
    log_entry = {
        "log_id": log_id,
        "timestamp": timestamp,
        "username": username,
        "description": description,
        "additional_info": additional_info,
        "suspicious": suspicious,
        "read": False
    }
    
    # JSON NEEDED FOR ENCRYPTION
    json_log = json.dumps(log_entry)
    encrypted_log_entry = encrypt_data(json_log) + "\n"

    try:
        os.makedirs(_OUTPUT_DIR, exist_ok=True)
        with open(LOG_FILE_PATH, "a") as log_file:
            log_file.write(encrypted_log_entry)
    except Exception as e:
        print(f"Error writing to log file: {e}")

def get_unread_suspicious_logs():
    """Returns a list of all unread suspicious logs."""
    return [log for log in read_logs() if log.get("suspicious", False) and not log.get("read", False)]

def mark_suspicious_logs_as_read():
    """Marks all suspicious logs as read."""
    logs = read_logs()
    updated_logs = []
    
    for log in logs:
        if log.get("suspicious", False) and not log.get("read", False):
            log["read"] = True
        updated_logs.append(log)
    
    try:
        os.makedirs(_OUTPUT_DIR, exist_ok=True)
        with open(LOG_FILE_PATH, "w") as log_file:
            for log in updated_logs:
                json_log = json.dumps(log)
                encrypted_log_entry = encrypt_data(json_log) + "\n"
                log_file.write(encrypted_log_entry)
    except Exception as e:
        print(f"Error updating log file: {e}")

def show_suspicious_alert():
    """Shows an alert for unread suspicious activities."""
    unread_suspicious = get_unread_suspicious_logs()
    if unread_suspicious:
        print("\n" + "="*60)
        print("🚨 SECURITY ALERT: SUSPICIOUS ACTIVITIES DETECTED 🚨")
        print("="*60)
        print(f"There are {len(unread_suspicious)} unread suspicious activities:")
        print()
        
        for log in unread_suspicious[:5]:  
            print(f"⚠️  [{log['timestamp']}] User: {log['username']}")
            print(f"   Description: {log['description']}")
            if log.get('additional_info'):
                print(f"   Details: {log['additional_info']}")
            print()
        
        if len(unread_suspicious) > 5:
            print(f"... and {len(unread_suspicious) - 5} more suspicious activities.")
        
        print("="*60)
        print("Please review the system logs immediately!")
        print("="*60)
        
        return unread_suspicious
    return []

def read_logs():
    """Reads and decrypts all logs from the log file."""
    try:
        os.makedirs(_OUTPUT_DIR, exist_ok=True)
        with open(LOG_FILE_PATH, "r") as log_file:
            encrypted_logs = log_file.readlines()
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"Error reading log file: {e}")
        return []

    decrypted_logs = []
    for encrypted_log in encrypted_logs:
        try:
            decrypted_json = decrypt_data(encrypted_log.strip())
            log_entry = json.loads(decrypted_json)
            decrypted_logs.append(log_entry)
        except Exception as e:
            print(f"Error decrypting log entry: {e}")
            continue

    return decrypted_logs

def print_logs():
    logs = read_logs()
    print("\nLogs:")
    for log in logs:
        print(f"ID: {log['log_id']}  |  Date: {log['timestamp']}  |  User: {log['username']}  |  Desc: {log['description']}  |  Info: {log['additional_info']}  |  Suspicious: {log['suspicious']}")    

def delete_logs():
    """Deletes all logs from the log file by clearing its content."""
    try:
        os.makedirs(_OUTPUT_DIR, exist_ok=True)
        with open(LOG_FILE_PATH, "w") as log_file:
            log_file.write("")
        print("All logs deleted successfully.")
    except Exception as e:
        print(f"Error deleting logs: {e}")

def get_suspicious_logs():
    """Geeft een lijst van alle verdachte logs."""
    return [log for log in read_logs() if log.get("suspicious", False)]

if __name__ == '__main__':

    # Adding logs
    # log_activity("test_user", "Pipe | Test", "Special & Characters", True)
    # log_activity("test_user", "boohooy | Test", "Special & Characters", False)
    # log_activity("test_user", "attempted sql injection", "Special & Characters", True)
    

    # Reading logs
    print_logs()

    # Deleting logs
    # delete_logs()    
 
    # Test security
    #log_activity("hacker", "Attempted SQL: DROP TABLE users;", "", True)
    #print("All tests passed!")
