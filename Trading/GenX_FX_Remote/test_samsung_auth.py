#!/usr/bin/env python3
"""
Test script for Samsung Biometric Authentication
Demonstrates integration with existing authentication system
"""

import json
import time
from amp_auth import (
    authenticate_samsung_biometric, 
    get_samsung_device_status, 
    is_biometric_session,
    check_auth,
    get_user_info,
    logout_user
)

def test_samsung_device_info():
    """Test Samsung device information retrieval"""
    print("📱 Samsung Device Information")
    print("=" * 40)
    
    device_info = get_samsung_device_status()
    
    if "error" not in device_info:
        print(f"✅ Device Connected: {device_info['device_id']}")
        print(f"   Model: {device_info['model']}")
        print(f"   Android: {device_info['android_version']}")
        print(f"   Build: {device_info['build_info']}")
        return True
    else:
        print(f"❌ Error: {device_info['error']}")
        return False

def test_biometric_authentication():
    """Test Samsung biometric authentication"""
    print("\n🔐 Samsung Biometric Authentication Test")
    print("=" * 50)
    
    # Test authentication
    print("Starting authentication...")
    
    # First, logout any existing session
    logout_user()
    
    # Use a simulated approach since the full biometric flow needs user interaction
    # In real usage, this would prompt for fingerprint/face unlock
    
    # For testing, let's simulate the authentication flow
    from samsung_biometric_auth import SamsungBiometricAuth
    
    samsung_auth = SamsungBiometricAuth('R58N204KC4H')
    
    try:
        # Install fallback helper
        samsung_auth.install_fallback_helper()
        
        # Simulate authentication result parsing
        import subprocess
        result = subprocess.run([
            'adb', '-s', 'R58N204KC4H', 'shell', 'sh', '/data/local/tmp/biometric_fallback.sh'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Biometric authentication simulation successful")
            
            # Parse the authentication data
            auth_data = {}
            for line in result.stdout.strip().split('\n'):
                if '=' in line:
                    key, value = line.split('=', 1)
                    auth_data[key] = value
            
            print(f"   Status: {auth_data.get('AUTH_STATUS')}")
            print(f"   Device: {auth_data.get('DEVICE_MODEL')}")
            print(f"   Token: {auth_data.get('AUTH_TOKEN', '')[:16]}...")
            
            return True
        else:
            print("❌ Authentication simulation failed")
            return False
            
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False
    finally:
        samsung_auth.cleanup()

def test_session_management():
    """Test session management with Samsung authentication"""
    print("\n📋 Session Management Test")
    print("=" * 35)
    
    # Check current authentication status
    if check_auth():
        print("✅ Already authenticated")
        
        user_info = get_user_info()
        print(f"   User ID: {user_info.get('user_id', 'Unknown')}")
        print(f"   Session: {user_info.get('session_hash', '')[:16]}...")
        
        # Check if this is a biometric session
        if is_biometric_session():
            print("   🔐 This is a biometric authentication session")
        else:
            print("   🔑 This is a regular authentication session")
        
    else:
        print("❌ Not currently authenticated")

def test_integration_workflow():
    """Test complete integration workflow"""
    print("\n🔄 Integration Workflow Test")
    print("=" * 40)
    
    # Step 1: Check device
    print("1. Checking Samsung device...")
    if not test_samsung_device_info():
        print("   ⚠️ Device check failed, but continuing with test")
    
    # Step 2: Clear any existing session
    print("\n2. Clearing existing sessions...")
    logout_user()
    print("   ✅ Sessions cleared")
    
    # Step 3: Test authentication (simulated)
    print("\n3. Testing authentication flow...")
    test_biometric_authentication()
    
    # Step 4: Check session management
    print("\n4. Testing session management...")
    test_session_management()
    
    print("\n🎯 Integration test completed!")

def interactive_test():
    """Interactive test that allows user to test real authentication"""
    print("\n🖥️  Interactive Samsung Authentication Test")
    print("=" * 50)
    print("This test will attempt to authenticate using your Samsung device.")
    print("Make sure your Samsung device is unlocked and ready.")
    
    response = input("\nProceed with interactive test? (y/N): ").lower().strip()
    
    if response == 'y':
        print("\n🔐 Starting interactive authentication...")
        print("⚠️  You will need to respond to prompts on your Samsung device")
        
        # Attempt actual biometric authentication
        user_id = f"test_user_{int(time.time())}"
        
        if authenticate_samsung_biometric(user_id):
            print("🎉 Interactive authentication successful!")
            
            # Show session info
            if check_auth():
                user_info = get_user_info()
                print(f"   Authenticated as: {user_info.get('user_id')}")
                
                if is_biometric_session():
                    print("   🔐 Biometric session active")
                
        else:
            print("❌ Interactive authentication failed")
            print("   This is normal if using fallback mode")
    else:
        print("Interactive test skipped.")

if __name__ == "__main__":
    print("🔐 Samsung Biometric Authentication Test Suite")
    print("=" * 55)
    print("Testing integration between Samsung device and authentication system")
    print(f"Organization: A6-9V")
    print()
    
    try:
        # Run automated tests
        test_integration_workflow()
        
        # Offer interactive test
        interactive_test()
        
        print("\n✅ All tests completed!")
        print("\nNext steps:")
        print("1. Build the Android app for full biometric support")
        print("2. Install the app on your Samsung device")
        print("3. Test real fingerprint/face authentication")
        print("4. Integrate with your applications")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
        import traceback
        traceback.print_exc()