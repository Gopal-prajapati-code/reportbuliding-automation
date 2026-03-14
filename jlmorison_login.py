from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
import time
import os
import logging
from datetime import datetime, timedelta

# ================= CONFIGURATION =================
WEBSITE_URL = "https://jlmorison.xiotz.com/"
LOGIN_URL = "https://jlmorison.xiotz.com/app/login"

# Login Credentials
USERNAME = "jlmorison"
PASSWORD = "0hUblJLN@FyXEPsa"

# Session Profile Directory
USER_DATA_DIR = r"E:\Business client project\jlmorison_profile"

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('jlmorison_login.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================= BROWSER SETUP =================
def setup_browser(headless=False):
    """
    Chrome browser setup with 64-bit driver
    """
    logger.info("Setting up Chrome browser...")
    
    chrome_options = Options()
    
    # Add user data directory
    if os.path.exists(USER_DATA_DIR):
        chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        logger.info(f"Using existing profile: {USER_DATA_DIR}")
    else:
        os.makedirs(USER_DATA_DIR)
        chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
        logger.info(f"Created new profile: {USER_DATA_DIR}")
    
    # Browser options
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # Disable automation flags
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    try:
        # Force 64-bit driver download
        logger.info("Downloading 64-bit ChromeDriver...")
        
        # Method 1: Direct 64-bit version
        driver_path = ChromeDriverManager(
            version="145.0.7632.117",  # Specific version
            os_type="win64"  # Force 64-bit
        ).install()
        
        logger.info(f"Driver installed at: {driver_path}")
        
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 20)
        
        logger.info("Browser setup successful!")
        return driver, wait
        
    except Exception as e:
        logger.error(f"Browser setup failed: {str(e)}")
        
        # Fallback method
        logger.info("Trying fallback method...")
        try:
            # Alternative: Let webdriver_manager auto-detect
            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            wait = WebDriverWait(driver, 20)
            logger.info("Fallback browser setup successful!")
            return driver, wait
        except Exception as e2:
            logger.error(f"Fallback also failed: {str(e2)}")
            raise

# ================= LOGIN FUNCTION =================
def login_to_website(driver, wait, username, password):
    """
    Perform login to the website
    """
    logger.info("=" * 50)
    logger.info("Starting login process...")
    logger.info("=" * 50)
    
    try:
        # Open login page
        logger.info(f"Opening login page: {LOGIN_URL}")
        driver.get(LOGIN_URL)
        time.sleep(3)
        
        # Take screenshot
        driver.save_screenshot("before_login.png")
        logger.info("Screenshot saved: before_login.png")
        
        # Find username field
        logger.info("Looking for username field...")
        username_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-test-subj='user-name']"))
        )
        username_field.clear()
        username_field.send_keys(username)
        logger.info("✓ Username entered")
        
        # Find password field
        logger.info("Looking for password field...")
        password_field = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-test-subj='password']"))
        )
        password_field.clear()
        password_field.send_keys(password)
        logger.info("✓ Password entered")
        
        # Find and click login button
        logger.info("Looking for login button...")
        login_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-test-subj='submit']"))
        )
        
        # Scroll to button and click
        driver.execute_script("arguments[0].scrollIntoView(true);", login_button)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", login_button)
        logger.info("✓ Login button clicked")
        
        # Wait for login
        time.sleep(5)
        
        # Check success
        current_url = driver.current_url
        logger.info(f"Current URL: {current_url}")
        
        driver.save_screenshot("after_login.png")
        
        if "login" not in current_url.lower():
            logger.info("✓✓✓ LOGIN SUCCESSFUL! ✓✓✓")
            return True
        else:
            logger.error("Login failed")
            return False
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        driver.save_screenshot("login_error.png")
        return False

# ================= DATE PICKER FUNCTIONS =================

