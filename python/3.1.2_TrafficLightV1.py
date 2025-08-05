#!/usr/bin/env python3

"""
3.1.2_TrafficLight.py (Simple Version)

Traffic Light Controller with 4-Digit Display
Controls traffic lights with countdown timer using 74HC595 shift register.
"""

import RPi.GPIO as GPIO
import time
import threading
import signal
import sys

# Pin definitions for 74HC595 shift register
SDI = 24        # Serial data input
RCLK = 23       # Register clock (latch)
SRCLK = 18      # Shift register clock

# Pin arrays
digit_pins = [10, 22, 27, 17]      # 4-digit display control
led_pins = [25, 8, 7]              # Red, Green, Yellow LEDs

# 7-segment display patterns for digits 0-9
number_patterns = (0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f)

# Traffic light settings
light_duration = [60, 30, 5]       # Red, Green, Yellow times in seconds
light_names = ["Red", "Green", "Yellow"]

# Global state variables
current_light = 0                   # Current active light (0=Red, 1=Green, 2=Yellow)
countdown = 60                      # Countdown timer
display_digit = 0                   # Current digit being displayed (0-3)
timer_thread = None
running = True

def setup():
    """Initialize all GPIO pins."""
    print("Setting up traffic light system...")
    
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    
    # Setup shift register pins
    GPIO.setup(SDI, GPIO.OUT)
    GPIO.setup(RCLK, GPIO.OUT)
    GPIO.setup(SRCLK, GPIO.OUT)
    
    # Setup display digit pins (HIGH = off)
    for pin in digit_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
    
    # Setup LED pins (HIGH = off)
    for pin in led_pins:
        GPIO.setup(pin, GPIO.OUT)
        GPIO.output(pin, GPIO.HIGH)
    
    print("Hardware ready!")

def send_to_shift_register(data):
    """Send 8-bit data to 74HC595 shift register."""
    # Send 8 bits one by one
    for i in range(8):
        bit = (data << i) & 0x80
        GPIO.output(SDI, GPIO.HIGH if bit else GPIO.LOW)
        GPIO.output(SRCLK, GPIO.HIGH)
        GPIO.output(SRCLK, GPIO.LOW)
    
    # Latch data to output
    GPIO.output(RCLK, GPIO.HIGH)
    GPIO.output(RCLK, GPIO.LOW)

def clear_display():
    """Turn off all segments of the display."""
    send_to_shift_register(0x00)

def select_digit(digit):
    """Select which digit position to display on (0-3)."""
    # Turn off all digits
    for pin in digit_pins:
        GPIO.output(pin, GPIO.HIGH)
    # Turn on selected digit
    GPIO.output(digit_pins[digit], GPIO.LOW)

def update_display():
    """Update the 4-digit countdown display."""
    global display_digit
    
    # Extract digits: ones, tens, hundreds, thousands
    digits = [
        countdown % 10,
        (countdown // 10) % 10,
        (countdown // 100) % 10,
        (countdown // 1000) % 10
    ]
    
    clear_display()
    select_digit(display_digit)
    
    # Show digit if it's not a leading zero (except for ones place)
    if display_digit == 0 or countdown >= (10 ** display_digit):
        send_to_shift_register(number_patterns[digits[display_digit]])
    
    # Move to next digit
    display_digit = (display_digit + 1) % 4

def update_lights():
    """Control traffic lights - turn on current light, turn off others."""
    # Turn off all lights
    for pin in led_pins:
        GPIO.output(pin, GPIO.HIGH)
    # Turn on current light
    GPIO.output(led_pins[current_light], GPIO.LOW)

def timer_callback():
    """Called every second to update countdown and manage light changes."""
    global countdown, current_light, timer_thread, running
    
    if not running:
        return
    
    countdown -= 1
    print(f"{light_names[current_light]} Light: {countdown} seconds")
    
    # Check if time is up for current light
    if countdown == 0:
        # Switch to next light
        current_light = (current_light + 1) % 3
        countdown = light_duration[current_light]
        print(f"Switching to {light_names[current_light]} light")
    
    # Schedule next timer
    if running:
        timer_thread = threading.Timer(1.0, timer_callback)
        timer_thread.start()

def cleanup_and_exit(signal_num=None, frame=None):
    """Clean up GPIO and exit."""
    global running, timer_thread
    
    print("\nShutting down...")
    running = False
    
    # Cancel timer
    if timer_thread:
        timer_thread.cancel()
    
    # Turn off all LEDs and display
    for pin in led_pins:
        GPIO.output(pin, GPIO.HIGH)
    clear_display()
    for pin in digit_pins:
        GPIO.output(pin, GPIO.HIGH)
    
    GPIO.cleanup()
    print("Goodbye!")
    sys.exit(0)

def main_loop():
    """Main program loop - continuously update display and lights."""
    while running:
        update_display()
        update_lights()
        time.sleep(0.005)  # 5ms delay for display multiplexing

def main():
    """Main function."""
    global timer_thread
    
    print("=== Traffic Light Controller ===")
    print("Red: 60s, Green: 30s, Yellow: 5s")
    print("Press Ctrl+C to exit")
    
    # Setup signal handler for Ctrl+C
    signal.signal(signal.SIGINT, cleanup_and_exit)
    
    try:
        setup()
        
        # Start the countdown timer
        timer_thread = threading.Timer(1.0, timer_callback)
        timer_thread.start()
        
        # Run main display loop
        main_loop()
        
    except Exception as e:
        print(f"Error: {e}")
        cleanup_and_exit()

if __name__ == '__main__':
    main()