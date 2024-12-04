"""
Servo Motor Visualization Component
Provides a canvas widget for displaying servo motor positions
"""

import tkinter as tk
import math
import logging

class ServoVisualizer(tk.Canvas):
    """Visualizes dual servo positions with linear displacement."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.width = kwargs.get('width', 400)
        self.height = kwargs.get('height', 180)
        self.configure(width=self.width, height=self.height)
        
        # State initialization
        self.angle_a = 0
        self.angle_b = 0
        self.prev_angle_a = None
        self.prev_angle_b = None
        
        self.PATTERN_TO_ANGLE = [66, 84, 37, 128, 51, 26, 22, 0]
        self.STEP_DISTANCE = 2.1875
        
        self.draw_servos()

    def _angle_to_position(self, angle):
        """Convert angle to position index and displacement."""
        try:
            pos_index = self.PATTERN_TO_ANGLE.index(angle)
        except ValueError:
            pos_index = min(range(len(self.PATTERN_TO_ANGLE)), 
                          key=lambda i: abs(self.PATTERN_TO_ANGLE[i] - angle))
        
        displacement = pos_index * self.STEP_DISTANCE
        return pos_index, round(displacement, 2)

    def draw_servos(self):
        """Draw combined servo visualization with improved layout."""
        self.delete("all")
        
        # Dark outer box (for labels and angles)
        outer_margin = 20
        self.create_rectangle(outer_margin, outer_margin, 
                            self.width-outer_margin, self.height-outer_margin, 
                            fill="dark gray", width=2)
        
        # Inner lighter box (movement area)
        inner_margin = 60
        movement_box = self.create_rectangle(inner_margin, inner_margin, 
                                          self.width-inner_margin, self.height-inner_margin,
                                          fill="light gray", width=1)
        
        # Calculate positions
        _, disp_a = self._angle_to_position(self.angle_a)
        _, disp_b = self._angle_to_position(self.angle_b)
        
        # Bar dimensions
        bar_width = 40
        bar_height = 20
        max_travel = self.width - (2 * inner_margin + bar_width)
        
        # Map displacements to pixel positions
        pos_a = inner_margin + (disp_a / (7 * self.STEP_DISTANCE)) * max_travel
        pos_b = self.width - inner_margin - bar_width - (disp_b / (7 * self.STEP_DISTANCE)) * max_travel
        
        # Label backgrounds
        # Servo A (bottom left)
        self.create_rectangle(outer_margin+10, self.height-outer_margin-40,
                            outer_margin+140, self.height-outer_margin-5,
                            fill="dark gray", outline="black")
        # Servo B (top right)
        self.create_rectangle(self.width-outer_margin-140, outer_margin+5,
                            self.width-outer_margin-10, outer_margin+40,
                            fill="dark gray", outline="black")
        
        # Labels
        self.create_text(outer_margin+15, self.height-outer_margin-30,
                        text="Servo A", anchor="w", 
                        font=("Arial", 12, "bold"), fill="white")
        self.create_text(self.width-outer_margin-15, outer_margin+15,
                        text="Servo B", anchor="e", 
                        font=("Arial", 12, "bold"), fill="white")
        
        # Draw moving bars (entirely within light grey box)
        # Adjusted vertical positions to ensure bars stay within light grey area
        servo_spacing = (self.height - 2 * inner_margin - 2 * bar_height) // 3
        
        # Servo B bar (top)
        self.create_rectangle(pos_b, 
                            inner_margin + servo_spacing, 
                            pos_b + bar_width,
                            inner_margin + servo_spacing + bar_height,
                            fill="black")
        
        # Servo A bar (bottom)
        self.create_rectangle(pos_a,
                            self.height - inner_margin - servo_spacing - bar_height,
                            pos_a + bar_width,
                            self.height - inner_margin - servo_spacing,
                            fill="black")
        
        # Value labels
        self.create_text(outer_margin+65, self.height-outer_margin-15,
                        text=f"{self.angle_a}° | {disp_a:.2f}mm",
                        anchor="w", font=("Arial", 10), fill="white")
        
        self.create_text(self.width-outer_margin-65, outer_margin+30,
                        text=f"{self.angle_b}° | {disp_b:.2f}mm",
                        anchor="e", font=("Arial", 10), fill="white")

    def set_angle(self, angle_a: float, angle_b: float):
        """Update both servo angles."""
        try:
            if self.prev_angle_a != angle_a or self.prev_angle_b != angle_b:
                self.angle_a = angle_a
                self.angle_b = angle_b
                self.prev_angle_a = angle_a
                self.prev_angle_b = angle_b
                self.draw_servos()
                self.update()
        except Exception as e:
            logging.error(f"Error setting servo angles: {e}")