import os as o

# Styled Header
print("="*50)
print("      🔐 CRYPTOGRAPHIC SAMPLE PROJECT 🔐      ")
print("="*50)

purpose = """
PURPOSE:
This directory serves as a secure local environment for 
testing Symmetric Encryption using the Fernet (AES-128) 
standard. 

WORKFLOW:
1. Key Generation: 'thekey.key' is created.
2. Authentication: Requires 'SECRET_P' env variable.
3. Encryption: Scrambles non-Python/Jupyter files.
"""
print(purpose)

# Status Check
print("--- Directory Status ---")
files = o.listdir()

if 'thekey.key' in files:
    print("[✔] Master Key found (thekey.key)")
else:
    print("[!] WARNING: Master Key missing.")

vault_files = [f for f in files if f.endswith('.txt')]
print(f"[*] Target files in vault: {len(vault_files)}")
for f in vault_files:
    print(f"  - {f}")

print("="*50)
print("🄯 RSNPIIT (Ramrup Satpati) from IIT Madras\nReleased under the GNU GPLv3 license") 