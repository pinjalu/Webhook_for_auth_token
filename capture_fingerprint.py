#!/usr/bin/env python3
"""
Manual Fingerprint Capture Script
Captures your existing browser fingerprint for use in automation
"""

import json
import time
import os
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('fingerprint_capture.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_chrome_for_capture():
    """Setup Chrome browser for fingerprint capture"""
    try:
        options = Options()
        
        # Use your existing browser settings (no headless mode for manual capture)
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Use your actual user agent (you can check this in your browser)
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        return driver
        
    except Exception as e:
        logger.error(f"Failed to setup Chrome: {e}")
        return None

def capture_fingerprint():
    """Capture comprehensive browser fingerprint"""
    driver = None
    try:
        logger.info("Starting fingerprint capture...")
        
        # Setup Chrome
        driver = setup_chrome_for_capture()
        if not driver:
            return False
        
        # Navigate to ServiceM8 to capture fingerprint in the right context
        logger.info("Navigating to ServiceM8...")
        driver.get("https://go.servicem8.com")
        time.sleep(3)
        
        # Capture comprehensive fingerprint data
        fingerprint_data = {
            "user_agent": driver.execute_script("return navigator.userAgent"),
            "platform": driver.execute_script("return navigator.platform"),
            "language": driver.execute_script("return navigator.language"),
            "languages": driver.execute_script("return navigator.languages"),
            "timezone": driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone"),
            "screen_resolution": driver.execute_script("return screen.width + 'x' + screen.height"),
            "color_depth": driver.execute_script("return screen.colorDepth"),
            "pixel_ratio": driver.execute_script("return window.devicePixelRatio"),
            "webgl_vendor": driver.execute_script("""
                try {
                    var canvas = document.createElement('canvas');
                    var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                    return gl ? gl.getParameter(gl.VENDOR) : 'unknown';
                } catch(e) { return 'unknown'; }
            """),
            "webgl_renderer": driver.execute_script("""
                try {
                    var canvas = document.createElement('canvas');
                    var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                    return gl ? gl.getParameter(gl.RENDERER) : 'unknown';
                } catch(e) { return 'unknown'; }
            """),
            "hardware_concurrency": driver.execute_script("return navigator.hardwareConcurrency"),
            "max_touch_points": driver.execute_script("return navigator.maxTouchPoints"),
            "cookie_enabled": driver.execute_script("return navigator.cookieEnabled"),
            "do_not_track": driver.execute_script("return navigator.doNotTrack"),
            "timestamp": time.time(),
            "capture_method": "manual",
            "capture_date": datetime.now().isoformat()
        }
        
        # Save fingerprint data
        fingerprint_file = "device_fingerprint.json"
        with open(fingerprint_file, 'w') as f:
            json.dump(fingerprint_data, f, indent=2)
        
        logger.info(f"Fingerprint captured and saved to: {fingerprint_file}")
        
        # Display captured data
        print("\n" + "="*60)
        print("🎯 FINGERPRINT CAPTURED SUCCESSFULLY!")
        print("="*60)
        print(f"📱 User Agent: {fingerprint_data['user_agent']}")
        print(f"💻 Platform: {fingerprint_data['platform']}")
        print(f"🌍 Language: {fingerprint_data['language']}")
        print(f"📺 Screen Resolution: {fingerprint_data['screen_resolution']}")
        print(f"🕐 Timezone: {fingerprint_data['timezone']}")
        print(f"🎮 WebGL Vendor: {fingerprint_data['webgl_vendor']}")
        print(f"🎮 WebGL Renderer: {fingerprint_data['webgl_renderer']}")
        print(f"⚡ Hardware Concurrency: {fingerprint_data['hardware_concurrency']}")
        print("="*60)
        print("✅ This fingerprint will be used for automation")
        print("✅ It should help avoid 'new location' detection")
        print("="*60)
        print("\n📋 NEXT STEPS:")
        print("1. Run your automation script (main1.py)")
        print("2. The script will use this fingerprint automatically")
        print("3. You should see 'Applied existing device fingerprint' in logs")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to capture fingerprint: {e}")
        return False
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("Browser closed")
            except:
                pass

def main():
    """Main function"""
    try:
        print("🔍 ServiceM8 Fingerprint Capture Tool")
        print("="*40)
        print("This tool captures your browser fingerprint")
        print("to help avoid 'new location' detection in automation.")
        print("="*40)
        
        # Check if fingerprint already exists
        if os.path.exists("device_fingerprint.json"):
            print("⚠️  Existing fingerprint found!")
            response = input("Do you want to overwrite it? (y/n): ").lower()
            if response != 'y':
                print("❌ Fingerprint capture cancelled")
                return
        
        # Capture fingerprint
        if capture_fingerprint():
            print("🎉 Fingerprint capture completed successfully!")
        else:
            print("❌ Fingerprint capture failed!")
            
    except KeyboardInterrupt:
        print("\n❌ Fingerprint capture cancelled by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
