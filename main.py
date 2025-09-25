#!/usr/bin/env python3
"""
Simple ServiceM8 API Token & Cookie Extractor
Extracts tokens and cookies for specific APIs without saving files
"""

import json
import time
import os
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
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

class TimingLogger:
    """Utility class for tracking execution times"""
    def __init__(self):
        self.start_time = None
        self.step_times = {}
        
    def start_timer(self, step_name="process"):
        self.start_time = datetime.now()
        logger.info(f"[TIMER] Starting {step_name} at {self.start_time.strftime('%H:%M:%S')}")
        
    def log_step(self, step_name):
        if self.start_time:
            current_time = datetime.now()
            elapsed = current_time - self.start_time
            self.step_times[step_name] = elapsed
            logger.info(f"[SUCCESS] {step_name} completed in {elapsed.total_seconds():.2f} seconds")
            return elapsed
        return None
    
    def finish_timer(self, process_name="process"):
        if self.start_time:
            total_time = datetime.now() - self.start_time
            logger.info(f"[COMPLETE] Total {process_name} time: {total_time.total_seconds():.2f} seconds")
            logger.info(f"[FINISHED] Process finished at {datetime.now().strftime('%H:%M:%S')}")
            return total_time
        return None

class ServiceM8APIExtractor:
    def __init__(self, max_retries=3):
        self.driver = None
        self.email = os.getenv("EMAIL")
        self.password = os.getenv("PASSWORD")
        self.max_retries = max_retries
        logger.info("ServiceM8APIExtractor initialized")
        
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
                options.add_argument("--headless=new")
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--disable-gpu")
                options.add_argument("--window-size=1920,1080")
                options.add_argument("--disable-blink-features=AutomationControlled")
                options.add_experimental_option("excludeSwitches", ["enable-automation"])
                options.add_experimental_option('useAutomationExtension', False)
                
                # Enhanced stealth settings for GitHub Actions
                options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
                options.add_argument("--disable-web-security")
                options.add_argument("--allow-running-insecure-content")
                options.add_argument("--disable-features=VizDisplayCompositor")
                options.add_argument("--disable-logging")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                options.add_argument("--disable-field-trial-config")
                options.add_argument("--disable-ipc-flooding-protection")
                
                # Set additional preferences to avoid detection
                prefs = {
                    "profile.default_content_setting_values": {
                        "notifications": 2,
                        "geolocation": 2,
                        "media_stream": 2,
                    },
                    "profile.managed_default_content_settings": {
                        "images": 2
                    }
                }
                options.add_experimental_option("prefs", prefs)
                
                # Additional stability options
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
                options.add_argument("--disable-images")
                options.add_argument("--disable-web-security")
                options.add_argument("--allow-running-insecure-content")
                options.add_argument("--disable-background-timer-throttling")
                options.add_argument("--disable-backgrounding-occluded-windows")
                options.add_argument("--disable-renderer-backgrounding")
                
                self.driver = webdriver.Chrome(options=options)
                
                # Enhanced stealth JavaScript for GitHub Actions
                stealth_js = """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
                Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
                Object.defineProperty(navigator, 'permissions', {get: () => ({query: () => Promise.resolve({state: 'granted'})})});
                window.chrome = {runtime: {}};
                Object.defineProperty(navigator, 'maxTouchPoints', {get: () => 1});
                Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});
                Object.defineProperty(navigator, 'productSub', {get: () => '20030107'});
                Object.defineProperty(navigator, 'vendorSub', {get: () => ''});
                """
                self.driver.execute_script(stealth_js)
                
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
                
                wait = WebDriverWait(self.driver, 15)
                wait.until(EC.presence_of_element_located((By.ID, "user_email")))
                
                # Human-like typing delays
                email_field = self.driver.find_element(By.ID, "user_email")
                email_field.clear()
                time.sleep(1)  # Wait after clearing
                
                # Type email slowly like a human
                for char in self.email:
                    email_field.send_keys(char)
                    time.sleep(0.1)  # Small delay between keystrokes
                
                time.sleep(2)  # Pause between fields
                
                password_field = self.driver.find_element(By.ID, "user_password")
                password_field.clear()
                time.sleep(1)
                
                # Type password slowly like a human
                for char in self.password:
                    password_field.send_keys(char)
                    time.sleep(0.1)
                
                time.sleep(2)  # Pause before clicking submit
                
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                # Move to button first (human-like behavior)
                self.driver.execute_script("arguments[0].scrollIntoView();", submit_button)
                time.sleep(1)
                submit_button.click()
                
                time.sleep(5)
                
                current_url = self.driver.current_url
                if "login" not in current_url.lower() and "servicem8.com" in current_url:
                    logger.info("Login successful")
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
    
    def navigate_to_dispatch(self):
        """Navigate to Dispatch Board with multiple fallback strategies"""
        navigation_retries = 5
        for attempt in range(navigation_retries):
            try:
                logger.info(f"Navigation to Dispatch Board attempt {attempt + 1}/{navigation_retries}")
                wait = WebDriverWait(self.driver, 45)  # Increased to 45 seconds
                
                # Set page load timeout to 90 seconds
                self.driver.set_page_load_timeout(90)
                
                # Strategy 1: Try direct URL navigation first (most reliable)
                logger.info("Trying direct URL navigation to dispatch board...")
                current_url = self.driver.current_url
                base_url = current_url.split('/')[0] + '//' + current_url.split('/')[2]
                dispatch_url = f"{base_url}/job_dispatch"
                
                try:
                    self.driver.get(dispatch_url)
                    logger.info("Direct URL navigation attempted")
                    
                    # Wait for page to load
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    time.sleep(10)
                    
                # Check if we're on dispatch page
                current_url = self.driver.current_url
                page_title = self.driver.title
                
                # Check for access denied
                if "access denied" in page_title.lower() or "access denied" in self.driver.page_source.lower():
                    logger.error(f"[ACCESS_DENIED] User does not have permission to access Dispatch Board")
                    logger.error(f"[ACCESS_DENIED] Current URL: {current_url}")
                    logger.error(f"[ACCESS_DENIED] Page Title: {page_title}")
                    logger.error(f"[ACCESS_DENIED] This is a ServiceM8 user permission issue, not a technical problem")
                    logger.error(f"[ACCESS_DENIED] Please check if the user account has 'Dispatch Board' permissions in ServiceM8")
                    return False
                
                if "job_dispatch" in current_url or "dispatch" in current_url.lower():
                    logger.info("[SUCCESS] Successfully navigated to Dispatch Board via direct URL")
                    return True
                        
                except Exception as direct_error:
                    logger.warning(f"Direct URL navigation failed: {direct_error}")
                
                # Strategy 2: Look for navigation menu and dispatch link
                logger.info("Trying navigation menu approach...")
                
                # Wait for page to be fully loaded first
                wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                time.sleep(5)
                
                # Multiple selectors to try for the navigation menu
                nav_selectors = [
                    (By.CLASS_NAME, "ThemeMainMenu"),
                    (By.CSS_SELECTOR, ".main-menu"),
                    (By.CSS_SELECTOR, "[class*='menu']"),
                    (By.CSS_SELECTOR, "nav"),
                    (By.TAG_NAME, "nav")
                ]
                
                nav_menu = None
                for selector_type, selector_value in nav_selectors:
                    try:
                        nav_menu = wait.until(EC.presence_of_element_located((selector_type, selector_value)))
                        logger.info(f"Navigation menu found using {selector_type}: {selector_value}")
                        break
                    except TimeoutException:
                        logger.debug(f"Navigation menu not found with {selector_type}: {selector_value}")
                        continue
                
                if not nav_menu:
                    logger.warning("No navigation menu found, trying alternative approach...")
                
                # Multiple selectors for dispatch link
                dispatch_selectors = [
                    (By.XPATH, "//a[contains(@href, 'job_dispatch')]"),
                    (By.XPATH, "//a[contains(@href, 'dispatch')]"),
                    (By.XPATH, "//a[contains(text(), 'Dispatch')]"),
                    (By.XPATH, "//a[contains(text(), 'dispatch')]"),
                    (By.CSS_SELECTOR, "a[href*='job_dispatch']"),
                    (By.CSS_SELECTOR, "a[href*='dispatch']"),
                    (By.XPATH, "//span[contains(text(), 'Dispatch')]/parent::a"),
                    (By.XPATH, "//div[contains(text(), 'Dispatch')]/parent::a")
                ]
                
                dispatch_link = None
                for selector_type, selector_value in dispatch_selectors:
                    try:
                        dispatch_link = wait.until(EC.element_to_be_clickable((selector_type, selector_value)))
                        logger.info(f"Dispatch link found using {selector_type}: {selector_value}")
                        break
                    except TimeoutException:
                        logger.debug(f"Dispatch link not found with {selector_type}: {selector_value}")
                        continue
                
                if dispatch_link:
                    # Scroll to the element and click
                    self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", dispatch_link)
                    time.sleep(3)
                    
                    # Try JavaScript click if regular click fails
                    try:
                        dispatch_link.click()
                        logger.info("Dispatch link clicked successfully")
                    except Exception as click_error:
                        logger.warning(f"Regular click failed, trying JavaScript click: {click_error}")
                        self.driver.execute_script("arguments[0].click();", dispatch_link)
                        logger.info("Dispatch link clicked via JavaScript")
                    
                    # Wait for navigation to complete
                    time.sleep(10)
                    
                    # Wait for page to be ready
                    wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
                    time.sleep(5)
                    
                    # Verify navigation success
                    final_url = self.driver.current_url
                    if "job_dispatch" in final_url or "dispatch" in final_url.lower():
                        logger.info("[SUCCESS] Successfully navigated to Dispatch Board via menu link")
                        return True
                    else:
                        logger.warning(f"Navigation via link may have failed - URL: {final_url}")
                else:
                    logger.error("No dispatch link found with any selector")
                
                # Strategy 3: Try searching for any links and examine them
                logger.info("Trying to find all links and search for dispatch...")
                try:
                    all_links = self.driver.find_elements(By.TAG_NAME, "a")
                    logger.info(f"Found {len(all_links)} total links on page")
                    
                    for link in all_links:
                        try:
                            href = link.get_attribute("href") or ""
                            text = link.text.lower()
                            if "dispatch" in href.lower() or "dispatch" in text:
                                logger.info(f"Found potential dispatch link: {href} | {text}")
                                link.click()
                                time.sleep(10)
                                if "dispatch" in self.driver.current_url.lower():
                                    logger.info("[SUCCESS] Successfully navigated via link search")
                                    return True
                        except Exception as link_error:
                            continue
                            
                except Exception as search_error:
                    logger.warning(f"Link search strategy failed: {search_error}")
                
                # If we get here, this attempt failed
                if attempt < navigation_retries - 1:
                    logger.info("Waiting 15 seconds before retry...")
                    time.sleep(15)
                    # Try to refresh the page
                    try:
                        self.driver.refresh()
                        time.sleep(10)
                        logger.info("Page refreshed before retry")
                    except Exception as refresh_error:
                        logger.warning(f"Failed to refresh page: {refresh_error}")
                else:
                    logger.error("All navigation strategies failed")
                
            except TimeoutException as e:
                logger.error(f"Navigation timeout on attempt {attempt + 1}: {e}")
                if attempt < navigation_retries - 1:
                    logger.info("Waiting 15 seconds before retry...")
                    time.sleep(15)
                    try:
                        self.driver.refresh()
                        time.sleep(10)
                        logger.info("Page refreshed after timeout")
                    except Exception as refresh_error:
                        logger.warning(f"Failed to refresh page: {refresh_error}")
                else:
                    return False
            except Exception as e:
                logger.error(f"Navigation error on attempt {attempt + 1}: {e}")
                if attempt < navigation_retries - 1:
                    logger.info("Waiting 15 seconds before retry...")
                    time.sleep(15)
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
        """Extract API tokens and cookies with comprehensive debugging and search patterns"""
        try:
            logger.info("[EXTRACT] Starting comprehensive API data extraction...")
            
            # First, let's debug what's actually on the page
            debug_js = """
            var debugInfo = {
                url: window.location.href,
                title: document.title,
                scriptCount: document.getElementsByTagName('script').length,
                hasCalendar: document.body.innerHTML.includes('CalendarStoreRequest'),
                hasPluginReminders: document.body.innerHTML.includes('PluginReminders'),
                hasAuthToken: document.body.innerHTML.includes('s_auth='),
                pageLength: document.body.innerHTML.length
            };
            return debugInfo;
            """
            
            debug_result = self.driver.execute_script(debug_js)
            logger.info(f"[DEBUG] Page Debug Info:")
            logger.info(f"   URL: {debug_result['url']}")
            logger.info(f"   Title: {debug_result['title']}")
            logger.info(f"   Script tags: {debug_result['scriptCount']}")
            logger.info(f"   Has CalendarStoreRequest: {debug_result['hasCalendar']}")
            logger.info(f"   Has PluginReminders: {debug_result['hasPluginReminders']}")
            logger.info(f"   Has s_auth tokens: {debug_result['hasAuthToken']}")
            logger.info(f"   Page content size: {debug_result['pageLength']} chars")
            
            # Enhanced JavaScript to find tokens with multiple strategies
            js_code = """
            var apiData = [];
            var authTokens = {};
            var allUrls = [];
            var searchResults = {
                scriptsSearched: 0,
                tokensFound: 0,
                searchPatterns: []
            };
            
            // Strategy 1: Search all script tags with enhanced patterns
            var scripts = document.getElementsByTagName('script');
            searchResults.scriptsSearched = scripts.length;
            
            for (var i = 0; i < scripts.length; i++) {
                var scriptContent = scripts[i].innerHTML || scripts[i].textContent || '';
                
                // Enhanced patterns for CalendarStoreRequest
                var calendarPatterns = [
                    /CalendarStoreRequest[^'"]*s_auth=([a-f0-9]+)/gi,
                    /CalendarStoreRequest.*?s_auth=([a-f0-9]+)/gi,
                    /'CalendarStoreRequest'[^']*s_auth=([a-f0-9]+)/gi,
                    /"CalendarStoreRequest"[^"]*s_auth=([a-f0-9]+)/gi
                ];
                
                calendarPatterns.forEach(function(pattern) {
                    var matches = scriptContent.match(pattern);
                    if (matches) {
                        matches.forEach(function(match) {
                            var authMatch = match.match(/s_auth=([a-f0-9]+)/);
                            if (authMatch) {
                                authTokens['CalendarStoreRequest'] = authMatch[1];
                                allUrls.push('CalendarStoreRequest');
                                searchResults.tokensFound++;
                                searchResults.searchPatterns.push('CalendarStoreRequest pattern');
                            }
                        });
                    }
                });
                
                // Enhanced patterns for UpdateReminderForJobActivity
                var updatePatterns = [
                    /PluginReminders_UpdateReminderForJobActivity[^'"]*s_auth=([a-f0-9]+)/gi,
                    /UpdateReminderForJobActivity[^'"]*s_auth=([a-f0-9]+)/gi,
                    /'UpdateReminderForJobActivity'[^']*s_auth=([a-f0-9]+)/gi,
                    /"UpdateReminderForJobActivity"[^"]*s_auth=([a-f0-9]+)/gi
                ];
                
                updatePatterns.forEach(function(pattern) {
                    var matches = scriptContent.match(pattern);
                    if (matches) {
                        matches.forEach(function(match) {
                            var authMatch = match.match(/s_auth=([a-f0-9]+)/);
                            if (authMatch) {
                                authTokens['UpdateReminderForJobActivity'] = authMatch[1];
                                allUrls.push('UpdateReminderForJobActivity');
                                searchResults.tokensFound++;
                                searchResults.searchPatterns.push('UpdateReminderForJobActivity pattern');
                            }
                        });
                    }
                });
                
                // Enhanced patterns for SaveRecurringJobSchedule
                var savePatterns = [
                    /PluginReminders_SaveRecurringJobSchedule[^'"]*s_auth=([a-f0-9]+)/gi,
                    /SaveRecurringJobSchedule[^'"]*s_auth=([a-f0-9]+)/gi,
                    /'SaveRecurringJobSchedule'[^']*s_auth=([a-f0-9]+)/gi,
                    /"SaveRecurringJobSchedule"[^"]*s_auth=([a-f0-9]+)/gi
                ];
                
                savePatterns.forEach(function(pattern) {
                    var matches = scriptContent.match(pattern);
                    if (matches) {
                        matches.forEach(function(match) {
                            var authMatch = match.match(/s_auth=([a-f0-9]+)/);
                            if (authMatch) {
                                authTokens['SaveRecurringJobSchedule'] = authMatch[1];
                                allUrls.push('SaveRecurringJobSchedule');
                                searchResults.tokensFound++;
                                searchResults.searchPatterns.push('SaveRecurringJobSchedule pattern');
                            }
                        });
                    }
                });
                
                // General s_auth token search for any missed tokens
                var generalAuthMatches = scriptContent.match(/s_auth=([a-f0-9]+)/g);
                if (generalAuthMatches && !authTokens['GeneralAuth']) {
                    generalAuthMatches.forEach(function(match) {
                        var authMatch = match.match(/s_auth=([a-f0-9]+)/);
                        if (authMatch) {
                            authTokens['GeneralAuth'] = authMatch[1];
                            allUrls.push('GeneralAuth');
                            searchResults.tokensFound++;
                            searchResults.searchPatterns.push('General s_auth pattern');
                        }
                    });
                }
            }
            
            // Strategy 2: Search in window object with enhanced patterns
            for (var prop in window) {
                try {
                    if (typeof window[prop] === 'string' && window[prop].includes('s_auth=')) {
                        var propContent = window[prop];
                        
                        if (propContent.includes('CalendarStoreRequest')) {
                            var authMatch = propContent.match(/s_auth=([a-f0-9]+)/);
                            if (authMatch && !authTokens['CalendarStoreRequest']) {
                                authTokens['CalendarStoreRequest'] = authMatch[1];
                                searchResults.searchPatterns.push('Window CalendarStoreRequest');
                            }
                        }
                        if (propContent.includes('UpdateReminderForJobActivity') || propContent.includes('PluginReminders_UpdateReminderForJobActivity')) {
                            var authMatch = propContent.match(/s_auth=([a-f0-9]+)/);
                            if (authMatch && !authTokens['UpdateReminderForJobActivity']) {
                                authTokens['UpdateReminderForJobActivity'] = authMatch[1];
                                searchResults.searchPatterns.push('Window UpdateReminderForJobActivity');
                            }
                        }
                        if (propContent.includes('SaveRecurringJobSchedule') || propContent.includes('PluginReminders_SaveRecurringJobSchedule')) {
                            var authMatch = propContent.match(/s_auth=([a-f0-9]+)/);
                            if (authMatch && !authTokens['SaveRecurringJobSchedule']) {
                                authTokens['SaveRecurringJobSchedule'] = authMatch[1];
                                searchResults.searchPatterns.push('Window SaveRecurringJobSchedule');
                            }
                        }
                    }
                } catch (e) {
                    // Skip properties that can't be accessed
                }
            }
            
            // Strategy 3: Search entire page HTML as fallback
            var pageHTML = document.documentElement.outerHTML;
            var allAuthMatches = pageHTML.match(/s_auth=([a-f0-9]+)/g);
            if (allAuthMatches && Object.keys(authTokens).length === 0) {
                // If no specific tokens found, grab the first available s_auth token
                var firstAuthMatch = allAuthMatches[0].match(/s_auth=([a-f0-9]+)/);
                if (firstAuthMatch) {
                    authTokens['FallbackAuth'] = firstAuthMatch[1];
                    searchResults.searchPatterns.push('Fallback HTML search');
                }
            }
            
            // Strategy 4: Search for any API endpoints in the page
            var apiEndpoints = [];
            var endpointPatterns = [
                /https?:\/\/[^'"]+\.servicem8\.com[^'"]+s_auth=([a-f0-9]+)/g,
                /\/[^'"]*s_auth=([a-f0-9]+)/g
            ];
            
            endpointPatterns.forEach(function(pattern) {
                var matches = pageHTML.match(pattern);
                if (matches) {
                    matches.forEach(function(match) {
                        apiEndpoints.push(match);
                        var authMatch = match.match(/s_auth=([a-f0-9]+)/);
                        if (authMatch && Object.keys(authTokens).length === 0) {
                            authTokens['EndpointAuth'] = authMatch[1];
                            searchResults.searchPatterns.push('API endpoint search');
                        }
                    });
                }
            });
            
            return {
                authTokens: authTokens,
                foundUrls: allUrls,
                searchResults: searchResults,
                apiEndpoints: apiEndpoints.slice(0, 5) // Return first 5 endpoints for debugging
            };
            """
            
            result = self.driver.execute_script(js_code)
            
            # Enhanced logging of search results
            logger.info(f"[SEARCH] Search Results:")
            logger.info(f"   Scripts searched: {result['searchResults']['scriptsSearched']}")
            logger.info(f"   Tokens found: {result['searchResults']['tokensFound']}")
            logger.info(f"   Search patterns used: {result['searchResults']['searchPatterns']}")
            logger.info(f"   API endpoints found: {len(result['apiEndpoints'])}")
            
            if result['apiEndpoints']:
                logger.info(f"[ENDPOINTS] Sample API endpoints:")
                for endpoint in result['apiEndpoints']:
                    logger.info(f"   {endpoint[:100]}...")
            
            # Get cookies
            all_cookies = self.driver.get_cookies()
            cookie_string = ""
            for cookie in all_cookies:
                if cookie_string:
                    cookie_string += "; "
                cookie_string += f"{cookie['name']}={cookie['value']}"
            
            logger.info(f"[TOKENS] Found {len(result['authTokens'])} auth tokens: {list(result['authTokens'].keys())}")
            if result['authTokens']:
                for token_name, token_value in result['authTokens'].items():
                    logger.info(f"   {token_name}: {token_value[:8]}...")
            
            return result['authTokens'], cookie_string
            
        except WebDriverException as e:
            logger.error(f"WebDriver error during API data extraction: {e}")
            return {}, ""
        except Exception as e:
            logger.error(f"Error extracting API data: {e}")
            return {}, ""
    
    def create_api_response(self, auth_tokens, cookie_string):
        """Create the response in the requested format with support for fallback tokens"""
        api_data = []
        
        # CalendarStoreRequest
        if 'CalendarStoreRequest' in auth_tokens:
            api_data.append({
                "url": f"https://go.servicem8.com/CalendarStoreRequest?s_cv=&s_form_values=query-start-limit-_dc-callback-records-xaction-end-id-strJobUUID&s_auth={auth_tokens['CalendarStoreRequest']}",
                "cookie": cookie_string,
                "s_auth": auth_tokens['CalendarStoreRequest']
            })
        
        # UpdateReminderForJobActivity
        if 'UpdateReminderForJobActivity' in auth_tokens:
            api_data.append({
                "url": f"https://ap-southeast-2.go.servicem8.com/PluginReminders_UpdateReminderForJobActivity?s_form_values=strReminderUUID-strOriginalStartDate-strOriginalEndDate-strOriginalStaffUUID-strNewStartDate-strNewEndDate-strNewStaffUUID-strNewStaffUUIDList-boolModifyAllFollowingRecurrences&s_auth={auth_tokens['UpdateReminderForJobActivity']}",
                "cookie": cookie_string,
                "s_auth": auth_tokens['UpdateReminderForJobActivity']
            })
        
        # SaveRecurringJobSchedule
        if 'SaveRecurringJobSchedule' in auth_tokens:
            api_data.append({
                "url": f"https://ap-southeast-2.go.servicem8.com/PluginReminders_SaveRecurringJobSchedule?s_form_values=strReminderUUID-strCustomerUUID-strJobTemplateUUID-strAlertMode-strAllocationWindowUUID-strScheduledStartTime-intScheduledDuration-strStaffUUID-strStaffUUIDList-strAlertDescription-strRecurrenceType-strDailyMode-strWeeklyMode-strMonthlyMode-strYearlyMode-intDailyInterval-intWeeklyInterval-intWeeklyWeeksAfterCompletion-arrWeeklyDayNames-intMonthlyDayEveryMonth-intMonthlyDayEveryMonthInterval-strMonthlyMode2WeekType-intMonthlyMode2DayName-intMonthlyMode2MonthInterval-strYearlyMode2WeekType-intYearlyMode1Month-intYearlyMode1Day-intYearlyMode2DayName-intYearlyMode2Month-strPatternStartDate-strPatternEndDateMode-strPatternEndDate-intPatternEndDateOccurrences-boolCancelReminder&s_auth={auth_tokens['SaveRecurringJobSchedule']}",
                "cookie": cookie_string,
                "s_auth": auth_tokens['SaveRecurringJobSchedule']
            })
        
        # If we found fallback tokens, create generic endpoints
        if not api_data:
            logger.warning("[WARNING] No specific API tokens found, creating fallback endpoints...")
            
            if 'GeneralAuth' in auth_tokens:
                api_data.append({
                    "url": f"https://go.servicem8.com/CalendarStoreRequest?s_cv=&s_form_values=query-start-limit-_dc-callback-records-xaction-end-id-strJobUUID&s_auth={auth_tokens['GeneralAuth']}",
                    "cookie": cookie_string,
                    "s_auth": auth_tokens['GeneralAuth'],
                    "type": "fallback_calendar"
                })
                
            if 'FallbackAuth' in auth_tokens:
                api_data.append({
                    "url": f"https://go.servicem8.com/CalendarStoreRequest?s_cv=&s_form_values=query-start-limit-_dc-callback-records-xaction-end-id-strJobUUID&s_auth={auth_tokens['FallbackAuth']}",
                    "cookie": cookie_string,
                    "s_auth": auth_tokens['FallbackAuth'],
                    "type": "fallback_general"
                })
                
            if 'EndpointAuth' in auth_tokens:
                api_data.append({
                    "url": f"https://go.servicem8.com/CalendarStoreRequest?s_cv=&s_form_values=query-start-limit-_dc-callback-records-xaction-end-id-strJobUUID&s_auth={auth_tokens['EndpointAuth']}",
                    "cookie": cookie_string,
                    "s_auth": auth_tokens['EndpointAuth'],
                    "type": "fallback_endpoint"
                })
        
        if api_data:
            logger.info(f"[SUCCESS] Created {len(api_data)} API endpoints")
        else:
            logger.warning("[WARNING] No API endpoints could be created from available tokens")
            
        return api_data
    
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
            
            # Wait additional time for dynamic content to load after navigation
            logger.info("[WAIT] Waiting for dynamic content to load...")
            time.sleep(20)  # Give extra time for any JavaScript to execute and load tokens
            
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

