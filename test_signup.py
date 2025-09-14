#!/usr/bin/env python3
"""
Simple test script to verify signup functionality
"""

import requests
import json

def test_signup():
    """Test the signup functionality"""
    
    # Test data
    signup_data = {
        "name": "Test User",
        "email": "testuser123@example.com",
        "password": "TestPassword123!",
        "confirm_password": "TestPassword123!"
    }
    
    try:
        print("🧪 Testing signup functionality...")
        
        # Make POST request to signup endpoint
        response = requests.post(
            'http://127.0.0.1:5000/auth/signup',
            json=signup_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"📡 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Signup Response: {data}")
            
            if data.get('success'):
                print("🎉 Signup successful!")
                return True
            else:
                print(f"❌ Signup failed: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP Error {response.status_code}")
            try:
                error_data = response.json()
                print(f"❌ Error details: {error_data}")
            except:
                print(f"❌ Error text: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection error - make sure Flask app is running on http://127.0.0.1:5000")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

if __name__ == "__main__":
    success = test_signup()
    print(f"\n{'✅ TEST PASSED' if success else '❌ TEST FAILED'}")