def click_date_picker_button(driver, wait):
    """
    Click on the main date picker button
    """
    logger.info("=" * 50)
    logger.info("Clicking Main Date Picker Button...")
    logger.info("=" * 50)
    
    try:
        # Wait for date picker button to be clickable
        logger.info("Waiting for date picker button...")
        
        # Multiple selector strategies
        selectors = [
            (By.CSS_SELECTOR, "button[data-test-subj='superDatePickerShowDatesButton']"),
            (By.CSS_SELECTOR, ".euiSuperDatePicker__prettyFormat"),
            (By.XPATH, "//button[contains(@class, 'euiSuperDatePicker__prettyFormat')]"),
            (By.XPATH, "//button[span[contains(text(), 'Show dates')]]")
        ]
        
        date_button = None
        for selector_type, selector_value in selectors:
            try:
                date_button = wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                logger.info(f"✓ Date picker found with selector: {selector_value}")
                break
            except:
                continue
        
        if not date_button:
            # Try to find by text content
            logger.info("Trying to find by text content...")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                if "Show dates" in button.text or "Last" in button.text:
                    date_button = button
                    logger.info(f"✓ Found button with text: {button.text}")
                    break
        
        if not date_button:
            logger.error("Could not find date picker button")
            return False
        
        # Get button text before clicking
        button_text = date_button.text
        logger.info(f"Date picker button text: {button_text}")
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", date_button)
        time.sleep(1)
        
        # Try multiple click methods
        try:
            # Method 1: Normal click
            date_button.click()
            logger.info("✓ Clicked using normal click")
        except:
            try:
                # Method 2: JavaScript click
                driver.execute_script("arguments[0].click();", date_button)
                logger.info("✓ Clicked using JavaScript")
            except:
                # Method 3: Action chains
                from selenium.webdriver.common.action_chains import ActionChains
                actions = ActionChains(driver)
                actions.move_to_element(date_button).click().perform()
                logger.info("✓ Clicked using ActionChains")
        
        time.sleep(2)
        
        # Verify click worked - check if popup appeared
        try:
            # Check for start date popover button
            start_date = driver.find_element(By.CSS_SELECTOR, "button[data-test-subj='superDatePickerstartDatePopoverButton']")
            logger.info("✓ Date picker popup opened successfully")
            return True
        except:
            # Check for any popup/dialog
            popups = driver.find_elements(By.CSS_SELECTOR, ".euiPopover, [role='dialog']")
            if popups:
                logger.info(f"✓ Found {len(popups)} popup elements")
                return True
            else:
                logger.warning("Could not verify popup opened, but continuing...")
                return True
        
    except Exception as e:
        logger.error(f"Error clicking date picker: {str(e)}")
        driver.save_screenshot("date_picker_error.png")
        return False

def click_start_date_popover(driver, wait):
    """
    Click on the start date popover button (initial click)
    """
    logger.info("=" * 50)
    logger.info("Clicking Start Date Popover Button...")
    logger.info("=" * 50)
    
    try:
        # Wait for start date button to be clickable
        logger.info("Waiting for start date button...")
        
        # Multiple selector strategies
        selectors = [
            (By.CSS_SELECTOR, "button[data-test-subj='superDatePickerstartDatePopoverButton']"),
            (By.CSS_SELECTOR, ".euiDatePopoverButton.euiDatePopoverButton--start"),
            (By.XPATH, "//button[contains(@class, 'euiDatePopoverButton--start')]"),
            (By.XPATH, "//button[@title='now-60m']"),
            (By.XPATH, "//button[contains(text(), 'an hour ago')]")
        ]
        
        start_date_button = None
        for selector_type, selector_value in selectors:
            try:
                start_date_button = wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                logger.info(f"✓ Start date button found with selector: {selector_value}")
                break
            except:
                continue
        
        if not start_date_button:
            # Try to find by attributes
            logger.info("Trying to find by attributes...")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                class_name = button.get_attribute("class") or ""
                data_test = button.get_attribute("data-test-subj") or ""
                title = button.get_attribute("title") or ""
                
                if "euiDatePopoverButton--start" in class_name or "startDatePopover" in data_test or "now-60m" in title:
                    start_date_button = button
                    logger.info(f"✓ Found button with class: {class_name}")
                    break
        
        if not start_date_button:
            logger.error("Could not find start date button")
            return False
        
        # Get button text
        button_text = start_date_button.text
        logger.info(f"Start date button text: {button_text}")
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", start_date_button)
        time.sleep(1)
        
        # Try multiple click methods
        try:
            # Method 1: Normal click
            start_date_button.click()
            logger.info("✓ Clicked using normal click")
        except Exception as e1:
            logger.warning(f"Normal click failed: {str(e1)}")
            try:
                # Method 2: JavaScript click
                driver.execute_script("arguments[0].click();", start_date_button)
                logger.info("✓ Clicked using JavaScript")
            except Exception as e2:
                logger.warning(f"JavaScript click failed: {str(e2)}")
                try:
                    # Method 3: Action chains
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(start_date_button).click().perform()
                    logger.info("✓ Clicked using ActionChains")
                except Exception as e3:
                    logger.error(f"All click methods failed: {str(e3)}")
                    return False
        
        time.sleep(2)
        
        # Verify click worked - check for date picker popup content
        try:
            # Check for absolute/relative tabs
            absolute_tab = driver.find_elements(By.CSS_SELECTOR, "button[data-test-subj='superDatePickerAbsoluteTab']")
            if absolute_tab:
                logger.info("✓ Start date popup opened successfully (Absolute tab found)")
            else:
                # Check for any date picker content
                date_content = driver.find_elements(By.CSS_SELECTOR, ".euiDatePopoverContent, .react-datepicker")
                if date_content:
                    logger.info(f"✓ Found {len(date_content)} date picker elements")
                else:
                    logger.warning("Could not verify popup content, but continuing...")
        except:
            logger.warning("Could not verify popup content, but continuing...")
        
        return True
        
    except Exception as e:
        logger.error(f"Error clicking start date button: {str(e)}")
        driver.save_screenshot("start_date_error.png")
        return False

