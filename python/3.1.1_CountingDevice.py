#!/usr/bin/env python3
"""
@file digital_counter_display.py
@brief 4-Digit Digital Counter with Sensor Input (Fixed Version)
@description This program creates a digital counter that increments when a sensor
             detects an object. The count is displayed on a 4-digit 7-segment display
             using a 74HC595 shift register for multiplexing.
@author Enhanced Python version - Fixed math issues only
"""

import RPi.GPIO as GPIO
import time
import signal
import sys
from threading import Event

# ========== PIN CONFIGURATION ==========
SENSOR_INPUT_PIN = 26        # Pin connected to the sensor (detects objects)

# 74HC595 Shift Register Control Pins (BCM numbering)
DATA_PIN = 24               # SDI - Serial Data Input to shift register
LATCH_PIN = 23              # RCLK - Register Clock (latch data to output)
CLOCK_PIN = 18              # SRCLK - Shift Register Clock

# 4-Digit Display Control Pins (BCM numbering)
DIGIT_CONTROL_PINS = [10, 22, 27, 17]  # Controls which digit is active
TOTAL_DIGITS = 4            # Number of digits in the display

# ========== 7-SEGMENT DISPLAY PATTERNS ==========
# Each number represents the LED segments to light up for digits 0-9
DIGIT_PATTERNS = [
    0x3F,  # 0: segments A,B,C,D,E,F
    0x06,  # 1: segments B,C
    0x5B,  # 2: segments A,B,D,E,G
    0x4F,  # 3: segments A,B,C,D,G
    0x66,  # 4: segments B,C,F,G
    0x6D,  # 5: segments A,C,D,F,G
    0x7D,  # 6: segments A,C,D,E,F,G
    0x07,  # 7: segments A,B,C
    0x7F,  # 8: segments A,B,C,D,E,F,G
    0x6F   # 9: segments A,B,C,D,F,G
]

# ========== GLOBAL VARIABLES ==========
object_count = 0                    # Counter for detected objects
program_active = Event()            # Event object to control program execution
program_active.set()               # Set the event (program is running)
previous_sensor_state = 1          # Previous state of sensor (for edge detection)

