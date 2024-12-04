"""
Serial Communication Manager Module
Handles all serial communication with the Arduino device
"""

import serial
import serial.tools.list_ports
import threading
import time
import logging
from typing import Optional, List, Callable

class SerialManager:
    """Manages serial communication with Arduino device."""
    
    def __init__(self, message_callback: Callable[[str], None]):
        """
        Initialize Serial Manager.
        
        Args:
            message_callback: Callback function to handle received messages
        """
        self.connection: Optional[serial.Serial] = None
        self.is_connected: bool = False
        self.message_callback = message_callback
        self._read_thread: Optional[threading.Thread] = None
        self._stop_thread: bool = False

    def get_available_ports(self) -> List[str]:
        """Get list of available serial ports."""
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port: str) -> None:
        """
        Connect to specified serial port.
        
        Args:
            port: Serial port to connect to
            
        Raises:
            ValueError: If no port specified
            serial.SerialException: If connection fails
        """
        if not port:
            raise ValueError("No port selected")

        try:
            self.connection = serial.Serial(
                port=port,
                baudrate=9600,
                timeout=1,
                write_timeout=1
            )
            
            # Hardware flow control sequence
            self.connection.dtr = False
            time.sleep(0.1)
            self.connection.dtr = True
            time.sleep(2)  # Allow Arduino initialization
            
            self.is_connected = True
            self._stop_thread = False
            self._start_read_thread()
            logging.info(f"Connected to {port}")
        except Exception as e:
            logging.error(f"Failed to connect to {port}: {e}")
            raise

    def disconnect(self) -> None:
        """Disconnect from serial port and cleanup resources."""
        self._stop_thread = True
        self.is_connected = False
        
        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join(timeout=1)
            
        if self.connection and self.connection.is_open:
            self.connection.close()
            logging.info("Serial connection closed")

    def send_text(self, text: str, char_delay: int, servo_delay: int) -> None:
        """
        Send text command to Arduino.
        
        Args:
            text: Text to send
            char_delay: Character delay in milliseconds
            servo_delay: Servo movement delay in milliseconds
            
        Raises:
            ConnectionError: If not connected
            ValueError: If invalid parameters
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to device")

        if not text.strip():
            raise ValueError("Empty text")

        try:
            # Prepare text command
            text_command = f"TEXT:{text}\n"
            
            # Clear buffers
            self.connection.reset_input_buffer()
            self.connection.reset_output_buffer()
            
            # Send command
            self.connection.write(text_command.encode())
            self.connection.flush()
            logging.debug(f"Text command sent: {text_command.strip()}")
        except Exception as e:
            logging.error(f"Failed to send text: {e}")
            raise

    def send_configuration(self, dual_servo_mode: bool) -> None:
        """
        Send configuration command to Arduino.
        
        Args:
            dual_servo_mode: Enable/disable dual servo mode
            
        Raises:
            ConnectionError: If not connected
        """
        if not self.is_connected:
            raise ConnectionError("Not connected to device")

        try:
            config_command = f"CONFIG:DUAL={int(dual_servo_mode)}\n"
            self.connection.write(config_command.encode())
            self.connection.flush()
            logging.debug(f"Configuration command sent: {config_command.strip()}")
        except Exception as e:
            logging.error(f"Failed to send configuration: {e}")
            raise

    def _start_read_thread(self) -> None:
        """Start asynchronous read thread."""
        self._read_thread = threading.Thread(target=self._read_serial, daemon=True)
        self._read_thread.start()

    def _read_serial(self) -> None:
        """Continuous serial read loop."""
        while not self._stop_thread and self.is_connected and self.connection and self.connection.is_open:
            try:
                if self.connection.in_waiting:
                    line = self.connection.readline().decode().strip()
                    if line:
                        logging.debug(f"Received: {line}")
                        self.message_callback(line)
                time.sleep(0.1)  # Prevent CPU saturation
            except serial.SerialException as e:
                logging.error(f"Serial read error: {e}")
                break
            except UnicodeDecodeError as e:
                logging.warning(f"Unicode decode error: {e}")
                continue
            except Exception as e:
                logging.error(f"Unexpected error in read thread: {e}")
                break
        
        # Ensure cleanup if thread exits
        self.is_connected = False