def click_updated_start_date_popover(driver, wait):
    """
    Click on the updated start date popover button after date/time selection
    """
    logger.info("=" * 50)
    logger.info("Clicking Updated Start Date Popover Button...")
    logger.info("=" * 50)
    
    try:
        # Wait for updated start date button to be clickable
        logger.info("Waiting for updated start date button...")
        time.sleep(2)
        
        # Multiple selector strategies for the updated button
        selectors = [
            (By.CSS_SELECTOR, "button[data-test-subj='superDatePickerstartDatePopoverButton'].euiDatePopoverButton-isSelected"),
            (By.CSS_SELECTOR, ".euiDatePopoverButton.euiDatePopoverButton--start.euiDatePopoverButton-isSelected"),
            (By.XPATH, "//button[contains(@class, 'euiDatePopoverButton--start') and contains(@class, 'euiDatePopoverButton-isSelected')]"),
            (By.XPATH, "//button[@data-test-subj='superDatePickerstartDatePopoverButton' and contains(@class, 'isSelected')]"),
            (By.XPATH, "//button[contains(text(), 'Mar 13, 2026') and contains(text(), '00:00')]")
        ]
        
        start_date_button = None
        for selector_type, selector_value in selectors:
            try:
                start_date_button = wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                logger.info(f"✓ Updated start date button found with selector: {selector_value}")
                break
            except:
                continue
        
        if not start_date_button:
            # Try to find by any start date button (fallback)
            logger.info("Trying to find any start date button...")
            buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-test-subj='superDatePickerstartDatePopoverButton']")
            if buttons:
                start_date_button = buttons[0]
                logger.info("✓ Found start date button (generic)")
        
        if not start_date_button:
            logger.error("Could not find updated start date button")
            return False
        
        # Get button text to verify it's the updated one
        button_text = start_date_button.text
        button_title = start_date_button.get_attribute("title") or ""
        button_class = start_date_button.get_attribute("class") or ""
        
        logger.info(f"Updated start date button text: {button_text}")
        logger.info(f"Button title: {button_title}")
        logger.info(f"Button class: {button_class}")
        
        # Verify it's the updated button
        if "Mar 13" in button_text and "00:00" in button_text:
            logger.info("✓ Verified button shows correct date: Mar 13, 2026 @ 00:00")
        else:
            logger.warning(f"Button shows: {button_text} - may not be updated yet")
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", start_date_button)
        time.sleep(1)
        
        # Try multiple click methods
        try:
            # Method 1: Normal click
            start_date_button.click()
            logger.info("✓ Clicked updated start date button using normal click")
        except Exception as e1:
            logger.warning(f"Normal click failed: {str(e1)}")
            try:
                # Method 2: JavaScript click
                driver.execute_script("arguments[0].click();", start_date_button)
                logger.info("✓ Clicked updated start date button using JavaScript")
            except Exception as e2:
                logger.warning(f"JavaScript click failed: {str(e2)}")
                try:
                    # Method 3: Action chains
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(start_date_button).click().perform()
                    logger.info("✓ Clicked updated start date button using ActionChains")
                except Exception as e3:
                    logger.error(f"All click methods failed: {str(e3)}")
                    return False
        
        time.sleep(2)
        
        # Verify the click opened the popup again
        try:
            # Check if absolute tab is visible (popup opened)
            absolute_tab = driver.find_elements(By.CSS_SELECTOR, "button[data-test-subj='superDatePickerAbsoluteTab']")
            if absolute_tab:
                logger.info("✓ Date picker popup reopened successfully")
            else:
                # Check for any date picker content
                date_content = driver.find_elements(By.CSS_SELECTOR, ".euiDatePopoverContent, .react-datepicker")
                if date_content:
                    logger.info(f"✓ Found {len(date_content)} date picker elements - popup reopened")
                else:
                    logger.warning("Could not verify popup reopened, but continuing...")
        except:
            logger.warning("Could not verify popup reopening, but continuing...")
        
        # Take screenshot
        driver.save_screenshot("updated_start_date_clicked.png")
        logger.info("✓ Updated start date button clicked successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error clicking updated start date button: {str(e)}")
        driver.save_screenshot("updated_start_date_error.png")
        return False

# ================= FUNCTION: CLICK END DATE POPOVER =================

def click_end_date_popover(driver, wait):
    """
    Click on the end date popover button
    """
    logger.info("=" * 50)
    logger.info("Clicking End Date Popover Button...")
    logger.info("=" * 50)
    
    try:
        # Wait for end date button to be clickable
        logger.info("Waiting for end date button...")
        time.sleep(2)
        
        # Multiple selector strategies for end date button
        selectors = [
            (By.CSS_SELECTOR, "button[data-test-subj='superDatePickerendDatePopoverButton']"),
            (By.CSS_SELECTOR, ".euiDatePopoverButton.euiDatePopoverButton--end"),
            (By.XPATH, "//button[contains(@class, 'euiDatePopoverButton--end')]"),
            (By.XPATH, "//button[@data-test-subj='superDatePickerendDatePopoverButton']"),
            (By.XPATH, "//button[contains(text(), 'now') and contains(@class, 'euiDatePopoverButton')]")
        ]
        
        end_date_button = None
        for selector_type, selector_value in selectors:
            try:
                end_date_button = wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                logger.info(f"✓ End date button found with selector: {selector_value}")
                break
            except:
                continue
        
        if not end_date_button:
            logger.error("Could not find end date button")
            return False
        
        # Get button text
        button_text = end_date_button.text
        logger.info(f"End date button text: {button_text}")
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", end_date_button)
        time.sleep(1)
        
        # Click the button
        try:
            end_date_button.click()
            logger.info("✓ Clicked end date button using normal click")
        except:
            driver.execute_script("arguments[0].click();", end_date_button)
            logger.info("✓ Clicked end date button using JavaScript")
        
        time.sleep(2)
        
        # Verify click opened popup
        try:
            absolute_tab = driver.find_elements(By.CSS_SELECTOR, "button[data-test-subj='superDatePickerAbsoluteTab']")
            if absolute_tab:
                logger.info("✓ End date popup opened successfully")
        except:
            pass
        
        driver.save_screenshot("end_date_clicked.png")
        logger.info("✓ End date button clicked successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error clicking end date button: {str(e)}")
        driver.save_screenshot("end_date_error.png")
        return False

