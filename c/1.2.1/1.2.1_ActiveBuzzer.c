#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h> // Required for exit()

// Define the GPIO pin connected to the active buzzer.
#define BUZZER_PIN 0

// Define the duration for each beep state (on/off) in milliseconds.
#define BEEP_INTERVAL_MS 100

/**
 * @brief Initializes wiringPi and configures the buzzer pin as an output.
 */
void setup_buzzer() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }
    pinMode(BUZZER_PIN, OUTPUT);
}

/**
 * @brief Main application loop to make the buzzer beep intermittently.
 */
void beep_loop() {
    while (1) {
        // Turn the buzzer ON. A LOW signal is used, which is common
        // for modules connected between VCC and a GPIO pin.
        printf("Buzzer ON\n");
        digitalWrite(BUZZER_PIN, LOW);
        delay(BEEP_INTERVAL_MS);

        // Turn the buzzer OFF.
        printf("Buzzer OFF\n");
        digitalWrite(BUZZER_PIN, HIGH);
        delay(BEEP_INTERVAL_MS);
    }
}

/**
 * @brief Main function.
 * @return Integer status code.
 */
int main(void) {
    setup_buzzer();
    beep_loop();
    return 0; // This code is unreachable.
}

