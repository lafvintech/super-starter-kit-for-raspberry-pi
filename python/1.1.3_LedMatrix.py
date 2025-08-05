#!/usr/bin/env python3
"""
@file led_matrix_animation.py
@brief LED Matrix Control Program using 74HC595 Shift Register - Python Version
@description This program creates animated patterns on an 8x8 LED matrix
             Hardware: Raspberry Pi + 74HC595 + 8x8 LED Matrix
@author Python version with RPi.GPIO library
"""

import RPi.GPIO as GPIO
import time
import signal
import sys
from threading import Event

# ========== PIN CONFIGURATION ==========
# Pin definitions for 74HC595 shift register (BCM numbering)
SDI_PIN = 17        # Serial Data Input (DS pin on 74HC595)
RCLK_PIN = 18       # Register Clock (ST_CP pin) - latches data to output
SRCLK_PIN = 27      # Shift Register Clock (SH_CP pin) - shifts data

# ========== TIMING CONFIGURATION ==========
DISPLAY_DELAY = 0.1     # Delay between pattern changes (seconds)
ARROW_DURATION = 1.0    # Duration for each arrow display (seconds)
STAGE_PAUSE = 0.2       # Pause between animation stages (seconds)
CLEAR_PAUSE = 0.1       # Pause after clearing display (seconds)

# ========== ANIMATION PATTERN DATA ==========
# Stage 1: Top-to-bottom scanning (8 frames)
scan_down_high = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]
scan_down_low  = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

# Stage 2: Left-to-right scanning (8 frames)  
scan_right_high = [0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff]
scan_right_low  = [0x7f, 0xbf, 0xdf, 0xef, 0xf7, 0xfb, 0xfd, 0xfe]

# Stage 3: Arrow patterns (4 directions)
# Row selection data (same for all arrows)
arrow_row_select = [0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80]

# Column data for different arrow directions
arrow_up_cols    = [0xe7, 0xc3, 0x81, 0x00, 0xe7, 0xe7, 0xe7, 0xe7]  # Arrow pointing UP ↑
arrow_right_cols = [0xef, 0xcf, 0x8f, 0x00, 0x00, 0x8f, 0xcf, 0xef]  # Arrow pointing RIGHT →
arrow_down_cols  = [0xe7, 0xe7, 0xe7, 0xe7, 0x00, 0x81, 0xc3, 0xe7]  # Arrow pointing DOWN ↓
arrow_left_cols  = [0xf7, 0xf3, 0xf1, 0x00, 0x00, 0xf1, 0xf3, 0xf7]  # Arrow pointing LEFT ←

# ========== GLOBAL VARIABLES ==========
program_running = Event()
program_running.set()

