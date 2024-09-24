# scraping/scraper.py

import threading
import queue
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from config import settings
from utils.helpers import is_easy_match, scrape_data
from excel.excel_handler import load_excel_data

# Queues for inter-thread communication
data_queue = queue.Queue()       # For sending scraped data to the main thread
response_queue = queue.Queue()   # For receiving user responses

def scraping_thread_function():
    # Initialize the WebDriver
    driver = webdriver.Chrome()
    driver.get(settings.BIA_URL)

    # Load Excel data for matching
    excel_data = load_excel_data(settings.EXCEL_FILE_PATH)

    try:
        while True:
            # Press the pull button
            pull_button = driver.find_element(By.ID, settings.PULL_BUTTON_ID)
            pull_button.click()

            # Scrape data from the page
            data = scrape_data(driver)

            # Check for easy match
            if is_easy_match(data, excel_data):
                # Automatically submit green with policy number as TID
                submit_green(driver, data['policy_number'])
                continue  # Proceed to next iteration

            # Send data to the main thread
            data_queue.put(data)

            # Wait for the main thread's response
            response = response_queue.get()  # Blocks until response is received

            # Process the response
            if response['action'] == 'green':
                submit_green(driver, response['tid'])
            elif response['action'] == 'red':
                submit_red(driver, response['reason'])

            # Loop back to press the pull button again

    except Exception as e:
        logging.error(f"Scraping thread error: {e}")
    finally:
        driver.quit()

def submit_green(driver, tid):
    # Enter TID
    tid_field = driver.find_element(By.ID, settings.TID_INPUT_ID)
    tid_field.clear()
    tid_field.send_keys(tid)
    # Click green button
    green_button = driver.find_element(By.ID, settings.GREEN_BUTTON_ID)
    green_button.click()

def submit_red(driver, reason):
    # Enter reason
    reason_field = driver.find_element(By.ID, settings.REASON_INPUT_ID)
    reason_field.clear()
    reason_field.send_keys(reason)
    # Click red button
    red_button = driver.find_element(By.ID, settings.RED_BUTTON_ID)
    red_button.click()
