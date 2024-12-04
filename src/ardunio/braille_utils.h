#ifndef BRAILLE_UTILS_H
#define BRAILLE_UTILS_H

#include <ArduinoJson.h>

// Constants
#define PWM_RESOLUTION 16
#define PWM_PERIOD_US 20000
#define MAX_INPUT_LENGTH 1000

// Lookup table for 3-bit patterns to pulse widths in microseconds
const unsigned int PATTERN_TO_PULSEWIDTH[] = {
    844,  // 000 -> 0.0mm (Home Position)
    1151, // 001 -> 2.5mm
    1268, // 010 -> 5.0mm
    1324, // 011 -> 7.5mm
    1613, // 100 -> 10.0mm
    1920, // 101 -> 12.5mm
    2037, // 110 -> 15.0mm
    2094  // 111 -> 17.5mm
};

// Function Prototypes
uint8_t translate_braille_character(char c);
uint32_t map_pulsewidth_to_duty(unsigned int pulse_width_us);
unsigned int get_servo_pulse(uint8_t pattern_bits);
void process_serial_input(const char* json_input, const char** text, int* char_delay, int* servo_delay, bool* dual_servo, bool* debug_mode);

#endif
