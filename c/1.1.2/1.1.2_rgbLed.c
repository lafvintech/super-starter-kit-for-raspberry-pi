#include <wiringPi.h>
#include <softPwm.h>
#include <stdio.h>

// Define GPIO pins for the RGB LED.
#define LED_PIN_RED    0
#define LED_PIN_GREEN  1
#define LED_PIN_BLUE   2

// Define PWM range for colors (0-255).
#define PWM_RANGE 255

// Define a structure to hold color values and names.
typedef struct {
    const char* name;
    unsigned char red;
    unsigned char green;
    unsigned char blue;
} Color;

// Array of colors to display in sequence.
const Color COLORS[] = {
    {"Red",    0xff, 0x00, 0x00},
    {"Green",  0x00, 0xff, 0x00},
    {"Blue",   0x00, 0x00, 0xff},
    {"Yellow", 0xff, 0xff, 0x00},
    {"Purple", 0xff, 0x00, 0xff},
    {"Cyan",   0xc0, 0xff, 0x3e}
};
const int NUM_COLORS = sizeof(COLORS) / sizeof(COLORS[0]);

/**
 * @brief Initializes wiringPi and sets up software PWM for RGB LED pins.
 * @return 0 on success, 1 on failure.
 */
int setupHardware() {
    // Attempt to initialize the wiringPi library.
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        return 1;
    }
    
    // Create software PWM on each of the RGB pins with a range of 0-255.
    softPwmCreate(LED_PIN_RED,   0, PWM_RANGE);
    softPwmCreate(LED_PIN_GREEN, 0, PWM_RANGE);
    softPwmCreate(LED_PIN_BLUE,  0, PWM_RANGE);
    
    return 0;
}

/**
 * @brief Sets the RGB LED to a specific color.
 * @param red   The red intensity (0-255).
 * @param green The green intensity (0-255).
 * @param blue  The blue intensity (0-255).
 */
void setLedColor(unsigned char red, unsigned char green, unsigned char blue) {
    softPwmWrite(LED_PIN_RED,   red);
    softPwmWrite(LED_PIN_GREEN, green);
    softPwmWrite(LED_PIN_BLUE,  blue);
}

/**
 * @brief The main application loop to cycle through a predefined set of colors.
 */
void colorCycleLoop() {
    int colorIndex = 0;
    while (1) {
        // Get the current color from the array.
        const Color* currentColor = &COLORS[colorIndex];

        printf("Displaying color: %s\n", currentColor->name);
        
        // Set the LED to the current color.
        setLedColor(currentColor->red, currentColor->green, currentColor->blue);
        
        // Wait for 500ms before changing to the next color.
        delay(500);

        // Move to the next color, and loop back to the start if at the end.
        colorIndex = (colorIndex + 1) % NUM_COLORS;
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
    
    // Start the color cycling loop.
    colorCycleLoop();
    
    return 0; // This is unreachable.
}
