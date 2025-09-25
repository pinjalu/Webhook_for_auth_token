#!/usr/bin/env python3
"""
Simple ServiceM8 API Token & Cookie Extractor
Extracts tokens and cookies for specific APIs without saving files
"""

import json
import time
import os
import logging
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
                options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36")
                
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
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
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
                
                email_field = self.driver.find_element(By.ID, "user_email")
                email_field.clear()
                email_field.send_keys(self.email)
                
                password_field = self.driver.find_element(By.ID, "user_password")
                password_field.clear()
                password_field.send_keys(self.password)
                
                submit_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
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
        """Navigate to Dispatch Board with retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Navigation to Dispatch Board attempt {attempt + 1}/{self.max_retries}")
                wait = WebDriverWait(self.driver, 10)
                
                # Wait for navigation menu to be present
                nav_menu = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "ThemeMainMenu")))
                
                # Wait for dispatch link to be clickable
                dispatch_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'job_dispatch')]")))
                dispatch_link.click()
                
                # Wait for page to load
                wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                time.sleep(10)
                
                # Verify we're on the dispatch page
                current_url = self.driver.current_url
                if "job_dispatch" in current_url or "dispatch" in current_url.lower():
                    logger.info("Successfully navigated to Dispatch Board")
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
        """Create the response in the requested format"""
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
    """Main function with comprehensive error handling"""
    try:
        logger.info("Starting ServiceM8 API Token Extractor...")
        
        # Check environment variables
        email = os.getenv("EMAIL")
        password = os.getenv("PASSWORD")
        
        if not email or not password:
            logger.error("EMAIL and PASSWORD environment variables not found!")
            logger.error("Please create a .env file with your ServiceM8 credentials")
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