# ================= NEW FUNCTION: CLICK UPDATED END DATE POPOVER =================

def click_updated_end_date_popover(driver, wait):
    """
    Click on the updated end date popover button after date/time selection
    Button: <button class="euiDatePopoverButton euiDatePopoverButton--end" title="2026-03-13T18:30:00.000Z" data-test-subj="superDatePickerendDatePopoverButton">Mar 14, 2026 @ 00:00:00.000</button>
    """
    logger.info("=" * 50)
    logger.info("Clicking Updated End Date Popover Button...")
    logger.info("=" * 50)
    
    try:
        # Wait for updated end date button to be clickable
        logger.info("Waiting for updated end date button...")
        time.sleep(2)
        
        # Multiple selector strategies for updated end date button
        selectors = [
            (By.CSS_SELECTOR, "button[data-test-subj='superDatePickerendDatePopoverButton']"),
            (By.CSS_SELECTOR, ".euiDatePopoverButton.euiDatePopoverButton--end"),
            (By.XPATH, "//button[contains(@class, 'euiDatePopoverButton--end')]"),
            (By.XPATH, "//button[@data-test-subj='superDatePickerendDatePopoverButton']"),
            (By.XPATH, "//button[contains(text(), 'Mar 14, 2026') and contains(text(), '00:00')]"),
            (By.XPATH, "//button[@title='2026-03-13T18:30:00.000Z']")
        ]
        
        end_date_button = None
        for selector_type, selector_value in selectors:
            try:
                end_date_button = wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                logger.info(f"✓ Updated end date button found with selector: {selector_value}")
                break
            except:
                continue
        
        if not end_date_button:
            logger.error("Could not find updated end date button")
            return False
        
        # Get button text to verify it's the updated one
        button_text = end_date_button.text
        button_title = end_date_button.get_attribute("title") or ""
        button_class = end_date_button.get_attribute("class") or ""
        
        logger.info(f"Updated end date button text: {button_text}")
        logger.info(f"Button title: {button_title}")
        logger.info(f"Button class: {button_class}")
        
        # Verify it's the updated button
        if "Mar 14" in button_text and "00:00" in button_text:
            logger.info("✓ Verified button shows correct date: Mar 14, 2026 @ 00:00")
        else:
            logger.warning(f"Button shows: {button_text} - may not be updated yet")
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", end_date_button)
        time.sleep(1)
        
        # Click the button
        try:
            end_date_button.click()
            logger.info("✓ Clicked updated end date button using normal click")
        except:
            driver.execute_script("arguments[0].click();", end_date_button)
            logger.info("✓ Clicked updated end date button using JavaScript")
        
        time.sleep(2)
        
        # Take screenshot
        driver.save_screenshot("updated_end_date_clicked.png")
        logger.info("✓ Updated end date button clicked successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error clicking updated end date button: {str(e)}")
        driver.save_screenshot("updated_end_date_error.png")
        return False

# ================= NEW FUNCTION: CLICK UPDATE BUTTON =================

