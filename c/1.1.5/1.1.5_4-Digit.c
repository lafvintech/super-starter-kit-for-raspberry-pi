#include <wiringPi.h>
#include <stdio.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h> // For exit()

// Pin definitions for the 74HC595 shift register
#define SDI_PIN   5   // Serial Data Input (DS)
#define RCLK_PIN  4   // Storage Register Clock (STCP)
#define SRCLK_PIN 1   // Shift Register Clock (SHCP)

// Pins for selecting one of the four digits on the 4-digit display
const int DIGIT_PINS[] = {12, 3, 2, 0};
const int NUM_OF_DIGITS = sizeof(DIGIT_PINS) / sizeof(DIGIT_PINS[0]);

// Common-anode 7-segment display codes for digits 0-9
const unsigned char SEGMENT_CODES[] = {0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f};

// Volatile counter updated by the timer interrupt
volatile int counter = 0;

/**
 * @brief Sends a byte to the 74HC595 shift register.
 * @param data The 8-bit data to send.
 */
void writeToShiftRegister(unsigned char data) {
    for (int i = 0; i < 8; i++) {
        digitalWrite(SDI_PIN, (0x80 & (data << i)) ? 1 : 0);
        digitalWrite(SRCLK_PIN, 1);
        delayMicroseconds(1);
        digitalWrite(SRCLK_PIN, 0);
    }
    digitalWrite(RCLK_PIN, 1);
    delayMicroseconds(1);
    digitalWrite(RCLK_PIN, 0);
}

/**
 * @brief Selects which of the 4 digits to activate.
 * @param digitIndex The index of the digit to activate (0-3).
 */
void selectDigit(int digitIndex) {
    // Deactivate all digits first
    for (int i = 0; i < NUM_OF_DIGITS; i++) {
        digitalWrite(DIGIT_PINS[i], HIGH);
    }
    // Activate the selected digit by setting its pin to LOW
    if (digitIndex >= 0 && digitIndex < NUM_OF_DIGITS) {
        digitalWrite(DIGIT_PINS[digitIndex], LOW);
    }
}

/**
 * @brief Displays a single number on a single digit.
 * This function is called rapidly for each digit to create the illusion of a solid number.
 */
void displayNumber() {
    int digits[NUM_OF_DIGITS];
    int tempCounter = counter;

    // Extract each digit from the counter
    digits[0] = tempCounter % 10;
    digits[1] = (tempCounter / 10) % 10;
    digits[2] = (tempCounter / 100) % 10;
    digits[3] = (tempCounter / 1000) % 10;

    // Rapidly cycle through each digit, displaying its corresponding number
    for (int i = 0; i < NUM_OF_DIGITS; i++) {
        writeToShiftRegister(0x00); // Clear display before switching digits to prevent ghosting
        selectDigit(i);
        writeToShiftRegister(SEGMENT_CODES[digits[i]]);
        delay(1); // Small delay for persistence of vision (POV)
    }
}

/**
 * @brief Signal handler for the timer. Increments the counter every second.
 * @param signum The signal number.
 */
void timerHandler(int signum) {
    if (signum == SIGALRM) {
        counter++;
        printf("Counter: %d\n", counter);
        alarm(1); // Reschedule the alarm for 1 second later
    }
}

/**
 * @brief Initializes hardware, sets up GPIOs and the timer interrupt.
 */
void setup() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }

    // Setup shift register pins
    pinMode(SDI_PIN, OUTPUT);
    pinMode(RCLK_PIN, OUTPUT);
    pinMode(SRCLK_PIN, OUTPUT);

    // Setup digit selection pins
    for (int i = 0; i < NUM_OF_DIGITS; i++) {
        pinMode(DIGIT_PINS[i], OUTPUT);
        digitalWrite(DIGIT_PINS[i], HIGH); // Deactivate all digits initially
    }

    // Setup the timer interrupt
    signal(SIGALRM, timerHandler);
    alarm(1); // Trigger the first alarm after 1 second
}

/**
 * @brief Main function.
 */
int main(void) {
    setup();

    // Main loop for display multiplexing
    while (1) {
        displayNumber();
    }

    return 0; // Unreachable
}
