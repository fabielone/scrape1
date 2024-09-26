import tkinter as tk
from tkinter import ttk, messagebox
from threading import Thread
from scraping.scraper import data_queue, response_queue
from excel.excel_handler import add_to_excel
from utils.helpers import apply_filters

def main_gui():
    root = tk.Tk()
    root.title("Data Processing GUI")
    root.geometry("1200x600")

    # Variables to hold data and user input
    data_vars = {
        'name': tk.StringVar(),
        'policy_number': tk.StringVar(),
        'amount': tk.StringVar(),
        'tid': tk.StringVar(),
        'organizer': tk.StringVar(),
        'bank_description': tk.StringVar(),
        'reason': tk.StringVar(),
        'reason': tk.StringVar(),
        'filter_name': tk.StringVar(),
        'filter_policy': tk.StringVar()
    }

    global current_data
    current_data = {}

    # Counters for green and red submissions
    green_counter = tk.IntVar(value=0)
    red_counter = tk.IntVar(value=0)

    # Top right corner: Green and Red boxes
    counter_frame = tk.Frame(root)
    counter_frame.grid(row=0, column=0, padx=0, pady=0)

    green_counter_label = tk.Label(counter_frame, textvariable=green_counter, fg="green", width=5, bg="lightgreen")
    green_counter_label.grid(row=0, column=0)

    red_counter_label = tk.Label(counter_frame, textvariable=red_counter, fg="red", width=5, bg="lightcoral")
    red_counter_label.grid(row=0, column=1)

    # Organizer and amount
    tk.Label(root, text="Organization:").grid(row=0, column=2, padx=5, pady=5)
    organizer_entry = tk.Entry(root, textvariable=data_vars['organizer'])
    organizer_entry.grid(row=0, column=3)

    tk.Label(root, text="Amount:").grid(row=0, column=4, padx=5, pady=5)
    amount_label = tk.Label(root, textvariable=data_vars['amount'])
    amount_label.grid(row=0, column=5)

    tk.Label(root, text="Carrier:").grid(row=0, column=6, padx=5, pady=5)
    carrier_label = tk.Label(root, textvariable=data_vars['name'])
    carrier_label.grid(row=0, column=7)

    tk.Label(root, text="Policy:").grid(row=0, column=8, padx=5, pady=5)
    policy_label = tk.Label(root, textvariable=data_vars['policy_number'])
    policy_label.grid(row=0, column=9)

    # Copy button for the policy
    copy_policy_button = tk.Button(root, text="Copy", command=lambda: copy_to_clipboard(data_vars['policy_number'].get()))
    copy_policy_button.grid(row=0, column=10, padx=5, pady=5)
    def copy_to_clipboard(text):
        root.clipboard_clear()  # Clear clipboard contents
        root.clipboard_append(text)  # Append new text to clipboard
        messagebox.showinfo("Copied", f"Policy '{text}' copied to clipboard!")

    # Bank description and tip
    tk.Label(root, text="Bank Description:").grid(row=1, column=0, padx=5, pady=5)
    bank_description_entry = tk.Entry(root, textvariable=data_vars['bank_description'])
    bank_description_entry.grid(row=1, column=1,columnspan=4, sticky="we")

    # Input boxes for filtering by name and policy
    tk.Label(root, text="Filter by Name:").grid(row=2, column=0, padx=5, pady=5)
    filter_name_entry = tk.Entry(root, textvariable=data_vars['filter_name'])
    filter_name_entry.grid(row=2, column=1)

    tk.Label(root, text="Filter by Policy:").grid(row=2, column=2, padx=5, pady=5)
    filter_policy_entry = tk.Entry(root, textvariable=data_vars['filter_policy'])
    filter_policy_entry.grid(row=2, column=3)

    # Bind KeyRelease event to both input fields to apply filters dynamically on text change
    filter_name_entry.bind('<KeyRelease>', lambda event: apply_filters_to_treeview(record_table, data_vars['filter_name'].get(), data_vars['filter_policy'].get()))
    filter_policy_entry.bind('<KeyRelease>', lambda event: apply_filters_to_treeview(record_table, data_vars['filter_name'].get(), data_vars['filter_policy'].get()))
    # Transaction ID and reason dropdown
    tk.Label(root, text="Transaction ID (TID):").grid(row=2, column=4, padx=5, pady=5)
    tid_entry = tk.Entry(root, textvariable=data_vars['tid'])
    tid_entry.grid(row=2, column=5)

    reasons = ['Reason A', 'Reason B', 'Reason C']
    reason_var = tk.StringVar()
    reason_dropdown = tk.OptionMenu(root, reason_var, *reasons)
    reason_dropdown.grid(row=2, column=7)

    # Green and Red buttons
    green_button = tk.Button(root, text="Submit Green", command=lambda: on_green_button_click(data_vars['tid'].get(), green_counter, response_queue))
    green_button.grid(row=2, column=8, padx=5, pady=5)

    red_button = tk.Button(root, text="Submit Red", command=lambda: on_red_button_click(data_vars, red_counter, response_queue, reason_var))
    red_button.grid(row=2, column=9, padx=5, pady=5)

    # Table to display Excel records
    columns = ('TID', 'Date', 'Name', 'Carrier', 'Policy', '$$$', 'State')
    record_table = ttk.Treeview(root, columns=columns, show="headings")

    # Define column headings and widths
    for col in columns:
        record_table.heading(col, text=col)
    record_table.column('TID', width=50)
    record_table.column('Date', width=100)
    record_table.column('Name', width=150)
    record_table.column('Carrier', width=100)
    record_table.column('Policy', width=100)
    record_table.column('$$$', width=80)
    record_table.column('State', width=50)

    record_table.grid(row=3, column=0, columnspan=len(columns), padx=5, pady=5)

    def apply_filters_to_treeview(table, name_filter, policy_filter):
    # Assume `all_data` contains the entire dataset initially
        all_data = data_list  # This would be your original unfiltered data from Excel

    # Apply policy filter (if applicable)
        if policy_filter:
            all_data = [record for record in all_data if policy_filter.lower() in record[4].lower()]  # Assuming policy is in the 5th column

    # Apply name filter (if applicable)
        if name_filter:
            name_words = name_filter.strip().split()  # Split input into individual words

            def name_matches(record_name, words):
                """Check if a name matches all words (AND logic)."""
                return all(word.lower() in record_name.lower() for word in words)

        # First, apply AND logic to match all words
            filtered_data = [record for record in all_data if name_matches(record[2], name_words)]  # Assuming name is in the 3rd column

        # If no records match with AND logic, fallback to OR logic
            if not filtered_data:
                filtered_data = [record for record in all_data if any(word.lower() in record[2].lower() for word in name_words)]
        else:
        # If name filter is empty, return the data filtered only by policy or the whole dataset
            filtered_data = all_data

    # Clear the Treeview
        for row in table.get_children():
            table.delete(row)

    # Insert the filtered data into the Treeview
        for record in filtered_data:
            table.insert('', 'end', values=record)

    # Add dummy data to table
    data_list = [
        ('123', '2024-09-01', 'John Doe', 'Carrier X', 'Policy ABC', '$500', 'CA'),
        ('456', '2024-09-02', 'Jane Smith', 'Carrier Y', 'Policy XYZ', '$600', 'NY')
    ]

    for record in data_list:
        record_table.insert('', 'end', values=record)

    # Bind click event to the Treeview
    def on_row_click(event):
        selected_item = record_table.selection()[0]  # Get selected row
        record_values = record_table.item(selected_item, 'values')  # Get values of the selected row
        tid = record_values[0]  # Get the TID from the first column
        data_vars['tid'].set(tid)  # Set the TID to the entry field

    # Bind the left mouse click to the Treeview
    record_table.bind('<ButtonRelease-1>', on_row_click)

    # Periodic check for new data
    def check_for_new_data():
        if not data_queue.empty():
            current_data = data_queue.get()
            data_vars['name'].set(current_data['name'])
            data_vars['policy_number'].set(current_data['policy_number'])
            data_vars['amount'].set(current_data['amount'])
        root.after(100, check_for_new_data)

    check_for_new_data()
    root.mainloop()

# Helper functions for green and red button clicks
def on_green_button_click(tid, green_counter, response_queue):
    if not tid:
        messagebox.showerror("Error", "No TID provided.")
        return
    # Send response with the provided TID
    response_queue.put({'action': 'green', 'tid': tid})
    green_counter.set(green_counter.get() + 1)

def on_red_button_click(data_vars, red_counter, response_queue, reason_var):
    reason = reason_var.get()
    if not reason:
        messagebox.showerror("Error", "Please select a reason.")
        return
    # Send response for the red button action
    response_queue.put({'action': 'red', 'reason': reason})
    red_counter.set(red_counter.get() + 1)
    add_to_excel(data_vars, reason)
    reason_var.set('')


