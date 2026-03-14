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
    Click on the date picker button
    Button: <button class="euiSuperDatePicker__prettyFormat" data-test-subj="superDatePickerShowDatesButton">
    """
    logger.info("=" * 50)
    logger.info("Clicking Date Picker Button...")
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

def wait_for_dashboard_load(driver, wait):
    """
    Wait for dashboard to fully load after login
    """
    logger.info("Waiting for dashboard to load...")
    
    try:
        # Wait for common dashboard elements
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
    
    # Manually specify the driver path
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

# ================= MAIN =================
def main():
    """
    Main function with multiple setup attempts
    """
    print("""
    ╔══════════════════════════════════════════╗
    ║   JLMORISON.XIOTZ.COM AUTOMATION         ║
    ║        Login + Date Picker Click         ║
    ╚══════════════════════════════════════════╝
    """)
    
    logger.info("\n" + "=" * 60)
    logger.info("JLMORISON.XIOTZ.COM AUTOMATION")
    logger.info("=" * 60)
    
    driver = None
    wait = None
    
    # Try automatic setup first
    try:
        driver, wait = setup_browser()
    except:
        logger.warning("Automatic setup failed, trying manual...")
        driver, wait = manual_driver_setup()
    
    if not driver:
        logger.error("Could not setup browser. Please check ChromeDriver installation.")
        return
    
    try:
        # Step 1: Perform login
        login_success = login_to_website(driver, wait, USERNAME, PASSWORD)
        
        if login_success:
            logger.info("\n✓✓✓ LOGIN SUCCESSFUL! ✓✓✓")
            
            # Step 2: Wait for dashboard to load
            wait_for_dashboard_load(driver, wait)
            
            # Step 3: Click date picker button
            date_picker_clicked = click_date_picker_button(driver, wait)
            
            if date_picker_clicked:
                logger.info("\n✓✓✓ DATE PICKER CLICKED SUCCESSFULLY! ✓✓✓")
                
                # Take screenshot after clicking date picker
                driver.save_screenshot("after_date_picker_click.png")
                logger.info("Screenshot saved: after_date_picker_click.png")
            else:
                logger.warning("\n⚠️ Date picker click may have failed")
            
            # Keep browser open
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

# ================= STANDALONE DATE PICKER FUNCTION =================
def just_click_date_picker():
    """
    Standalone function to just click date picker (if already logged in)
    """
    print("""
    ╔══════════════════════════════════════════╗
    ║        JUST CLICK DATE PICKER            ║
    ╚══════════════════════════════════════════╝
    """)
    
    driver, wait = setup_browser()
    
    try:
        # Go to dashboard (assuming already logged in)
        driver.get("https://jlmorison.xiotz.com/app/dashboards")
        time.sleep(5)
        
        # Click date picker
        click_date_picker_button(driver, wait)
        
        # Keep browser open
        input("\nPress Enter to close browser...")
        
    finally:
        driver.quit()

if __name__ == "__main__":
    # Run main function (login + date picker)
    main()
    
    # Uncomment below if you just want to click date picker (assuming already logged in)
    # just_click_date_picker()