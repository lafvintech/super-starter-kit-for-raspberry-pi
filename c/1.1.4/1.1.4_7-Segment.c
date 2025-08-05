#include <wiringPi.h>
#include <stdio.h>

// Pin definitions for the 74HC595 shift register.
#define SDI_PIN   0   // Serial Data Input (DS)
#define RCLK_PIN  1   // Storage Register Clock (STCP)
#define SRCLK_PIN 2   // Shift Register Clock (SHCP)

// Delay between displaying numbers in milliseconds.
#define DISPLAY_DELAY 500

/**
 * @brief Common-anode 7-segment display codes for 0-F.
 * Segments are mapped as: g, f, e, d, c, b, a
 * A low bit turns a segment ON.
 */
const unsigned char SEGMENT_CODES[16] = {
    0x3f, // 0
    0x06, // 1
    0x5b, // 2
    0x4f, // 3
    0x66, // 4
    0x6d, // 5
    0x7d, // 6
    0x07, // 7
    0x7f, // 8
    0x6f, // 9
    0x77, // A
    0x7c, // B
    0x39, // C
    0x5e, // D
    0x79, // E
    0x71  // F
};
const int NUM_DIGITS = sizeof(SEGMENT_CODES) / sizeof(SEGMENT_CODES[0]);

/**
 * @brief Initializes GPIO pins for the shift register.
 * @return 0 on success, 1 on failure.
 */
int setupHardware() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        return 1;
    }

    pinMode(SDI_PIN, OUTPUT);
    pinMode(RCLK_PIN, OUTPUT);
    pinMode(SRCLK_PIN, OUTPUT);

    digitalWrite(SDI_PIN, 0);
    digitalWrite(RCLK_PIN, 0);
    digitalWrite(SRCLK_PIN, 0);
    
    return 0;
}

/**
 * @brief Sends a segment pattern to the 74HC595 shift register.
 * @param segmentData The 8-bit pattern for the 7-segment display.
 */
void displayDigit(unsigned char segmentData) {
    // Shift out the 8 bits of data (MSB first).
    for (int i = 0; i < 8; i++) {
        digitalWrite(SDI_PIN, (0x80 & (segmentData << i)) ? 1 : 0);
        // Pulse the shift register clock to shift the bit in.
        digitalWrite(SRCLK_PIN, 1);
        delayMicroseconds(1);
        digitalWrite(SRCLK_PIN, 0);
    }

    // Pulse the storage register clock to update the display output.
    digitalWrite(RCLK_PIN, 1);
    delayMicroseconds(1);
    digitalWrite(RCLK_PIN, 0);
}

/**
 * @brief Main application loop to cycle through digits 0-F.
 */
void cycleDigitsLoop() {
    while (1) {
        for (int i = 0; i < NUM_DIGITS; i++) {
            printf("Displaying '0x%X' on 7-segment display.\n", i);
            displayDigit(SEGMENT_CODES[i]);
            delay(DISPLAY_DELAY);
        }
    }
}

/**
 * @brief Main function.
 * @return Integer status code.
 */
int main(void) {
    if (setupHardware() != 0) {
        return 1; // Exit if hardware setup fails.
    }

    cycleDigitsLoop();

    return 0; // Unreachable.
}

