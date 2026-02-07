# Quick diagnostic script to understand the credential format

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("CREDENTIAL DIAGNOSTIC")
print("=" * 60)

cred_id = os.getenv("AMAZON_CREDENTIAL_ID")
cred_secret = os.getenv("AMAZON_CREDENTIAL_SECRET")
tag = os.getenv("AMAZON_TAG")

print(f"\nCredential ID: {cred_id}")
print(f"Length: {len(cred_id) if cred_id else 0} characters")
print(f"Format: {'Alphanumeric lowercase' if cred_id and cred_id.isalnum() and cred_id.islower() else 'Other'}")

print(f"\nCredential Secret: {cred_secret[:10]}... (truncated)")
print(f"Length: {len(cred_secret) if cred_secret else 0} characters")

print(f"\nPartner Tag: {tag}")

print("\n" + "=" * 60)
print("ANALYSIS")
print("=" * 60)

if cred_id and len(cred_id) == 25:
    print("✅ Credential ID length matches expected format (25 chars)")
else:
    print(f"⚠️  Unexpected Credential ID length: {len(cred_id) if cred_id else 0}")

if cred_secret and len(cred_secret) > 40:
    print("✅ Credential Secret appears to be correct length")
else:
    print(f"⚠️  Unexpected Secret length: {len(cred_secret) if cred_secret else 0}")

print("\n" + "=" * 60)
print("RECOMMENDATION")
print("=" * 60)

print("""
Based on your Creators API screenshot, these credentials are from:
• Amazon Associates Creators API Version 2.2
• Application: Moneypit-detector
• Application ID: nocreditai-21.moneypit-detector

The Creators API may require:
1. Different authentication endpoint
2. Application ID instead of just credential ID  
3. Specific API version headers

NEXT STEP: Please check the "View API references" link in your
Amazon Associates dashboard and share:
- The authentication section
- Any example code or endpoints shown
- The base URL for API requests
""")
