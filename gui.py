import tkinter as tk

# Create the main window
root = tk.Tk()
root.title("Tkinter Window Background Color")

# Set the window size
root.geometry("400x300")

# Create a frame and place it in the window
frame = tk.Frame(root, bg='#3E4149')
frame.place(relwidth=1, relheight=1)

# Run the application
root.mainloop()
