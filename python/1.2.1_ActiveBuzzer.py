#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys

# Define the GPIO pin connected to the active buzzer
BUZZER_PIN = 17

# Define the duration for each beep state (on/off) in seconds
BEEP_INTERVAL_MS = 0.1

def setup_buzzer():
    """
    Initializes GPIO and configures the buzzer pin as an output.
    Returns: 0 on success, 1 on failure.
    """
    try:
        # Set the GPIO modes to BCM Numbering
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Set buzzer pin's mode to output with initial level High (3.3V)
        # HIGH = buzzer off, LOW = buzzer on for active buzzer modules
        GPIO.setup(BUZZER_PIN, GPIO.OUT, initial=GPIO.HIGH)
        
        print("Buzzer GPIO setup successful!")
        return 0
        
    except Exception as e:
        print(f"Failed to setup GPIO: {e}")
        return 1

def beep_loop():
    """
    Main application loop to make the buzzer beep intermittently.
    This function runs indefinitely until interrupted.
    """
    try:
        while True:
            # Turn the buzzer ON. A LOW signal is used, which is common
            # for modules connected between VCC and a GPIO pin.
            print("Buzzer ON")
            GPIO.output(BUZZER_PIN, GPIO.LOW)
            time.sleep(BEEP_INTERVAL_MS)

            # Turn the buzzer OFF.
            print("Buzzer OFF")
            GPIO.output(BUZZER_PIN, GPIO.HIGH)
            time.sleep(BEEP_INTERVAL_MS)
            
    except KeyboardInterrupt:
        print("\nBuzzer loop interrupted by user")
        raise  # Re-raise to be handled by main()

def destroy():
    """
    Clean up function for GPIO resources.
    Ensures buzzer is turned off and GPIO is properly cleaned up.
    """
    try:
        # Turn off buzzer
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
        # Release GPIO resources
        GPIO.cleanup()
        print("GPIO cleanup completed")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """
    Main function.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    # Initialize the buzzer GPIO
    if setup_buzzer() != 0:
        return 1  # Exit if setup fails
    
    try:
        # Start the main beeping loop
        beep_loop()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        destroy()
        return 0
        
    except Exception as e:
        print(f"An error occurred: {e}")
        destroy()
        return 1

# If run this script directly, do:
if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)