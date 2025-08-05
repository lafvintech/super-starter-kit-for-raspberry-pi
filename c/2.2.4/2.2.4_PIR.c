#include <wiringPi.h>
#include <softPwm.h>
#include <stdio.h>
#include <stdlib.h> // Required for exit()

// --- Pin Definitions ---
#define PIR_SENSOR_PIN  0 // GPIO pin for the PIR motion sensor.
#define LED_RED_PIN     1
#define LED_GREEN_PIN   2
#define LED_BLUE_PIN    3

// PWM range for the LED (0-255 is a common choice).
#define PWM_RANGE 255

/**
 * @brief Sets the color of the RGB LED using software PWM.
 * @param red   Red intensity (0-255).
 * @param green Green intensity (0-255).
 * @param blue  Blue intensity (0-255).
 */
void set_led_color(int red, int green, int blue) {
    softPwmWrite(LED_RED_PIN, red);
    softPwmWrite(LED_GREEN_PIN, green);
    softPwmWrite(LED_BLUE_PIN, blue);
}

/**
 * @brief Initializes wiringPi, sensor pin, and software PWM for the LED.
 */
void setup_hardware() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }
    
    // Set up PIR sensor pin as input.
    pinMode(PIR_SENSOR_PIN, INPUT);
    
    // Create software PWM pins for the RGB LED.
    softPwmCreate(LED_RED_PIN,   0, PWM_RANGE);
    softPwmCreate(LED_GREEN_PIN, 0, PWM_RANGE);
    softPwmCreate(LED_BLUE_PIN,  0, PWM_RANGE);
}

/**
 * @brief Main loop to check for motion and update the LED accordingly.
 */
void motion_detection_loop() {
    int motion_detected_state = 0; // 0 for no motion, 1 for motion.
    
    printf("PIR motion sensor ready. Waiting for motion...\n");
    // Initially set the LED to blue (no motion).
    set_led_color(0, 0, 255); 

    while (1) {
        int current_pir_state = digitalRead(PIR_SENSOR_PIN);
        
        // Check if the state has changed.
        if (current_pir_state != motion_detected_state) {
            motion_detected_state = current_pir_state;
            
            if (motion_detected_state == HIGH) {
                // Motion detected.
                printf("Motion DETECTED! LED is now yellow.\n");
                set_led_color(255, 255, 0); // Yellow
            } else {
                // Motion has stopped.
                printf("No motion. LED is now blue.\n");
                set_led_color(0, 0, 255); // Blue
            }
        }
        
        delay(100); // Poll every 100ms.
    }
}

/**
 * @brief Main function.
 * @return Integer status code.
 */
int main(void) {
    setup_hardware();
    motion_detection_loop();
    return 0; // Unreachable.
}
