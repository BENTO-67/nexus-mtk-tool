import os
import json
import base64
import platform
import subprocess
from datetime import datetime, timedelta

class TrialLicenseManager:
    def __init__(self, trial_days=3):
        self.trial_days = trial_days
        # Hidden file path to store trial/activation data locally
        self.license_file = "nexus_system_auth.dat"

    def get_hardware_id(self):
        """Generates a unique and reliable hardware ID based on Windows MachineGuid."""
        try:
            if platform.system().lower() == "windows":
                import winreg
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                    guid = winreg.QueryValueEx(key, "MachineGuid")[0]
                    return f"NX-{guid[:16].upper()}"
            else:
                return "NX-GENERIC-HWID"
        except Exception:
            return "NX-PC-USER-001"

    def check_license_status(self, user_entered_key=None):
        """Checks whether a valid permanent license or an active 3-day trial exists."""
        hwid = self.get_hardware_id()
        
        # Verify permanent activation key if provided by the user
        if user_entered_key:
            expected_key = self.generate_activation_key(hwid)
            if user_entered_key.strip() == expected_key:
                self._save_auth_data(is_trial=False, expiry=None)
                return "activated"
            else:
                return "invalid_key"

        # Check existing license file
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, "r") as f:
                    encrypted_data = f.read()
                    decrypted_json = json.loads(base64.b64decode(encrypted_data.encode()).decode())
                    
                    if not decrypted_json.get("active", True):
                        return "expired"
                    
                    if decrypted_json.get("is_trial") == False:
                        return "activated" # Permanent key is valid
                    
                    # Verify 3-day trial period expiration
                    start_time = datetime.fromisoformat(decrypted_json.get("start_time"))
                    expiry_time = start_time + timedelta(days=self.trial_days)
                    
                    if datetime.now() > expiry_time:
                        self._lock_trial()
                        return "expired"
                    else:
                        remaining = expiry_time - datetime.now()
                        return {"status": "trial_active", "remaining_hours": int(remaining.total_seconds() / 3600)}
            except Exception:
                return "expired"
        else:
            # First application run: initialize the 3-day trial period
            start_data = {
                "hwid": hwid,
                "is_trial": True,
                "start_time": datetime.now().isoformat(),
                "active": True
            }
            self._save_raw_data(start_data)
            return {"status": "trial_active", "remaining_hours": self.trial_days * 24}

    def generate_activation_key(self, hwid):
        """Generates a secure permanent activation key unique to the client's hardware ID."""
        raw_string = f"NEXUS_MTK_2026_{hwid}_SECURE"
        encoded = base64.b64encode(raw_string.encode()).decode()
        return f"NXK-{encoded[4:12]}-{encoded[12:20]}".upper()

    def _save_auth_data(self, is_trial, expiry):
        data = {
            "hwid": self.get_hardware_id(),
            "is_trial": is_trial,
            "start_time": datetime.now().isoformat(),
            "active": True
        }
        self._save_raw_data(data)

    def _save_raw_data(self, data):
        json_data = json.dumps(data)
        encoded_data = base64.b64encode(json_data.encode()).decode()
        with open(self.license_file, "w") as f:
            f.write(encoded_data)

    def _lock_trial(self):
        if os.path.exists(self.license_file):
            try:
                with open(self.license_file, "r") as f:
                    data = json.loads(base64.b64decode(f.read().encode()).decode())
                data["active"] = False
                self._save_raw_data(data)
            except Exception:
                pass