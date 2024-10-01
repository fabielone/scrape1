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
        
        # Store Amount in $ .00 format
        df['Amount'] = df['Amount'].apply(lambda x: "${:,.2f}".format(float(x.replace('$', '').replace(',', '').strip())) if pd.notnull(x) else x)
        
        # Convert to SQLite
        df.to_sql("records", conn, if_exists="replace", index=False)
        messagebox.showinfo("Success", "Excel file has been successfully converted to SQLite database.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to filter records from SQLite (triggered by a button or enter)
def filter_records(event=None):
    name_filter = name_entry.get().strip()
    pol_filter = pol_entry.get().strip()
    amount_filter = amount_entry.get().strip()  # Do not remove $ or commas, use as entered
    
    query = "SELECT * FROM records WHERE 1=1"  # Base query
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
        # Match the stored $ .00 format exactly
        query += " AND Amount = ?"
        params.append(amount_filter)

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
    
    # Insert new rows without modifying Amount (it is already formatted in the database)
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
        

# Function to handle clicking the amount field: clear, paste clipboard content, and search
def on_amount_click(event):
    # Clear the amount entry field
    amount_entry.delete(0, tk.END)
    
    # Get the clipboard content
    clipboard_content = root.clipboard_get()
    
    # Paste clipboard content into the entry field
    amount_entry.insert(0, clipboard_content)
    
    # Automatically trigger the search
    filter_records()

# Function to clear, paste clipboard content, and trigger search for the right-click event
def on_right_click(event):
    # Get the widget that triggered the event (could be name_entry or pol_entry)
    entry_widget = event.widget
    
    # Clear the entry field
    entry_widget.delete(0, tk.END)
    
    # Get the clipboard content
    clipboard_content = root.clipboard_get()
    
    # Paste clipboard content into the entry field
    entry_widget.insert(0, clipboard_content)
    
    # Automatically trigger the search
    filter_records()

# Function to clear filters and reset Treeview
def clear_filters(event=None):
    name_entry.delete(0, tk.END)
    pol_entry.delete(0, tk.END)
    amount_entry.delete(0, tk.END)

    # Clear Treeview
    for i in tree.get_children():
        tree.delete(i)

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

# Clear button to reset filters and Treeview
clear_button = tk.Button(filter_frame, text="Clear", command=clear_filters)
clear_button.grid(row=0, column=0, padx=5)

tk.Label(filter_frame, text="Name:").grid(row=0, column=1, padx=5)
name_entry = tk.Entry(filter_frame)
name_entry.grid(row=0, column=2, padx=5)

tk.Label(filter_frame, text="Policy Number:").grid(row=0, column=3, padx=5)
pol_entry = tk.Entry(filter_frame)
pol_entry.grid(row=0, column=4, padx=5)

tk.Label(filter_frame, text="Amount:").grid(row=0, column=5, padx=5)
amount_entry = tk.Entry(filter_frame)
amount_entry.grid(row=0, column=6, padx=5)

# Button to trigger the filtering action
search_button = tk.Button(filter_frame, text="Search", command=filter_records)
search_button.grid(row=0, column=7, padx=10)

# Bind Enter key for name and policy fields to search function
name_entry.bind("<Return>", filter_records)
pol_entry.bind("<Return>", filter_records)

# Bind right-click event to name and policy fields for clipboard paste and search
name_entry.bind("<Button-3>", on_right_click)
pol_entry.bind("<Button-3>", on_right_click)


# Bind Esc key to clear filters
root.bind("<Escape>", clear_filters)

# Bind click event to amount field to clear, paste clipboard, and search
amount_entry.bind("<Button-1>", on_amount_click)

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
