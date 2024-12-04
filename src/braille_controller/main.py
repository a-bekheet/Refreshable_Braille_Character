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

def setup_window_icon(root: tk.Tk):
    """Set up the application icon based on platform."""
    try:
        icon_dir = Path(__file__).parent / "resources" / "icons"
        
        if sys.platform == "darwin":  # macOS
            icon_path = icon_dir / "braille_controller.icns"
            if icon_path.exists():
                img = tk.Image("photo", file=str(icon_path))
                root.tk.call('wm', 'iconphoto', root._w, img)
        
        elif sys.platform == "win32":  # Windows
            icon_path = icon_dir / "braille_controller.ico"
            if icon_path.exists():
                root.iconbitmap(str(icon_path))
        
        else:  # Linux
            icon_path = icon_dir / "braille_controller.xbm"
            if icon_path.exists():
                root.iconbitmap('@' + str(icon_path))
        
        logging.debug(f"Application icon set from {icon_path}")
    except Exception as e:
        logging.warning(f"Failed to set application icon: {e}")

def setup_window_style(root: tk.Tk):
    """Configure window styling and theme."""
    # Set window style
    root.configure(bg='#2E2E2E')  # Dark background
    
    # Configure default styles
    style = tk.ttk.Style()
    style.configure('TFrame', background='#2E2E2E')
    style.configure('TLabel', background='#2E2E2E', foreground='white')
    style.configure('TButton', padding=5)
    
    # Configure window behavior
    root.protocol("WM_DELETE_WINDOW", root.quit)  # Proper cleanup on close

def main():
    """Initialize and run the application."""
    try:
        # Setup logging first
        log_file = setup_logging()
        logging.info("Starting Braille Controller Application")

        # Create the main window
        root = tk.Tk()
        root.title("Braille Controller")

        # Set minimum window size and position
        root.minsize(800, 600)
        
        # Center window on screen
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - 800) // 2
        y = (screen_height - 600) // 2
        root.geometry(f"800x600+{x}+{y}")

        # Set up application icon
        setup_window_icon(root)
        
        # Set up window styling
        setup_window_style(root)

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