def click_update_button(driver, wait):
    """
    Click on the Update button to apply the date range
    Button: <button class="euiButton euiButton--success euiButton--fill euiSuperUpdateButton" type="button" data-test-subj="querySubmitButton">
    """
    logger.info("=" * 50)
    logger.info("Clicking Update Button...")
    logger.info("=" * 50)
    
    try:
        # Wait for update button to be clickable
        logger.info("Waiting for Update button...")
        time.sleep(2)
        
        # Multiple selector strategies for update button
        selectors = [
            (By.CSS_SELECTOR, "button[data-test-subj='querySubmitButton']"),
            (By.CSS_SELECTOR, ".euiButton.euiButton--success.euiSuperUpdateButton"),
            (By.XPATH, "//button[contains(@class, 'euiSuperUpdateButton')]"),
            (By.XPATH, "//button[@data-test-subj='querySubmitButton']"),
            (By.XPATH, "//button[span[contains(text(), 'Update')]]"),
            (By.XPATH, "//button[contains(@class, 'euiButton--success') and contains(text(), 'Update')]")
        ]
        
        update_button = None
        for selector_type, selector_value in selectors:
            try:
                update_button = wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                logger.info(f"✓ Update button found with selector: {selector_value}")
                break
            except:
                continue
        
        if not update_button:
            # Try to find by class and text
            logger.info("Trying to find by class and text...")
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                class_name = button.get_attribute("class") or ""
                button_text = button.text
                if "euiSuperUpdateButton" in class_name and "Update" in button_text:
                    update_button = button
                    logger.info(f"✓ Found Update button with class: {class_name}")
                    break
        
        if not update_button:
            logger.error("Could not find Update button")
            return False
        
        # Get button info
        button_text = update_button.text
        button_class = update_button.get_attribute("class") or ""
        logger.info(f"Update button text: {button_text}")
        logger.info(f"Button class: {button_class}")
        
        # Check if button is enabled
        is_enabled = update_button.is_enabled()
        logger.info(f"Button enabled: {is_enabled}")
        
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoView(true);", update_button)
        time.sleep(1)
        
        # Try multiple click methods
        try:
            # Method 1: Normal click
            update_button.click()
            logger.info("✓ Clicked Update button using normal click")
        except Exception as e1:
            logger.warning(f"Normal click failed: {str(e1)}")
            try:
                # Method 2: JavaScript click
                driver.execute_script("arguments[0].click();", update_button)
                logger.info("✓ Clicked Update button using JavaScript")
            except Exception as e2:
                logger.warning(f"JavaScript click failed: {str(e2)}")
                try:
                    # Method 3: Action chains
                    from selenium.webdriver.common.action_chains import ActionChains
                    actions = ActionChains(driver)
                    actions.move_to_element(update_button).click().perform()
                    logger.info("✓ Clicked Update button using ActionChains")
                except Exception as e3:
                    logger.error(f"All click methods failed: {str(e3)}")
                    return False
        
        time.sleep(3)  # Wait for update to complete
        
        # Verify update clicked
        try:
            # Check for loading indicator or success message
            loading = driver.find_elements(By.CSS_SELECTOR, ".euiLoadingSpinner, .euiProgress")
            if loading:
                logger.info("✓ Update in progress...")
            else:
                logger.info("✓ Update button clicked successfully")
        except:
            pass
        
        # Take screenshot
        driver.save_screenshot("update_button_clicked.png")
        logger.info("✓ Update button clicked successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error clicking Update button: {str(e)}")
        driver.save_screenshot("update_button_error.png")
        return False

def click_end_date_absolute_tab(driver, wait):
    """
    Click on the Absolute tab for end date
    """
    logger.info("=" * 50)
    logger.info("Clicking End Date Absolute Tab...")
    logger.info("=" * 50)
    
    try:
        # Wait for absolute tab to be clickable (specifically for end date)
        logger.info("Waiting for End Date Absolute tab...")
        time.sleep(2)
        
        # Multiple selector strategies for end date absolute tab
        selectors = [
            (By.XPATH, "//button[@role='tab' and @data-test-subj='superDatePickerAbsoluteTab' and contains(@aria-label, 'End date')]"),
            (By.XPATH, "//button[@aria-label='End date: Absolute']"),
            (By.CSS_SELECTOR, "button[data-test-subj='superDatePickerAbsoluteTab'][aria-label='End date: Absolute']")
        ]
        
        absolute_tab = None
        for selector_type, selector_value in selectors:
            try:
                absolute_tab = wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                logger.info(f"✓ End date Absolute tab found with selector: {selector_value}")
                break
            except:
                continue
        
        if not absolute_tab:
            # Try to find by searching all absolute tabs
            logger.info("Trying to find by searching all absolute tabs...")
            all_absolute_tabs = driver.find_elements(By.CSS_SELECTOR, "button[data-test-subj='superDatePickerAbsoluteTab']")
            for tab in all_absolute_tabs:
                aria_label = tab.get_attribute("aria-label") or ""
                if "End date" in aria_label:
                    absolute_tab = tab
                    logger.info(f"✓ Found End date Absolute tab with aria-label: {aria_label}")
                    break
        
        if not absolute_tab:
            logger.error("Could not find End date Absolute tab")
            return False
        
        # Check if already selected
        aria_selected = absolute_tab.get_attribute("aria-selected")
        if aria_selected == "true":
            logger.info("End date Absolute tab is already selected")
            return True
        
        # Click the tab
        driver.execute_script("arguments[0].scrollIntoView(true);", absolute_tab)
        time.sleep(1)
        
        try:
            absolute_tab.click()
            logger.info("✓ Clicked End date Absolute tab using normal click")
        except:
            driver.execute_script("arguments[0].click();", absolute_tab)
            logger.info("✓ Clicked End date Absolute tab using JavaScript")
        
        time.sleep(2)
        
        driver.save_screenshot("end_date_absolute_tab_clicked.png")
        logger.info("✓ End date Absolute tab clicked successfully!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error clicking End date Absolute tab: {str(e)}")
        driver.save_screenshot("end_date_absolute_tab_error.png")
        return False

# ================= FUNCTION: SELECT TODAY'S DATE FOR END DATE =================

