import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ---------------- CONFIGURABLE PARAMETERS ----------------
username = "your_username"
password = "your_password"
usernames_to_unfollow = ['natgeo', 'nasa', 'python.learning', 'someotheraccount']

# Rate limiting settings
MAX_UNFOLLOWS_PER_HOUR = 20
MAX_UNFOLLOWS_PER_DAY = 100
MIN_DELAY = 30  # seconds
MAX_DELAY = 60  # seconds
# --------------------------------------------------------

unfollows_today = 0
unfollows_this_hour = 0
hour_start_time = time.time()
day_start_time = time.time()

# Setup Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Login
driver.get("https://www.instagram.com/accounts/login/")
time.sleep(5)

driver.find_element(By.NAME, 'username').send_keys(username)
driver.find_element(By.NAME, 'password').send_keys(password + Keys.RETURN)
time.sleep(5)

# Loop through each username to unfollow
for user in usernames_to_unfollow:
    current_time = time.time()

    # Reset hourly counter
    if current_time - hour_start_time > 3600:
        unfollows_this_hour = 0
        hour_start_time = current_time

    # Stop if limits are exceeded
    if unfollows_today >= MAX_UNFOLLOWS_PER_DAY:
        print("Daily limit reached. Stopping.")
        break
    if unfollows_this_hour >= MAX_UNFOLLOWS_PER_HOUR:
        wait = 3600 - (current_time - hour_start_time)
        print(f"Hourly limit reached. Waiting {int(wait)} seconds.")
        time.sleep(wait)
        unfollows_this_hour = 0
        hour_start_time = time.time()

    # Visit user profile
    driver.get(f"https://www.instagram.com/{user}/")
    time.sleep(random.uniform(4, 6))

    try:
        unfollow_button = driver.find_element(By.XPATH, "//button[text()='Following']")
        unfollow_button.click()
        time.sleep(random.uniform(2, 3))

        # Confirm unfollow
        confirm_button = driver.find_element(By.XPATH, "//button[text()='Unfollow']")
        confirm_button.click()
        print(f"Unfollowed {user}")
        unfollows_today += 1
        unfollows_this_hour += 1
    except:
        print(f"Could not unfollow {user} (maybe not following or button not found)")

    # Delay between actions
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"Waiting {int(delay)} seconds before next attempt...")
    time.sleep(delay)

driver.quit()
