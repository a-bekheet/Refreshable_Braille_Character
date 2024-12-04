#include <Servo.h>
#include <string.h>

// Constants
#define SERVO_A_PIN 8    // Top servo pin
#define SERVO_B_PIN 9    // Bottom servo pin
#define MAX_INPUT_LENGTH 1000

// Create servo objects
Servo myServoA;  // For top 3 bits (b5b4b3)
Servo myServoB;  // For bottom 3 bits (b2b1b0)

// Lookup table for 3-bit patterns to microseconds
// Index corresponds to binary value (000 = 0, 111 = 7)
const unsigned int PATTERN_TO_MICROSECONDS[] = {
    844,  // 000 -> 75.0686°
    1151, // 001 -> 69.5277°
    1268, // 010 -> 58.1092°
    1324, // 011 -> 28.1786°
    1613, // 100 -> -28.1786°
    1920, // 101 -> -58.1092°
    2037, // 110 -> -69.5277°
    2094  // 111 -> -75.0686°
};

// Braille patterns for lowercase letters a-z
const char *braille_patterns[26] = {
    "100000", "101000", "110000", "110100", "100100", // a-e
    "111000", "111100", "101100", "011000", "011100", // f-j
    "100010", "101010", "110010", "110110", "100110", // k-o
    "111010", "111110", "101110", "011010", "011110", // p-t
    "100011", "101011", "011101", "110011", "110111", // u-y
    "100111"  // z
};

// Braille patterns for numbers 0-9
const char *braille_numbers[10] = {
    "010110", "100000", "101000", "110000", "110100", // 0-4
    "100100", "111000", "111100", "101100", "011000"  // 5-9
};

// Other Braille patterns
const char *braille_space = "000000";
const char *braille_period = "010011";
const char *braille_comma = "010000";
const char *braille_question = "011001";
const char *braille_exclamation = "011010";

// Mode flag
bool dual_servo_mode = true;  // Default to dual servo mode

// Function to convert a character to its 6-bit Braille representation
uint8_t translate_braille_character(char c) {
    uint8_t pattern = 0;

    if (c >= 'a' && c <= 'z') {
        const char* str_pattern = braille_patterns[c - 'a'];
        for (int i = 0; i < 6; i++) {
            if (str_pattern[i] == '1') {
                pattern |= (1 << (5 - i));
            }
        }
    } else if (c >= '0' && c <= '9') {
        const char* str_pattern = braille_numbers[c - '0'];
        for (int i = 0; i < 6; i++) {
            if (str_pattern[i] == '1') {
                pattern |= (1 << (5 - i));
            }
        }
    } else {
        switch(c) {
            case ' ': pattern = 0x00; break;  // 000000
            case '.': pattern = 0x13; break;  // 010011
            case ',': pattern = 0x10; break;  // 010000
            case '?': pattern = 0x19; break;  // 011001
            case '!': pattern = 0x1A; break;  // 011010
            default: pattern = 0x00; break;   // Default to space
        }
    }
    return pattern;
}

// Function to write a 6-bit Braille pattern using two servos
void write_braille_character(uint8_t pattern) {
    // Split the 6-bit pattern into two 3-bit patterns for each servo
    uint8_t servo_a_bits = (pattern >> 3) & 0x07;  // Top 3 bits (b5b4b3)
    uint8_t servo_b_bits = pattern & 0x07;         // Bottom 3 bits (b2b1b0)

    // Get microseconds directly from lookup table
    unsigned int pulse_a = PATTERN_TO_MICROSECONDS[servo_a_bits];
    unsigned int pulse_b = PATTERN_TO_MICROSECONDS[servo_b_bits];

    if (dual_servo_mode) {
        // Write pulses to both servos
        myServoA.writeMicroseconds(pulse_a);
        myServoB.writeMicroseconds(pulse_b);
    } else {
        // Write only to Servo A
        myServoA.writeMicroseconds(pulse_a);
        // Optionally reset Servo B to home position
        myServoB.writeMicroseconds(844); // Home position
    }

    // Debug output
    Serial.print("Pattern: ");
    Serial.print(pattern, BIN);
    Serial.print(" Servo A (");
    Serial.print(servo_a_bits, BIN);
    Serial.print("): ");
    Serial.print(pulse_a);
    Serial.print("µs");
    if (dual_servo_mode) {
        Serial.print(", Servo B (");
        Serial.print(servo_b_bits, BIN);
        Serial.print("): ");
        Serial.print(pulse_b);
        Serial.print("µs");
    }
    Serial.println();

    // Add delay to allow servos to reach position
    delay(1000);
}

// Function to process an entire string
void process_string(const char* input) {
    for (size_t i = 0; i < strlen(input); i++) {
        char c = tolower(input[i]);  // Convert to lowercase
        uint8_t pattern = translate_braille_character(c);
        Serial.print("Character: ");
        Serial.print(c);
        Serial.print(" -> ");
        write_braille_character(pattern);
        delay(500);  // Delay between characters
    }
}

void setup() {
    Serial.begin(9600);

    // Attach servos to their pins
    myServoA.attach(SERVO_A_PIN);
    myServoB.attach(SERVO_B_PIN);

    // Move servos to home position (000 pattern = 844µs)
    myServoA.writeMicroseconds(844);
    myServoB.writeMicroseconds(844);

    Serial.println("Braille Servo Controller Ready");
    Serial.println("Enter text to convert to Braille");
}

void loop() {
    static char input_buffer[MAX_INPUT_LENGTH];
    static int buffer_pos = 0;

    while (Serial.available() > 0) {
        char c = Serial.read();

        if (c == '\n' || c == '\r') {
            if (buffer_pos > 0) {
                input_buffer[buffer_pos] = '\0';
                // Check if it's a configuration command
                if (strncmp(input_buffer, "CONFIG:DUAL=", 12) == 0) {
                    char mode = input_buffer[12];
                    if (mode == '1') {
                        dual_servo_mode = true;
                        Serial.println("Dual Servo Mode Enabled");
                    } else if (mode == '0') {
                        dual_servo_mode = false;
                        Serial.println("Dual Servo Mode Disabled");
                    } else {
                        Serial.println("Invalid Dual Servo Mode Command");
                    }
                }
                // Check if it's a text command
                else if (strncmp(input_buffer, "TEXT:", 5) == 0) {
                    const char* text = input_buffer + 5;
                    Serial.print("Processing: ");
                    Serial.println(text);
                    process_string(text);
                }
                // Handle other commands or default behavior
                else {
                    Serial.print("Unknown Command: ");
                    Serial.println(input_buffer);
                }
                buffer_pos = 0;  // Reset buffer
            }
        } else if (buffer_pos < MAX_INPUT_LENGTH - 1) {
            input_buffer[buffer_pos++] = c;
        }
    }
}
