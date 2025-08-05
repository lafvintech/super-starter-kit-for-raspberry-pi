/**
 * @file 1.3.5_LedBarGraph.c
 * @brief Simple LED Bar Graph Controller
 * @description Controls 10 LEDs with different animation patterns
 */

#include <wiringPi.h>
#include <stdio.h>
#include <signal.h>
#include <stdlib.h>

// --- Pin Configuration ---
const int led_pins[10] = {0, 1, 2, 3, 4, 5, 6, 8, 9, 10};

/**
 * @brief Initialize LED pins and turn them off
 */
void setup_leds() {
    printf("Setting up LED bar graph...\n");
    
    for (int i = 0; i < 10; i++) {
        pinMode(led_pins[i], OUTPUT);
        digitalWrite(led_pins[i], HIGH);  // Turn off LEDs (common anode)
    }
    
    printf("✅ Ready!\n\n");
}

/**
 * @brief Light odd LEDs (positions 0,2,4,6,8)
 */
void light_odd_leds() {
    printf("🔸 Odd pattern\n");
    for (int i = 0; i < 10; i += 2) {
        digitalWrite(led_pins[i], LOW);   // Turn ON
        delay(300);
        digitalWrite(led_pins[i], HIGH);  // Turn OFF
    }
}

/**
 * @brief Light even LEDs (positions 1,3,5,7,9)
 */
void light_even_leds() {
    printf("🔹 Even pattern\n");
    for (int i = 1; i < 10; i += 2) {
        digitalWrite(led_pins[i], LOW);   // Turn ON
        delay(300);
        digitalWrite(led_pins[i], HIGH);  // Turn OFF
    }
}

/**
 * @brief Light all LEDs in sequence
 */
void light_all_leds() {
    printf("🔸 All LEDs\n");
    for (int i = 0; i < 10; i++) {
        digitalWrite(led_pins[i], LOW);   // Turn ON
        delay(300);
        digitalWrite(led_pins[i], HIGH);  // Turn OFF
    }
}

/**
 * @brief Clean up and exit when Ctrl+C is pressed
 */
void cleanup_exit(int sig) {
    printf("\n🧹 Turning off LEDs...\n");
    for (int i = 0; i < 10; i++) {
        digitalWrite(led_pins[i], HIGH);  // Turn OFF all LEDs
    }
    printf("✅ Goodbye!\n");
    exit(0);
}

/**
 * @brief Main function
 */
int main(void) {
    // Handle Ctrl+C
    signal(SIGINT, cleanup_exit);
    
    printf("=== LED Bar Graph Controller ===\n");
    printf("Press Ctrl+C to exit\n\n");
    
    // Initialize wiringPi
    if (wiringPiSetup() == -1) {
        printf("❌ Setup failed!\n");
        return 1;
    }
    
    // Setup LEDs
    setup_leds();
    
    // Main loop
    while (1) {
        light_odd_leds();
        delay(300);
        
        light_even_leds();
        delay(300);
        
        light_all_leds();
        delay(300);
        
        printf("--- Cycle complete ---\n\n");
    }
    
    return 0;
}