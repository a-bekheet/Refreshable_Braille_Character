#include "braille_utils.h"
#include <ctype.h>  // For tolower()

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

// Function to convert a character to its 6-bit Braille representation
uint8_t translate_braille_character(char c) {
    uint8_t pattern = 0;
    c = tolower(c);
    
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
        if (c == ' ') {
            pattern = 0x00; // 000000
        } else if (c == '.') {
            pattern = 0x13; // 010011
        } else if (c == ',') {
            pattern = 0x10; // 010000
        } else if (c == '?') {
            pattern = 0x19; // 011001
        } else if (c == '!') {
            pattern = 0x1A; // 011010
        } else {
            pattern = 0x00; // Default to space for unknown characters
        }
    }
    return pattern;
}

// Function to map pulse width in microseconds to duty cycle
uint32_t map_pulsewidth_to_duty(unsigned int pulse_width_us) {
    // Calculate duty cycle based on PWM resolution and frequency
    uint32_t max_duty = (1 << PWM_RESOLUTION) - 1;
    return ((uint32_t)pulse_width_us * max_duty) / PWM_PERIOD_US;
}

// Function to get servo pulse width based on pattern bits
unsigned int get_servo_pulse(uint8_t pattern_bits) {
    if (pattern_bits > 7) {
        return PATTERN_TO_PULSEWIDTH[0]; // Default to home position
    }
    return PATTERN_TO_PULSEWIDTH[pattern_bits];
}

// Function to process incoming JSON input
void process_serial_input(const char* json_input, const char** text, int* char_delay, int* servo_delay, bool* dual_servo, bool* debug_mode) {
    StaticJsonDocument<512> doc;
    DeserializationError error = deserializeJson(doc, json_input);
    
    if (error) {
        Serial.println("Error parsing JSON");
        return;
    }
    
    *text = doc["text"] | "";
    *char_delay = doc["char_delay"] | 3000; // Default 3000ms
    *servo_delay = doc["servo_delay"] | 750; // Default 750ms
    *dual_servo = doc["dual_servo"] | false; // Default false
    *debug_mode = doc["debug_mode"] | false; // Default false
}