def main():
    """Main function with comprehensive error handling and timing"""
    timer = TimingLogger()
    timer.start_timer("ServiceM8 API Token Extraction")
    
    try:
        logger.info("[START] Starting ServiceM8 API Token Extractor...")
        logger.info(f"[TIME] Execution started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check environment variables
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        
        if not email or not password:
            logger.error("[ERROR] EMAIL and PASSWORD environment variables not found!")
            logger.error("Please create a .env file with your ServiceM8 credentials")
            return
        
        logger.info("[SUCCESS] Environment variables loaded successfully")
        timer.log_step("Environment setup")
        
        # Run extraction with increased retries for better resilience
        extractor = ServiceM8APIExtractor(max_retries=5)
        extraction_start = datetime.now()
        result = extractor.extract()
        timer.log_step("ServiceM8 extraction")

        # Store result in json file with enhanced validation
        try:
            save_start = datetime.now()
            
            # Validate result before saving
            if result is None:
                logger.error("[ERROR] Cannot save result - extraction returned None")
                with open("result.json", "w") as f:
                    json.dump([], f, indent=3)  # Save empty array instead of null
                logger.warning("[WARNING] Saved empty array to result.json to prevent webhook errors")
            elif not result:
                logger.warning("[WARNING] Extraction returned empty result")
                with open("result.json", "w") as f:
                    json.dump([], f, indent=3)  # Save empty array
                logger.info("[INFO] Saved empty array to result.json")
            else:
                with open("result.json", "w") as f:
                    json.dump(result, f, indent=3)
                logger.info(f"[SUCCESS] Results saved to result.json in {(datetime.now() - save_start).total_seconds():.2f} seconds")
            
            timer.log_step("File save")
        except Exception as e:
            logger.error(f"[ERROR] Failed to save results to file: {e}")
            # Create a fallback empty file to prevent webhook errors
            try:
                with open("result.json", "w") as f:
                    json.dump([], f, indent=3)
                logger.warning("[WARNING] Created fallback empty result.json file")
            except Exception as fallback_error:
                logger.error(f"[ERROR] Failed to create fallback result.json: {fallback_error}")
        
        if result:
            logger.info("[SUCCESS] Extraction completed successfully!")
            logger.info(f"[RESULT] Found {len(result)} API endpoints")
            logger.info(f"[ENDPOINTS] Endpoints extracted: {[item.get('url', 'Unknown')[:50] + '...' for item in result]}")
        else:
            logger.error("[ERROR] Extraction failed - no data retrieved")
            logger.error("[DEBUG] Possible causes:")
            logger.error("   - Navigation to Dispatch Board failed")
            logger.error("   - Page did not load completely")
            logger.error("   - API tokens not found in page source")
            logger.error("   - ServiceM8 UI has changed")
            logger.error("[INFO] Empty result.json created to prevent downstream errors")
            
    except Exception as e:
        logger.error(f"[CRITICAL] Critical error in main function: {e}")
    finally:
        timer.finish_timer("ServiceM8 API Token Extraction")
        logger.info("[FINISHED] ServiceM8 API Token Extractor finished")
        logger.info("=" * 80)

if __name__ == "__main__":
    main()
