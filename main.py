# main.py

import threading
from scraping.scraper import scraping_thread_function
from gui.main_gui import main_gui

if __name__ == '__main__':
    # Start the scraping thread
    scrape_thread = threading.Thread(
        target=scraping_thread_function, daemon=True
    )
    scrape_thread.start()

    # Start the GUI
    main_gui()
