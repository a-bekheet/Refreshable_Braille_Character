"""
Braille pattern definitions matching Arduino implementation
"""

# Braille patterns for lowercase letters a-z
BRAILLE_PATTERNS = {
    'a': "100000", 'b': "101000", 'c': "110000", 'd': "110100", 'e': "100100",
    'f': "111000", 'g': "111100", 'h': "101100", 'i': "011000", 'j': "011100",
    'k': "100010", 'l': "101010", 'm': "110010", 'n': "110110", 'o': "100110",
    'p': "111010", 'q': "111110", 'r': "101110", 's': "011010", 't': "011110",
    'u': "100011", 'v': "101011", 'w': "011101", 'x': "110011", 'y': "110111",
    'z': "100111"
}

# Braille patterns for numbers 0-9
BRAILLE_NUMBERS = {
    '0': "010110", '1': "100000", '2': "101000", '3': "110000", '4': "110100",
    '5': "100100", '6': "111000", '7': "111100", '8': "101100", '9': "011000"
}

# Other Braille patterns
BRAILLE_SPECIAL = {
    ' ': "000000",  # space
    '.': "010011",  # period
    ',': "010000",  # comma
    '?': "011001",  # question mark
    '!': "011010"   # exclamation mark
}

# Pattern to angle mapping (matches Arduino PATTERN_TO_ANGLE array)
PATTERN_TO_ANGLE = [
    66,  # 000
    84,  # 001
    37,  # 010
    128, # 011
    51,  # 100
    26,  # 101
    22,  # 110
    0    # 111
]

def get_pattern_for_char(char: str) -> str:
    """Get the Braille pattern for a given character."""
    char = char.lower()
    if char in BRAILLE_PATTERNS:
        return BRAILLE_PATTERNS[char]
    elif char in BRAILLE_NUMBERS:
        return BRAILLE_NUMBERS[char]
    elif char in BRAILLE_SPECIAL:
        return BRAILLE_SPECIAL[char]
    return BRAILLE_SPECIAL[' ']  # Default to space pattern

def pattern_to_angles(pattern: str) -> tuple[int, int]:
    """Convert a 6-bit pattern string to servo angles."""
    # Convert pattern string to integer
    pattern_int = int(pattern, 2)
    
    # Split into two 3-bit patterns
    servo_a_bits = (pattern_int >> 3) & 0x07  # Top 3 bits (b5b4b3)
    servo_b_bits = pattern_int & 0x07         # Bottom 3 bits (b2b1b0)
    
    # Get angles from lookup table
    angle_a = PATTERN_TO_ANGLE[servo_a_bits]
    angle_b = PATTERN_TO_ANGLE[servo_b_bits]
    
    return angle_a, angle_b

def validate_pattern(pattern: str) -> bool:
    """Validate that a pattern string is correct format."""
    if not pattern or len(pattern) != 6:
        return False
    return all(bit in '01' for bit in pattern)