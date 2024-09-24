# utils/helpers.py

import pandas as pd
from selenium.webdriver.common.by import By

def is_easy_match(data, excel_data):
    matches = excel_data[
        excel_data['Name'].str.contains(data['name'], case=False, na=False) &
        excel_data['Policy Number'].str.contains(data['policy_number'], na=False)
    ]
    return not matches.empty

def scrape_data(driver):
    data = {
        'name': driver.find_element(By.ID, 'name_id').text,
        'policy_number': driver.find_element(By.ID, 'policy_id').text,
        'amount': driver.find_element(By.ID, 'amount_id').text,
        # Add more fields as necessary
    }
    return data

def apply_filters(data, name_filter='', policy_filter=''):
    if name_filter:
        data = data[data['Name'].str.contains(name_filter, case=False, na=False)]
    if policy_filter:
        data = data[data['Policy Number'].str.contains(policy_filter, na=False)]
    return data
