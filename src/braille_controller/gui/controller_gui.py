"""
Main GUI Controller for Braille Display Application
Integrates all components and provides user interface
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
import threading
import re
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # Add parent directory to path

# Import custom components
from config.configuration import Configuration
from communication.serial_manager import SerialManager
from visualization.braille_canvas import BraillePatternCanvas
from visualization.servo_canvas import ServoVisualizer
from visualization.braille_character_display import BrailleCharacterDisplay


class BrailleControllerGUI:
    """Main GUI class for the Braille Controller application."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Braille Controller Interface")
        
        # Initialize components
        self.config = Configuration()
        self.serial_manager = SerialManager(self.process_serial_message)
        
        # Set up GUI elements
        self._setup_gui()
        self._setup_bindings()
        logging.debug("BrailleControllerGUI initialized")

    def _setup_gui(self):
        """Set up all GUI elements."""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both", padx=5, pady=5)
        
        # Create main tabs
        self.main_tab = ttk.Frame(self.notebook)
        self.config_tab = ttk.Frame(self.notebook)
        self.visual_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.main_tab, text="Control")
        self.notebook.add(self.config_tab, text="Configuration")
        self.notebook.add(self.visual_tab, text="Visualization")
        
        self._create_main_tab()
        self._create_config_tab()
        self._create_visual_tab()

    def _create_main_tab(self):
        """Create the main control tab."""
        # Connection Frame
        connection_frame = ttk.LabelFrame(self.main_tab, text="Connection", padding="5")
        connection_frame.pack(fill="x", padx=5, pady=5)

        # Port selection
        port_frame = ttk.Frame(connection_frame)
        port_frame.pack(fill="x")

        ttk.Label(port_frame, text="Port:").pack(side="left", padx=5)
        
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(port_frame, textvariable=self.port_var, state="readonly")
        self.port_combo.pack(side="left", padx=5, expand=True, fill="x")

        self.connect_button = ttk.Button(port_frame, text="Connect", command=self._toggle_connection)
        self.connect_button.pack(side="left", padx=5)

        refresh_button = ttk.Button(port_frame, text="↻", width=3, command=self._refresh_ports)
        refresh_button.pack(side="left", padx=5)

        # Text Input Frame
        input_frame = ttk.LabelFrame(self.main_tab, text="Text Input", padding="5")
        input_frame.pack(fill="x", padx=5, pady=5)

        self.text_input = ttk.Entry(input_frame)
        self.text_input.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        self.send_button = ttk.Button(input_frame, text="Send", command=self._send_text)
        self.send_button.pack(side="left", padx=5, pady=5)

        self.upload_button = ttk.Button(input_frame, text="Upload Image", command=self._upload_image)
        self.upload_button.pack(side="left", padx=5, pady=5)

        # Status Frame
        status_frame = ttk.LabelFrame(self.main_tab, text="Status", padding="5")
        status_frame.pack(fill="x", padx=5, pady=5)

        self.status_label = ttk.Label(status_frame, text="Disconnected")
        self.status_label.pack(padx=5, pady=5)

        self.char_display = ttk.Label(status_frame, text="Current Character: -", font=('Arial', 16))
        self.char_display.pack(padx=5, pady=5)

        self.progress = ttk.Progressbar(status_frame, mode='determinate')
        self.progress.pack(fill="x", padx=5, pady=5)

    def _create_config_tab(self):
        """Create the configuration tab."""
        # Timing Configuration
        timing_frame = ttk.LabelFrame(self.config_tab, text="Timing Configuration", padding="5")
        timing_frame.pack(fill="x", padx=5, pady=5)

        # Add Character Count Configuration
        char_frame = ttk.LabelFrame(self.config_tab, text="Display Configuration", padding="5")
        char_frame.pack(fill="x", padx=5, pady=5)
        
        ttk.Label(char_frame, text="Number of Characters:").pack(anchor="w", padx=5, pady=5)
        self.char_count_var = tk.IntVar(value=1)
        char_count_spinbox = ttk.Spinbox(
            char_frame,
            from_=1,
            to=7,
            textvariable=self.char_count_var,
            width=5,
            state="readonly",
            command=self._update_character_displays
        )
        char_count_spinbox.pack(anchor="w", padx=5, pady=5)

        # Character Delay
        ttk.Label(timing_frame, text="Character Delay (ms):").pack(anchor="w", padx=5, pady=(5, 0))
        self.char_delay_var = tk.StringVar(value=str(self.config.get("char_delay")))
        ttk.Entry(timing_frame, textvariable=self.char_delay_var).pack(fill="x", padx=5, pady=2)

        # Servo Delay
        ttk.Label(timing_frame, text="Servo Movement Delay (ms):").pack(anchor="w", padx=5, pady=(5, 0))
        self.servo_delay_var = tk.StringVar(value=str(self.config.get("servo_delay")))
        ttk.Entry(timing_frame, textvariable=self.servo_delay_var).pack(fill="x", padx=5, pady=2)

        # Servo Configuration
        servo_frame = ttk.LabelFrame(self.config_tab, text="Servo Configuration", padding="5")
        servo_frame.pack(fill="x", padx=5, pady=5)

        # Dual Servo Mode
        self.dual_servo_var = tk.BooleanVar(value=self.config.get("dual_servo_mode"))
        ttk.Checkbutton(
            servo_frame,
            text="Dual Servo Mode",
            variable=self.dual_servo_var,
            command=self._on_dual_servo_toggle
        ).pack(anchor="w", padx=5, pady=(5, 0))

        # Debug Mode
        self.debug_var = tk.BooleanVar(value=self.config.get("debug_mode"))
        ttk.Checkbutton(servo_frame, text="Debug Mode", variable=self.debug_var).pack(anchor="w", padx=5, pady=(5, 0))

        # Save Button
        ttk.Button(self.config_tab, text="Save Configuration", command=self._save_configuration).pack(pady=10)

    def _create_visual_tab(self):
        """Create the visualization tab with centered content."""
        # Create main container that fills the tab
        main_container = ttk.Frame(self.visual_tab)
        main_container.pack(fill="both", expand=True)
        
        # Create scrollable frame
        self.canvas = tk.Canvas(main_container)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.canvas.yview)
        
        # Configure canvas size
        self.canvas.configure(width=800)  # Set minimum width
        
        # Create frame for content
        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.pack(expand=True, fill="both", padx=20, pady=20)
        
        def _on_frame_configure(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Ensure minimum width
            if event.width < 800:
                self.scroll_frame.configure(width=800)
        
        self.scroll_frame.bind("<Configure>", _on_frame_configure)
        
        # Create window in canvas
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="n", width=800)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Initialize character displays list
        self.char_displays = []
        self._update_character_displays()

    def _update_character_displays(self):
            """Update the number of character displays."""
            num_chars = self.char_count_var.get()
            
            # Remove excess displays
            while len(self.char_displays) > num_chars:
                self.char_displays[-1].destroy()
                self.char_displays.pop()
            
            # Add new displays
            while len(self.char_displays) < num_chars:
                idx = len(self.char_displays) + 1
                display = BrailleCharacterDisplay(self.scroll_frame, character_index=idx)
                display.pack(pady=5)
                self.char_displays.append(display)

    def _setup_bindings(self):
        """Set up event bindings."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.text_input.bind('<Return>', lambda e: self._send_text())
        self._refresh_ports()

    def _refresh_ports(self):
        """Refresh available serial ports."""
        ports = self.serial_manager.get_available_ports()
        self.port_combo['values'] = ports
        if ports:
            self.port_combo.set(ports[0])
            logging.info(f"Available serial ports: {ports}")
        else:
            self.port_combo.set('')
            logging.warning("No serial ports found")

    def _toggle_connection(self):
        """Toggle serial connection state."""
        try:
            if not self.serial_manager.is_connected:
                self.serial_manager.connect(self.port_var.get())
                self.connect_button.configure(text="Disconnect")
                self.status_label.configure(text=f"Connected to {self.port_var.get()}")
            else:
                self.serial_manager.disconnect()
                self.connect_button.configure(text="Connect")
                self.status_label.configure(text="Disconnected")
                self.char_display.configure(text="Current Character: -")
                self.progress['value'] = 0
        except Exception as e:
            logging.error(f"Connection error: {e}")
            messagebox.showerror("Connection Error", str(e))

    def _send_text(self):
        """Send text to the device based on active character count."""
        try:
            text = self.text_input.get().strip()
            if not text:
                raise ValueError("Please enter some text to send")

            char_delay = int(self.char_delay_var.get())
            servo_delay = int(self.servo_delay_var.get())
            num_active_chars = self.char_count_var.get()

            # Store the text and setup initial state
            self.current_text = text
            self.current_position = 0

            if num_active_chars == 1:
                # For single character mode, send one character
                if self.current_position < len(text):
                    self.serial_manager.send_text(text[0], char_delay, servo_delay)
                    self.progress['value'] = 0
                    self.char_display.configure(text=f"Current Character: {text[0]}")
            else:
                # For multi-character mode, split text into groups
                text_groups = [text[i:i+num_active_chars] for i in range(0, len(text), num_active_chars)]
                self.current_text_groups = text_groups
                self.current_group_index = 0
                
                # Send first group as a single string
                if text_groups:
                    first_group = text_groups[0]
                    self.serial_manager.send_text(first_group, char_delay, servo_delay)
                    self.progress['value'] = 0
                    self.char_display.configure(text=f"Current Characters: {', '.join(first_group)}")

            # Reset all character displays
            for display in self.char_displays:
                display.update_letter("-")
                display.pattern_canvas.update_pattern("000000")

        except Exception as e:
            logging.error(f"Send error: {e}")
            messagebox.showerror("Send Error", str(e))

    def _save_configuration(self):
        """Save current configuration."""
        try:
            self.config.set("char_delay", int(self.char_delay_var.get()))
            self.config.set("servo_delay", int(self.servo_delay_var.get()))
            self.config.set("dual_servo_mode", self.dual_servo_var.get())
            self.config.set("debug_mode", self.debug_var.get())
            messagebox.showinfo("Success", "Configuration saved successfully")
        except Exception as e:
            logging.error(f"Configuration save error: {e}")
            messagebox.showerror("Save Error", str(e))

    def _on_dual_servo_toggle(self):
        """Handle dual servo mode toggle."""
        self.config.set("dual_servo_mode", self.dual_servo_var.get())
        if self.serial_manager.is_connected:
            self.serial_manager.send_configuration(self.dual_servo_var.get())

    def process_serial_message(self, message: str):
        """Process incoming serial messages and handle group transitions."""
        logging.debug(f"Received message: {message}")
        
        try:
            if "Character:" in message:
                parts = message.split("->")
                if len(parts) == 2:
                    char = parts[0].split(":")[1].strip()
                    pattern_info = parts[1].strip()
                    
                    if hasattr(self, 'current_text_groups') and self.current_text_groups:
                        current_group = self.current_text_groups[self.current_group_index]
                        logging.debug(f"Current group: {current_group}, Current char: {char}")
                        
                        try:
                            char_position = current_group.index(char)
                            logging.debug(f"Found char {char} at position {char_position}")
                            
                            # Direct update to the display
                            display = self.char_displays[char_position]
                            display.letter_display.configure(text=char)
                            display.current_letter = char
                            
                            if "Pattern:" in pattern_info:
                                # Updated regex to match any length of bits
                                binary_match = re.search(r'Pattern:\s*([01]+)', pattern_info)
                                if binary_match:
                                    pattern = binary_match.group(1).zfill(6)  # Pad to 6 bits
                                    logging.debug(f"Updating display {char_position} with char {char} and pattern {pattern}")
                                    # Force braille pattern update
                                    display.pattern_canvas.update_pattern(pattern)
                                    display.pattern_canvas.update_idletasks()
                                else:
                                    logging.warning(f"No pattern found for character {char}")
                                    
                                servo_matches = re.findall(r'Servo ([AB]) \((?:\d+)\): (\d+)µs', pattern_info)
                                if servo_matches:
                                    pulses = {}
                                    for servo, pulse in servo_matches:
                                        pulses[servo] = int(pulse)
                                    
                                    if 'A' in pulses and 'B' in pulses:
                                        angle_a = self._pulse_to_angle(pulses['A'])
                                        angle_b = self._pulse_to_angle(pulses['B'])
                                        display.servo_canvas.set_angle(angle_a, angle_b)
                            
                            # Force update of the display components
                            display.letter_display.update_idletasks()
                            
                            # If this was the last character in the group
                            if char_position == len(current_group) - 1:
                                self.current_group_index += 1
                                if self.current_group_index < len(self.current_text_groups):
                                    next_group = self.current_text_groups[self.current_group_index]
                                    char_delay = int(self.char_delay_var.get())
                                    servo_delay = int(self.servo_delay_var.get())
                                    
                                    self.char_display.configure(text=f"Current Characters: {', '.join(next_group)}")
                                    self.root.after(char_delay, lambda: self.serial_manager.send_text(
                                        next_group, char_delay, servo_delay))
                                
                        except ValueError:
                            logging.error(f"Character {char} not found in current group {current_group}")
                        
        except Exception as e:
            logging.error(f"Message processing error: {e}", exc_info=True)

    def _pulse_to_angle(self, pulse_width: int) -> float:
        """Convert servo pulse width to angle using observed pulse range."""
        # Adjusted based on observed values in logs
        MIN_PULSE = 500    # Slightly below minimum observed (844)
        MAX_PULSE = 2500   # Slightly above maximum observed (2037)
        MIN_ANGLE = 0
        MAX_ANGLE = 180
        
        # Ensure pulse width is within bounds
        pulse_width = max(MIN_PULSE, min(pulse_width, MAX_PULSE))
        logging.debug(f"Pulse width (bounded): {pulse_width}µs")
        
        # Linear conversion
        angle = (pulse_width - MIN_PULSE) * (MAX_ANGLE - MIN_ANGLE) / (MAX_PULSE - MIN_PULSE)
        angle = round(angle, 1)
        
        logging.debug(f"Converted {pulse_width}µs to {angle}°")
        return angle

    def _on_closing(self):
        """Handle application closure."""
        self.serial_manager.disconnect()
        self.root.destroy()

    def _upload_image(self):
        """Handle image upload and OCR processing."""
        try:
            # Import easyocr here to avoid startup delay
            import easyocr
            
            # Open file dialog to select image
            image_path = filedialog.askopenfilename(
                title="Select Image",
                filetypes=[
                    ("Image Files", ("*.png", "*.jpg", "*.jpeg", "*.tiff")),
                    ("All Files", "*.*")
                ]
            )
            
            if not image_path:
                return
                
            # Disable the upload button to prevent multiple clicks
            self.upload_button.config(state='disabled')
            
            try:
                # Initialize reader
                reader = easyocr.Reader(['en'])
                
                # Process image
                result = reader.readtext(image_path)
                
                # Extract text with confidence threshold
                extracted_text = []
                for bbox, text, prob in result:
                    if prob > 0.5:  # Confidence threshold
                        extracted_text.append(text)
                        
                if extracted_text:
                    final_text = ' '.join(extracted_text)
                    self.text_input.delete(0, tk.END)
                    self.text_input.insert(0, final_text)
                    messagebox.showinfo("Success", "Text extracted from image")
                else:
                    messagebox.showwarning("No Text Found", 
                        "No text could be extracted from the image with sufficient confidence")
                        
            except ImportError as e:
                logging.error(f"Failed to import easyocr module: {e}")
                messagebox.showerror("Error", 
                    "OCR module not available. Please ensure EasyOCR is properly installed.")
            except Exception as e:
                logging.error(f"OCR processing error: {e}")
                messagebox.showerror("Error", f"Failed to process image: {str(e)}")
                    
        except Exception as e:
            logging.error(f"Image upload error: {e}")
            messagebox.showerror("Upload Error", str(e))
        finally:
            # Re-enable the upload button
            self.upload_button.config(state='normal')