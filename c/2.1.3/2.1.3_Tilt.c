#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h>
#include <signal.h>

// Define GPIO pins.
#define TILT_SWITCH_PIN 0
#define LED_GREEN_PIN   2
#define LED_RED_PIN     3

// Define an enumeration for LED colors for type-safe control.
typedef enum {
    OFF,
    GREEN,
    RED
} LedColor;

volatile int running = 1;

void signal_handler(int sig) {
    running = 0;
}

/**
 * @brief Controls the state of the dual-color LED.
 * @param color The desired color (OFF, GREEN, or RED).
 */
void set_led_color(LedColor color) {
    switch (color) {
        case GREEN:
            digitalWrite(LED_GREEN_PIN, HIGH);
            digitalWrite(LED_RED_PIN, LOW);
            break;
        case RED:
            digitalWrite(LED_GREEN_PIN, LOW);
            digitalWrite(LED_RED_PIN, HIGH);
            break;
        case OFF:
        default:
            digitalWrite(LED_GREEN_PIN, LOW);
            digitalWrite(LED_RED_PIN, LOW);
            break;
    }
}

/**
 * @brief Initializes wiringPi and configures GPIO pins.
 */
void setup_hardware() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }
    
    // Set up the tilt switch pin as an input with pull-up resistor
    pinMode(TILT_SWITCH_PIN, INPUT);
    pullUpDnControl(TILT_SWITCH_PIN, PUD_UP);  // 🔑 关键修复！
    
    // Set up LED pins as outputs.
    pinMode(LED_GREEN_PIN, OUTPUT);
    pinMode(LED_RED_PIN, OUTPUT);

    // Start with the green LED on to indicate normal state.
    set_led_color(GREEN);
    
    printf("Tilt switch hardware setup successful!\n");
    printf("Press Ctrl+C to stop...\n");
}

/**
 * @brief Main loop to poll the tilt switch and update the LED.
 */
void poll_tilt_loop() {
    int last_tilt_state = -1; // Use -1 to force an initial update.

    while (running) {
        int current_tilt_state = digitalRead(TILT_SWITCH_PIN);
        
        // Simple debounce: check the pin state twice with a small delay
        delay(10);
        if (digitalRead(TILT_SWITCH_PIN) != current_tilt_state) {
            continue; // State changed during delay, skip this reading.
        }

        // Only update the LED and print a message if the state has changed.
        if (current_tilt_state != last_tilt_state) {
            if (current_tilt_state == LOW) {
                printf("Device is TILTED!\n");
                set_led_color(RED);
            } else {
                printf("Device is UPRIGHT.\n");
                set_led_color(GREEN);
            }
            last_tilt_state = current_tilt_state;
        }
        
        delay(50);
    }
}

/**
 * @brief Clean up function
 */
void cleanup() {
    printf("\nCleaning up...\n");
    set_led_color(OFF);
    printf("LEDs turned off\n");
}

/**
 * @brief Main function.
 * @return Integer status code.
 */
int main(void) {
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);
    
    setup_hardware();
    poll_tilt_loop();
    cleanup();
    
    return 0;
}
