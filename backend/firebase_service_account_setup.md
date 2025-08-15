Loopy Backend – Firebase Service Account Key & Environment Variable Setup
Date: 2025-08-09
Audience: Backend devs, mentors, and cross-functional teammates

1) Purpose
Securely set up the Firebase Service Account Key and configure environment variables for local backend development.

2) Get the Service Account Key
Go to Firebase Console → Select the Loopy project.
Navigate to Project Settings → Service Accounts.
Click Generate new private key.
Save the .json file outside the project folder to keep it out of Git. Example: C:/secure/loopy_service_account.json
3) Environment Variable Setup
Chosen Method: ✅ Option A — System Environment Variable (Permanent)

Windows:

Open Edit the system environment variables.
Click Environment Variables….
Under User variables, click New….
Name: GOOGLE_APPLICATION_CREDENTIALS
Value: C:/secure/loopy_service_account.json
Save and restart VS Code.
Debugging / Verification:

echo $env:GOOGLE_APPLICATION_CREDENTIALS
Should output the full path.

Test-Path $env:GOOGLE_APPLICATION_CREDENTIALS
Should return True.

macOS/Linux:

export GOOGLE_APPLICATION_CREDENTIALS="/path/to/loopy_service_account.json"
source ~/.bashrc   # or ~/.zshrc
Check:

echo $GOOGLE_APPLICATION_CREDENTIALS
Option B — .env File (Alternative for Dev)
Install dependency:
pip install python-dotenv
Create backend/.env:
GOOGLE_APPLICATION_CREDENTIALS=C:/secure/loopy_service_account.json
Add .env to .gitignore.
Update firebase_client.py:
import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, firestore

load_dotenv()

cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
if not cred_path:
    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS env var not set.")
if not os.path.exists(cred_path):
    raise FileNotFoundError(f"Service account key not found at: {cred_path}")

if not firebase_admin._apps:
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)

db = firestore.client()
SERVER_TS = firestore.SERVER_TIMESTAMP  # type: ignore
4) Verify Setup
Run from project root:

python -m backend.test_main
Expected output:

✅ Firebase initialized with credentials from: C:/secure/loopy_service_account.json
Retrieved User: {...}
5) Security Notes
Never commit your .json key.
Rotate the key in Firebase if exposed.
Each developer keeps their own .env or environment variable with their local path.
6) Troubleshooting
Env var not set: Re-check system variable in Windows or shell config in macOS/Linux.
FileNotFoundError: Path is wrong; confirm with Test-Path (Windows) or ls (macOS/Linux).
ImportError: Run from project root:
python -m backend.test_main