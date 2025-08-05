#include <wiringPi.h>
#include <stdio.h>

// Define the GPIO pin used for the LED.
#define LED_PIN 0

// Define the blinking interval in milliseconds.
#define BLINK_DELAY 500

/**
 * @brief Initializes wiringPi and configures the LED pin.
 * @return 0 on success, 1 on failure.
 */
int setupHardware() {
    // Attempt to initialize the wiringPi library.
    if (wiringPiSetup() == -1) {
        // Print an error message if initialization fails.
        printf("Failed to setup wiringPi!\n");
        return 1;
    }
    // Configure the LED pin as an output.
    pinMode(LED_PIN, OUTPUT);
    return 0;
}

/**
 * @brief The main application loop to blink the LED.
 */
void blinkLoop() {
    while (1) {
        // Turn the LED on.
        // A LOW signal is used, which is common for LEDs connected to VCC.
        digitalWrite(LED_PIN, LOW);
        printf("LED is ON\n");
        delay(BLINK_DELAY);

        // Turn the LED off.
        digitalWrite(LED_PIN, HIGH);
        printf("LED is OFF\n");
        delay(BLINK_DELAY);
    }
}

/**
 * @brief Main function.
 * @return Integer status code. 0 for success, 1 for error.
 */
int main(void) {
    // Initialize the hardware.
    if (setupHardware() != 0) {
        return 1; // Exit if setup fails.
    }
    
    // Start the LED blinking loop.
    blinkLoop();
    
    // This part of the code is unreachable because blinkLoop is an infinite loop,
    // but it's good practice to include a return statement in main.
    return 0;
}

