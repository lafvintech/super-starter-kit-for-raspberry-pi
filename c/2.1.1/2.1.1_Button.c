#include <wiringPi.h>    // Library for GPIO control on Raspberry Pi
#include <stdio.h>       // Standard input/output library

// Define GPIO pin numbers (using WiringPi numbering scheme)
#define LED_PIN         0    // LED connected to WiringPi pin 0
#define BUTTON_PIN      1    // Button connected to WiringPi pin 1

// Define logic states for better readability
#define LED_ON          LOW   // LED turns on when GPIO outputs LOW
#define LED_OFF         HIGH  // LED turns off when GPIO outputs HIGH
#define BUTTON_PRESSED  0     // Button reads LOW when pressed (pull-up resistor)
#define BUTTON_RELEASED 1     // Button reads HIGH when released

int main(void)
{
    printf("Starting Button Control LED Demo...\n");
    
    // Initialize WiringPi library
    // This must be called before using any GPIO functions
    if(wiringPiSetup() == -1){
        printf("Error: Failed to initialize WiringPi library!\n");
        printf("Make sure you are running with proper permissions.\n");
        return 1; 
    }
    
    printf("WiringPi initialized successfully.\n");
    
    // Configure GPIO pins
    pinMode(LED_PIN, OUTPUT);       // Set LED pin as output
    pinMode(BUTTON_PIN, INPUT);     // Set button pin as input
    
    // Set initial state: LED off
    digitalWrite(LED_PIN, LED_OFF);
    printf("LED pin configured as OUTPUT, Button pin configured as INPUT.\n");
    printf("Press the button to control the LED. Press Ctrl+C to exit.\n\n");
    
    // Variable to track previous button state for change detection
    int previousButtonState = BUTTON_RELEASED;  // Assume button starts released
    
    // Main control loop - runs continuously
    while(1)
    {
        // Read the current state of the button
        int currentButtonState = digitalRead(BUTTON_PIN);
        
        // Only act when button state changes (avoid continuous printing)
        if(currentButtonState != previousButtonState)
        {
            if(currentButtonState == BUTTON_PRESSED)
            {
                // Turn on the LED when button is pressed
                digitalWrite(LED_PIN, LED_ON);
                printf("Button pressed - LED ON\n");
            }
            else
            {
                // Turn off the LED when button is released
                digitalWrite(LED_PIN, LED_OFF);
                printf("Button released - LED OFF\n");
            }
            
            // Update previous state for next comparison
            previousButtonState = currentButtonState;
        }
        
        // Small delay to prevent excessive CPU usage and debounce button
        delay(50);  // 50ms delay (reduced for better responsiveness)
    }
    
    // This code will never be reached due to infinite loop above
    // But it's good practice to include cleanup code
    return 0;
}