class LEDMatrixController:
    """Class to control 8x8 LED Matrix using 74HC595 shift register"""
    
    def __init__(self):
        """Initialize the LED Matrix controller"""
        self.setup_exit_handler()
        self.initialize_gpio()
        
    def setup_exit_handler(self):
        """Setup signal handler for graceful exit"""
        signal.signal(signal.SIGINT, self.handle_program_exit)
        print("🛡️  Press Ctrl+C to safely exit")
        
    def handle_program_exit(self, signum, frame):
        """Handle program exit (Ctrl+C)"""
        print("\n🛑 Ctrl+C pressed! Shutting down...")
        
        # Clear the display
        self.clear_display()
        print("📺 Display cleared")
        print("👋 LED Matrix Animation terminated!")
        
        program_running.clear()
        GPIO.cleanup()
        sys.exit(0)
        
    def initialize_gpio(self):
        """Initialize all GPIO pins"""
        print("🔧 Initializing LED Matrix System...")
        
        try:
            # Set GPIO mode to BCM numbering
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Configure shift register control pins as outputs
            GPIO.setup(SDI_PIN, GPIO.OUT)      # Data line to shift register
            GPIO.setup(RCLK_PIN, GPIO.OUT)     # Latch pin to update display
            GPIO.setup(SRCLK_PIN, GPIO.OUT)    # Clock pin for shifting data
            
            # Initialize all pins to LOW
            GPIO.output(SDI_PIN, GPIO.LOW)
            GPIO.output(RCLK_PIN, GPIO.LOW)
            GPIO.output(SRCLK_PIN, GPIO.LOW)
            
            print("✅ GPIO pins configured and initialized")
            print("🚀 Hardware initialization complete!\n")
            
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize GPIO: {e}")
            sys.exit(1)
            
    def shift_out_byte(self, data):
        """
        Send one byte of data to the 74HC595 shift register
        Data is sent MSB first (bit 7 to bit 0)
        
        Args:
            data (int): The 8-bit value to send (0-255)
        """
        for bit in range(8):
            # Extract the MSB and send it to SDI pin
            bit_value = (data & 0x80) != 0
            GPIO.output(SDI_PIN, bit_value)
            data <<= 1  # Shift left for next bit
            
            # Pulse the shift clock to move data into register
            GPIO.output(SRCLK_PIN, GPIO.HIGH)
            time.sleep(0.00001)  # 10 microseconds delay
            GPIO.output(SRCLK_PIN, GPIO.LOW)
            
    def latch_output(self):
        """
        Latch the data from shift register to output pins
        This makes the data visible on the LED matrix
        """
        GPIO.output(RCLK_PIN, GPIO.HIGH)
        time.sleep(0.00001)  # 10 microseconds delay
        GPIO.output(RCLK_PIN, GPIO.LOW)
        
    def clear_display(self):
        """
        Clear the entire LED matrix display
        Turns off all LEDs by sending zeros to both shift registers
        """
        self.shift_out_byte(0x00)  # Clear column data (all columns OFF)
        self.shift_out_byte(0x00)  # Clear row data (all rows OFF)
        self.latch_output()        # Apply the changes
        
    def display_pattern(self, low_byte, high_byte):
        """
        Display one frame of the LED matrix pattern
        
        Args:
            low_byte (int): Column data (0-255)
            high_byte (int): Row selection data (0-255)
        """
        self.shift_out_byte(low_byte)   # Send low byte first
        self.shift_out_byte(high_byte)  # Send high byte second
        self.latch_output()             # Update the display
        time.sleep(DISPLAY_DELAY)       # Hold the pattern
        
    def display_complete_pattern(self, row_data, col_data, duration_seconds):
        """
        Display a complete 8x8 pattern using row scanning (multiplexing)
        
        Args:
            row_data (list): List of 8 bytes for row selection
            col_data (list): List of 8 bytes for column patterns
            duration_seconds (float): How long to display the pattern
        """
        start_time = time.time()
        
        while (time.time() - start_time) < duration_seconds:
            if not program_running.is_set():
                break
                
            # One complete scan of all 8 rows
            for row in range(8):
                self.shift_out_byte(col_data[row])
                self.shift_out_byte(row_data[row])
                self.latch_output()
                time.sleep(0.0005)  # 0.5ms per row
                
                # Check if time is up during scanning
                if (time.time() - start_time) >= duration_seconds:
                    break
                    
    def play_top_to_bottom_scan(self):
        """
        Stage 1: Top-to-bottom scanning animation
        Lights up one row at a time from top to bottom
        """
        print("🔽 Playing: Top-to-bottom scan...")
        for i in range(8):
            if not program_running.is_set():
                break
            self.display_pattern(scan_down_low[i], scan_down_high[i])
        time.sleep(STAGE_PAUSE)
        
    def play_left_to_right_scan(self):
        """
        Stage 2: Left-to-right scanning animation  
        Lights up one column at a time from left to right
        """
        print("➡️  Playing: Left-to-right scan...")
        for i in range(8):
            if not program_running.is_set():
                break
            self.display_pattern(scan_right_low[i], scan_right_high[i])
        time.sleep(STAGE_PAUSE)
        
    def play_arrow_animation(self):
        """
        Stage 3: Arrow animation (clockwise rotation)
        Shows arrows pointing up → right → down → left
        """
        print("🏹 Playing: Arrow rotation...")
        
        arrows = [
            ("↑ UP", arrow_up_cols),
            ("→ RIGHT", arrow_right_cols),
            ("↓ DOWN", arrow_down_cols),
            ("← LEFT", arrow_left_cols)
        ]
        
        for direction, col_data in arrows:
            if not program_running.is_set():
                break
                
            print(f"  {direction}")
            self.display_complete_pattern(arrow_row_select, col_data, ARROW_DURATION)
            self.clear_display()  # Clear after each arrow
            time.sleep(CLEAR_PAUSE)
            
        print("🏹 Arrow sequence completed, clearing display...")
        time.sleep(0.5)  # Pause before next cycle
        
    def run_animation_loop(self):
        """Main animation loop"""
        print("🚀 Starting LED Matrix Animation...")
        print("📺 Animation sequence: Top-to-bottom → Left-to-right → Arrow rotation")
        print("✨ Display clears between animations for clean transitions")
        print("💡 Press Ctrl+C to exit\n")
        
        # Clear display at startup
        self.clear_display()
        print("📺 Display initialized and cleared\n")
        
        cycle_count = 0
        
        while program_running.is_set():
            try:
                cycle_count += 1
                print(f"🔄 === Animation Cycle {cycle_count} ===")
                
                # Stage 1: Top-to-bottom scanning
                self.play_top_to_bottom_scan()
                self.clear_display()
                time.sleep(CLEAR_PAUSE)
                
                # Stage 2: Left-to-right scanning
                self.play_left_to_right_scan()
                self.clear_display()
                time.sleep(CLEAR_PAUSE)
                
                # Stage 3: Arrow animations
                self.play_arrow_animation()
                
                print(f"✅ Cycle {cycle_count} completed\n")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Error in animation loop: {e}")
                time.sleep(0.1)
                
    def display_startup_info(self):
        """Display startup information"""
        print("=" * 50)
        print("🎮 LED Matrix Animation System - Python Version")
        print("=" * 50)
        print("📝 This program creates animated patterns on an 8x8 LED matrix")
        print("⚡ Uses 74HC595 shift register for multiplexing")
        print("🐍 Python version with RPi.GPIO library")
        print(f"📍 SDI pin: {SDI_PIN} (BCM)")
        print(f"📍 RCLK pin: {RCLK_PIN} (BCM)")
        print(f"📍 SRCLK pin: {SRCLK_PIN} (BCM)")
        print(f"⏱️  Arrow duration: {ARROW_DURATION}s each")
        print(f"⏱️  Display delay: {DISPLAY_DELAY}s")
        print()

def test_display_patterns():
    """Test function to verify display is working correctly"""
    print("🧪 Testing LED Matrix Display...")
    controller = LEDMatrixController()
    
    # Test simple patterns
    test_patterns = [
        (0x00, 0x01, "Single row"),
        (0xff, 0x01, "Full row"),
        (0x81, 0xff, "Two columns"),
        (0x00, 0x00, "All off")
    ]
    
    for low, high, description in test_patterns:
        print(f"📺 Testing: {description}")
        controller.display_pattern(low, high)
        time.sleep(1)
        
    controller.clear_display()
    print("✅ Display test complete!")

def main():
    """Main function - Program entry point"""
    try:
        # Create and run the LED matrix controller
        controller = LEDMatrixController()
        controller.display_startup_info()
        controller.run_animation_loop()
        
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        GPIO.cleanup()
        print("🧹 GPIO cleanup complete")

if __name__ == "__main__":
    # 🧪 Uncomment the next line to run display test instead of main program
    # test_display_patterns()
    
    main()
