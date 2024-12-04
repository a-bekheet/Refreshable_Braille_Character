# Braille Controller Interface

A Python-based GUI application for controlling and visualizing a refreshable Braille display system. This interface allows real-time control and visualization of servo motors that physically create Braille characters.

## Features

- Real-time Braille character visualization
- Servo motor position tracking and display
- Support for multiple simultaneous Braille characters (up to 7)
- Optical Character Recognition (OCR) for text input from images
- Configurable timing and servo parameters
- Visual feedback of servo positions with angle and displacement measurements

## System Requirements

- Python 3.8+
- tkinter (Python's standard GUI package)
- Supported Operating Systems: Windows, macOS, Linux

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd Refreshable_Braille_Character
```

2. Create and activate a virtual environment:
```bash
python -m venv braille_env
source braille_env/bin/activate  # On Unix/macOS
braille_env\Scripts\activate     # On Windows
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
braille_controller/
├── main.py
├── requirements.txt
├── brailleOCR.py           # OCR module
├── config/
│   └── configuration.py    # Configuration management
├── communication/
│   └── serial_manager.py   # Arduino communication
├── gui/
│   └── controller_gui.py   # Main GUI interface
├── visualization/
│   ├── braille_canvas.py   # Braille pattern visualization
│   └── servo_canvas.py     # Servo position visualization
└── logs/                   # Application logs
```

## Features in Detail

### Braille Visualization
- Real-time display of Braille patterns
- Support for standard 6-dot Braille characters
- Visual representation of dot patterns

### Servo Control
- Precise servo motor position tracking
- Angular position display
- Linear displacement measurements
- Support for dual servo operation

### OCR Capabilities
- Image-to-text conversion
- Supported formats: JPG, PNG, TIFF
- Confidence scoring for accuracy

### Configuration Options
- Character delay timing
- Servo movement timing
- Debug mode
- Multi-character display settings

## Usage

1. Start the application:
```bash
python src/braille_controller/main.py
```

2. Connect to Arduino:
   - Select the appropriate COM port
   - Click "Connect"

3. Input text:
   - Type directly into the text input field, or
   - Use the "Upload Image" button for OCR input

4. Configure settings:
   - Adjust character and servo delays
   - Set the number of active characters (1-7)
   - Toggle debug mode if needed

## Hardware Requirements

- Arduino board (tested with Arduino Uno)
- Servo motors compatible with Arduino
- USB connection for Arduino communication

## Development Notes

- EasyOCR is used for optical character recognition
- Serial communication runs at 9600 baud
- Servo pulse width range: 500-2500 µs
- Character processing supports multiple character groups

## Known Limitations

- OCR currently doesn't support handwritten text
- Maximum of 7 simultaneous Braille characters
- PDF support requires conversion to image format

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Authors

Ali Bekheet

Department of Physics, Engineering Physics

Queen's University
## Acknowledgments


- EasyOCR for text recognition capabilities
- PySerial for Arduino communication
- tkinter for GUI framework