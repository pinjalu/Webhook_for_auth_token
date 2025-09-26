#!/usr/bin/env python3
"""
Simple ServiceM8 API Token & Cookie Extractor
Extracts tokens and cookies for specific APIs without saving files
"""

import json
import time
import os
import logging
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('servicem8_extractor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ServiceM8APIExtractor:
    def __init__(self, max_retries=3):
        self.driver = None
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.auth_code = os.getenv("AUTH_CODE")  # For 2FA
        self.max_retries = max_retries
        self.is_server = os.getenv("SERVER_MODE", "false").lower() == "true"
        self.device_fingerprint_file = "device_fingerprint.json"
        self.screenshots_folder = "screenshots"
        self._create_screenshots_folder()
        logger.info("ServiceM8APIExtractor initialized")
    
    def _create_screenshots_folder(self):
        """Create screenshots folder if it doesn't exist"""
        try:
            if not os.path.exists(self.screenshots_folder):
                os.makedirs(self.screenshots_folder)
                logger.info(f"Screenshots folder created: {self.screenshots_folder}")
        except Exception as e:
            logger.warning(f"Failed to create screenshots folder: {e}")
    
    def take_screenshot(self, description):
        """Take a screenshot with timestamp and description"""
        try:
            if not self.driver:
                logger.warning("Cannot take screenshot - driver not initialized")
                return False
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{description}.png"
            filepath = os.path.join(self.screenshots_folder, filename)
            
            self.driver.save_screenshot(filepath)
            logger.info(f"Screenshot saved: {filepath}")
            return True
        except Exception as e:
            logger.warning(f"Failed to take screenshot '{description}': {e}")
            return False
        
    def setup_chrome(self):
        """Setup Chrome with retry mechanism for browser initialization failures"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Chrome browser setup attempt {attempt + 1}/{self.max_retries}")
                
                # Clean up any existing driver instance
                if self.driver:
                    try:
                        self.driver.quit()
                    except:
                        pass
                    self.driver = None
                
                options = Options()
                
                # Server-specific options - use Chrome's default temporary profile
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                # Enable headless mode for server environment
                if self.is_server:
                    options.add_argument("--headless=new")
                    logger.info("Running in server mode with headless browser")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                # Use consistent user agent to mimic existing device
                consistent_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                options.add_argument(f"--user-agent={consistent_user_agent}")
                
                # Add consistent browser fingerprinting to avoid "new location" detection
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Add consistent viewport and screen resolution
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--start-maximized")
                
                # Add consistent timezone (adjust as needed for your location)
                options.add_argument("--timezone=Australia/Sydney")
                
                # Add consistent language preferences
                options.add_argument("--lang=en-AU")
                options.add_argument("--accept-lang=en-AU,en;q=0.9")
                
                # Add consistent device characteristics
                options.add_argument("--force-device-scale-factor=1")
                options.add_argument("--high-dpi-support=1")
                
                # Add consistent network characteristics
                options.add_argument("--disable-background-networking")
                options.add_argument("--disable-default-apps")
                options.add_argument("--disable-sync")
                
                # Additional stability options for server environment
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument("--disable-images")
                options.add_argument("--disable-web-security")
                options.add_argument("--allow-running-insecure-content")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-logging")
                options.add_argument("--disable-default-apps")
                options.add_argument("--disable-sync")
                options.add_argument("--disable-translate")
                options.add_argument("--hide-scrollbars")
                options.add_argument("--mute-audio")
                options.add_argument("--no-first-run")
                options.add_argument("--disable-hang-monitor")
                options.add_argument("--disable-prompt-on-repost")
                options.add_argument("--disable-client-side-phishing-detection")
                options.add_argument("--disable-component-update")
                options.add_argument("--disable-domain-reliability")
                options.add_argument("--disable-features=TranslateUI")
                options.add_argument("--disable-ipc-flooding-protection")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-features=VizDisplayCompositor")
                options.add_argument("--disable-field-trial-config")
                options.add_argument("--disable-back-forward-cache")
                options.add_argument("--disable-background-networking")
                options.add_argument("--disable-breakpad")
                options.add_argument("--disable-component-extensions-with-background-pages")
                options.add_argument("--disable-extensions-file-access-check")
                options.add_argument("--disable-extensions-http-throttling")
                options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
                options.add_argument("--disable-hang-monitor")
                options.add_argument("--disable-ipc-flooding-protection")
                options.add_argument("--disable-popup-blocking")
                options.add_argument("--disable-prompt-on-repost")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-sync")
                options.add_argument("--force-color-profile=srgb")
                options.add_argument("--metrics-recording-only")
                options.add_argument("--no-first-run")
                options.add_argument("--safebrowsing-disable-auto-update")
                options.add_argument("--enable-automation")
                options.add_argument("--password-store=basic")
                options.add_argument("--use-mock-keychain")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu-sandbox")
                options.add_argument("--disable-software-rasterizer")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-features=TranslateUI")
                options.add_argument("--disable-ipc-flooding-protection")
                options.add_argument("--disable-hang-monitor")
                options.add_argument("--disable-prompt-on-repost")
                options.add_argument("--disable-sync")
                options.add_argument("--force-color-profile=srgb")
                options.add_argument("--metrics-recording-only")
                options.add_argument("--no-first-run")
                options.add_argument("--safebrowsing-disable-auto-update")
                options.add_argument("--enable-automation")
                options.add_argument("--password-store=basic")
                options.add_argument("--use-mock-keychain")
                
                # Additional server-specific options to prevent conflicts
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-features=VizDisplayCompositor")
                options.add_argument("--disable-field-trial-config")
                options.add_argument("--disable-back-forward-cache")
                options.add_argument("--disable-background-networking")
                options.add_argument("--disable-breakpad")
                options.add_argument("--disable-component-extensions-with-background-pages")
                options.add_argument("--disable-extensions-file-access-check")
                options.add_argument("--disable-extensions-http-throttling")
                options.add_argument("--disable-features=TranslateUI,BlinkGenPropertyTrees")
                options.add_argument("--disable-hang-monitor")
                options.add_argument("--disable-ipc-flooding-protection")
                options.add_argument("--disable-popup-blocking")
                options.add_argument("--disable-prompt-on-repost")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-sync")
                options.add_argument("--force-color-profile=srgb")
                options.add_argument("--metrics-recording-only")
                options.add_argument("--no-first-run")
                options.add_argument("--safebrowsing-disable-auto-update")
                options.add_argument("--enable-automation")
                options.add_argument("--password-store=basic")
                options.add_argument("--use-mock-keychain")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu-sandbox")
                options.add_argument("--disable-software-rasterizer")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-features=TranslateUI")
                options.add_argument("--disable-ipc-flooding-protection")
                options.add_argument("--disable-hang-monitor")
                options.add_argument("--disable-prompt-on-repost")
                options.add_argument("--disable-sync")
                options.add_argument("--force-color-profile=srgb")
                options.add_argument("--metrics-recording-only")
                options.add_argument("--no-first-run")
                options.add_argument("--safebrowsing-disable-auto-update")
                options.add_argument("--enable-automation")
                options.add_argument("--password-store=basic")
                options.add_argument("--use-mock-keychain")
                
                # Try to kill any existing Chrome processes
                try:
                    import subprocess
                    import psutil
                    
                    # Kill all Chrome processes
                    for proc in psutil.process_iter(['pid', 'name']):
                        try:
                            if proc.info['name'] and ('chrome' in proc.info['name'].lower() or 'chromedriver' in proc.info['name'].lower()):
                                proc.kill()
                        except (psutil.NoSuchProcess, psutil.AccessDenied):
                            pass
                    
                    # Also try pkill as backup
                    subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True, timeout=5)
                    subprocess.run(["pkill", "-9", "-f", "chromedriver"], capture_output=True, timeout=5)
                    time.sleep(2)
                except Exception as e:
                    logger.debug(f"Process cleanup failed: {e}")
                    pass
                
                self.driver = webdriver.Chrome(options=options)
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                # Load and apply device fingerprint to maintain consistent identity
                fingerprint_data = self.load_device_fingerprint()
                if fingerprint_data:
                    self.apply_device_fingerprint(fingerprint_data)
                    logger.info("Applied existing device fingerprint to avoid 'new location' detection")
                else:
                    logger.info("No existing fingerprint found, will create new one after first successful login")
                
                # Test if browser is working
                self.driver.get("about:blank")
                logger.info("Chrome browser setup successful")
                return True
                
            except WebDriverException as e:
                logger.error(f"WebDriver setup failed on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    return False
            except Exception as e:
                logger.error(f"Unexpected error during Chrome setup attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    return False
        
        return False
    
    def check_website_responsiveness(self, url):
        """Check if website is responsive by making a simple request"""
        try:
            import requests
            response = requests.get(url, timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Website responsiveness check failed: {e}")
            return False

    def load_website_with_retry(self, url, max_retries=3):
        """Load website with retry mechanism for loading failures"""
        for attempt in range(max_retries):
            try:
                logger.info(f"Loading website attempt {attempt + 1}/{max_retries}: {url}")
                
                # Check website responsiveness first
                if attempt == 0:  # Only check on first attempt
                    if not self.check_website_responsiveness(url):
                        logger.warning("Website responsiveness check failed, but continuing with browser load")
                
                self.driver.get(url)
                
                # Wait for page to load completely
                WebDriverWait(self.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                
                # Additional check for ServiceM8 specific elements
                if "servicem8.com" in url:
                    WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                
                # Verify page loaded correctly by checking title or URL
                current_url = self.driver.current_url
                if current_url and not current_url.startswith("data:"):
                    logger.info(f"Website loaded successfully on attempt {attempt + 1}")
                    return True
                else:
                    logger.warning(f"Website may not have loaded correctly - URL: {current_url}")
                    if attempt < max_retries - 1:
                        time.sleep(5)
                    else:
                        return False
                
            except TimeoutException as e:
                logger.warning(f"Website loading timeout on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    logger.error("Failed to load website after all retry attempts")
                    return False
                    
            except Exception as e:
                logger.warning(f"Website loading error on attempt {attempt + 1}: {e}")
                if attempt < max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    logger.error("Failed to load website after all retry attempts")
                    return False
        
        return False

    def save_device_fingerprint(self):
        """Save device fingerprint to maintain consistent identity"""
        try:
            if not self.driver:
                return False
                
            # Get browser fingerprint data
            fingerprint_data = {
                "user_agent": self.driver.execute_script("return navigator.userAgent"),
                "platform": self.driver.execute_script("return navigator.platform"),
                "language": self.driver.execute_script("return navigator.language"),
                "languages": self.driver.execute_script("return navigator.languages"),
                "timezone": self.driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone"),
                "screen_resolution": self.driver.execute_script("return screen.width + 'x' + screen.height"),
                "color_depth": self.driver.execute_script("return screen.colorDepth"),
                "pixel_ratio": self.driver.execute_script("return window.devicePixelRatio"),
                "webgl_vendor": self.driver.execute_script("""
                    try {
                        var canvas = document.createElement('canvas');
                        var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        return gl ? gl.getParameter(gl.VENDOR) : 'unknown';
                    } catch(e) { return 'unknown'; }
                """),
                "webgl_renderer": self.driver.execute_script("""
                    try {
                        var canvas = document.createElement('canvas');
                        var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        return gl ? gl.getParameter(gl.RENDERER) : 'unknown';
                    } catch(e) { return 'unknown'; }
                """),
                "timestamp": time.time()
            }
            
            with open(self.device_fingerprint_file, 'w') as f:
                json.dump(fingerprint_data, f, indent=2)
            
            logger.info("Device fingerprint saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save device fingerprint: {e}")
            return False

    def load_device_fingerprint(self):
        """Load existing device fingerprint to maintain consistent identity"""
        try:
            if not os.path.exists(self.device_fingerprint_file):
                logger.info("No device fingerprint found, will create new one")
                return None
            
            with open(self.device_fingerprint_file, 'r') as f:
                fingerprint_data = json.load(f)
            
            # Check if fingerprint is recent (within 30 days)
            current_time = time.time()
            fingerprint_age = current_time - fingerprint_data.get('timestamp', 0)
            if fingerprint_age > 30 * 24 * 60 * 60:  # 30 days
                logger.info("Device fingerprint is too old, will create new one")
                return None
            
            logger.info("Loaded existing device fingerprint")
            return fingerprint_data
            
        except Exception as e:
            logger.error(f"Failed to load device fingerprint: {e}")
            return None

    def apply_device_fingerprint(self, fingerprint_data):
        """Apply device fingerprint to browser to maintain consistent identity"""
        try:
            if not fingerprint_data or not self.driver:
                return False
            
            # Apply fingerprint data using JavaScript
            js_code = f"""
                // Override navigator properties
                Object.defineProperty(navigator, 'userAgent', {{
                    get: function() {{ return '{fingerprint_data.get('user_agent', '')}'; }}
                }});
                
                Object.defineProperty(navigator, 'platform', {{
                    get: function() {{ return '{fingerprint_data.get('platform', '')}'; }}
                }});
                
                Object.defineProperty(navigator, 'language', {{
                    get: function() {{ return '{fingerprint_data.get('language', '')}'; }}
                }});
                
                Object.defineProperty(navigator, 'languages', {{
                    get: function() {{ return {fingerprint_data.get('languages', [])}; }}
                }});
                
                // Override screen properties
                Object.defineProperty(screen, 'width', {{
                    get: function() {{ return {fingerprint_data.get('screen_resolution', '1920x1080').split('x')[0]}; }}
                }});
                
                Object.defineProperty(screen, 'height', {{
                    get: function() {{ return {fingerprint_data.get('screen_resolution', '1920x1080').split('x')[1]}; }}
                }});
                
                Object.defineProperty(screen, 'colorDepth', {{
                    get: function() {{ return {fingerprint_data.get('color_depth', 24)}; }}
                }});
                
                // Override device pixel ratio
                Object.defineProperty(window, 'devicePixelRatio', {{
                    get: function() {{ return {fingerprint_data.get('pixel_ratio', 1)}; }}
                }});
            """
            
            self.driver.execute_script(js_code)
            logger.info("Device fingerprint applied successfully")
            return True
            
                except Exception as e:
            logger.error(f"Failed to apply device fingerprint: {e}")
            return False

    def capture_manual_fingerprint(self):
        """Capture fingerprint from manual browser session for reuse in automation"""
        try:
            logger.info("Starting manual fingerprint capture...")
            
            # Setup Chrome for manual fingerprint capture
            if not self.setup_chrome():
                logger.error("Failed to setup Chrome for fingerprint capture")
                return False
            
            # Navigate to ServiceM8 to capture fingerprint
            self.driver.get("https://go.servicem8.com")
            time.sleep(3)
            
            # Capture comprehensive fingerprint data
            fingerprint_data = {
                "user_agent": self.driver.execute_script("return navigator.userAgent"),
                "platform": self.driver.execute_script("return navigator.platform"),
                "language": self.driver.execute_script("return navigator.language"),
                "languages": self.driver.execute_script("return navigator.languages"),
                "timezone": self.driver.execute_script("return Intl.DateTimeFormat().resolvedOptions().timeZone"),
                "screen_resolution": self.driver.execute_script("return screen.width + 'x' + screen.height"),
                "color_depth": self.driver.execute_script("return screen.colorDepth"),
                "pixel_ratio": self.driver.execute_script("return window.devicePixelRatio"),
                "webgl_vendor": self.driver.execute_script("""
                    try {
                        var canvas = document.createElement('canvas');
                        var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        return gl ? gl.getParameter(gl.VENDOR) : 'unknown';
                    } catch(e) { return 'unknown'; }
                """),
                "webgl_renderer": self.driver.execute_script("""
                    try {
                        var canvas = document.createElement('canvas');
                        var gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
                        return gl ? gl.getParameter(gl.RENDERER) : 'unknown';
                    } catch(e) { return 'unknown'; }
                """),
                "hardware_concurrency": self.driver.execute_script("return navigator.hardwareConcurrency"),
                "max_touch_points": self.driver.execute_script("return navigator.maxTouchPoints"),
                "cookie_enabled": self.driver.execute_script("return navigator.cookieEnabled"),
                "do_not_track": self.driver.execute_script("return navigator.doNotTrack"),
                "timestamp": time.time(),
                "capture_method": "manual"
            }
            
            # Save fingerprint data
            with open(self.device_fingerprint_file, 'w') as f:
                json.dump(fingerprint_data, f, indent=2)
            
            logger.info("Manual fingerprint captured and saved successfully!")
            logger.info(f"Fingerprint saved to: {self.device_fingerprint_file}")
            
            # Display captured data
            print("\n" + "="*50)
            print("CAPTURED FINGERPRINT DATA:")
            print("="*50)
            print(f"User Agent: {fingerprint_data['user_agent']}")
            print(f"Platform: {fingerprint_data['platform']}")
            print(f"Language: {fingerprint_data['language']}")
            print(f"Screen Resolution: {fingerprint_data['screen_resolution']}")
            print(f"Timezone: {fingerprint_data['timezone']}")
            print(f"WebGL Vendor: {fingerprint_data['webgl_vendor']}")
            print(f"WebGL Renderer: {fingerprint_data['webgl_renderer']}")
            print("="*50)
            print("This fingerprint will be used for automation to avoid 'new location' detection.")
            print("="*50 + "\n")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to capture manual fingerprint: {e}")
            return False
        finally:
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass

    def handle_2fa_authentication(self):
        """Handle 2FA authentication code input"""
        try:
            logger.info("Checking for 2FA authentication page...")
            
            # Wait for potential 2FA page to load
            time.sleep(3)
            
            # Check if we're on 2FA page
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            if "authentication code" in page_source or "enter your authentication" in page_source:
                logger.info("2FA authentication page detected")
                self.take_screenshot("2fa_page_detected")
                
                if not self.auth_code:
                    logger.error("2FA authentication code required but AUTH_CODE environment variable not set")
                return False
                
                # Find and fill the authentication code input
                auth_code_selectors = [
                    "input[type='text']",
                    "input[type='number']", 
                    "input[name*='code']",
                    "input[id*='code']",
                    "input[placeholder*='code']",
                    "input[placeholder*='digit']"
                ]
                
                auth_input = None
                for selector in auth_code_selectors:
                    try:
                        auth_input = self.driver.find_element(By.CSS_SELECTOR, selector)
                        logger.info(f"Found auth code input using selector: {selector}")
                        break
                    except:
                        continue
                
                if not auth_input:
                    logger.error("Could not find authentication code input field")
                    return False
                
                # Clear and enter the authentication code
                auth_input.clear()
                auth_input.send_keys(self.auth_code)
                logger.info("Authentication code entered")
                
                # Find and click continue button
                continue_selectors = [
                    "button[type='submit']",
                    "input[type='submit']",
                    "button:contains('Continue')",
                    "input[value*='Continue']",
                    "button:contains('Verify')",
                    "input[value*='Verify']"
                ]
                
                continue_button = None
                for selector in continue_selectors:
                    try:
                        if ":contains" in selector:
                            # Use XPath for text-based selectors
                            xpath_selector = f"//button[contains(text(), '{selector.split(':contains(')[1].split(')')[0]}')]"
                            continue_button = self.driver.find_element(By.XPATH, xpath_selector)
                        else:
                            continue_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        logger.info(f"Found continue button using selector: {selector}")
                        break
                    except:
                        continue
                
                if not continue_button:
                    # Try to find any button with continue/verify text
                    try:
                        continue_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Continue') or contains(text(), 'Verify')]")
                    except:
                        pass
                
                if continue_button:
                    continue_button.click()
                    logger.info("Continue button clicked")
                    time.sleep(5)
                    
                    # Check if 2FA was successful
                    new_url = self.driver.current_url
                    if "login" not in new_url.lower() and "servicem8.com" in new_url:
                        logger.info("2FA authentication successful")
                        self.take_screenshot("2fa_success")
                return True
            else:
                        logger.warning("2FA authentication may have failed")
                return False
                else:
                    logger.error("Could not find continue/verify button")
                    return False
            else:
                logger.info("No 2FA authentication page detected")
                return True
                
        except Exception as e:
            logger.error(f"Error handling 2FA authentication: {e}")
            return False

    def close_popup(self):
        """Close popup if present"""
        try:
            # Primary selectors for ExtJS close button based on the provided HTML
            primary_selectors = [
                "//div[@id='ext-gen17']",  # Direct ID selector
                "//div[@class='x-tool x-tool-close']",  # Class selector
                "//div[contains(@class, 'x-tool x-tool-close')]",  # Partial class match
                "//*[contains(@class, 'x-tool-close')]"  # Any element with x-tool-close class
            ]
            
            for selector in primary_selectors:
                try:
                    close_element = self.driver.find_element(By.XPATH, selector)
                    # Take screenshot before closing popup
                    self.take_screenshot("before_popup_close")
                    # Use ActionChains for more reliable clicking
                    action = ActionChains(self.driver)
                    action.move_to_element(close_element).click().perform()
                    logger.info(f"Popup closed successfully using selector: {selector}")
                    time.sleep(2)
                    # Take screenshot after closing popup
                    self.take_screenshot("after_popup_close")
                    return True
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # Try CSS selector as well
            try:
                close_element = self.driver.find_element(By.CSS_SELECTOR, ".x-tool.x-tool-close")
                # Take screenshot before closing popup
                self.take_screenshot("before_popup_close_css")
                action = ActionChains(self.driver)
                action.move_to_element(close_element).click().perform()
                logger.info("Popup closed successfully using CSS selector: .x-tool.x-tool-close")
                time.sleep(2)
                # Take screenshot after closing popup
                self.take_screenshot("after_popup_close_css")
                return True
            except Exception as e:
                logger.debug(f"CSS selector failed: {e}")
            
            # Fallback selectors
            fallback_selectors = [
                "//*[@id='ext-gen17']",
                "//div[contains(@class, 'x-window-header')]//div[contains(@class, 'x-tool-close')]",
                "//div[contains(@class, 'x-window-header')]//div[contains(@class, 'x-tool')]",
                "//span[contains(text(), 'Updates')]/../div[contains(@class, 'x-tool-close')]",
                "//*[contains(@class, 'x-window-header-text') and contains(text(), 'Updates')]/../div[contains(@class, 'x-tool-close')]"
            ]
            
            for selector in fallback_selectors:
                try:
                    close_element = self.driver.find_element(By.XPATH, selector)
                    # Take screenshot before closing popup
                    self.take_screenshot("before_popup_close_fallback")
                    action = ActionChains(self.driver)
                    action.move_to_element(close_element).click().perform()
                    logger.info(f"Popup closed successfully using fallback selector: {selector}")
                    time.sleep(2)
                    # Take screenshot after closing popup
                    self.take_screenshot("after_popup_close_fallback")
                    return True
                except:
                    continue
            
            # If no close button found, try pressing Escape key
            try:
                # Take screenshot before pressing Escape
                self.take_screenshot("before_popup_escape")
                self.driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
                logger.info("Popup closed using Escape key")
                time.sleep(2)
                # Take screenshot after pressing Escape
                self.take_screenshot("after_popup_escape")
                return True
            except:
                pass
                
            logger.debug("No popup close button found")
            return False
            
        except Exception as e:
            logger.debug(f"Failed to close popup: {e}")
            return False

    def login(self):
        """Login to ServiceM8 with retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Login attempt {attempt + 1}/{self.max_retries}")
                
                # Load website with retry
                if not self.load_website_with_retry("https://go.servicem8.com"):
                    logger.error("Failed to load ServiceM8 website")
                    if attempt < self.max_retries - 1:
                        time.sleep(5)
                        continue
                    else:
                        return False
                
                # Close popup if present (try multiple times)
                for popup_attempt in range(3):
                    if self.close_popup():
                        break
                    time.sleep(1)
                
                wait = WebDriverWait(self.driver, 15)
                wait.until(EC.presence_of_element_located((By.ID, "user_email")))
                
                email_field = self.driver.find_element(By.ID, "user_email")
                email_field.clear()
                
                # Type email with keyword-like behavior
                for char in self.email:
                    email_field.send_keys(char)
                    time.sleep(0.1)  # Small delay between keystrokes
                
                password_field = self.driver.find_element(By.ID, "user_password")
                password_field.clear()
                
                # Type password with keyword-like behavior
                for char in self.password:
                    password_field.send_keys(char)
                    time.sleep(0.1)  # Small delay between keystrokes
                
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                
                # Press button with ActionChains for more realistic behavior
                action = ActionChains(self.driver)
                action.move_to_element(submit_button).click().perform()
                
                time.sleep(5)
                
                # Handle 2FA authentication if required
                if not self.handle_2fa_authentication():
                    logger.warning("2FA authentication failed")
                    if attempt < self.max_retries - 1:
                        time.sleep(5)
                        continue
                    else:
                        return False
                
                current_url = self.driver.current_url
                if "login" not in current_url.lower() and "servicem8.com" in current_url:
                    logger.info("Login successful")
                    # Take screenshot after successful login
                    self.take_screenshot("after_login")
                    
                    # Save device fingerprint after successful login to maintain consistent identity
                    self.save_device_fingerprint()
                    
                    return True
                else:
                    logger.warning(f"Login failed on attempt {attempt + 1} - still on login page")
                    if attempt < self.max_retries - 1:
                        logger.info("Waiting 5 seconds before retry...")
                        time.sleep(5)
                    else:
                        return False
                        
            except TimeoutException as e:
                logger.error(f"Login timeout on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                else:
                    return False
            except NoSuchElementException as e:
                logger.error(f"Login element not found on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                else:
                    return False
            except Exception as e:
                logger.error(f"Login error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
                else:
                    return False
        
        return False
    
    def remove_extjs_mask(self):
        """Remove ExtJS mask that blocks clicks"""
        try:
            # Try to find and remove the mask
            mask_selectors = [
                "//div[@class='ext-el-mask']",
                "//div[contains(@class, 'ext-el-mask')]",
                "//div[@id='ext-gen20']",
                "//*[contains(@class, 'x-mask')]"
            ]
            
            for selector in mask_selectors:
                try:
                    mask_element = self.driver.find_element(By.XPATH, selector)
                    # Hide the mask using JavaScript
                    self.driver.execute_script("arguments[0].style.display = 'none';", mask_element)
                    logger.info(f"ExtJS mask removed using selector: {selector}")
                    time.sleep(1)
                    return True
                except:
                    continue
            
            # Try to remove all masks using JavaScript
            try:
                self.driver.execute_script("""
                    var masks = document.querySelectorAll('.ext-el-mask, .x-mask, [id*="ext-gen"]');
                    for (var i = 0; i < masks.length; i++) {
                        if (masks[i].style.zIndex > 1000) {
                            masks[i].style.display = 'none';
                        }
                    }
                """)
                logger.info("ExtJS masks removed using JavaScript")
                time.sleep(1)
                return True
            except:
                pass
                
            logger.debug("No ExtJS mask found to remove")
            return False
            
        except Exception as e:
            logger.debug(f"Failed to remove ExtJS mask: {e}")
            return False

    def navigate_to_dispatch(self):
        """Navigate to Dispatch Board with retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Navigation to Dispatch Board attempt {attempt + 1}/{self.max_retries}")
                wait = WebDriverWait(self.driver, 20)  # Increased timeout
                
                # Remove any ExtJS masks that might block clicks
                self.remove_extjs_mask()
                
                # Wait for page to be fully loaded
                time.sleep(5)
                
                # Try multiple strategies to find and click dispatch link
                dispatch_selectors = [
                    "//a[contains(@href, 'job_dispatch')]",
                    "//a[contains(text(), 'Dispatch')]",
                    "//a[contains(text(), 'dispatch')]",
                    "//span[contains(text(), 'Dispatch')]/parent::a",
                    "//div[contains(text(), 'Dispatch')]/parent::a",
                    "//*[contains(@class, 'dispatch')]//a",
                    "//*[contains(@id, 'dispatch')]//a"
                ]
                
                dispatch_link = None
                for selector in dispatch_selectors:
                    try:
                        dispatch_link = wait.until(EC.element_to_be_clickable((By.XPATH, selector)))
                        logger.info(f"Dispatch link found using selector: {selector}")
                        break
                    except TimeoutException:
                        logger.debug(f"Selector failed: {selector}")
                        continue
                
                if not dispatch_link:
                    # Try direct URL navigation as fallback (especially useful for server environment)
                    logger.info("No dispatch link found, trying direct URL navigation...")
                    current_url = self.driver.current_url
                    base_url = current_url.split('/')[0] + '//' + current_url.split('/')[2]
                    dispatch_url = f"{base_url}/job_dispatch"
                    
                    try:
                        self.driver.get(dispatch_url)
                        time.sleep(10)
                        
                        # Handle potential 2FA on dispatch page
                        if not self.handle_2fa_authentication():
                            logger.warning("2FA authentication failed on dispatch page")
                        
                        current_url = self.driver.current_url
                        if "job_dispatch" in current_url or "dispatch" in current_url.lower():
                            logger.info("Successfully navigated to Dispatch Board via direct URL")
                            # Take screenshot after reaching dispatch board via direct URL
                            self.take_screenshot("dispatch_board_direct_url")
                            return True
                    except Exception as direct_error:
                        logger.warning(f"Direct URL navigation failed: {direct_error}")
                    
                    logger.error("All navigation strategies failed")
                    if attempt < self.max_retries - 1:
                        logger.info("Waiting 5 seconds before retry...")
                        time.sleep(5)
                        continue
                    else:
                        return False
                
                # Human-like mouse movement to the dispatch link
                action = ActionChains(self.driver)
                
                # Move mouse in a natural path to the dispatch link
                action.move_to_element_with_offset(dispatch_link, random.randint(-15, 15), random.randint(-10, 10)).perform()
                time.sleep(random.uniform(0.5, 1.0))
                
                # Sometimes move mouse slightly before clicking (more human-like)
                if random.random() < 0.3:
                    action.move_by_offset(random.randint(-8, 8), random.randint(-8, 8)).perform()
                    time.sleep(random.uniform(0.2, 0.5))
                    action.move_to_element(dispatch_link).perform()
                    time.sleep(random.uniform(0.2, 0.5))
                
                # Try to click the dispatch link with multiple strategies
                try:
                    # Strategy 1: Regular click
                    dispatch_link.click()
                    logger.info("Dispatch link clicked successfully")
                except Exception as click_error:
                    logger.warning(f"Regular click failed: {click_error}")
                    try:
                        # Strategy 2: JavaScript click
                        self.driver.execute_script("arguments[0].click();", dispatch_link)
                        logger.info("Dispatch link clicked using JavaScript")
                    except Exception as js_error:
                        logger.warning(f"JavaScript click failed: {js_error}")
                        try:
                            # Strategy 3: ActionChains click with human-like movement
                            action.move_to_element_with_offset(dispatch_link, random.randint(-5, 5), random.randint(-5, 5)).perform()
                            time.sleep(random.uniform(0.1, 0.3))
                            action.click().perform()
                            logger.info("Dispatch link clicked using ActionChains with human-like movement")
                        except Exception as action_error:
                            logger.error(f"All click strategies failed: {action_error}")
                            raise action_error
                
                # Wait for page to load
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(10)
                
                # Verify we're on the dispatch page
                current_url = self.driver.current_url
                if "job_dispatch" in current_url or "dispatch" in current_url.lower():
                    logger.info("Successfully navigated to Dispatch Board")
                    # Take screenshot after reaching dispatch board
                    self.take_screenshot("dispatch_board")
                    return True
                else:
                    logger.warning(f"Navigation may have failed - URL doesn't contain dispatch: {current_url}")
                    if attempt < self.max_retries - 1:
                        logger.info("Waiting 5 seconds before retry...")
                        time.sleep(5)
                    else:
                        logger.warning("Navigation completed but URL verification failed")
                        return True  # Still return True as we may have reached the page
                
            except TimeoutException as e:
                logger.error(f"Navigation timeout on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    return False
            except NoSuchElementException as e:
                logger.error(f"Navigation element not found on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    return False
            except Exception as e:
                logger.error(f"Navigation error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    logger.info("Waiting 5 seconds before retry...")
                    time.sleep(5)
                else:
                    return False
        
        return False
    
    def extract_with_retry(self):
        """Extract API data with retry logic if no tokens found"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Token extraction attempt {attempt + 1}/{self.max_retries}")
                
                # Extract API data
                auth_tokens, cookie_string = self.extract_api_data()
                
                # Check if we found any tokens
                if auth_tokens:
                    logger.info(f"Successfully found {len(auth_tokens)} tokens on attempt {attempt + 1}")
                    return auth_tokens, cookie_string
                else:
                    logger.warning(f"No tokens found on attempt {attempt + 1}")
                    
                    # If not the last attempt, wait and try again
                    if attempt < self.max_retries - 1:
                        logger.info(f"Waiting 5 seconds before retry...")
                        time.sleep(5)
                        
                        # Try refreshing the page
                        try:
                            self.driver.refresh()
                            time.sleep(3)
                            logger.info("Page refreshed for retry")
                        except Exception as e:
                            logger.warning(f"Failed to refresh page: {e}")
                    
            except Exception as e:
                logger.error(f"Error during token extraction attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(5)
        
        logger.error("Failed to extract tokens after all retry attempts")
        return {}, ""
    
    def extract_api_data(self):
        """Extract API tokens and cookies for specific URLs"""
        try:
            logger.info("Extracting API data...")
            # JavaScript to find specific API URLs and tokens
            js_code = """
            var apiData = [];
            var authTokens = {};
            var allUrls = [];
            
            // Search all script tags
            var scripts = document.getElementsByTagName('script');
            for (var i = 0; i < scripts.length; i++) {
                var scriptContent = scripts[i].innerHTML;
                
                // Look for CalendarStoreRequest
                var calendarMatches = scriptContent.match(/CalendarStoreRequest[^'"]*s_auth=([a-f0-9]+)/g);
                if (calendarMatches) {
                    calendarMatches.forEach(function(match) {
                        var authMatch = match.match(/s_auth=([a-f0-9]+)/);
                        if (authMatch) {
                            authTokens['CalendarStoreRequest'] = authMatch[1];
                            allUrls.push('CalendarStoreRequest');
                        }
                    });
                }
                
                // Look for PluginReminders_UpdateReminderForJobActivity
                var updateMatches = scriptContent.match(/PluginReminders_UpdateReminderForJobActivity[^'"]*s_auth=([a-f0-9]+)/g);
                if (updateMatches) {
                    updateMatches.forEach(function(match) {
                        var authMatch = match.match(/s_auth=([a-f0-9]+)/);
                        if (authMatch) {
                            authTokens['UpdateReminderForJobActivity'] = authMatch[1];
                            allUrls.push('UpdateReminderForJobActivity');
                        }
                    });
                }
                
                // Look for PluginReminders_SaveRecurringJobSchedule
                var saveMatches = scriptContent.match(/PluginReminders_SaveRecurringJobSchedule[^'"]*s_auth=([a-f0-9]+)/g);
                if (saveMatches) {
                    saveMatches.forEach(function(match) {
                        var authMatch = match.match(/s_auth=([a-f0-9]+)/);
                        if (authMatch) {
                            authTokens['SaveRecurringJobSchedule'] = authMatch[1];
                            allUrls.push('SaveRecurringJobSchedule');
                        }
                    });
                }
            }
            
            // Also search in window object
            for (var prop in window) {
                if (typeof window[prop] === 'string' && window[prop].includes('s_auth=')) {
                    if (window[prop].includes('CalendarStoreRequest')) {
                        var authMatch = window[prop].match(/s_auth=([a-f0-9]+)/);
                        if (authMatch) {
                            authTokens['CalendarStoreRequest'] = authMatch[1];
                        }
                    }
                    if (window[prop].includes('PluginReminders_UpdateReminderForJobActivity')) {
                        var authMatch = window[prop].match(/s_auth=([a-f0-9]+)/);
                        if (authMatch) {
                            authTokens['UpdateReminderForJobActivity'] = authMatch[1];
                        }
                    }
                    if (window[prop].includes('PluginReminders_SaveRecurringJobSchedule')) {
                        var authMatch = window[prop].match(/s_auth=([a-f0-9]+)/);
                        if (authMatch) {
                            authTokens['SaveRecurringJobSchedule'] = authMatch[1];
                        }
                    }
                }
            }
            
            return {
                authTokens: authTokens,
                foundUrls: allUrls
            };
            """
            
            result = self.driver.execute_script(js_code)
            
            # Get cookies
            all_cookies = self.driver.get_cookies()
            cookie_string = ""
            for cookie in all_cookies:
                if cookie_string:
                    cookie_string += "; "
                cookie_string += f"{cookie['name']}={cookie['value']}"
            
            logger.info(f"Found {len(result['authTokens'])} auth tokens: {list(result['authTokens'].keys())}")
            return result['authTokens'], cookie_string
            
        except WebDriverException as e:
            logger.error(f"WebDriver error during API data extraction: {e}")
            return {}, ""
        except Exception as e:
            logger.error(f"Error extracting API data: {e}")
            return {}, ""
    
    def create_api_response(self, auth_tokens, cookie_string):
        """Create the response in the requested format with single cookie storage"""
        api_endpoints = []
        
        # CalendarStoreRequest
        if 'CalendarStoreRequest' in auth_tokens:
            api_endpoints.append({
                "url": f"https://go.servicem8.com/CalendarStoreRequest?s_cv=&s_form_values=query-start-limit-_dc-callback-records-xaction-end-id-strJobUUID&s_auth={auth_tokens['CalendarStoreRequest']}",
                "s_auth": auth_tokens['CalendarStoreRequest']
            })
        
        # UpdateReminderForJobActivity
        if 'UpdateReminderForJobActivity' in auth_tokens:
            api_endpoints.append({
                "url": f"https://ap-southeast-2.go.servicem8.com/PluginReminders_UpdateReminderForJobActivity?s_form_values=strReminderUUID-strOriginalStartDate-strOriginalEndDate-strOriginalStaffUUID-strNewStartDate-strNewEndDate-strNewStaffUUID-strNewStaffUUIDList-boolModifyAllFollowingRecurrences&s_auth={auth_tokens['UpdateReminderForJobActivity']}",
                "s_auth": auth_tokens['UpdateReminderForJobActivity']
            })
        
        # SaveRecurringJobSchedule
        if 'SaveRecurringJobSchedule' in auth_tokens:
            api_endpoints.append({
                "url": f"https://ap-southeast-2.go.servicem8.com/PluginReminders_SaveRecurringJobSchedule?s_form_values=strReminderUUID-strCustomerUUID-strJobTemplateUUID-strAlertMode-strAllocationWindowUUID-strScheduledStartTime-intScheduledDuration-strStaffUUID-strStaffUUIDList-strAlertDescription-strRecurrenceType-strDailyMode-strWeeklyMode-strMonthlyMode-strYearlyMode-intDailyInterval-intWeeklyInterval-intWeeklyWeeksAfterCompletion-arrWeeklyDayNames-intMonthlyDayEveryMonth-intMonthlyDayEveryMonthInterval-strMonthlyMode2WeekType-intMonthlyMode2DayName-intMonthlyMode2MonthInterval-strYearlyMode2WeekType-intYearlyMode1Month-intYearlyMode1Day-intYearlyMode2DayName-intYearlyMode2Month-strPatternStartDate-strPatternEndDateMode-strPatternEndDate-intPatternEndDateOccurrences-boolCancelReminder&s_auth={auth_tokens['SaveRecurringJobSchedule']}",
                "s_auth": auth_tokens['SaveRecurringJobSchedule']
            })
        
        # Return structured response with single cookie entry
        return {
            "cookie": cookie_string,
            "api_endpoints": api_endpoints
        }
    
    def extract(self):
        """Main extraction method with comprehensive error handling"""
        try:
            logger.info("Starting ServiceM8 API extraction process...")
            
            # Setup Chrome
            if not self.setup_chrome():
                logger.error("Failed to setup Chrome browser")
                return None
            
            # Login
            if not self.login():
                logger.error("Failed to login to ServiceM8")
                return None
            
            # Navigate to Dispatch Board
            if not self.navigate_to_dispatch():
                logger.error("Failed to navigate to Dispatch Board")
                return None
            
            # Extract API data with retry logic
            auth_tokens, cookie_string = self.extract_with_retry()
            
            if not auth_tokens:
                logger.error("No auth tokens found after all retry attempts")
                return None
            
            # Create response
            api_data = self.create_api_response(auth_tokens, cookie_string)
            
            if api_data:
                logger.info(f"Successfully extracted {len(api_data)} API endpoints")
            else:
                logger.warning("No API data created from extracted tokens")
            
            return api_data
            
        except Exception as e:
            logger.error(f"Critical error in extraction process: {e}")
            return None
        finally:
            if self.driver:
                try:
                    logger.info("Closing browser...")
                    self.driver.quit()
                except Exception as e:
                    logger.warning(f"Error closing browser: {e}")
            
            # Clean up any remaining Chrome processes
            try:
                import subprocess
                import psutil
                
                # Kill any remaining Chrome processes
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if proc.info['name'] and ('chrome' in proc.info['name'].lower() or 'chromedriver' in proc.info['name'].lower()):
                            proc.kill()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
                
                # Backup cleanup with pkill
                subprocess.run(["pkill", "-9", "-f", "chrome"], capture_output=True, timeout=5)
                subprocess.run(["pkill", "-9", "-f", "chromedriver"], capture_output=True, timeout=5)
            except Exception as e:
                logger.debug(f"Failed to clean up: {e}")

def main():
    """Main function with comprehensive error handling"""
    try:
        logger.info("Starting ServiceM8 API Token Extractor...")
        
        # Check environment variables
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        auth_code = os.getenv("AUTH_CODE")
        server_mode = os.getenv("SERVER_MODE", "false").lower() == "true"
        capture_fingerprint = os.getenv("CAPTURE_FINGERPRINT", "false").lower() == "true"
        
        if not email or not password:
            logger.error("EMAIL and PASSWORD environment variables not found!")
            logger.error("Please create a .env file with your ServiceM8 credentials")
            return
        
        if server_mode:
            logger.info("Running in SERVER_MODE")
            if not auth_code:
                logger.warning("AUTH_CODE not provided - 2FA may fail on server")
        else:
            logger.info("Running in local mode")
        
        if capture_fingerprint:
            logger.info("CAPTURE_FINGERPRINT mode enabled - will capture fingerprint only")
            extractor = ServiceM8APIExtractor(max_retries=3)
            if extractor.capture_manual_fingerprint():
                logger.info("Fingerprint capture completed successfully!")
            else:
                logger.error("Fingerprint capture failed!")
            return
        
        logger.info("Environment variables loaded successfully")
        
        # Run extraction
        extractor = ServiceM8APIExtractor(max_retries=3)
        result = extractor.extract()

        # Store result in json file
        try:
            with open("result.json", "w") as f:
                json.dump(result, f, indent=3)
            logger.info("Results saved to result.json")
        except Exception as e:
            logger.error(f"Failed to save results to file: {e}")
        
        if result:
            logger.info("Extraction completed successfully!")
            logger.info(f"Found {len(result)} API endpoints")
            # Uncomment the next line if you want to print results to console
            # print(json.dumps(result, indent=2))
        else:
            logger.error("Extraction failed - no data retrieved")
            
    except Exception as e:
        logger.error(f"Critical error in main function: {e}")
    finally:
        logger.info("ServiceM8 API Token Extractor finished")

if __name__ == "__main__":
    main()
