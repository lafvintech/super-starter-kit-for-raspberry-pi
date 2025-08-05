#!/usr/bin/env python3

import RPi.GPIO as GPIO  # Library for GPIO control on Raspberry Pi
import time             # Library for time delays
import signal           # Library for handling system signals
import sys              # Library for system operations

# Define GPIO pin numbers (using BCM numbering scheme)
# These correspond to the same physical pins as the C version:
# C version: LedPin 0 (WiringPi) = BCM GPIO 17 (Physical pin 11)
# C version: ButtonPin 1 (WiringPi) = BCM GPIO 18 (Physical pin 12)
LED_PIN = 17            # LED connected to GPIO 17 (Physical pin 11, WiringPi pin 0)
BUTTON_PIN = 18         # Button connected to GPIO 18 (Physical pin 12, WiringPi pin 1)

# Define logic states for better readability
LED_ON = GPIO.LOW       # LED turns on when GPIO outputs LOW
LED_OFF = GPIO.HIGH     # LED turns off when GPIO outputs HIGH
BUTTON_PRESSED = GPIO.LOW    # Button reads LOW when pressed (pull-up resistor)
BUTTON_RELEASED = GPIO.HIGH  # Button reads HIGH when released

def cleanup_and_exit(signal_num, frame):
    """
    Signal handler for graceful shutdown
    This function is called when Ctrl+C is pressed
    """
    print("\nShutting down gracefully...")
    GPIO.cleanup()  # Clean up GPIO settings
    sys.exit(0)

def setup_gpio():
    """
    Initialize and configure GPIO pins
    Returns True if successful, False otherwise
    """
    try:
        # Set GPIO numbering mode to BCM
        GPIO.setmode(GPIO.BCM)
        
        # Disable GPIO warnings
        GPIO.setwarnings(False)
        
        # Configure GPIO pins
        GPIO.setup(LED_PIN, GPIO.OUT)          # Set LED pin as output
        GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set button pin as input with pull-up
        
        # Set initial state: LED off
        GPIO.output(LED_PIN, LED_OFF)
        
        return True
        
    except Exception as e:
        print(f"Error: Failed to initialize GPIO! {e}")
        print("Make sure you are running with proper permissions (sudo).")
        return False

def main():
    """
    Main function - entry point of the program
    """
    print("Starting Button Control LED Demo (Python Version)...")
    
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, cleanup_and_exit)
    
    # Initialize GPIO
    if not setup_gpio():
        return 1
    
    print("GPIO initialized successfully.")
    print(f"LED pin (GPIO {LED_PIN}) configured as OUTPUT, Button pin (GPIO {BUTTON_PIN}) configured as INPUT with pull-up.")
    print("Hardware should match C version: LED on Physical pin 11, Button on Physical pin 12")
    print("Press the button to control the LED. Press Ctrl+C to exit.\n")
    
    # Variable to track previous button state for change detection
    previous_button_state = BUTTON_RELEASED  # Assume button starts released
    
    try:
        # Main control loop - runs continuously
        while True:
            # Read the current state of the button
            current_button_state = GPIO.input(BUTTON_PIN)
            
            # Only act when button state changes (avoid continuous printing)
            if current_button_state != previous_button_state:
                
                if current_button_state == BUTTON_PRESSED:
                    # Turn on the LED when button is pressed
                    GPIO.output(LED_PIN, LED_ON)
                    print("Button pressed - LED ON")
                else:
                    # Turn off the LED when button is released
                    GPIO.output(LED_PIN, LED_OFF)
                    print("Button released - LED OFF")
                
                # Update previous state for next comparison
                previous_button_state = current_button_state
            
            # Small delay to prevent excessive CPU usage and debounce button
            time.sleep(0.05)  # 50ms delay (reduced for better responsiveness)
            
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        cleanup_and_exit(None, None)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        GPIO.cleanup()
        return 1

if __name__ == "__main__":
    # Run the main function when script is executed directly
    exit_code = main()
    sys.exit(exit_code if exit_code else 0)