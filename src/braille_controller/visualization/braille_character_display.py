"""
Combined Braille Character Display Component
"""
import tkinter as tk
from tkinter import ttk
from .braille_canvas import BraillePatternCanvas
from .servo_canvas import ServoVisualizer

class BrailleCharacterDisplay(ttk.Frame):
    def __init__(self, parent, character_index=1, **kwargs):
        super().__init__(parent, **kwargs)
        self.character_index = character_index
        self.current_letter = "-"
        
        # Create main bounding box frame with dark background
        self.main_frame = ttk.Frame(self, style='Dark.TFrame')
        self.main_frame.pack(fill="x", expand=True, padx=20, pady=10)  # Increased padding
        
        # Create container with fixed minimum size
        self.content_frame = ttk.Frame(self.main_frame, style='Dark.TFrame')
        self.content_frame.pack(fill="x", expand=True)
        
        # Force minimum width
        self.content_frame.grid_columnconfigure(0, minsize=600)  # Set minimum width
        
        # Header with more padding
        self.header = ttk.Label(
            self.content_frame, 
            text=f"Braille Character {character_index}",
            font=("Arial", 12, "bold"),
            background='dark gray',
            foreground='white'
        )
        self.header.pack(pady=(15, 5))  # Increased top padding
        
        # Letter display
        self.letter_display = ttk.Label(
            self.content_frame,
            text=self.current_letter,
            font=("Arial", 24, "bold"),
            background='dark gray',
            foreground='white'
        )
        self.letter_display.pack(pady=(5, 15))  # Increased padding
        
        # Display container with more space
        self.display_container = ttk.Frame(self.content_frame, style='Dark.TFrame')
        self.display_container.pack(fill="x", expand=True, padx=30, pady=(0, 15))  # Increased padding
        
        # Pattern and servo displays with proper spacing
        self.pattern_canvas = BraillePatternCanvas(
            self.display_container, 
            character_index=character_index
        )
        self.pattern_canvas.pack(side="left", padx=20, expand=True)
        
        self.servo_canvas = ServoVisualizer(self.display_container)
        self.servo_canvas.pack(side="right", padx=20, expand=True)
        
    def update_pattern(self, pattern: str):
        """Delegate pattern update to pattern canvas."""
        self.pattern_canvas.update_pattern(pattern)
        
    def update_letter(self, letter: str):
        """Update the displayed letter."""
        self.current_letter = letter
        self.letter_display.configure(text=letter)
        
    def update_servos(self, angle_a: float, angle_b: float):
        """Delegate servo update to servo canvas."""
        self.servo_canvas.set_angle(angle_a, angle_b)
        
    def update_idletasks(self):
        """Force immediate update of the display."""
        super().update_idletasks()
        self.pattern_canvas.update_idletasks()
        self.servo_canvas.update_idletasks()