from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Browser setup
options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# Chrome driver start karo
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Website kholo
website_url = "https://jlmorison.xiotz.com/"
print(f"Opening website: {website_url}")
driver.get(website_url)

# 10 second ruko website dekhne ke liye
time.sleep(10)

# Browser band karo
driver.quit()
print("Browser closed")