import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Fetch the token
token = os.getenv("GITHUB_TOKEN")

if token:
    print(f"Success! Token loaded: {token[:5]}*****")  # Masking for security
else:
    print("Error: Could not load token. Check .env file.")