def select_end_date_today(driver, wait):
    """
    Select today's date from the end date picker
    """
    logger.info("=" * 50)
    logger.info("Selecting Today's Date for End Date...")
    logger.info("=" * 50)
    
    try:
        # Wait for date picker to be visible
        logger.info("Waiting for date picker calendar...")
        time.sleep(2)
        
        # Get today's date number
        today = datetime.now().day
        
        logger.info(f"Today is: {today}")
        
        # Find today's date
        today_element = None
        date_elements = driver.find_elements(By.CSS_SELECTOR, ".react-datepicker__day")
        
        for el in date_elements:
            class_name = el.get_attribute("class") or ""
            if "today" in class_name and el.text.strip() == str(today):
                today_element = el
                logger.info("✓ Found today's date")
                break
        
        if not today_element:
            logger.error("Could not find today's date")
            return False
        
        # Click today's date
        driver.execute_script("arguments[0].scrollIntoView(true);", today_element)
        time.sleep(1)
        
        try:
            today_element.click()
            logger.info("✓ Clicked today's date")
        except:
            driver.execute_script("arguments[0].click();", today_element)
            logger.info("✓ Clicked today's date using JavaScript")
        
        time.sleep(2)
        
        driver.save_screenshot(f"end_date_today_{today}_selected.png")
        logger.info(f"✓ Today's date ({today}) selected successfully for End Date!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error selecting today's date: {str(e)}")
        driver.save_screenshot("end_date_today_error.png")
        return False

# ================= FUNCTION: SELECT TIME 00:00 FOR END DATE =================

def select_end_date_time_0000(driver, wait):
    """
    Select 00:00 time from the end date time picker
    """
    logger.info("=" * 50)
    logger.info("Selecting Time 00:00 for End Date...")
    logger.info("=" * 50)
    
    try:
        # Wait for time container to be visible
        logger.info("Waiting for time picker container...")
        time.sleep(2)
        
        # Find 00:00 time
        time_element = None
        time_items = driver.find_elements(By.CSS_SELECTOR, ".react-datepicker__time-list-item")
        
        for item in time_items:
            if item.text == "00:00" and item.is_displayed():
                time_element = item
                logger.info("✓ Found 00:00 in time list")
                break
        
        if not time_element:
            logger.error("Could not find 00:00 time element")
            return False
        
        # Click the time
        driver.execute_script("arguments[0].scrollIntoView(true);", time_element)
        time.sleep(1)
        
        try:
            time_element.click()
            logger.info("✓ Clicked 00:00")
        except:
            driver.execute_script("arguments[0].click();", time_element)
            logger.info("✓ Clicked 00:00 using JavaScript")
        
        time.sleep(2)
        
        driver.save_screenshot("end_date_time_0000_selected.png")
        logger.info("✓ Time 00:00 selected successfully for End Date!")
        
        return True
        
    except Exception as e:
        logger.error(f"Error selecting time 00:00: {str(e)}")
        driver.save_screenshot("end_date_time_error.png")
        return False

def click_absolute_tab(driver, wait):
    """
    Click on the Absolute tab (for start date)
    """
    logger.info("=" * 50)
    logger.info("Clicking Absolute Tab (Start Date)...")
    logger.info("=" * 50)
    
    try:
        # Wait for absolute tab to be clickable
        logger.info("Waiting for Absolute tab...")
        
        # Multiple selector strategies
        selectors = [
            (By.CSS_SELECTOR, "button[data-test-subj='superDatePickerAbsoluteTab']"),
            (By.CSS_SELECTOR, "button#absolute.euiTab"),
            (By.XPATH, "//button[@role='tab' and @id='absolute']"),
            (By.XPATH, "//button[contains(@class, 'euiTab') and span[text()='Absolute']]"),
            (By.XPATH, "//button[@aria-label='Start date: Absolute']")
        ]
        
        absolute_tab = None
        for selector_type, selector_value in selectors:
            try:
                absolute_tab = wait.until(
                    EC.element_to_be_clickable((selector_type, selector_value))
                )
                logger.info(f"✓ Absolute tab found with selector: {selector_value}")
                break
            except:
                continue
        
        if not absolute_tab:
            # Try to find by text
            logger.info("Trying to find by text...")
            tabs = driver.find_elements(By.CSS_SELECTOR, "button[role='tab']")
            for tab in tabs:
                if "Absolute" in tab.text:
                    absolute_tab = tab
                    logger.info(f"✓ Found tab with text: {tab.text}")
                    break
        
        if not absolute_tab:
            logger.error("Could not find Absolute tab")
            return False
        
        # Check if already selected
        aria_selected = absolute_tab.get_attribute("aria-selected")
        if aria_selected == "true":
            logger.info("Absolute tab is already selected")
            return True
        
        # Click the tab
        driver.execute_script("arguments[0].scrollIntoView(true);", absolute_tab)
        time.sleep(1)
        
        try:
            absolute_tab.click()
            logger.info("✓ Clicked Absolute tab")
        except:
            driver.execute_script("arguments[0].click();", absolute_tab)
            logger.info("✓ Clicked Absolute tab using JavaScript")
        
        time.sleep(2)
        
        return True
        
    except Exception as e:
        logger.error(f"Error clicking Absolute tab: {str(e)}")
        driver.save_screenshot("absolute_tab_error.png")
        return False

