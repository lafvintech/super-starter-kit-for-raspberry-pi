/**
 * @file 3.1.2_TrafficLight.c
 * @brief Simple Traffic Light Controller with 4-Digit Display
 * @description Controls a traffic light system with countdown timer display
 */

#include <wiringPi.h>
#include <stdio.h>
#include <wiringShift.h>
#include <signal.h>
#include <unistd.h>
#include <stdlib.h>

// --- 74HC595 Shift Register Pins ---
#define SDI     5   // Serial Data Input
#define RCLK    4   // Register Clock (Latch)
#define SRCLK   1   // Shift Register Clock

// --- Pin Configuration ---
const int traffic_lights[3] = {6, 10, 11};  // Red, Green, Yellow LEDs
const int digit_pins[4] = {12, 3, 2, 0};    // 4-digit display control pins

// --- 7-Segment Display Patterns (0-9) ---
const unsigned char digit_patterns[10] = {
    0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f
};

// --- Traffic Light Timing (seconds) ---
const int light_duration[3] = {60, 30, 5};  // Red, Green, Yellow
const char* light_names[3] = {"Red", "Green", "Yellow"};

// --- Global Variables ---
int current_light = 0;    // 0=Red, 1=Green, 2=Yellow
int countdown = 60;       // Current countdown value
int display_digit = 0;    // Current digit being displayed (0-3)

/**
 * @brief Initialize all pins
 */
void setup_hardware() {
    printf("Setting up traffic light system...\n");
    
    // Setup shift register pins
    pinMode(SDI, OUTPUT);
    pinMode(RCLK, OUTPUT);
    pinMode(SRCLK, OUTPUT);
    
    // Setup digit display pins (HIGH = off)
    for (int i = 0; i < 4; i++) {
        pinMode(digit_pins[i], OUTPUT);
        digitalWrite(digit_pins[i], HIGH);
    }
    
    // Setup traffic light LEDs (HIGH = off)
    for (int i = 0; i < 3; i++) {
        pinMode(traffic_lights[i], OUTPUT);
        digitalWrite(traffic_lights[i], HIGH);
    }
    
    printf("✅ Hardware ready!\n");
}

/**
 * @brief Send data to 74HC595 shift register
 * @param data 8-bit data to send
 */
void send_to_display(unsigned char data) {
    // Send 8 bits to shift register
    for (int i = 0; i < 8; i++) {
        digitalWrite(SDI, (data << i) & 0x80);
        digitalWrite(SRCLK, HIGH);
        delayMicroseconds(1);
        digitalWrite(SRCLK, LOW);
    }
    
    // Latch the data to output
    digitalWrite(RCLK, HIGH);
    delayMicroseconds(1);
    digitalWrite(RCLK, LOW);
}

/**
 * @brief Clear the display
 */
void clear_display() {
    send_to_display(0x00);  // Send blank pattern
}

/**
 * @brief Select which digit to display on
 * @param digit Digit position (0-3)
 */
void select_digit(int digit) {
    // Turn off all digits first
    for (int i = 0; i < 4; i++) {
        digitalWrite(digit_pins[i], HIGH);
    }
    // Turn on selected digit
    digitalWrite(digit_pins[digit], LOW);
}

/**
 * @brief Display the countdown number (multiplexed)
 */
void update_display() {
    // Extract all digits
    int digits[4];
    digits[3] = countdown / 1000;           // Thousands
    digits[2] = (countdown / 100) % 10;     // Hundreds  
    digits[1] = (countdown / 10) % 10;      // Tens
    digits[0] = countdown % 10;             // Ones
    
    // Clear display first
    clear_display();
    
    // Select current digit
    select_digit(display_digit);
    
    // Display the digit (skip leading zeros except for ones place)
    if (display_digit == 0 || countdown >= (display_digit == 1 ? 10 : display_digit == 2 ? 100 : 1000)) {
        send_to_display(digit_patterns[digits[display_digit]]);
    }
    
    // Move to next digit
    display_digit = (display_digit + 1) % 4;
}

/**
 * @brief Control traffic lights (turn off all except current)
 */
void update_traffic_lights() {
    // Turn off all lights first
    for (int i = 0; i < 3; i++) {
        digitalWrite(traffic_lights[i], HIGH);
    }
    // Turn on current light
    digitalWrite(traffic_lights[current_light], LOW);
}

/**
 * @brief Timer interrupt handler (called every second)
 */
void timer_handler(int sig) {
    if (sig == SIGALRM) {
        countdown--;
        
        // Print status
        printf("⏰ %s Light: %d seconds remaining\n", 
               light_names[current_light], countdown);
        
        // Check if time is up
        if (countdown == 0) {
            // Move to next light
            current_light = (current_light + 1) % 3;
            countdown = light_duration[current_light];
            
            printf("🚦 Switching to %s light\n", light_names[current_light]);
        }
        
        // Set next alarm
        alarm(1);
    }
}

/**
 * @brief Main display loop
 */
void run_traffic_system() {
    printf("🚦 Traffic light system running...\n");
    printf("Press Ctrl+C to exit\n\n");
    
    while (1) {
        update_display();
        update_traffic_lights();
        delay(5);  // 5ms delay for proper display multiplexing
    }
}

/**
 * @brief Clean up and exit
 */
void cleanup_exit(int sig) {
    printf("\n🧹 Shutting down traffic light system...\n");
    
    // Turn off all lights
    for (int i = 0; i < 3; i++) {
        digitalWrite(traffic_lights[i], HIGH);
    }
    
    // Clear display
    clear_display();
    for (int i = 0; i < 4; i++) {
        digitalWrite(digit_pins[i], HIGH);
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
    
    printf("=== Traffic Light Controller ===\n");
    
    // Initialize wiringPi
    if (wiringPiSetup() == -1) {
        printf("❌ Setup failed!\n");
        return 1;
    }
    
    // Setup hardware
    setup_hardware();
    
    // Setup timer (1 second intervals)
    signal(SIGALRM, timer_handler);
    alarm(1);
    
    // Start the traffic system
    run_traffic_system();
    
    return 0;
}
