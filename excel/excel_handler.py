# excel/excel_handler.py

import pandas as pd
import os
from config import settings

def load_excel_data(file_path):
    if os.path.exists(file_path):
        df = pd.read_excel(file_path)
        return df
    else:
        return pd.DataFrame()

def add_to_excel(data, reason):
    df = pd.DataFrame([{
        'Name': data['name'],
        'Policy Number': data['policy_number'],
        'Amount': data['amount'],
        'Reason': reason
    }])
    if os.path.exists(settings.RED_RECORDS_FILE):
        existing_df = pd.read_excel(settings.RED_RECORDS_FILE)
        df = pd.concat([existing_df, df], ignore_index=True)
    df.to_excel(settings.RED_RECORDS_FILE, index=False)