# ================= FUNCTION: SELECT YESTERDAY'S DATE (START DATE) =================

def select_yesterday_date(driver, wait):
    """
    Select yesterday's date from the date picker (for start date)
    """
    logger.info("=" * 50)
    logger.info("Selecting Yesterday's Date (Start Date)...")
    logger.info("=" * 50)
    
    try:
        # Wait for date picker to be visible
        logger.info("Waiting for date picker calendar...")
        time.sleep(2)
        
        # Get yesterday's date
        yesterday = datetime.now().day - 1
        logger.info(f"Looking for yesterday: {yesterday}")
        
        # Find yesterday's date
        yesterday_element = None
        date_elements = driver.find_elements(By.CSS_SELECTOR, ".react-datepicker__day")
        
        for el in date_elements:
            if el.text.strip() == str(yesterday) and "outside-month" not in el.get_attribute("class"):
                yesterday_element = el
                logger.info(f"✓ Found yesterday's date ({yesterday})")
                break
        
        if not yesterday_element:
            logger.error(f"Could not find yesterday's date ({yesterday})")
            return False
        
        # Click yesterday's date
        driver.execute_script("arguments[0].scrollIntoView(true);", yesterday_element)
        time.sleep(1)
        
        try:
            yesterday_element.click()
            logger.info("✓ Clicked yesterday's date")
        except:
            driver.execute_script("arguments[0].click();", yesterday_element)
            logger.info("✓ Clicked yesterday's date using JavaScript")
        
        time.sleep(2)
        
        return True
        
    except Exception as e:
        logger.error(f"Error selecting yesterday's date: {str(e)}")
        driver.save_screenshot("yesterday_date_error.png")
        return False

# ================= FUNCTION: SELECT TIME 00:00 (START DATE) =================

def select_time_0000(driver, wait):
    """
    Select 00:00 time from the time picker (for start date)
    """
    logger.info("=" * 50)
    logger.info("Selecting Time 00:00 (Start Date)...")
    logger.info("=" * 50)
    
    try:
        # Wait for time container to be visible
        logger.info("Waiting for time picker container...")
        time.sleep(2)
        
        # Find 00:00 time
        time_element = None
        time_items = driver.find_elements(By.CSS_SELECTOR, ".react-datepicker__time-list-item")
        
        for item in time_items:
            if item.text == "00:00" and item.is_displayed():
                time_element = item
                logger.info("✓ Found 00:00 in time list")
                break
        
        if not time_element:
            logger.error("Could not find 00:00 time element")
            return False
        
        # Click the time
        driver.execute_script("arguments[0].scrollIntoView(true);", time_element)
        time.sleep(1)
        
        try:
            time_element.click()
            logger.info("✓ Clicked 00:00")
        except:
            driver.execute_script("arguments[0].click();", time_element)
            logger.info("✓ Clicked 00:00 using JavaScript")
        
        time.sleep(2)
        
        return True
        
    except Exception as e:
        logger.error(f"Error selecting time 00:00: {str(e)}")
        driver.save_screenshot("time_selection_error.png")
        return False

# ================= FUNCTION: CLICK PANEL ARROW =================

def click_panel_arrow(driver, wait):
    """
    Click on the panel arrow element (if needed)
    """
    logger.info("=" * 50)
    logger.info("Clicking Panel Arrow...")
    logger.info("=" * 50)
    
    try:
        selectors = [
            (By.CSS_SELECTOR, ".euiPopover__panelArrow"),
            (By.XPATH, "//div[contains(@class, 'euiPopover__panelArrow')]")
        ]
        
        arrow_element = None
        for selector_type, selector_value in selectors:
            try:
                elements = driver.find_elements(selector_type, selector_value)
                if elements:
                    arrow_element = elements[0]
                    logger.info(f"✓ Found panel arrow with selector: {selector_value}")
                    break
            except:
                continue
        
        if not arrow_element:
            logger.info("Panel arrow not found - continuing...")
            return True
        
        try:
            arrow_element.click()
            logger.info("✓ Clicked panel arrow")
        except:
            driver.execute_script("arguments[0].click();", arrow_element)
            logger.info("✓ Clicked panel arrow using JavaScript")
        
        time.sleep(1)
        return True
        
    except Exception as e:
        logger.warning(f"Error with panel arrow: {str(e)} - continuing...")
        return True

def wait_for_dashboard_load(driver, wait):
    """
    Wait for dashboard to fully load after login
    """
    logger.info("Waiting for dashboard to load...")
    
    try:
        wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                "button[data-test-subj='superDatePickerShowDatesButton'], .euiSuperDatePicker"))
        )
        logger.info("✓ Dashboard loaded")
        time.sleep(3)
        return True
    except:
        logger.warning("Dashboard elements not found, but continuing...")
        time.sleep(5)
        return True

