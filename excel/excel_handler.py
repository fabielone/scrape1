import pandas as pd
import sqlite3
import os

def excel_to_sqlite(file_path, db_path):
    """Convert an Excel file to an SQLite database, replacing the old database."""
    try:
        # Delete the old database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)

        # Load the Excel file
        df = pd.read_excel(file_path)
        
        # Create a connection to the SQLite database
        conn = sqlite3.connect(db_path)
        
        # Save the DataFrame to SQLite
        df.to_sql('records', conn, if_exists='replace', index=False)
        
        conn.close()
        print("Excel file successfully converted to SQLite.")
    
    except Exception as e:
        print(f"Error converting Excel to SQLite: {e}")

def filter_records_by_amount_sqlite(db_path, amount):
    """Query the SQLite database to retrieve records by amount."""
    try:
        # Clean the amount to remove the dollar sign and extra spaces
        amount = float(amount.replace('$', '').strip())
        
        # Create a connection to the SQLite database
        conn = sqlite3.connect(db_path)

        # Query the database for matching records
        query = f"SELECT * FROM records WHERE Amount = {amount}"
        df = pd.read_sql_query(query, conn)

        conn.close()
        return df

    except Exception as e:
        print(f"Error querying SQLite database: {e}")
        return pd.DataFrame()
