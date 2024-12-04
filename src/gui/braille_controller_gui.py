import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import serial
import serial.tools.list_ports
import threading
import time
import json
from typing import Dict, List
import logging
import re
import math

# Import the OCR module
import braille_controller.brailleOCR as brailleOCR

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# --- Class Definitions ---

class BraillePatternCanvas(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.dot_radius = 10
        self.dot_spacing = 30
        self.dots_state = [[False] * 2 for _ in range(3)]  # 3x2 grid for Braille
        self.configure(width=self.dot_spacing * 3 + 20, height=self.dot_spacing * 4)
        self.draw_pattern()

    def draw_pattern(self):
        self.delete("all")
        for i in range(3):
            for j in range(2):
                x = 20 + (i * self.dot_spacing)
                y = 20 + (j * self.dot_spacing)
                color = "black" if self.dots_state[i][j] else "lightgray"
                self.create_oval(
                    x - self.dot_radius,
                    y - self.dot_radius,
                    x + self.dot_radius,
                    y + self.dot_radius,
                    fill=color,
                    outline="gray"
                )

    def update_pattern(self, pattern: str):
        """Update pattern using 6-bit binary string"""
        bits = [bool(int(b)) for b in pattern.zfill(6)]
        self.dots_state = [
            [bits[0], bits[3]],
            [bits[1], bits[4]],
            [bits[2], bits[5]]
        ]
        self.draw_pattern()


class ServoVisualizer(tk.Canvas):
    """
    Implements a precise servo motor visualization system with integrated
    geometric transformations and dynamic state management.
    """
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        # Fundamental geometric parameters
        self.width = kwargs.get('width', 200)
        self.height = kwargs.get('height', 100)
        self.configure(width=self.width, height=self.height)

        # State initialization
        self.angle = 0
        self.previous_angle = None

        # Initial rendering
        self.draw_servo()

    def draw_servo(self):
        """
        Executes geometric rendering of servo mechanism through
        parametric transformations and vector calculations.
        """
        logging.debug(f"Redrawing servo at angle: {self.angle}°")
        
        # Clear previous rendering state
        self.delete("all")

        # Geometric constants
        BASE_WIDTH = 100
        BASE_HEIGHT = 40
        SHAFT_LENGTH = 25

        # Coordinate system transformation
        center_x = self.width // 2
        center_y = self.height // 2

        # Servo base visualization
        x1 = center_x - BASE_WIDTH // 2
        y1 = center_y - BASE_HEIGHT // 2
        x2 = center_x + BASE_WIDTH // 2
        y2 = center_y + BASE_HEIGHT // 2

        self.create_rectangle(
            x1, y1, x2, y2,
            fill="gray75",
            outline="gray45",
            width=2
        )

        # Angular transformation computation
        theta = math.radians(self.angle)
        shaft_x = center_x + SHAFT_LENGTH * math.cos(theta)
        shaft_y = center_y - SHAFT_LENGTH * math.sin(theta)  # Inverted y-axis

        # Shaft vector rendering
        self.create_line(
            center_x, center_y,
            shaft_x, shaft_y,
            width=3,
            fill="black",
            capstyle=tk.ROUND
        )

        # Angular position indicator
        angle_text = f"{self.angle:.1f}°"
        self.create_text(
            x2 + 10,
            y1,
            text=angle_text,
            anchor="w",
            font=("Arial", 10, "bold")
        )

        # Force a redraw of the canvas
        self.update_idletasks()

    def set_angle(self, angle: float):
        """
        Updates servo angular position with boundary validation
        and state management.

        Parameters:
            angle (float): Target angle in degrees [0, 180]
        """
        # Boundary constraint application
        angle = max(0, min(180, float(angle)))

        # State change detection
        if self.previous_angle != angle:
            logging.debug(f"Updating servo angle from {self.previous_angle}° to {angle}°")
            self.previous_angle = angle
            self.angle = angle
            self.draw_servo()
        else:
            logging.debug(f"Servo angle unchanged at {angle}°")


class Configuration:
    DEFAULT_CONFIG = {
        "char_delay": 3000,
        "servo_delay": 750,
        "dual_servo_mode": True,
        "debug_mode": False,
        "theme": "default"
    }

    def __init__(self):
        self.config = self.DEFAULT_CONFIG.copy()
        self.load_config()

    def load_config(self):
        try:
            with open("braille_config.json", "r") as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
                logging.debug("Configuration loaded from braille_config.json.")
        except FileNotFoundError:
            logging.warning("braille_config.json not found. Creating default configuration.")
            self.save_config()

    def save_config(self):
        try:
            with open("braille_config.json", "w") as f:
                json.dump(self.config, f, indent=4)
                logging.debug("Configuration saved to braille_config.json.")
        except Exception as e:
            logging.error(f"Failed to save configuration: {e}")
            messagebox.showerror("Save Error", f"Failed to save configuration.\nError: {e}")

    def get(self, key: str):
        return self.config.get(key, self.DEFAULT_CONFIG.get(key))

    def set(self, key: str, value):
        self.config[key] = value
        self.save_config()
        logging.debug(f"Configuration updated: {key} = {value}")


# --- Main GUI Class ---

class BrailleControllerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Braille Controller Interface")
        self.config = Configuration()
        self.setup_styles()
        self.create_gui()
        self.setup_variables()
        self.setup_bindings()
        logging.debug("Initialized BrailleControllerGUI")

    def setup_styles(self):
        style = ttk.Style()
        style.configure("Active.TButton", foreground="white", background="green")
        style.map("Active.TButton",
                  foreground=[('active', 'white')],
                  background=[('active', 'green')])
        style.configure("Warning.TLabel", foreground="red")
        logging.debug("Styles configured.")

    def create_gui(self):
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        logging.debug("Notebook for tabs created.")

        # Main control tab
        self.main_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.main_tab, text="Control")
        self.create_main_tab()
        logging.debug("Main Control tab created.")

        # Configuration tab
        self.config_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.config_tab, text="Configuration")
        self.create_config_tab()
        logging.debug("Configuration tab created.")

        # Visualization tab
        self.visual_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.visual_tab, text="Visualization")
        self.create_visual_tab()
        logging.debug("Visualization tab created.")

    def create_main_tab(self):
        # Connection Frame
        self.connection_frame = ttk.LabelFrame(self.main_tab, text="Connection", padding="5")
        self.connection_frame.pack(fill="x", padx=5, pady=5)
        logging.debug("Connection frame created.")

        # Port selection and connection controls
        self.port_frame = ttk.Frame(self.connection_frame)
        self.port_frame.pack(fill="x")

        self.port_label = ttk.Label(self.port_frame, text="Port:")
        self.port_label.pack(side="left", padx=5)

        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(self.port_frame, textvariable=self.port_var, state="readonly")
        self.port_combo.pack(side="left", padx=5, expand=True, fill="x")

        self.connect_button = ttk.Button(self.port_frame, text="Connect", command=self.toggle_connection)
        self.connect_button.pack(side="left", padx=5)

        self.refresh_button = ttk.Button(self.port_frame, text="↻", width=3, command=self.refresh_ports)
        self.refresh_button.pack(side="left", padx=5)

        # Text Input Frame
        self.input_frame = ttk.LabelFrame(self.main_tab, text="Text Input", padding="5")
        self.input_frame.pack(fill="x", padx=5, pady=5)
        logging.debug("Text Input frame created.")

        self.text_input = ttk.Entry(self.input_frame)
        self.text_input.pack(side="left", padx=5, pady=5, expand=True, fill="x")
        self.text_input.focus()

        self.send_button = ttk.Button(self.input_frame, text="Send", command=self.send_text)
        self.send_button.pack(side="left", padx=5, pady=5)

        self.upload_button = ttk.Button(self.input_frame, text="Upload Image", command=self.upload_image)
        self.upload_button.pack(side="left", padx=5, pady=5)

        # Status Frame
        self.status_frame = ttk.LabelFrame(self.main_tab, text="Status", padding="5")
        self.status_frame.pack(fill="x", padx=5, pady=5)
        logging.debug("Status frame created.")

        self.status_label = ttk.Label(self.status_frame, text="Disconnected")
        self.status_label.pack(padx=5, pady=5)

        self.char_display = ttk.Label(self.status_frame, text="Current Character: -", font=('Arial', 16))
        self.char_display.pack(padx=5, pady=5)

        self.progress = ttk.Progressbar(self.status_frame, mode='determinate')
        self.progress.pack(fill="x", padx=5, pady=5)

    def create_config_tab(self):
        # Timing Configuration
        timing_frame = ttk.LabelFrame(self.config_tab, text="Timing Configuration", padding="5")
        timing_frame.pack(fill="x", padx=5, pady=5)
        logging.debug("Timing Configuration frame created.")

        # Character Delay
        ttk.Label(timing_frame, text="Character Delay (ms):").pack(anchor="w", padx=5, pady=(5, 0))
        self.char_delay_var = tk.StringVar(value=str(self.config.get("char_delay")))
        char_delay_entry = ttk.Entry(timing_frame, textvariable=self.char_delay_var)
        char_delay_entry.pack(fill="x", padx=5, pady=2)

        # Servo Delay
        ttk.Label(timing_frame, text="Servo Movement Delay (ms):").pack(anchor="w", padx=5, pady=(5, 0))
        self.servo_delay_var = tk.StringVar(value=str(self.config.get("servo_delay")))
        servo_delay_entry = ttk.Entry(timing_frame, textvariable=self.servo_delay_var)
        servo_delay_entry.pack(fill="x", padx=5, pady=2)

        # Servo Configuration
        servo_frame = ttk.LabelFrame(self.config_tab, text="Servo Configuration", padding="5")
        servo_frame.pack(fill="x", padx=5, pady=5)
        logging.debug("Servo Configuration frame created.")

        # Dual Servo Mode
        self.dual_servo_var = tk.BooleanVar(value=self.config.get("dual_servo_mode"))
        dual_servo_check = ttk.Checkbutton(
            servo_frame,
            text="Dual Servo Mode",
            variable=self.dual_servo_var,
            command=self.on_dual_servo_toggle  # Bind the toggle event
        )
        dual_servo_check.pack(anchor="w", padx=5, pady=(5, 0))

        # Debug Mode
        self.debug_var = tk.BooleanVar(value=self.config.get("debug_mode"))
        debug_check = ttk.Checkbutton(servo_frame, text="Debug Mode", variable=self.debug_var)
        debug_check.pack(anchor="w", padx=5, pady=(5, 0))

        # Save Button
        save_button = ttk.Button(self.config_tab, text="Save Configuration", command=self.save_configuration)
        save_button.pack(pady=10)
        logging.debug("Save Configuration button created.")

    def create_visual_tab(self):
        """
        Creates the Visualization tab with Braille pattern and Servo Positions.
        """
        # Braille Pattern Display
        pattern_frame = ttk.LabelFrame(self.visual_tab, text="Braille Pattern", padding="5")
        pattern_frame.pack(side="left", padx=5, pady=5, fill="both", expand=True)

        self.pattern_canvas = BraillePatternCanvas(pattern_frame)
        self.pattern_canvas.pack(padx=5, pady=5, expand=True, fill="both")

        # Servo Position Display
        servo_frame = ttk.LabelFrame(self.visual_tab, text="Servo Positions", padding="5")
        servo_frame.pack(side="right", padx=5, pady=5, fill="both", expand=True)

        self.servo_a_canvas = ServoVisualizer(servo_frame)
        self.servo_a_canvas.pack(padx=5, pady=5)
        ttk.Label(servo_frame, text="Servo A").pack()

        self.servo_b_canvas = ServoVisualizer(servo_frame)
        self.servo_b_canvas.pack(padx=5, pady=5)
        ttk.Label(servo_frame, text="Servo B").pack()

    def setup_variables(self):
        self.serial_connection = None
        self.is_connected = False
        self.last_pattern = "000000"
        self.refresh_ports()
        logging.debug("Variables setup completed.")

    def setup_bindings(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.text_input.bind('<Return>', lambda e: self.send_text())
        logging.debug("Event bindings set up.")

    def refresh_ports(self):
        ports = [port.device for port in serial.tools.list_ports.comports()]
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
            logging.info(f"Available serial ports: {ports}")
        else:
            self.port_combo.set('')
            logging.warning("No serial ports found.")

    def toggle_connection(self):
        if not self.is_connected:
            try:
                self.connect()
            except Exception as e:
                logging.error(f"Failed to toggle connection: {e}")
                messagebox.showerror("Connection Error", f"Failed to connect: {e}")
        else:
            self.disconnect()
            # Ensure thread termination
            if hasattr(self, 'read_thread') and self.read_thread.is_alive():
                self.read_thread.join(timeout=1)
                logging.debug("Serial read thread terminated.")

    def connect(self):
        """
        Establishes and validates serial communication with the Arduino device.
        Implements comprehensive connection management protocols including:
        - Port validation
        - Hardware flow control
        - Connection state management
        - Asynchronous read thread initialization
        """
        port = self.port_var.get()
        logging.debug(f"Attempting to connect to port: {port}")
        if not port:
            messagebox.showwarning("Warning", "No port selected.")
            logging.warning("No port selected for connection.")
            return
        try:
            # Initialize serial connection with specified parameters
            self.serial_connection = serial.Serial(
                port=port,
                baudrate=9600,
                timeout=1,
                write_timeout=1
            )
            logging.info(f"Serial connection established on port {port}.")

            # Implement hardware flow control sequence
            self.serial_connection.dtr = False  # Disable Data Terminal Ready
            time.sleep(0.1)
            self.serial_connection.dtr = True   # Enable Data Terminal Ready
            time.sleep(2)  # Allow sufficient time for Arduino initialization
            logging.debug("Hardware flow control toggled (DTR).")

            # Update connection state and UI elements
            self.is_connected = True
            self.connect_button.configure(text="Disconnect", style="Active.TButton")
            self.status_label.configure(text=f"Connected to {port}")
            logging.info(f"Connected to {port}.")

            # Initialize asynchronous read thread
            self.read_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.read_thread.start()
            logging.debug("Serial read thread started.")
        except Exception as e:
            logging.error(f"Failed to connect to {port}: {e}")
            messagebox.showerror("Connection Error", f"Failed to connect to {port}.\nError: {e}")

    def disconnect(self):
        if self.serial_connection and self.serial_connection.is_open:
            self.serial_connection.close()
            logging.info("Serial connection closed.")
        self.is_connected = False
        self.connect_button.configure(text="Connect", style="TButton")
        self.status_label.configure(text="Disconnected")
        self.char_display.configure(text="Current Character: -")
        self.progress['value'] = 0
        logging.debug("Disconnected from serial port and UI reset.")

    def send_text(self):
        """
        Transmits formatted commands to Arduino with comprehensive error handling.
        Implements:
        - Input validation
        - Buffer management
        - Error handling
        - Connection state verification
        """
        logging.debug("send_text called")
        # Verify connection state
        if not self.is_connected:
            logging.warning("Attempted to send text without an active connection.")
            messagebox.showwarning("Warning", "Please connect to Arduino first.")
            return

        # Validate input text
        text = self.text_input.get().strip()
        logging.debug(f"Text input received: '{text}'")
        if not text:
            logging.warning("No text entered to send.")
            messagebox.showwarning("Warning", "Please enter some text to send.")
            return

        # Validate numerical parameters
        try:
            char_delay = int(self.char_delay_var.get())
            servo_delay = int(self.servo_delay_var.get())
            logging.debug(f"Character Delay: {char_delay} ms, Servo Delay: {servo_delay} ms")
        except ValueError as e:
            logging.error(f"Invalid delay values: {e}")
            messagebox.showerror("Invalid Input", "Please enter valid numerical values for delays.")
            return

        # Prepare text command
        text_command = f"TEXT:{text}\n"

        # Transmit data with error handling
        try:
            # Send configuration command first if necessary
            # Assuming configuration is already handled via checkbox toggle

            # Prepare and encode text command
            logging.debug(f"Text command to send: {text_command}")

            # Clear communication buffers
            self.serial_connection.reset_input_buffer()
            self.serial_connection.reset_output_buffer()
            logging.debug("Serial buffers reset.")

            # Transmit text data
            self.serial_connection.write(text_command.encode())
            self.serial_connection.flush()
            logging.info("Text data sent to Arduino successfully.")

            # Reset UI elements
            self.progress['value'] = 0
            self.char_display.configure(text="Current Character: -")
            logging.debug("UI elements reset after sending data.")
        except Exception as e:
            logging.error(f"Failed to send data: {e}")
            messagebox.showerror("Send Error", f"Failed to send data.\nError: {e}")
            self.disconnect()  # Terminate connection on critical error

    def send_configuration(self):
        """
        Sends configuration commands to Arduino.
        """
        logging.debug("send_configuration called.")
        config_command = f"CONFIG:DUAL={int(self.dual_servo_var.get())}\n"
        try:
            self.serial_connection.write(config_command.encode())
            self.serial_connection.flush()
            logging.info(f"Configuration command sent: {config_command.strip()}")
        except Exception as e:
            logging.error(f"Failed to send configuration command: {e}")
            messagebox.showerror("Send Error", f"Failed to send configuration command.\nError: {e}")
            self.disconnect()

    def read_serial(self):
        """
        Asynchronous serial data reception handler.
        Implements continuous monitoring of serial input with error handling.
        """
        logging.debug("read_serial thread running.")
        while self.is_connected and self.serial_connection and self.serial_connection.is_open:
            try:
                if self.serial_connection.in_waiting:
                    line = self.serial_connection.readline().decode().strip()
                    logging.debug(f"Received line from Arduino: '{line}'")
                    if line:
                        self.process_serial_message(line)
                time.sleep(0.1)  # Prevent CPU saturation
            except serial.SerialException as e:
                logging.error(f"Serial communication error: {e}")
                break  # Exit on serial communication error
            except UnicodeDecodeError as e:
                logging.warning(f"Unicode decode error: {e}")
                continue  # Skip malformed data
            except Exception as e:
                logging.error(f"Unexpected error in read_serial: {e}")
                break  # Exit on critical error

    def process_serial_message(self, message: str) -> None:
        """
        Processes incoming serial messages from Arduino for visualization updates.
        """
        logging.debug(f"Processing serial message: '{message}'")
        try:
            if "Character:" in message:
                # Extract character and pattern data
                parts = message.split("->")
                if len(parts) == 2:
                    char = parts[0].split(":")[1].strip()
                    pattern_info = parts[1].strip()
                    
                    # Update character display
                    self.root.after(0, self.update_display, char)
                    
                    # Extract binary pattern
                    if "Pattern:" in pattern_info:
                        binary_match = re.search(r'Pattern:\s*([01]{6})', pattern_info)
                        if binary_match:
                            binary = binary_match.group(1)
                            self.root.after(0, self.update_pattern, binary)
                        else:
                            logging.error("Binary pattern not found in message.")
            elif "Servo" in message and "µs" in message:
                # Process servo position data
                pulse_matches = re.findall(r'(\d+)µs', message)
                if len(pulse_matches) >= 1:
                    pulse_a = int(pulse_matches[0])
                    pulse_b = pulse_a  # Default if single servo mode
                    
                    if len(pulse_matches) >= 2:
                        pulse_b = int(pulse_matches[1])
                        
                    self.root.after(0, self.update_servo_positions, f"{pulse_a},{pulse_b}")
                    
        except Exception as e:
            logging.error(f"Message processing error: {e}")

    def update_display(self, char: str) -> None:
        """Updates the character display with progress tracking."""
        self.char_display.configure(text=f"Current Character: {char}")
        self.progress['value'] = (self.progress['value'] + 10) % 100
        logging.debug(f"Display updated with character: {char}")

    def update_pattern(self, pattern: str) -> None:
        """Updates Braille pattern visualization."""
        if not pattern or len(pattern) != 6 or not all(bit in '01' for bit in pattern):
            logging.error(f"Invalid pattern format: {pattern}")
            return
            
        self.pattern_canvas.update_pattern(pattern)
        self.last_pattern = pattern
        logging.debug(f"Pattern visualization updated: {pattern}")

    def update_servo_positions(self, positions: str) -> None:
        """Updates servo position visualizations."""
        try:
            pulse_a, pulse_b = map(int, positions.split(','))
            
            # Validate pulse width ranges
            if not (500 <= pulse_a <= 2500 and 500 <= pulse_b <= 2500):
                raise ValueError("Pulse width out of valid range (500-2500µs)")
                
            angle_a = self.pulse_to_angle(pulse_a)
            angle_b = self.pulse_to_angle(pulse_b)
            
            self.servo_a_canvas.set_angle(angle_a)
            self.servo_b_canvas.set_angle(angle_b)
            logging.debug(f"Servo visualizations updated - A: {angle_a}°, B: {angle_b}°")
            
        except Exception as e:
            logging.error(f"Servo position update error: {e}")

    def pulse_to_angle(self, pulse_width: int) -> float:
        """Converts servo pulse width to angular position."""
        MIN_PULSE = 500
        MAX_PULSE = 2500
        MIN_ANGLE = 0
        MAX_ANGLE = 180
        
        # Constrain pulse width to valid range
        pulse_width = max(MIN_PULSE, min(pulse_width, MAX_PULSE))
        
        # Linear interpolation
        angle = (pulse_width - MIN_PULSE) * (MAX_ANGLE - MIN_ANGLE) / (MAX_PULSE - MIN_PULSE) + MIN_ANGLE
        return round(angle, 2)

    def save_configuration(self):
        """
        Validates and saves the current configuration settings.
        """
        logging.debug("save_configuration called.")
        # Validate and save configuration
        try:
            char_delay = int(self.char_delay_var.get())
            servo_delay = int(self.servo_delay_var.get())
            logging.debug(f"Saving configuration: char_delay={char_delay}, servo_delay={servo_delay}")
        except ValueError as e:
            logging.error(f"Invalid delay values during save: {e}")
            messagebox.showerror("Invalid Input", "Please enter valid numbers for delays.")
            return

        self.config.set("char_delay", char_delay)
        self.config.set("servo_delay", servo_delay)
        self.config.set("dual_servo_mode", self.dual_servo_var.get())
        self.config.set("debug_mode", self.debug_var.get())

        messagebox.showinfo("Configuration Saved", "Configuration settings have been saved successfully.")
        logging.info("Configuration saved successfully.")

    def on_dual_servo_toggle(self):
        """
        Handler for Dual Servo Mode checkbox toggle.
        Sends configuration command to Arduino.
        """
        logging.debug(f"Dual Servo Mode toggled to {self.dual_servo_var.get()}")
        # Update configuration
        self.config.set("dual_servo_mode", self.dual_servo_var.get())
        # Send configuration to Arduino
        if self.is_connected:
            self.send_configuration()

    def upload_image(self):
        """
        Handles the image upload process, extracts text using OCR,
        and displays the extracted text for user confirmation before sending.
        """
        logging.debug("upload_image called.")
        # Open file dialog to select image
        image_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=[
                ("Image Files", ("*.png", "*.jpg", "*.tiff")),
                ("All Files", "*.*")
            ]
        )
        if image_path:
            # Disable the upload button to prevent multiple clicks
            self.upload_button.config(state='disabled')
            # Start a new thread to process the image
            threading.Thread(target=self.process_image, args=(image_path,), daemon=True).start()

    def process_image(self, image_path):
        """
        Processes the uploaded image using the OCR function to extract text.
        """
        logging.debug(f"Processing image: {image_path}")
        try:
            # Extract text from the image
            text = brailleOCR.extract_text_from_image(image_path=image_path)
            logging.debug(f"Extracted text: '{text}'")
            if text:
                # Update the GUI in the main thread
                self.root.after(0, self.display_extracted_text, text)
            else:
                self.root.after(0, messagebox.showwarning, "No Text Found", "No text could be extracted from the image.")
        except Exception as e:
            logging.error(f"Error extracting text from image: {e}")
            self.root.after(0, messagebox.showerror, "Error", f"Failed to extract text from image.\nError: {e}")
        finally:
            # Re-enable the upload button
            self.root.after(0, self.upload_button.config, {'state': 'normal'})

    def display_extracted_text(self, text):
        """
        Displays the extracted text in the text input field and notifies the user.
        """
        logging.debug("Displaying extracted text.")
        # Display the extracted text in the text_input Entry widget
        self.text_input.delete(0, tk.END)
        self.text_input.insert(0, text)
        # Optionally, update the status label or show a message
        messagebox.showinfo("Text Extracted", "Text has been extracted from the image.")
        logging.info("Extracted text displayed in the input field.")

    def on_closing(self):
        """
        Handles the application closure event.
        Ensures proper disconnection and resource cleanup.
        """
        logging.debug("Application closing initiated.")
        self.disconnect()
        self.root.destroy()
        logging.info("Application closed.")


# Main application execution
if __name__ == "__main__":
    root = tk.Tk()
    app = BrailleControllerGUI(root)
    root.mainloop()
