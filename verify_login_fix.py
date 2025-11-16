"""
Quick verification script to check if login API is working correctly.
Run this after starting the Flask server to verify the fix.
"""
import requests
import sys

def verify_login_api():
    """Quick check that login API returns JSON"""
    print("🔍 Verifying Login API Fix...")
    print("-" * 50)
    
    try:
        # Test /api/login endpoint
        response = requests.post(
            'http://localhost:5000/api/login',
            json={'username': 'admin', 'password': 'admin123'},
            timeout=5
        )
        
        # Check if response is JSON
        content_type = response.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            data = response.json()
            
            if data.get('success'):
                print("✅ Login API is working correctly!")
                print(f"   • Endpoint: /api/login")
                print(f"   • Status: {response.status_code}")
                print(f"   • Content-Type: {content_type}")
                print(f"   • Response: Valid JSON")
                print(f"   • Success: {data.get('success')}")
                print("\n✅ No 'Unexpected token' errors!")
                return True
            else:
                print("⚠️  Login failed but JSON is valid")
                print(f"   Message: {data.get('message')}")
                return True
        else:
            print("❌ Login API is returning HTML instead of JSON!")
            print(f"   Content-Type: {content_type}")
            print(f"   This will cause 'Unexpected token' errors")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("   Make sure Flask server is running on port 5000")
        print("   Run: python ad_ai_app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = verify_login_api()
    sys.exit(0 if success else 1)
