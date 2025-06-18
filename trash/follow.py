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
usernames_to_follow = ['natgeo', 'nasa', 'python.learning', 'someotheraccount']

# Rate limiting settings (adjust to stay under limits)
MAX_FOLLOWS_PER_HOUR = 20
MAX_FOLLOWS_PER_DAY = 100
MIN_DELAY = 35  # seconds
MAX_DELAY = 75  # seconds
# --------------------------------------------------------

follows_today = 0
follows_this_hour = 0
hour_start_time = time.time()
day_start_time = time.time()

# Setup driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

# Login
driver.get("https://www.instagram.com/accounts/login/")
time.sleep(5)

driver.find_element(By.NAME, 'username').send_keys(username)
driver.find_element(By.NAME, 'password').send_keys(password + Keys.RETURN)
time.sleep(5)

# Loop through usernames
for user in usernames_to_follow:
    current_time = time.time()

    # Reset hourly counter
    if current_time - hour_start_time > 3600:
        follows_this_hour = 0
        hour_start_time = current_time

    # Stop if limits are exceeded
    if follows_today >= MAX_FOLLOWS_PER_DAY:
        print("Daily limit reached. Stopping.")
        break
    if follows_this_hour >= MAX_FOLLOWS_PER_HOUR:
        wait = 3600 - (current_time - hour_start_time)
        print(f"Hourly limit reached. Waiting {int(wait)} seconds.")
        time.sleep(wait)
        follows_this_hour = 0
        hour_start_time = time.time()

    # Visit user profile and follow
    driver.get(f"https://www.instagram.com/{user}/")
    time.sleep(random.uniform(4, 7))

    try:
        follow_button = driver.find_element(By.XPATH, "//button[text()='Follow']")
        follow_button.click()
        print(f"Followed {user}")
        follows_today += 1
        follows_this_hour += 1
    except:
        print(f"Already following or could not follow {user}")

    # Wait between follow attempts
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    print(f"Waiting {int(delay)} seconds before next attempt...")
    time.sleep(delay)

driver.quit()
