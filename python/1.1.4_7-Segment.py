#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Pin definitions for the 74HC595 shift register
SDI_PIN = 17     # Serial Data Input (DS)
RCLK_PIN = 18    # Storage Register Clock (STCP)  
SRCLK_PIN = 27   # Shift Register Clock (SHCP)

# Delay between displaying numbers in milliseconds
DISPLAY_DELAY = 0.5

# Common-anode 7-segment display codes for 0-F
# Segments are mapped as: g, f, e, d, c, b, a
# A low bit turns a segment ON
SEGMENT_CODES = [
    0x3f, # 0
    0x06, # 1
    0x5b, # 2
    0x4f, # 3
    0x66, # 4
    0x6d, # 5
    0x7d, # 6
    0x07, # 7
    0x7f, # 8
    0x6f, # 9
    0x77, # A
    0x7c, # B
    0x39, # C
    0x5e, # D
    0x79, # E
    0x71  # F
]

NUM_DIGITS = len(SEGMENT_CODES)

def setupHardware():
    """
    Initializes GPIO pins for the shift register.
    Returns: 0 on success, 1 on failure.
    """
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        GPIO.setup(SDI_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(RCLK_PIN, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(SRCLK_PIN, GPIO.OUT, initial=GPIO.LOW)
        
        print("GPIO setup successful!")
        return 0
        
    except Exception as e:
        print(f"Failed to setup GPIO: {e}")
        return 1

def displayDigit(segmentData):
    """
    Sends a segment pattern to the 74HC595 shift register.
    Parameters: segmentData - The 8-bit pattern for the 7-segment display.
    """
    # Shift out the 8 bits of data (MSB first)
    for i in range(8):
        GPIO.output(SDI_PIN, 0x80 & (segmentData << i))
        # Pulse the shift register clock to shift the bit in
        GPIO.output(SRCLK_PIN, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(SRCLK_PIN, GPIO.LOW)
    
    # Pulse the storage register clock to update the display output
    GPIO.output(RCLK_PIN, GPIO.HIGH)
    time.sleep(0.001)
    GPIO.output(RCLK_PIN, GPIO.LOW)

def cycleDigitsLoop():
    """
    Main application loop to cycle through digits 0-F.
    """
    while True:
        for i in range(NUM_DIGITS):
            print(f"Displaying '0x{i:X}' on 7-segment display.")
            displayDigit(SEGMENT_CODES[i])
            time.sleep(DISPLAY_DELAY)

def destroy():
    """
    Clean up function for GPIO resources.
    """
    GPIO.cleanup()
    print("GPIO cleanup completed")

def main():
    """
    Main function.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    # Initialize the hardware
    if setupHardware() != 0:
        return 1  # Exit if hardware setup fails
    
    try:
        # Start the digit cycling loop
        cycleDigitsLoop()
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