class DigitalCounterSystem:
    """Class to manage the 4-digit digital counter system"""
    
    def __init__(self):
        """Initialize the digital counter system"""
        self.setup_exit_handler()
        self.initialize_hardware()
        
    def setup_exit_handler(self):
        """Setup signal handler for graceful exit"""
        signal.signal(signal.SIGINT, self.handle_program_exit)
        print("🛡️  Press Ctrl+C to safely exit")
        
    def handle_program_exit(self, signum, frame):
        """Handle program exit (Ctrl+C)"""
        global object_count
        
        print("\n🛑 Ctrl+C pressed! Shutting down...")
        
        # Clear the display
        self.clear_all_segments()
        for pin in DIGIT_CONTROL_PINS:
            GPIO.output(pin, GPIO.HIGH)
            
        print("📺 Display cleared")
        print(f"📊 Final count: {object_count} objects detected")
        print("👋 Digital Counter program terminated!")
        
        program_active.clear()
        GPIO.cleanup()
        sys.exit(0)
        
    def initialize_hardware(self):
        """Initialize all GPIO pins and hardware components"""
        print("🔧 Initializing Digital Counter System...")
        
        try:
            # Set GPIO mode to BCM numbering
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Configure shift register control pins as outputs
            GPIO.setup(DATA_PIN, GPIO.OUT)      # Data line to shift register
            GPIO.setup(LATCH_PIN, GPIO.OUT)     # Latch pin to update display
            GPIO.setup(CLOCK_PIN, GPIO.OUT)     # Clock pin for shifting data
            print("✅ Shift register pins configured")
            
            # Configure digit control pins as outputs (for multiplexing)
            for pin in DIGIT_CONTROL_PINS:
                GPIO.setup(pin, GPIO.OUT)
                GPIO.output(pin, GPIO.HIGH)     # Start with all digits OFF
            print("✅ Display digit control pins configured")
            
            # Configure sensor pin as input
            GPIO.setup(SENSOR_INPUT_PIN, GPIO.IN)
            print("✅ Sensor input pin configured")
            
            print("🚀 Hardware initialization complete!\n")
            
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize hardware: {e}")
            sys.exit(1)
            
    def clear_all_segments(self):
        """
        Clear all segments on the display - EXACTLY like original
        """
        for i in range(8):
            GPIO.output(DATA_PIN, GPIO.LOW)  # Send 0
            GPIO.output(CLOCK_PIN, GPIO.HIGH)
            GPIO.output(CLOCK_PIN, GPIO.LOW)
        GPIO.output(LATCH_PIN, GPIO.HIGH)
        GPIO.output(LATCH_PIN, GPIO.LOW)
        
    def send_data_to_shift_register(self, data):
        """
        Send 8-bit data to the 74HC595 shift register - EXACTLY like original
        
        Args:
            data (int): The 8-bit pattern to send
        """
        for i in range(8):
            # 🔧 Keep original bit extraction method - it was working!
            GPIO.output(DATA_PIN, 0x80 & (data << i))
            GPIO.output(CLOCK_PIN, GPIO.HIGH)
            GPIO.output(CLOCK_PIN, GPIO.LOW)
        GPIO.output(LATCH_PIN, GPIO.HIGH)
        GPIO.output(LATCH_PIN, GPIO.LOW)
        
    def activate_digit_position(self, digit_number):
        """
        Activate a specific digit position - EXACTLY like original
        
        Args:
            digit_number (int): Which digit to activate (0=rightmost, 3=leftmost)
        """
        # Turn OFF all digits first
        for pin in DIGIT_CONTROL_PINS:
            GPIO.output(pin, GPIO.HIGH)
        # Turn ON the selected digit
        GPIO.output(DIGIT_CONTROL_PINS[digit_number], GPIO.LOW)
            
    def update_display_output(self):
        """
        Update the 4-digit display - EXACTLY like original but with FIXED MATH
        """
        global object_count
        
        # 🔧 FIX: Only fix the math errors, keep everything else the same
        self.clear_all_segments()
        self.activate_digit_position(0)
        self.send_data_to_shift_register(DIGIT_PATTERNS[object_count % 10])

        self.clear_all_segments()
        self.activate_digit_position(1)
        self.send_data_to_shift_register(DIGIT_PATTERNS[(object_count // 10) % 10])  # ✅ FIXED

        self.clear_all_segments()
        self.activate_digit_position(2)
        self.send_data_to_shift_register(DIGIT_PATTERNS[(object_count // 100) % 10])  # ✅ FIXED

        self.clear_all_segments()
        self.activate_digit_position(3)
        self.send_data_to_shift_register(DIGIT_PATTERNS[(object_count // 1000) % 10])  # ✅ FIXED
            
    def detect_sensor_changes(self):
        """
        Detect changes in sensor state and increment counter - EXACTLY like original
        """
        global object_count, previous_sensor_state
        
        current_sensor_state = GPIO.input(SENSOR_INPUT_PIN)
        
        # Check for falling edge (object detected)
        if (previous_sensor_state == 1) and (current_sensor_state == 0):
            object_count += 1  # Increment the counter
            
            # Print status to console
            print(f"🎯 Object detected! Count: {object_count}")
            
            # Prevent counter overflow (reset at 10000)
            if object_count >= 10000:
                object_count = 0
                print("🔄 Counter reset to 0")
                
        # Update previous state for next comparison
        previous_sensor_state = current_sensor_state
        
    def run_counter_program(self):
        """Main program execution loop - EXACTLY like original"""
        global previous_sensor_state
        
        print("🚀 Starting Digital Counter...")
        print(f"📊 Current count: {object_count}")
        print("👁️  Monitoring sensor for object detection...")
        print("💡 Press Ctrl+C to exit\n")
        
        # Initialize sensor state
        previous_sensor_state = GPIO.input(SENSOR_INPUT_PIN)
        
        # Main program loop - EXACTLY like original
        while program_active.is_set():
            try:
                # Update display
                self.update_display_output()
                
                # Check sensor
                self.detect_sensor_changes()
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(0.1)
                
    def display_startup_info(self):
        """Display startup information"""
        print("========================================")
        print("🔢 4-Digit Digital Counter System")
        print("========================================")
        print("📝 This program counts objects detected by a sensor")
        print("📺 Count is displayed on a 4-digit 7-segment display")
        print("⚡ Uses 74HC595 shift register for multiplexing")
        print("🐍 Python version - Fixed math only!")
        print(f"📍 Sensor pin: {SENSOR_INPUT_PIN} (BCM)")
        print(f"📍 Data pin: {DATA_PIN}, Latch: {LATCH_PIN}, Clock: {CLOCK_PIN}")
        print(f"📍 Digit pins: {DIGIT_CONTROL_PINS}\n")

def main():
    """Main function - Program entry point"""
    try:
        # Create and run the counter system
        counter = DigitalCounterSystem()
        counter.display_startup_info()
        counter.run_counter_program()
        
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        GPIO.cleanup()
        print("🧹 GPIO cleanup complete")

if __name__ == "__main__":
    main()
