from license_manager import TrialLicenseManager

manager = TrialLicenseManager()
hwid = manager.get_hardware_id()
key = manager.generate_activation_key(hwid)

print("=" * 40)
print(f"YOUR HWID: {hwid}")
print(f"ACTIVATION KEY: {key}")
print("=" * 40)