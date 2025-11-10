#!/usr/bin/env python3
"""
Google Drive Authentication Setup
Sets up Google Drive API credentials
"""

import json
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

def setup_credentials():
    """Setup Google Drive API credentials"""
    print("🔐 Google Drive API Setup")
    print("=" * 30)
    
    # Check if credentials.json exists
    if not os.path.exists('credentials.json'):
        print("❌ credentials.json not found!")
        print("\n📋 To get credentials.json:")
        print("1. Go to https://console.developers.google.com/")
        print("2. Create a new project or select existing")
        print("3. Enable Google Drive API")
        print("4. Create credentials (OAuth 2.0 Client ID)")
        print("5. Download as credentials.json")
        print("6. Place in this directory")
        return False
    
    print("✅ credentials.json found")
    
    # Create sample credentials structure for reference
    sample_creds = {
        "installed": {
            "client_id": "your-client-id.googleusercontent.com",
            "project_id": "your-project-id",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": "your-client-secret",
            "redirect_uris": ["http://localhost"]
        }
    }
    
    # Save sample for reference
    with open('credentials_sample.json', 'w') as f:
        json.dump(sample_creds, f, indent=2)
    
    print("📄 Sample credentials structure saved to credentials_sample.json")
    return True

def test_authentication():
    """Test Google Drive authentication"""
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    try:
        creds = None
        
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
        
        print("✅ Authentication successful!")
        print("🔑 Token saved to token.json")
        return True
        
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def main():
    print("🚀 Google Drive Scanner Setup")
    print("=" * 40)
    
    # Setup credentials
    if not setup_credentials():
        return
    
    # Test authentication
    print("\n🔐 Testing authentication...")
    if test_authentication():
        print("\n✅ Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Run: python payment-link-scanner.py")
        print("2. Run: python link-organizer.py")
    else:
        print("\n❌ Setup failed. Check your credentials.json file.")

if __name__ == "__main__":
    main()