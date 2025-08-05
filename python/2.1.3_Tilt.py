#!/usr/bin/env python3
"""
Tilt Switch Sensor Control - Python version matching C implementation

This implementation replicates the C code's features:
1. Polling method instead of interrupt for better control
2. LED color enumeration for type-safe control
3. Debounce mechanism to prevent false triggers
4. State change detection to reduce unnecessary updates
5. Professional function naming and structure
"""

import RPi.GPIO as GPIO
import time
import sys
from enum import Enum

# Define GPIO pins (C wiringPi pins mapped to BOARD pins)
# C: TILT_SWITCH_PIN 0 -> BOARD pin 11 (BCM GPIO 17)
# C: LED_GREEN_PIN   2 -> BOARD pin 13 (BCM GPIO 27) 
# C: LED_RED_PIN     3 -> BOARD pin 15 (BCM GPIO 22)
TILT_SWITCH_PIN = 11
LED_GREEN_PIN = 13
LED_RED_PIN = 15

# Define an enumeration for LED colors for type-safe control (matching C code)
class LedColor(Enum):
    OFF = 0
    GREEN = 1
    RED = 2

def set_led_color(color):
    """
    Controls the state of the dual-color LED.
    Parameters: color - The desired color (LedColor.OFF, GREEN, or RED)
    """
    if color == LedColor.GREEN:
        GPIO.output(LED_GREEN_PIN, GPIO.HIGH)
        GPIO.output(LED_RED_PIN, GPIO.LOW)
    elif color == LedColor.RED:
        GPIO.output(LED_GREEN_PIN, GPIO.LOW) 
        GPIO.output(LED_RED_PIN, GPIO.HIGH)
    else:  # LedColor.OFF or default
        GPIO.output(LED_GREEN_PIN, GPIO.LOW)
        GPIO.output(LED_RED_PIN, GPIO.LOW)

def setup_hardware():
    """
    Initializes GPIO and configures pins.
    Returns: 0 on success, 1 on failure.
    """
    try:
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Set up the tilt switch pin as an input
        # Assumes an external pull-up or pull-down resistor is part of the module
        GPIO.setup(TILT_SWITCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Set up LED pins as outputs
        GPIO.setup(LED_GREEN_PIN, GPIO.OUT)
        GPIO.setup(LED_RED_PIN, GPIO.OUT)
        
        # Start with the green LED on to indicate normal state
        set_led_color(LedColor.GREEN)
        
        print("Tilt switch hardware setup successful!")
        print(f"Tilt switch pin: {TILT_SWITCH_PIN}")
        print(f"Green LED pin: {LED_GREEN_PIN}")
        print(f"Red LED pin: {LED_RED_PIN}")
        print("Initial state: GREEN (Device upright)")
        print("-" * 50)
        return 0
        
    except Exception as e:
        print(f"Failed to setup hardware: {e}")
        return 1

def poll_tilt_loop():
    """
    Main loop to poll the tilt switch and update the LED.
    This function runs indefinitely until interrupted.
    """
    try:
        last_tilt_state = -1  # Use -1 to force an initial update
        
        while True:
            current_tilt_state = GPIO.input(TILT_SWITCH_PIN)
            
            # Simple debounce: check the pin state twice with a small delay
            # to ensure it wasn't a momentary flicker (matching C code)
            time.sleep(0.01)  # 10ms delay
            if GPIO.input(TILT_SWITCH_PIN) != current_tilt_state:
                continue  # State changed during delay, skip this reading
            
            # Only update the LED and print message if the state has changed
            if current_tilt_state != last_tilt_state:
                if current_tilt_state == GPIO.LOW:
                    # A LOW signal typically indicates the sensor is tilted
                    print("Device is TILTED!")
                    set_led_color(LedColor.RED)
                else:
                    # A HIGH signal indicates the sensor is upright
                    print("Device is UPRIGHT.")
                    set_led_color(LedColor.GREEN)
                    
                last_tilt_state = current_tilt_state
            
            # A longer delay to prevent busy-waiting (matching C code)
            time.sleep(0.05)  # 50ms delay
            
    except KeyboardInterrupt:
        print("\nTilt switch polling interrupted by user")
        raise  # Re-raise to be handled by main()

def destroy():
    """
    Clean up function for GPIO resources.
    Ensures LEDs are turned off and GPIO is properly cleaned up.
    """
    try:
        # Turn off both LEDs
        set_led_color(LedColor.OFF)
        GPIO.cleanup()
        print("LEDs turned off and GPIO cleaned up")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """
    Main function - matches C code structure.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    print("Tilt Switch Sensor Control")
    print("Monitoring tilt state with dual-color LED indicator")
    print("GREEN = Device upright, RED = Device tilted")
    print("Press Ctrl+C to stop...")
    print("=" * 50)
    
    # Initialize the hardware
    if setup_hardware() != 0:
        return 1  # Exit if setup fails
    
    try:
        # Start the main polling loop
        poll_tilt_loop()
        
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

