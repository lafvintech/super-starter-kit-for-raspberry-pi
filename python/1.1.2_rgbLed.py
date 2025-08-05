#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Define GPIO pins for the RGB LED
LED_PIN_RED = 17
LED_PIN_GREEN = 18
LED_PIN_BLUE = 27

# Define PWM frequency
PWM_FREQ = 2000

# Define a structure to hold color values and names (using dictionary)
COLORS = [
    {"name": "Red",    "red": 0xff, "green": 0x00, "blue": 0x00},
    {"name": "Green",  "red": 0x00, "green": 0xff, "blue": 0x00},
    {"name": "Blue",   "red": 0x00, "green": 0x00, "blue": 0xff},
    {"name": "Yellow", "red": 0xff, "green": 0xff, "blue": 0x00},
    {"name": "Purple", "red": 0xff, "green": 0x00, "blue": 0xff},
    {"name": "Cyan",   "red": 0xc0, "green": 0xff, "blue": 0x3e}
]

NUM_COLORS = len(COLORS)

# Global PWM objects
p_R = None
p_G = None  
p_B = None

def setupHardware():
    """
    Initializes RPi.GPIO and sets up software PWM for RGB LED pins.
    Returns: 0 on success, 1 on failure.
    """
    global p_R, p_G, p_B
    
    try:
        # Set the GPIO modes to BCM Numbering
        GPIO.setmode(GPIO.BCM)
        # Disable GPIO warnings
        GPIO.setwarnings(False)
        
        # Set all LedPin's mode to output and initial level to High(3.3v)
        GPIO.setup(LED_PIN_RED, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(LED_PIN_GREEN, GPIO.OUT, initial=GPIO.HIGH)
        GPIO.setup(LED_PIN_BLUE, GPIO.OUT, initial=GPIO.HIGH)
        
        # Create software PWM on each of the RGB pins with frequency 2KHz
        p_R = GPIO.PWM(LED_PIN_RED, PWM_FREQ)
        p_G = GPIO.PWM(LED_PIN_GREEN, PWM_FREQ)
        p_B = GPIO.PWM(LED_PIN_BLUE, PWM_FREQ)
        
        # Set all begin with value 0
        p_R.start(0)
        p_G.start(0)
        p_B.start(0)
        
        print("GPIO setup successful!")
        return 0
        
    except Exception as e:
        print(f"Failed to setup GPIO: {e}")
        return 1

def MAP(x, in_min, in_max, out_min, out_max):
    """
    Define a MAP function for mapping values. Like from 0~255 to 0~100
    """
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def setLedColor(red, green, blue):
    """
    Sets the RGB LED to a specific color.
    Parameters:
        red   - The red intensity (0-255)
        green - The green intensity (0-255) 
        blue  - The blue intensity (0-255)
    """
    # Map color value from 0~255 to 0~100
    R_val = MAP(red, 0, 255, 0, 100)
    G_val = MAP(green, 0, 255, 0, 100)
    B_val = MAP(blue, 0, 255, 0, 100)
    
    # Change the colors - Assign the mapped duty cycle value to the corresponding PWM channel
    p_R.ChangeDutyCycle(R_val)
    p_G.ChangeDutyCycle(G_val)
    p_B.ChangeDutyCycle(B_val)
    
    print(f"color_msg: R_val = {R_val:.1f}, G_val = {G_val:.1f}, B_val = {B_val:.1f}")

def colorCycleLoop():
    """
    The main application loop to cycle through a predefined set of colors.
    """
    colorIndex = 0
    while True:
        # Get the current color from the array
        currentColor = COLORS[colorIndex]
        
        print(f"Displaying color: {currentColor['name']}")
        
        # Set the LED to the current color
        setLedColor(currentColor['red'], currentColor['green'], currentColor['blue'])
        
        # Wait for 500ms before changing to the next color
        time.sleep(0.5)
        
        # Move to the next color, and loop back to the start if at the end
        colorIndex = (colorIndex + 1) % NUM_COLORS

def destroy():
    """
    Clean up function for GPIO resources.
    """
    # Stop all pwm channel
    p_R.stop()
    p_G.stop()
    p_B.stop()
    # Release resource
    GPIO.cleanup()
    print("GPIO cleanup completed")

def main():
    """
    Main function.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    # Initialize the hardware
    if setupHardware() != 0:
        return 1  # Exit if setup fails
    
    try:
        # Start the color cycling loop
        colorCycleLoop()
    except KeyboardInterrupt:
        # When 'Ctrl+C' is pressed, the program destroy() will be executed
        print("\nProgram interrupted by user")
        destroy()
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        destroy()
        return 1

# If run this script directly, do:
if __name__ == '__main__':
    main()