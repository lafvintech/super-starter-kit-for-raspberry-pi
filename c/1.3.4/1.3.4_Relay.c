#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h> // Required for exit()

// Define the GPIO pin connected to the relay module.
#define RELAY_PIN 0

// Define the interval for switching the relay state in milliseconds.
#define SWITCH_INTERVAL_MS 1000

/**
 * @brief Initializes wiringPi and configures the relay pin as an output.
 */
void setup_relay() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }
    pinMode(RELAY_PIN, OUTPUT);
}

/**
 * @brief Main application loop to toggle the relay.
 */
void relay_toggle_loop() {
    while (1) {
        // Close the relay circuit (often by pulling the pin LOW).
        // This might turn an external device (like an LED) ON.
        printf("Relay CLOSED (circuit complete).\n");
        digitalWrite(RELAY_PIN, LOW);
        delay(SWITCH_INTERVAL_MS);

        // Open the relay circuit (by pulling the pin HIGH).
        // This will turn the external device OFF.
        printf("Relay OPEN (circuit broken).\n");
        digitalWrite(RELAY_PIN, HIGH);
        delay(SWITCH_INTERVAL_MS);
    }
}

/**
 * @brief Main function.
 * @return Integer status code.
 */
int main(void) {
    setup_relay();
    relay_toggle_loop();
    return 0; // Unreachable code.
}
