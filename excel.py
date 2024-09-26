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
        
        # Strip any extra spaces and keep Amount as a string
        df['Amount'] = df['Amount'].astype(str).apply(lambda x: x.strip())
        
        # Convert to SQLite
        df.to_sql("records", conn, if_exists="replace", index=False)
        messagebox.showinfo("Success", "Excel file has been successfully converted to SQLite database.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to normalize the amount (remove $ and convert to float with 2 decimal places)
def normalize_amount(amount_str):
    try:
        # Remove any $ or commas, convert to float, and format as .00
        amount_value = float(amount_str.replace('$', '').replace(',', '').strip())
        return "{:.2f}".format(amount_value)
    except ValueError:
        return None

# Function to filter records from SQLite (triggered by a button)
def filter_records():
    name_filter = name_entry.get().strip()
    pol_filter = pol_entry.get().strip()
    amount_filter = amount_entry.get().strip()

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
        # Normalize the input to ensure it's in .00 format for querying
        normalized_amount = normalize_amount(amount_filter)
        if normalized_amount:
            query += " AND Amount = ?"
            params.append(normalized_amount)
        else:
            messagebox.showerror("Error", "Invalid amount format. Please enter a valid $ .00 amount.")
            return  # Stop the query if the amount is invalid

    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        display_records(rows)
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while filtering: {str(e)}")

# Function to format Amount as currency and display records in Treeview
def display_records(rows):
    # Clear existing rows
    for i in tree.get_children():
        tree.delete(i)
    
    # Insert new rows, formatting the Amount field as a currency
    for row in rows:
        # Convert the Amount column (index 5) to a currency format
        formatted_row = list(row)
        try:
            amount_value = float(formatted_row[5].replace('$', '').replace(',', '').strip())  # Convert to float
            formatted_row[5] = "${:,.2f}".format(amount_value)  # Format as $ .00
        except ValueError:
            formatted_row[5] = row[5]  # If there's a parsing issue, keep the original value

        # Insert the formatted row into the Treeview
        tree.insert("", "end", values=formatted_row)

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

# Function to clear filters and reset Treeview
def clear_filters():
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
