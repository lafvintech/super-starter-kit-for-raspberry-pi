#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import threading

# Pin definitions for the 74HC595 shift register
SDI_PIN = 24     # Serial Data Input (DS)
RCLK_PIN = 23    # Storage Register Clock (STCP)
SRCLK_PIN = 18   # Shift Register Clock (SHCP)

# Pins for selecting one of the four digits on the 4-digit display
DIGIT_PINS = [10, 22, 27, 17]
NUM_OF_DIGITS = len(DIGIT_PINS)

# Common-anode 7-segment display codes for digits 0-9
SEGMENT_CODES = [0x3f, 0x06, 0x5b, 0x4f, 0x66, 0x6d, 0x7d, 0x07, 0x7f, 0x6f]

# Volatile counter updated by the timer interrupt
counter = 0
timer1 = None

def writeToShiftRegister(data):
    """
    Sends a byte to the 74HC595 shift register.
    Parameters: data - The 8-bit data to send.
    """
    for i in range(8):
        GPIO.output(SDI_PIN, 0x80 & (data << i))
        GPIO.output(SRCLK_PIN, GPIO.HIGH)
        time.sleep(0.0001)
        GPIO.output(SRCLK_PIN, GPIO.LOW)
    
    GPIO.output(RCLK_PIN, GPIO.HIGH)
    time.sleep(0.0001)
    GPIO.output(RCLK_PIN, GPIO.LOW)

def selectDigit(digitIndex):
    """
    Selects which of the 4 digits to activate.
    Parameters: digitIndex - The index of the digit to activate (0-3).
    """
    # Deactivate all digits first
    for i in range(NUM_OF_DIGITS):
        GPIO.output(DIGIT_PINS[i], GPIO.HIGH)
    
    # Activate the selected digit by setting its pin to LOW
    if 0 <= digitIndex < NUM_OF_DIGITS:
        GPIO.output(DIGIT_PINS[digitIndex], GPIO.LOW)

def displayNumber():
    """
    Displays a single number on a single digit.
    This function is called rapidly for each digit to create the illusion of a solid number.
    """
    digits = [0] * NUM_OF_DIGITS
    tempCounter = counter
    
    # Extract each digit from the counter
    digits[0] = tempCounter % 10
    digits[1] = (tempCounter // 10) % 10
    digits[2] = (tempCounter // 100) % 10
    digits[3] = (tempCounter // 1000) % 10
    
    # Rapidly cycle through each digit, displaying its corresponding number
    for i in range(NUM_OF_DIGITS):
        for j in range(NUM_OF_DIGITS):
            GPIO.output(DIGIT_PINS[j], GPIO.HIGH)
        
        writeToShiftRegister(SEGMENT_CODES[digits[i]])
        GPIO.output(DIGIT_PINS[i], GPIO.LOW)
        
        time.sleep(0.0025)

def timerHandler():
    """
    Timer handler function. Increments the counter every second.
    """
    global counter, timer1
    
    counter += 1
    print(f"Counter: {counter}")
    
    # Reschedule the timer for 1 second later
    timer1 = threading.Timer(1.0, timerHandler)
    timer1.start()

def setup():
    """
    Initializes hardware, sets up GPIOs and the timer interrupt.
    Returns: 0 on success, 1 on failure.
    """
    global timer1
    
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup shift register pins
        GPIO.setup(SDI_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RCLK_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(SRCLK_PIN, GPIO.OUT, initial=GPIO.LOW)
        
        # Setup digit selection pins
        for i in range(NUM_OF_DIGITS):
            GPIO.setup(DIGIT_PINS[i], GPIO.OUT, initial=GPIO.HIGH)  # Deactivate all digits initially
        
        # Setup the timer interrupt
        timer1 = threading.Timer(1.0, timerHandler)
        timer1.start()
        
        print("GPIO and timer setup successful!")
        return 0
        
    except Exception as e:
        print(f"Failed to setup hardware: {e}")
        return 1

def destroy():
    """
    Clean up function for GPIO resources and timer.
    """
    global timer1
    
    if timer1:
        timer1.cancel()  # Cancel the timer
    
    GPIO.cleanup()
    print("GPIO cleanup and timer cancelled")

def main():
    """
    Main function.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    # Initialize the hardware
    if setup() != 0:
        return 1  # Exit if setup fails
    
    try:
        # Main loop for display multiplexing
        while True:
            displayNumber()
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
    main()