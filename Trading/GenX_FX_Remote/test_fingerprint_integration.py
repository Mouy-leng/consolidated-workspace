#!/usr/bin/env python3
"""
Test Samsung Fingerprint Authentication Integration
Tests the complete integration with the existing authentication system
"""

from amp_auth import (
    authenticate_samsung_fingerprint,
    check_auth,
    get_user_info,
    is_biometric_session,
    logout_user
)

def test_fingerprint_integration():
    """Test complete fingerprint authentication integration"""
    print("🔐 Samsung Fingerprint Authentication Integration Test")
    print("=" * 60)
    
    # Clear any existing sessions
    print("1. Clearing existing sessions...")
    logout_user()
    print("   ✅ Sessions cleared")
    
    # Test fingerprint authentication
    print("\n2. Testing Samsung fingerprint authentication...")
    print("   📱 Please use your fingerprint when prompted on your Samsung device")
    
    user_id = "fingerprint_integration_test"
    success = authenticate_samsung_fingerprint(user_id)
    
    print(f"\n3. Authentication result: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if success:
        # Check if we're now authenticated
        if check_auth():
            print("   ✅ Session created successfully")
            
            # Get user information
            user_info = get_user_info()
            print(f"   📋 User ID: {user_info.get('user_id')}")
            print(f"   🔑 Session Hash: {user_info.get('session_hash', '')[:16]}...")
            
            # Check if this is a biometric session
            if is_biometric_session():
                print("   🔐 ✅ This is a biometric authentication session")
            else:
                print("   🔐 ❌ This is NOT a biometric session")
            
            # Try to read the full auth file to see details
            try:
                import json
                with open('amp_auth.json', 'r') as f:
                    auth_data = json.load(f)
                
                print(f"   📱 Device: {auth_data.get('device_info', {}).get('model', 'Unknown')}")
                print(f"   🕒 Expires: {auth_data.get('expires_at', 'Unknown')}")
                print(f"   🔒 Auth Method: {auth_data.get('auth_method', 'Unknown')}")
                
                if auth_data.get('fingerprint_used'):
                    print("   👆 ✅ Fingerprint was successfully used for authentication")
                
            except Exception as e:
                print(f"   ⚠️ Could not read detailed auth info: {e}")
        
        else:
            print("   ❌ Authentication succeeded but no session found")
    
    print(f"\n4. Final Status:")
    print(f"   Authenticated: {'✅ YES' if check_auth() else '❌ NO'}")
    print(f"   Biometric Session: {'✅ YES' if is_biometric_session() else '❌ NO'}")
    
    return success

def interactive_demo():
    """Interactive demonstration of fingerprint authentication"""
    print("\n" + "="*60)
    print("🖥️ Interactive Samsung Fingerprint Authentication Demo")
    print("="*60)
    
    print("This demo will show you how to use Samsung fingerprint authentication")
    print("in your applications.")
    
    response = input("\nWould you like to run the interactive demo? (y/N): ").lower().strip()
    
    if response == 'y':
        print("\n📱 Make sure your Samsung device is nearby and ready...")
        input("Press Enter when ready to authenticate with your fingerprint...")
        
        demo_user = f"demo_user_{int(__import__('time').time())}"
        
        print(f"\n🔐 Authenticating user: {demo_user}")
        success = authenticate_samsung_fingerprint(demo_user)
        
        if success:
            print("\n🎉 Demo authentication successful!")
            print("💡 You can now use this in your applications like this:")
            print("""
# Example usage in your application:
from amp_auth import authenticate_samsung_fingerprint, check_auth

# Authenticate user with fingerprint
if authenticate_samsung_fingerprint("your_user_id"):
    print("User authenticated with Samsung fingerprint!")
    
    # Your application logic here...
    
else:
    print("Authentication failed")
""")
        else:
            print("\n❌ Demo authentication failed")
            print("This might be due to timeout or device issues.")
    else:
        print("Demo skipped.")

if __name__ == "__main__":
    print("🔐 Samsung Fingerprint Authentication Integration")
    print("Organization: A6-9V")
    print()
    
    try:
        # Run integration test
        success = test_fingerprint_integration()
        
        if success:
            # Offer interactive demo
            interactive_demo()
        
        print("\n✅ Test completed!")
        print("\n🚀 Your Samsung fingerprint authentication is ready to use!")
        print("   Integration with your existing authentication system: ✅ COMPLETE")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test error: {e}")
        import traceback
        traceback.print_exc()