# ================= MANUAL DRIVER SETUP =================
def manual_driver_setup():
    """
    Manual ChromeDriver setup if automatic fails
    """
    logger.info("Attempting manual driver setup...")
    
    chrome_options = Options()
    chrome_options.add_argument(f"--user-data-dir={USER_DATA_DIR}")
    chrome_options.add_argument("--start-maximized")
    
    manual_path = r"C:\Windows\chromedriver.exe"
    
    try:
        if os.path.exists(manual_path):
            service = Service(manual_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            wait = WebDriverWait(driver, 20)
            logger.info("Manual driver setup successful!")
            return driver, wait
        else:
            logger.error(f"Manual driver not found at: {manual_path}")
            return None, None
    except Exception as e:
        logger.error(f"Manual setup failed: {str(e)}")
        return None, None

# ================= COMPLETE DATE SELECTION PROCESS =================
def complete_date_selection_process(driver, wait):
    """
    Complete the entire date selection process
    Step 1: Click main date picker
    Step 2: Click start date popover (initial)
    Step 3: Click Absolute tab (start date)
    Step 4: Select yesterday's date (start date)
    Step 5: Select time 00:00 (start date)
    Step 6: Click panel arrow (if needed)
    Step 7: Click updated start date popover
    Step 8: Click end date popover
    Step 9: Click End date Absolute tab
    Step 10: Select today's date (end date)
    Step 11: Select time 00:00 (end date)
    Step 12: Click updated end date popover
    Step 13: Click Update button
    """
    logger.info("=" * 60)
    logger.info("STARTING COMPLETE DATE SELECTION PROCESS")
    logger.info("=" * 60)
    
    steps = [
        ("Step 1: Click main date picker", click_date_picker_button),
        ("Step 2: Click start date popover (initial)", click_start_date_popover),
        ("Step 3: Click Absolute tab (start date)", click_absolute_tab),
        ("Step 4: Select yesterday's date (start date)", select_yesterday_date),
        ("Step 5: Select time 00:00 (start date)", select_time_0000),
        ("Step 6: Click panel arrow (if needed)", click_panel_arrow),
        ("Step 7: Click updated start date popover", click_updated_start_date_popover),
        ("Step 8: Click end date popover", click_end_date_popover),
        ("Step 9: Click End date Absolute tab", click_end_date_absolute_tab),
        ("Step 10: Select today's date (end date)", select_end_date_today),
        ("Step 11: Select time 00:00 (end date)", select_end_date_time_0000),
        ("Step 12: Click updated end date popover", click_updated_end_date_popover),
        ("Step 13: Click Update button", click_update_button)
    ]
    
    for step_name, step_function in steps:
        logger.info(f"\n▶ {step_name}")
        if not step_function(driver, wait):
            logger.error(f"❌ Failed at {step_name}")
            return False
        logger.info(f"✓ {step_name} completed")
        time.sleep(2)
    
    logger.info("\n" + "=" * 60)
    logger.info("✓✓✓ DATE SELECTION PROCESS COMPLETED SUCCESSFULLY! ✓✓✓")
    logger.info("=" * 60)
    
    driver.save_screenshot("date_selection_complete.png")
    logger.info("Screenshot saved: date_selection_complete.png")
    
    return True

# ================= MAIN =================
def main():
    """
    Main function with multiple setup attempts
    """
    print("""
    ╔══════════════════════════════════════════╗
    ║   JLMORISON.XIOTZ.COM AUTOMATION         ║
    ║   Login + Complete Date Selection        ║
    ║   Start Date: Yesterday + 00:00          ║
    ║   End Date: Today + 00:00                ║
    ║   + Update Button Click                  ║
    ╚══════════════════════════════════════════╝
    """)
    
    logger.info("\n" + "=" * 60)
    logger.info("JLMORISON.XIOTZ.COM AUTOMATION")
    logger.info("=" * 60)
    
    driver = None
    wait = None
    
    try:
        driver, wait = setup_browser()
    except:
        logger.warning("Automatic setup failed, trying manual...")
        driver, wait = manual_driver_setup()
    
    if not driver:
        logger.error("Could not setup browser. Please check ChromeDriver installation.")
        return
    
    try:
        login_success = login_to_website(driver, wait, USERNAME, PASSWORD)
        
        if login_success:
            logger.info("\n✓✓✓ LOGIN SUCCESSFUL! ✓✓✓")
            
            wait_for_dashboard_load(driver, wait)
            selection_complete = complete_date_selection_process(driver, wait)
            
            if selection_complete:
                logger.info("\n✓✓✓ ALL STEPS COMPLETED SUCCESSFULLY! ✓✓✓")
            else:
                logger.warning("\n⚠️ Some steps may have failed")
            
            logger.info("\n" + "=" * 50)
            logger.info("Browser will remain open.")
            logger.info("Press Ctrl+C to close.")
            logger.info("=" * 50)
            
            try:
                while True:
                    time.sleep(10)
                    logger.info("Session active...")
            except KeyboardInterrupt:
                logger.info("\nUser interrupted. Closing browser...")
        else:
            logger.error("\n✗✗✗ LOGIN FAILED! ✗✗✗")
            
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    main()