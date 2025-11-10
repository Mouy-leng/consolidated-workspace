#!/usr/bin/env python3
"""Firebase Authentication Helper for GenX FX"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirebaseAuth:
    def __init__(self):
        self.auth_uid = os.getenv('FIREBASE_AUTH_UID')
        
    def get_auth_uid(self):
        """Get the Firebase authentication UID"""
        return self.auth_uid
    
    def is_authenticated(self):
        """Check if Firebase authentication is configured"""
        return bool(self.auth_uid)
    
    def get_auth_token(self):
        """Get authentication token for API calls"""
        return self.auth_uid

if __name__ == "__main__":
    auth = FirebaseAuth()
    print(f"Firebase Auth UID: {auth.get_auth_uid()}")
    print(f"Authenticated: {auth.is_authenticated()}")