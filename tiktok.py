import os
import requests
from dotenv import load_dotenv
from httpcore import TimeoutException
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import pickle
import time

import undetected_chromedriver as uc
from tiktok_captcha_solver import SeleniumSolver

load_dotenv()

TIKTOK_EMAIL = os.getenv("TIKTOK_EMAIL")
TIKTOK_PASSWORD = os.getenv("TIKTOK_PASSWORD")
CAPTCHA_KEY = os.getenv("CAPTCHA_KEY")


def login_and_get_cookies(username, password):
    """Login to TikTok and handle CAPTCHA solving."""

    # Set up Chrome options
    options = uc.ChromeOptions()

    # Add arguments to Chrome options
    options.add_argument("--headless=new")  # Run headless
    options.add_argument("--no-sandbox")  # Needed for CI/CD environments
    options.add_argument("--disable-dev-shm-usage")  # Avoid issues with shared memory in CI environments
    options.add_argument("--disable-blink-features=AutomationControlled")  # Prevent detection as automated bot

    # Use undetected_chromedriver with the options
    driver = uc.Chrome(options=options)

    # Initialize the CAPTCHA solver
    sadcaptcha = SeleniumSolver(
        driver,
        CAPTCHA_KEY,
        mouse_step_size=1,  # Adjust mouse movement speed
        mouse_step_delay_ms=10  # Adjust delay between mouse steps
    )

    driver.get("https://www.tiktok.com/login/phone-or-email/email")

    # Wait for the email input field
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Email or username']"))
        )
    except TimeoutException:
        print("Email input field not found within the timeout period.")
        driver.quit()
        return

    input_email = driver.find_element(By.XPATH, "//input[@placeholder='Email or username']")
    input_email.send_keys(TIKTOK_EMAIL)

    # Wait for the password input field
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
        )
    except TimeoutException:
        print("Password input field not found within the timeout period.")
        driver.quit()
        return

    input_password = driver.find_element(By.XPATH, "//input[@placeholder='Password']")
    input_password.send_keys(TIKTOK_PASSWORD)

    # Click login button
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//button[@data-e2e='login-button']"))
        ).click()
    except TimeoutException:
        print("Login button not found within the timeout period.")
        driver.quit()
        return

    # Now check for CAPTCHA presence
    sadcaptcha.solve_captcha_if_present()

    time.sleep(10)
    driver.get("https://www.tiktok.com/tiktokstudio/upload")

    # Wait for the file input to be present
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input = driver.find_element(By.XPATH, "//input[@type='file']")

    # Send the file path of the video you want to upload
    video_path = os.path.join(os.getcwd(), "beauty_summary_in_en.mp4")
    file_input.send_keys(video_path)

    # Scroll down the page
    time.sleep(3)
    driver.execute_script("window.scrollBy(0, 10000);")

    # Wait for the Post button to be clickable
    wait = WebDriverWait(driver, 20)
    post_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-e2e='post_video_button']")))

    # Click the button
    post_button.click()

    time.sleep(10)
    driver.quit()


login_and_get_cookies(TIKTOK_EMAIL, TIKTOK_PASSWORD)
