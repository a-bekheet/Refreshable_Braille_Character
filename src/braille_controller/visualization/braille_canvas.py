"""
Braille Pattern Visualization Component
"""
import tkinter as tk
import logging

class BraillePatternCanvas(tk.Canvas):
    """Visualizes Braille dot patterns in a 3x2 grid."""
    
    def __init__(self, parent, character_index=1, **kwargs):
        super().__init__(parent, **kwargs)
        self.dot_radius = 10
        self.dot_spacing = 30
        self.character_index = character_index
        
        # Adjust canvas size
        self.width = self.dot_spacing * 3 + 40
        self.height = self.dot_spacing * 4
        self.configure(width=self.width, height=self.height)
        
        # Initialize dots state (2x3 grid for standard braille)
        self.dots_state = [[False] * 3 for _ in range(2)]
        self.draw_pattern()

    def draw_pattern(self):
        """Draws the current Braille dot pattern."""
        self.delete("all")
        
        # Calculate center positions
        center_x = self.width / 2
        center_y = self.height / 2
        
        # Calculate pattern offset based on dot spacing
        pattern_width = self.dot_spacing * 2  # 2 columns
        pattern_height = self.dot_spacing * 3  # 3 rows
        start_x = center_x - (pattern_width / 2) + self.dot_spacing/2
        start_y = center_y - (pattern_height / 2) + self.dot_spacing/2
        
        # Draw dots in upright orientation
        for i in range(2):  # columns
            for j in range(3):  # rows
                x = start_x + (i * self.dot_spacing)
                y = start_y + (j * self.dot_spacing)
                color = "black" if self.dots_state[i][j] else "white"
                self.create_oval(
                    x - self.dot_radius,
                    y - self.dot_radius,
                    x + self.dot_radius,
                    y + self.dot_radius,
                    fill=color,
                    outline="gray"
                )

    def update_pattern(self, pattern: str):
        """Update pattern using 6-bit binary string."""
        try:
            bits = [bool(int(b)) for b in pattern.zfill(6)]
            self.dots_state = [
                [bits[0], bits[2], bits[4]],  # Left column (1,2,3)
                [bits[1], bits[3], bits[5]]   # Right column (4,5,6)
            ]
            self.draw_pattern()
            logging.debug(f"Pattern updated: {pattern}")
        except Exception as e:
            logging.error(f"Error updating Braille pattern: {e}")