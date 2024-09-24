# gui/main_gui.py

import tkinter as tk
from tkinter import messagebox
from threading import Thread
from scraping.scraper import data_queue, response_queue
from excel.excel_handler import add_to_excel
from utils.helpers import apply_filters

def main_gui():
    root = tk.Tk()
    root.title("Data Processing GUI")

    # Variables to hold data and user input
    data_vars = {
        'name': tk.StringVar(),
        'policy_number': tk.StringVar(),
        'amount': tk.StringVar(),
        'tid': tk.StringVar(),
        'reason': tk.StringVar(),
    }

    # Display labels and entries
    tk.Label(root, text="Name:").grid(row=0, column=0)
    tk.Label(root, textvariable=data_vars['name']).grid(row=0, column=1)

    tk.Label(root, text="Policy Number:").grid(row=1, column=0)
    tk.Label(root, textvariable=data_vars['policy_number']).grid(row=1, column=1)

    tk.Label(root, text="Amount:").grid(row=2, column=0)
    tk.Label(root, textvariable=data_vars['amount']).grid(row=2, column=1)

    # TID input
    tk.Label(root, text="Transaction ID (TID):").grid(row=3, column=0)
    tid_entry = tk.Entry(root, textvariable=data_vars['tid'])
    tid_entry.grid(row=3, column=1)

    # Reason dropdown
    tk.Label(root, text="Reason:").grid(row=4, column=0)
    reasons = ['Reason A', 'Reason B', 'Reason C']
    reason_var = tk.StringVar()
    reason_dropdown = tk.OptionMenu(root, reason_var, *reasons)
    reason_dropdown.grid(row=4, column=1)

    # Counters
    red_counter = tk.IntVar(value=0)
    green_counter = tk.IntVar(value=0)
    tk.Label(root, text="Red Count:").grid(row=5, column=0)
    tk.Label(root, textvariable=red_counter).grid(row=5, column=1)
    tk.Label(root, text="Green Count:").grid(row=6, column=0)
    tk.Label(root, textvariable=green_counter).grid(row=6, column=1)

    # Current data placeholder
    current_data = {}

    # Function to handle green button click
    def on_green_button_click():
        tid = data_vars['tid'].get()
        if not tid:
            messagebox.showerror("Error", "Please enter TID.")
            return
        # Send response
        response_queue.put({'action': 'green', 'tid': tid})
        green_counter.set(green_counter.get() + 1)
        data_vars['tid'].set('')

    # Function to handle red button click
    def on_red_button_click():
        reason = reason_var.get()
        if not reason:
            messagebox.showerror("Error", "Please select a reason.")
            return
        # Send response
        response_queue.put({'action': 'red', 'reason': reason})
        red_counter.set(red_counter.get() + 1)
        add_to_excel(current_data, reason)
        reason_var.set('')

    # Green and Red buttons
    green_button = tk.Button(root, text="Submit Green",
                             command=on_green_button_click)
    green_button.grid(row=7, column=0)
    red_button = tk.Button(root, text="Submit Red",
                           command=on_red_button_click)
    red_button.grid(row=7, column=1)

    # Periodic check for new data
    def check_for_new_data():
        nonlocal current_data
        if not data_queue.empty():
            current_data = data_queue.get()
            data_vars['name'].set(current_data['name'])
            data_vars['policy_number'].set(current_data['policy_number'])
            data_vars['amount'].set(current_data['amount'])
        root.after(100, check_for_new_data)

    check_for_new_data()
    root.mainloop()
