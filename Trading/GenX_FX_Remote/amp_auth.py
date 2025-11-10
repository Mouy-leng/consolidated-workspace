#!/usr/bin/env python3
"""
AMP Authentication Module
Handles user authentication and session management
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from pathlib import Path

# Import Samsung biometric authentication
try:
    from samsung_biometric_auth import authenticate_with_samsung, get_samsung_device_info
    SAMSUNG_AUTH_AVAILABLE = True
except ImportError:
    SAMSUNG_AUTH_AVAILABLE = False
    print("Warning: Samsung biometric authentication not available")

# Import working fingerprint authentication
try:
    from simple_fingerprint_auth import SimpleFingerprintAuth
    FINGERPRINT_AUTH_AVAILABLE = True
except ImportError:
    FINGERPRINT_AUTH_AVAILABLE = False

class AMPAuth:
    def __init__(self):
        self.auth_file = Path("amp_auth.json")
        self.session_token = None
        self.user_id = None
        self.session_hash = None
        
    def parse_token(self, token: str) -> Dict[str, str]:
        """Parse the session token into components"""
        try:
            # Remove prefix if present
            if token.startswith("sgamp_user_"):
                token = token[11:]  # Remove "sgamp_user_" prefix
            
            # Split by underscore to separate user ID and hash
            parts = token.split("_")
            if len(parts) >= 2:
                user_id = parts[0]
                session_hash = "_".join(parts[1:])
                
                return {
                    "user_id": user_id,
                    "session_hash": session_hash,
                    "full_token": f"sgamp_user_{token}"
                }
            else:
                raise ValueError("Invalid token format")
                
        except Exception as e:
            print(f"Error parsing token: {e}")
            return {}
    
    def authenticate(self, token: str) -> bool:
        """Authenticate using the provided token"""
        print(f"🔐 Authenticating with token...")
        
        # Parse the token
        token_data = self.parse_token(token)
        if not token_data:
            print("❌ Invalid token format")
            return False
        
        # Store authentication data
        self.session_token = token_data["full_token"]
        self.user_id = token_data["user_id"]
        self.session_hash = token_data["session_hash"]
        
        # Save to auth file
        auth_data = {
            "user_id": self.user_id,
            "session_hash": self.session_hash,
            "session_token": self.session_token,
            "authenticated_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }
        
        with open(self.auth_file, 'w') as f:
            json.dump(auth_data, f, indent=2)
        
        print(f"✅ Authentication successful!")
        print(f"   User ID: {self.user_id}")
        print(f"   Session: {self.session_hash[:16]}...")
        print(f"   Expires: {auth_data['expires_at']}")
        
        return True
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        if not self.auth_file.exists():
            return False
        
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
            
            # Check if session is expired
            expires_at = datetime.fromisoformat(auth_data["expires_at"])
            if datetime.now() > expires_at:
                print("⚠️ Session expired")
                return False
            
            # Load current session data
            self.user_id = auth_data["user_id"]
            self.session_hash = auth_data["session_hash"]
            self.session_token = auth_data["session_token"]
            
            return True
            
        except Exception as e:
            print(f"Error checking authentication: {e}")
            return False
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        if not self.is_authenticated():
            return {}
        
        return {
            "Authorization": f"Bearer {self.session_token}",
            "X-User-ID": self.user_id,
            "X-Session-Hash": self.session_hash
        }
    
    def logout(self):
        """Logout and clear session"""
        if self.auth_file.exists():
            self.auth_file.unlink()
        
        self.session_token = None
        self.user_id = None
        self.session_hash = None
        
        print("✅ Logged out successfully")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get current user information"""
        if not self.is_authenticated():
            return {}
        
        return {
            "user_id": self.user_id,
            "session_hash": self.session_hash,
            "authenticated": True
        }
    
    def authenticate_with_samsung_biometric(self, user_id: str = None) -> bool:
        """Authenticate using Samsung biometric (fingerprint, face, etc.)"""
        if not SAMSUNG_AUTH_AVAILABLE:
            print("❌ Samsung biometric authentication not available")
            print("   Make sure samsung_biometric_auth.py is in the same directory")
            return False
        
        print("🔐 Starting Samsung biometric authentication...")
        
        try:
            success, session_data = authenticate_with_samsung(user_id)
            
            if success:
                # Extract session information compatible with existing system
                self.session_token = session_data["session_token"]
                self.user_id = session_data["user_id"]
                self.session_hash = session_data["session_hash"]
                
                # Save enhanced auth data with biometric info
                auth_data = {
                    "user_id": self.user_id,
                    "session_hash": self.session_hash,
                    "session_token": self.session_token,
                    "authenticated_at": session_data["created_at"],
                    "expires_at": session_data["expires_at"],
                    "auth_method": "samsung_biometric",
                    "device_id": session_data.get("device_id"),
                    "device_info": session_data.get("device_info", {})
                }
                
                with open(self.auth_file, 'w') as f:
                    json.dump(auth_data, f, indent=2)
                
                print("✅ Samsung biometric authentication successful!")
                device_model = session_data.get("device_info", {}).get("model", "Unknown Samsung Device")
                print(f"   Device: {device_model}")
                print(f"   User ID: {self.user_id}")
                print(f"   Session: {self.session_hash[:16]}...")
                print(f"   Expires: {auth_data['expires_at']}")
                
                return True
            else:
                print(f"❌ Samsung biometric authentication failed: {session_data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Samsung biometric authentication error: {e}")
            return False
    
    def get_samsung_device_status(self) -> Dict[str, Any]:
        """Get Samsung device information and status"""
        if not SAMSUNG_AUTH_AVAILABLE:
            return {"error": "Samsung authentication not available"}
        
        try:
            return get_samsung_device_info()
        except Exception as e:
            return {"error": str(e)}
    
    def is_biometric_session(self) -> bool:
        """Check if current session was created using biometric authentication"""
        if not self.auth_file.exists():
            return False
        
        try:
            with open(self.auth_file, 'r') as f:
                auth_data = json.load(f)
            auth_method = auth_data.get("auth_method", "")
            return auth_method in ["samsung_biometric", "samsung_fingerprint"]
        except Exception:
            return False
    
    def authenticate_with_fingerprint(self, user_id: str = None) -> bool:
        """Authenticate using Samsung fingerprint (working version)"""
        if not FINGERPRINT_AUTH_AVAILABLE:
            print("❌ Samsung fingerprint authentication not available")
            return False
        
        print("🔐 Starting Samsung fingerprint authentication...")
        
        try:
            # Use the working fingerprint authentication
            fingerprint_auth = SimpleFingerprintAuth()
            success, session_data = fingerprint_auth.authenticate_with_fingerprint(user_id)
            
            if success:
                # Extract session information compatible with existing system
                self.session_token = session_data["session_token"]
                self.user_id = session_data["user_id"]
                self.session_hash = session_data["session_hash"]
                
                # Save enhanced auth data with fingerprint info
                auth_data = {
                    "user_id": self.user_id,
                    "session_hash": self.session_hash,
                    "session_token": self.session_token,
                    "authenticated_at": session_data["created_at"],
                    "expires_at": session_data["expires_at"],
                    "auth_method": "samsung_fingerprint",
                    "device_id": session_data.get("device_id"),
                    "device_info": session_data.get("device_info", {}),
                    "fingerprint_used": True
                }
                
                with open(self.auth_file, 'w') as f:
                    json.dump(auth_data, f, indent=2)
                
                print("✅ Samsung fingerprint authentication successful!")
                device_model = session_data.get("device_info", {}).get("model", "Unknown Samsung Device")
                print(f"   Device: {device_model}")
                print(f"   User ID: {self.user_id}")
                print(f"   Session: {self.session_hash[:16]}...")
                print(f"   Expires: {auth_data['expires_at']}")
                print(f"   👆 Fingerprint authentication used")
                
                return True
            else:
                print(f"❌ Samsung fingerprint authentication failed: {session_data.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Samsung fingerprint authentication error: {e}")
            return False

# Global auth instance
amp_auth = AMPAuth()

def authenticate_user(token: str) -> bool:
    """Authenticate user with provided token"""
    return amp_auth.authenticate(token)

def check_auth() -> bool:
    """Check if user is authenticated"""
    return amp_auth.is_authenticated()

def get_auth_headers() -> Dict[str, str]:
    """Get authentication headers"""
    return amp_auth.get_auth_headers()

def logout_user():
    """Logout current user"""
    amp_auth.logout()

def get_user_info() -> Dict[str, Any]:
    """Get current user information"""
    return amp_auth.get_user_info()

def authenticate_samsung_biometric(user_id: str = None) -> bool:
    """Authenticate using Samsung biometric"""
    return amp_auth.authenticate_with_samsung_biometric(user_id)

def get_samsung_device_status() -> Dict[str, Any]:
    """Get Samsung device information"""
    return amp_auth.get_samsung_device_status()

def is_biometric_session() -> bool:
    """Check if current session uses biometric authentication"""
    return amp_auth.is_biometric_session()

def authenticate_samsung_fingerprint(user_id: str = None) -> bool:
    """Authenticate using Samsung fingerprint (working version)"""
    return amp_auth.authenticate_with_fingerprint(user_id)
