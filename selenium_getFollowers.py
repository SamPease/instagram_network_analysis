import time
import pandas as pd
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from getpass import getpass  # Import getpass for secure password input

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle  # Import pickle to save and load cookies

USERNAME = "sampease24"
OUTPUT_FILE = "mutual_followers.csv"
COOKIES_FILE = "instagram_cookies.pkl"  # File to store cookies


def wait_for_element(driver, xpath, timeout=15):
    try:
        return WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
    except Exception as e:
        driver.save_screenshot("failed_wait.png")
        raise e

def login(driver):
    driver.get("https://www.instagram.com/accounts/login/")
    time.sleep(5)

    # Enter username and password
    password = getpass("Enter your Instagram password: ")  # Securely prompt for password
    driver.find_element(By.NAME, "username").send_keys(USERNAME)
    driver.find_element(By.NAME, "password").send_keys(password + Keys.RETURN)

    time.sleep(7)  # Wait for login + potential 2FA

    # Save cookies after successful login
    with open(COOKIES_FILE, "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    print("✅ Session cookies saved.")




def scroll_popup(driver, popup_xpath=None, max_users=1000):
    print("📜 Starting scroll...")

    dialog = driver.find_element(By.XPATH, "//div[@role='dialog']")

    # Wait for scroll container to appear
    try:
        scroll_box = WebDriverWait(dialog, 10).until(
            lambda d: d.find_element(By.CLASS_NAME, "xyi19xy")

        )
    except Exception as e:
        driver.save_screenshot("no_scrollbox.png")
        print("❌ Could not find scrollable container. Screenshot saved.")
        raise e

    usernames = set()
    stagnant_cycles = 0

    for cycle in range(60):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", scroll_box)
        time.sleep(2.5)

        links = scroll_box.find_elements(By.TAG_NAME, "a")
        new_users = {link.text for link in links if link.text}
        prev_count = len(usernames)
        usernames.update(new_users)

        driver.save_screenshot(f"scroll_cycle_{cycle}.png")
        print(f"[{cycle}] New users: {len(new_users)} | Total: {len(usernames)}")

        if len(usernames) == prev_count:
            stagnant_cycles += 1
        else:
            stagnant_cycles = 0

        if stagnant_cycles >= 5 or len(usernames) >= max_users:
            break

    print(f"✅ Finished with {len(usernames)} usernames.")
    return usernames


def open_popup(driver, label):
    print(f"🔍 Navigating to {label} list...")
    driver.get(f"https://www.instagram.com/{USERNAME}/")
    wait_for_element(driver, "//h2")  # Wait for profile header

    # Handle "Not Now" pop-up if it appears
    try:
        not_now_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//button[text()='Not Now']"))
        )
        not_now_button.click()
    except:
        pass

    xpath_map = {
        "followers": "//a[contains(@href, '/followers')]",
        "following": "//a[contains(@href, '/following')]"
    }

    link = wait_for_element(driver, xpath_map[label])
    link.click()
    time.sleep(1)

    # Retry click once if needed
    try:
        wait_for_element(driver, "//div[@role='dialog']", timeout=5)
    except:
        print("🔁 Retrying click for dialog...")
        link.click()
        wait_for_element(driver, "//div[@role='dialog']")

    # Updated scroll container xpath
    return scroll_popup(driver, "//div[@role='dialog']//div[@style]")

def load_cookies(driver):
    try:
        with open(COOKIES_FILE, "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        print("✅ Session cookies loaded.")
        return True
    except FileNotFoundError:
        print("⚠️ No cookies file found. Logging in manually.")
        return False

def main():
    options = uc.ChromeOptions()
    options.add_argument("--headless=new")  # Optional: run with window for debugging
    driver = uc.Chrome(options=options)

    try:
        driver.get("https://www.instagram.com/")
        time.sleep(5)

        if not load_cookies(driver):
            login(driver)
            driver.get("https://www.instagram.com/")  # Refresh to apply cookies
            time.sleep(5)

        followers = open_popup(driver, "followers")
        print(f"✅ Followers: {len(followers)}")

        following = open_popup(driver, "following")
        print(f"✅ Following: {len(following)}")

        mutuals = sorted(followers & following)

        pd.DataFrame({"username": mutuals}).to_csv(OUTPUT_FILE, index=False)
        print(f"✅ Saved {len(mutuals)} mutuals to {OUTPUT_FILE}")
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
