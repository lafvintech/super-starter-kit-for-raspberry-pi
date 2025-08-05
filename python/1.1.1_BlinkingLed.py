#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Define the GPIO pin used for the LED
LedPin = 17

# Define the blinking interval in seconds
BLINK_DELAY = 0.5

def setupHardware():
    """
    Initializes RPi.GPIO and configures the LED pin.
    Returns: 0 on success, 1 on failure.
    """
    try:
        # Set the GPIO modes to BCM Numbering
        GPIO.setmode(GPIO.BCM)
        # Disable GPIO warnings
        GPIO.setwarnings(False)
        # Set LedPin's mode to output, and initial level to High(3.3v)
        GPIO.setup(LedPin, GPIO.OUT, initial=GPIO.HIGH)
        print("GPIO setup successful!")
        return 0
    except Exception as e:
        # Print an error message if initialization fails
        print(f"Failed to setup GPIO: {e}")
        return 1

def blinkLoop():
    """
    The main application loop to blink the LED.
    """
    while True:
        # Turn the LED on
        # A LOW signal is used, which is common for LEDs connected to VCC
        GPIO.output(LedPin, GPIO.LOW)
        print("LED is ON")
        time.sleep(BLINK_DELAY)
        
        # Turn the LED off
        GPIO.output(LedPin, GPIO.HIGH)
        print("LED is OFF")
        time.sleep(BLINK_DELAY)

def destroy():
    """
    Clean up function for GPIO resources.
    """
    # Turn off LED
    GPIO.output(LedPin, GPIO.HIGH)
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
        # Start the LED blinking loop
        blinkLoop()
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