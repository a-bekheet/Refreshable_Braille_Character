"""
Braille Controller Application
Main entry point that initializes and runs the application
"""

import tkinter as tk
import sys
import logging
from pathlib import Path
from datetime import datetime

# Import the main GUI class
from gui.controller_gui import BrailleControllerGUI

def setup_logging():
    """Configure logging with file and console output."""
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"braille_controller_{timestamp}.log"
    
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    logging.info("Logging initialized")
    return log_file

def setup_exception_handling(root: tk.Tk):
    """Configure global exception handler for unhandled exceptions."""
    def handle_exception(exc_type, exc_value, exc_traceback):
        """Handle uncaught exceptions."""
        if issubclass(exc_type, KeyboardInterrupt):
            # Handle keyboard interrupt
            root.destroy()
            return
            
        # Log the error
        logging.error(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, exc_traceback)
        )
        
        # Show error message to user
        import tkinter.messagebox as messagebox
        messagebox.showerror(
            "Error",
            f"An unexpected error occurred:\n{exc_type.__name__}: {exc_value}"
        )
    
    # Set up the exception hook
    sys.excepthook = handle_exception

def main():
    """Initialize and run the application."""
    try:
        # Setup logging first
        log_file = setup_logging()
        logging.info("Starting Braille Controller Application")
        
        # Create the main window
        root = tk.Tk()
        root.title("Braille Controller")
        
        # Set minimum window size
        root.minsize(800, 600)
        
        # Configure exception handling
        setup_exception_handling(root)
        
        # Initialize the GUI
        app = BrailleControllerGUI(root)
        logging.info("GUI initialized successfully")
        
        # Log application start
        logging.info(f"Application started - Log file: {log_file}")
        
        # Start the main event loop
        root.mainloop()
        
    except Exception as e:
        logging.critical(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logging.info("Application shutdown complete")

if __name__ == "__main__":
    main()