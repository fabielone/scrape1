import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import sqlite3

# Ensure the database is created in the same folder as the script
script_directory = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(script_directory, "records.db")

# Create SQLite connection
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Function to convert Excel to SQLite (only specific columns)
def convert_excel_to_sqlite():
    file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx *.xls")])
    if not file_path:
        return
    
    try:
        # Read Excel file, selecting only the necessary columns
        df = pd.read_excel(file_path, usecols=[
            'Transaction ID', 'Created Date', 'Name', 'Carrier Name', 
            'Policy Number', 'Amount', 'State'], dtype={'Amount': str})  # Read Amount as string
        
        # Convert to SQLite
        df.to_sql("records", conn, if_exists="replace", index=False)
        messagebox.showinfo("Success", "Excel file has been successfully converted to SQLite database.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to filter records from SQLite
def filter_records():
    name_filter = name_entry.get().strip()
    pol_filter = pol_entry.get().strip()
    amount_filter = amount_entry.get().strip()

    query = "SELECT * FROM records WHERE 1=1"
    params = []

    # Apply name filter (AND/OR logic)
    if name_filter:
        name_parts = name_filter.split()
        if len(name_parts) > 1:
            # Prioritize AND for name filtering
            query += " AND (" + " AND ".join(["Name LIKE ?"] * len(name_parts)) + ")"
            params += ['%' + part + '%' for part in name_parts]
        else:
            # Single word uses OR
            query += " AND Name LIKE ?"
            params.append('%' + name_parts[0] + '%')

    # Apply policy number filter
    if pol_filter:
        query += " AND [Policy Number] LIKE ?"
        params.append('%' + pol_filter + '%')

    # Apply amount filter
    if amount_filter:
        query += " AND Amount LIKE ?"
        params.append('%' + amount_filter + '%')

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        display_records(rows)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while filtering: {str(e)}")

# Function to display records in Treeview
def display_records(rows):
    # Clear existing rows
    for i in tree.get_children():
        tree.delete(i)
    
    # Insert new rows
    for row in rows:
        tree.insert("", "end", values=row)

# Function to copy only the Transaction ID (assuming TID is in the 1st column)
def on_tree_click(event):
    selected_item = tree.focus()  # Get the selected item
    if selected_item:
        record_values = tree.item(selected_item, "values")  # Get the values of the selected record
        
        # Assume Transaction ID is in the 1st column (index 0)
        transaction_id = record_values[0]
        
        # Copy Transaction ID to clipboard
        root.clipboard_clear()
        root.clipboard_append(transaction_id)
        messagebox.showinfo("Copied", f"Transaction ID copied to clipboard: {transaction_id}")

# Create main window
root = tk.Tk()
root.title("Excel to SQLite Converter & Record Filter")
root.geometry("1000x600")

# Button to convert Excel to SQLite
convert_button = tk.Button(root, text="Convert Excel to SQLite", command=convert_excel_to_sqlite)
convert_button.pack(pady=10)

# Filters: Name, Policy, Amount
filter_frame = tk.Frame(root)
filter_frame.pack(pady=10)

tk.Label(filter_frame, text="Name:").grid(row=0, column=0, padx=5)
name_entry = tk.Entry(filter_frame)
name_entry.grid(row=0, column=1, padx=5)

tk.Label(filter_frame, text="Policy Number:").grid(row=0, column=2, padx=5)
pol_entry = tk.Entry(filter_frame)
pol_entry.grid(row=0, column=3, padx=5)

tk.Label(filter_frame, text="Amount:").grid(row=0, column=4, padx=5)
amount_entry = tk.Entry(filter_frame)
amount_entry.grid(row=0, column=5, padx=5)

# Bind events to automatically trigger the filtering when fields change
name_entry.bind("<KeyRelease>", lambda e: filter_records())
pol_entry.bind("<KeyRelease>", lambda e: filter_records())
amount_entry.bind("<KeyRelease>", lambda e: filter_records())

# Create Treeview to display records (Transaction ID, Created Date, Name, Carrier Name, Policy Number, Amount, State)
tree_frame = tk.Frame(root)
tree_frame.pack(fill="both", expand=True)

# Define Treeview columns
tree = ttk.Treeview(tree_frame, columns=("Transaction ID", "Created Date", "Name", "Carrier Name", "Policy Number", "Amount", "State"), show="headings")
tree.heading("Transaction ID", text="Transaction ID")
tree.heading("Created Date", text="Created Date")
tree.heading("Name", text="Name")
tree.heading("Carrier Name", text="Carrier Name")
tree.heading("Policy Number", text="Policy Number")
tree.heading("Amount", text="Amount")
tree.heading("State", text="State")
tree.pack(fill="both", expand=True)

# Bind the click event to the tree
tree.bind("<ButtonRelease-1>", on_tree_click)

# Start the main loop
root.mainloop()
