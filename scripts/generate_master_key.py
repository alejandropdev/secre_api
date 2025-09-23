#!/usr/bin/env python3
"""Generate a master API key and save it to a file."""

import secrets
import string
from pathlib import Path

def generate_master_key(length: int = 64) -> str:
    """Generate a secure random master API key."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def main():
    """Generate and save master API key."""
    master_key = generate_master_key()
    
    # Save to file
    key_file = Path("master_api_key.txt")
    with open(key_file, "w") as f:
        f.write(f"Master API Key: {master_key}\n")
        f.write(f"Generated at: {__import__('datetime').datetime.now().isoformat()}\n")
        f.write("\n")
        f.write("Use this key in the X-Api-Key header for admin operations.\n")
        f.write("Example: curl -H 'X-Api-Key: {master_key}' http://localhost:8000/v1/admin/tenants\n")
    
    print(f"Master API key generated and saved to {key_file}")
    print(f"Key: {master_key}")
    print("\nIMPORTANT: Keep this key secure and don't commit it to version control!")

if __name__ == "__main__":
    main()
