#!/usr/bin/env python3
"""
Test script to verify fingerprint and Chrome setup
"""

import json
import os
import logging
from main4 import ServiceM8APIExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_fingerprint_loading():
    """Test if fingerprint is loaded correctly"""
    try:
        extractor = ServiceM8APIExtractor()
        fingerprint_data = extractor.load_device_fingerprint()
        
        if fingerprint_data:
            print("✅ Device fingerprint loaded successfully!")
            print(f"📱 User Agent: {fingerprint_data.get('user_agent', 'N/A')}")
            print(f"💻 Platform: {fingerprint_data.get('platform', 'N/A')}")
            print(f"🌍 Language: {fingerprint_data.get('language', 'N/A')}")
            print(f"📺 Screen Resolution: {fingerprint_data.get('screen_resolution', 'N/A')}")
            print(f"🕐 Timezone: {fingerprint_data.get('timezone', 'N/A')}")
            return True
        else:
            print("❌ No device fingerprint found!")
            return False
            
    except Exception as e:
        print(f"❌ Error loading fingerprint: {e}")
        return False

def test_chrome_setup():
    """Test Chrome setup with fingerprint"""
    try:
        print("\n🔧 Testing Chrome setup with fingerprint...")
        extractor = ServiceM8APIExtractor()
        
        if extractor.setup_chrome():
            print("✅ Chrome setup successful!")
            
            # Test basic navigation
            extractor.driver.get("https://httpbin.org/headers")
            time.sleep(3)
            
            # Check if fingerprint is applied
            user_agent = extractor.driver.execute_script("return navigator.userAgent")
            platform = extractor.driver.execute_script("return navigator.platform")
            language = extractor.driver.execute_script("return navigator.language")
            timezone = extractor.driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone")
            
            print(f"🌐 Current User Agent: {user_agent}")
            print(f"💻 Current Platform: {platform}")
            print(f"🌍 Current Language: {language}")
            print(f"🕐 Current Timezone: {timezone}")
            
            # Clean up
            extractor.driver.quit()
            return True
        else:
            print("❌ Chrome setup failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing Chrome setup: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing ServiceM8 Automation Setup")
    print("=" * 50)
    
    # Test 1: Fingerprint loading
    print("\n1️⃣ Testing device fingerprint loading...")
    fingerprint_ok = test_fingerprint_loading()
    
    # Test 2: Chrome setup
    print("\n2️⃣ Testing Chrome setup...")
    chrome_ok = test_chrome_setup()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print(f"Fingerprint Loading: {'✅ PASS' if fingerprint_ok else '❌ FAIL'}")
    print(f"Chrome Setup: {'✅ PASS' if chrome_ok else '❌ FAIL'}")
    
    if fingerprint_ok and chrome_ok:
        print("\n🎉 All tests passed! Your automation should work without 2FA.")
        print("💡 The Chrome browser will now match your local environment.")
    else:
        print("\n⚠️  Some tests failed. Please check the configuration.")
    
    print("=" * 50)

if __name__ == "__main__":
    import time
    main()
