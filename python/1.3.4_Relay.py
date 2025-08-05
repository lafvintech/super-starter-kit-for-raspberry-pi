#!/usr/bin/env python3
"""
Relay Module Control - Python version matching C implementation

This implementation replicates the C code's features:
1. Professional function separation and naming
2. Clear relay state descriptions (CLOSED/OPEN)
3. Proper constant definitions
4. Enhanced error handling and status codes
"""

import RPi.GPIO as GPIO
import time
import sys

# Define the GPIO pin connected to the relay module
RELAY_PIN = 17

# Define the interval for switching the relay state in seconds
SWITCH_INTERVAL_MS = 1.0  # 1000ms converted to 1.0 seconds

def setup_relay():
    """
    Initializes GPIO and configures the relay pin as an output.
    Returns: 0 on success, 1 on failure.
    """
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configure relay pin as output with initial HIGH state
        # HIGH = relay open (circuit open), LOW = relay closed (circuit closed)
        GPIO.setup(RELAY_PIN, GPIO.OUT, initial=GPIO.HIGH)
        
        print("Relay module GPIO setup successful!")
        print(f"Relay pin: {RELAY_PIN}")
        print(f"Switch interval: {SWITCH_INTERVAL_MS} seconds")
        print("Initial state: Relay OPEN (external device OFF)")
        return 0
        
    except Exception as e:
        print(f"Failed to setup relay module: {e}")
        return 1

def relay_toggle_loop():
    """
    Main application loop to toggle the relay.
    This function runs indefinitely until interrupted.
    """
    try:
        cycle_count = 0
        
        while True:
            cycle_count += 1
            
            # Close the relay circuit (often by pulling the pin LOW)
            # This might turn an external device (like an LED) ON
            print(f"[Cycle {cycle_count}] Relay CLOSED (LED OFF)")
            GPIO.output(RELAY_PIN, GPIO.LOW)
            time.sleep(SWITCH_INTERVAL_MS)
            
            # Open the relay circuit (by pulling the pin HIGH)  
            # This will turn the external device OFF
            print(f"[Cycle {cycle_count}] Relay OPEN (LED ON)")
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            time.sleep(SWITCH_INTERVAL_MS)
            
    except KeyboardInterrupt:
        print("\nRelay toggle loop interrupted by user")
        raise  # Re-raise to be handled by main()

def destroy():
    """
    Clean up function for GPIO resources.
    Ensures relay is in safe state (OPEN) and GPIO is properly cleaned up.
    """
    try:
        # Ensure relay is in OPEN state (safe state)
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        GPIO.cleanup()
        print("Relay set to OPEN state and GPIO cleaned up")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """
    Main function - matches C code structure.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    print("Relay Module Control")
    print("Toggling relay state every 1 second")
    print("HIGH = Relay OPEN (external device OFF)")
    print("LOW = Relay CLOSED (external device ON)")
    print("Press Ctrl+C to stop...")
    print("-" * 50)
    
    # Initialize the relay module
    if setup_relay() != 0:
        return 1  # Exit if setup fails
    
    try:
        # Start the main relay toggle loop
        relay_toggle_loop()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        destroy()
        return 0
        
    except Exception as e:
        print(f"An error occurred: {e}")
        destroy()
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
