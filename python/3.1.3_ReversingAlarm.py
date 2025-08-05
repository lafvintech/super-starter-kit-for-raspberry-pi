#!/usr/bin/env python3
"""
@file ultrasonic_distance_sensor.py
@brief Smart Distance Measurement System (Python Version)
@description Uses ultrasonic sensor to measure distance and displays results on LCD
             with audio alerts based on proximity
@author LAFVIN (Python version)
"""

import RPi.GPIO as GPIO
import time
import signal
import sys
import smbus
from threading import Event

# ========== PIN DEFINITIONS ==========
TRIGGER_PIN = 4     # Ultrasonic sensor trigger pin
ECHO_PIN = 5        # Ultrasonic sensor echo pin  
BUZZER_PIN = 0      # Active buzzer pin (BCM numbering)

# Convert wiringPi pins to BCM pins
TRIGGER_BCM = 23    # wiringPi 4 = BCM 23
ECHO_BCM = 24       # wiringPi 5 = BCM 24
BUZZER_BCM = 17     # wiringPi 0 = BCM 17

# ========== LCD CONFIGURATION ==========
LCD_I2C_ADDRESS = 0x27
LCD_BACKLIGHT_ON = 1
LCD_BACKLIGHT_OFF = 0

# ========== DISTANCE THRESHOLDS ==========
SAFE_DISTANCE = 50.0        # Distance > 50cm (safe zone)
WARNING_DISTANCE = 20.0     # Distance 20-50cm (warning zone)
DANGER_DISTANCE = 20.0      # Distance < 20cm (danger zone)
MAX_VALID_DISTANCE = 400.0  # Maximum sensor range

# ========== GLOBAL VARIABLES ==========
bus = None
backlight_status = LCD_BACKLIGHT_ON
program_running = Event()
program_running.set()

class UltrasonicDistanceSensor:
    """Smart Distance Measurement System Class"""
    
    def __init__(self):
        """Initialize the distance sensor system"""
        self.setup_gpio()
        self.setup_lcd()
        self.setup_exit_handler()
        
    def setup_exit_handler(self):
        """Setup signal handler for Ctrl+C"""
        signal.signal(signal.SIGINT, self.handle_exit)
        print("🛡️  Press Ctrl+C to safely exit")
        
    def handle_exit(self, signum, frame):
        """Handle Ctrl+C signal - turn off buzzer and exit"""
        print("\n🛑 Ctrl+C pressed! Shutting down...")
        
        # Turn off buzzer immediately
        GPIO.output(BUZZER_BCM, GPIO.LOW)
        print("🔇 Buzzer turned off")
        
        # Clear LCD and show goodbye message
        self.lcd_clear_screen()
        self.lcd_display_text(3, 0, "Goodbye!")
        self.lcd_display_text(1, 1, "See you later")
        time.sleep(2)  # Show message for 2 seconds
        
        # Clear screen completely
        self.lcd_clear_screen()
        
        # Set program flag to stop main loop
        program_running.clear()
        
        print("👋 Thank you for using Distance Sensor! Goodbye!")
        
        # Cleanup GPIO
        GPIO.cleanup()
        sys.exit(0)
        
    def setup_gpio(self):
        """Initialize GPIO pins"""
        print("🔧 Setting up GPIO pins...")
        
        # Set GPIO mode
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup ultrasonic sensor pins
        GPIO.setup(ECHO_BCM, GPIO.IN)
        GPIO.setup(TRIGGER_BCM, GPIO.OUT)
        GPIO.output(TRIGGER_BCM, GPIO.LOW)
        
        # Setup buzzer pin
        GPIO.setup(BUZZER_BCM, GPIO.OUT)
        GPIO.output(BUZZER_BCM, GPIO.LOW)
        
        print("✅ GPIO setup complete!")
        
    def setup_lcd(self):
        """Initialize LCD display"""
        global bus
        print("🔧 Initializing LCD display...")
        
        try:
            bus = smbus.SMBus(1)  # I2C bus 1
            
            # LCD initialization sequence for 4-bit mode
            self.lcd_send_command(0x33)
            time.sleep(0.005)
            self.lcd_send_command(0x32)
            time.sleep(0.005)
            self.lcd_send_command(0x28)  # 4-bit mode, 2 lines, 5x7 font
            time.sleep(0.005)
            self.lcd_send_command(0x0C)  # Display ON, cursor OFF, blink OFF
            time.sleep(0.005)
            self.lcd_send_command(0x01)  # Clear display
            time.sleep(0.005)
            
            bus.write_byte(LCD_I2C_ADDRESS, 0x08)  # Turn on backlight
            
            print("✅ LCD initialization complete!")
            
        except Exception as e:
            print(f"❌ ERROR: Failed to initialize LCD: {e}")
            sys.exit(1)
            
    def lcd_write_byte(self, data_byte):
        """Send raw data to LCD via I2C"""
        temp_data = data_byte
        
        if backlight_status == LCD_BACKLIGHT_ON:
            temp_data |= 0x08  # Set backlight bit
        else:
            temp_data &= 0xF7  # Clear backlight bit
            
        bus.write_byte(LCD_I2C_ADDRESS, temp_data)
        
    def lcd_send_command(self, command):
        """Send command to LCD (4-bit mode)"""
        # Send upper 4 bits first
        buffer = command & 0xF0
        buffer |= 0x04  # Set Enable bit (RS=0, RW=0, EN=1)
        self.lcd_write_byte(buffer)
        time.sleep(0.0001)
        
        buffer &= 0xFB  # Clear Enable bit (EN=0)
        self.lcd_write_byte(buffer)
        
        # Send lower 4 bits
        buffer = (command & 0x0F) << 4
        buffer |= 0x04  # Set Enable bit
        self.lcd_write_byte(buffer)
        time.sleep(0.0001)
        
        buffer &= 0xFB  # Clear Enable bit
        self.lcd_write_byte(buffer)
        
    def lcd_send_character(self, character):
        """Send data (character) to LCD"""
        # Send upper 4 bits first
        buffer = ord(character) & 0xF0
        buffer |= 0x05  # Set RS and Enable bits (RS=1, RW=0, EN=1)
        self.lcd_write_byte(buffer)
        time.sleep(0.0001)
        
        buffer &= 0xFB  # Clear Enable bit
        self.lcd_write_byte(buffer)
        
        # Send lower 4 bits
        buffer = (ord(character) & 0x0F) << 4
        buffer |= 0x05  # Set RS and Enable bits
        self.lcd_write_byte(buffer)
        time.sleep(0.0001)
        
        buffer &= 0xFB  # Clear Enable bit
        self.lcd_write_byte(buffer)
        
    def lcd_clear_screen(self):
        """Clear LCD screen"""
        self.lcd_send_command(0x01)
        time.sleep(0.002)
        
    def lcd_display_text(self, column, row, text):
        """Display text at specific position on LCD"""
        # Validate and limit input parameters
        column = max(0, min(15, column))
        row = max(0, min(1, row))
        
        # Calculate cursor position (LCD memory address)
        cursor_address = 0x80 + (0x40 * row) + column
        self.lcd_send_command(cursor_address)
        
        # Send each character of the text
        for char in text:
            self.lcd_send_character(char)
            
    def measure_distance(self):
        """Measure distance using ultrasonic sensor"""
        # Send trigger pulse
        GPIO.output(TRIGGER_BCM, GPIO.LOW)
        time.sleep(0.000002)  # 2µs
        
        GPIO.output(TRIGGER_BCM, GPIO.HIGH)
        time.sleep(0.00001)   # 10µs
        GPIO.output(TRIGGER_BCM, GPIO.LOW)
        
        # Wait for echo to go HIGH (start of return signal)
        timeout_start = time.time()
        while GPIO.input(ECHO_BCM) == 0 and program_running.is_set():
            if time.time() - timeout_start > 0.1:  # 100ms timeout
                return MAX_VALID_DISTANCE + 1
                
        if not program_running.is_set():
            return 0
            
        start_time = time.time()
        
        # Wait for echo to go LOW (end of return signal)
        timeout_start = time.time()
        while GPIO.input(ECHO_BCM) == 1 and program_running.is_set():
            if time.time() - timeout_start > 0.1:  # 100ms timeout
                return MAX_VALID_DISTANCE + 1
                
        if not program_running.is_set():
            return 0
            
        end_time = time.time()
        
        # Calculate distance
        # Formula: Distance = (Time × Speed_of_Sound) / 2
        # Speed of sound = 34300 cm/s
        duration = end_time - start_time
        distance_cm = (duration * 34300) / 2
        
        return distance_cm
        
    def play_proximity_alert(self, distance):
        """Play buzzer pattern based on distance"""
        GPIO.output(BUZZER_BCM, GPIO.LOW)
        
        if not program_running.is_set():
            return
            
        if distance >= SAFE_DISTANCE:
            # Safe zone: No sound, longer delay
            for i in range(50):
                if not program_running.is_set():
                    break
                time.sleep(0.01)
                
        elif distance > WARNING_DISTANCE and distance < SAFE_DISTANCE:
            # Warning zone: Slow beeping
            print("⚠️  WARNING: Object approaching!")
            for beep in range(2):
                if not program_running.is_set():
                    break
                GPIO.output(BUZZER_BCM, GPIO.HIGH)
                time.sleep(0.1)  # 100ms
                GPIO.output(BUZZER_BCM, GPIO.LOW)
                time.sleep(0.3)  # 300ms
                
        elif distance <= WARNING_DISTANCE:
            # Danger zone: Fast beeping
            print("🚨 DANGER: Object very close!")
            for beep in range(5):
                if not program_running.is_set():
                    break
                GPIO.output(BUZZER_BCM, GPIO.HIGH)
                time.sleep(0.08)  # 80ms
                GPIO.output(BUZZER_BCM, GPIO.LOW)
                time.sleep(0.08)  # 80ms
                
    def show_startup_message(self):
        """Display welcome message"""
        self.lcd_clear_screen()
        self.lcd_display_text(0, 0, "Distance Sensor")
        self.lcd_display_text(2, 1, "Starting Up...")
        time.sleep(2)
        
        self.lcd_clear_screen()
        self.lcd_display_text(1, 0, "LAFVIN Project")
        self.lcd_display_text(0, 1, "Ready to measure")
        time.sleep(2)
        
    def display_distance_info(self, distance):
        """Display distance measurement results"""
        self.lcd_clear_screen()
        
        if distance > MAX_VALID_DISTANCE:
            # Out of range error
            self.lcd_display_text(3, 0, "ERROR!")
            self.lcd_display_text(1, 1, "Out of Range")
            print(f"❌ Measurement error: Distance too far ({distance:.2f} cm)")
        else:
            # Valid measurement - display distance
            self.lcd_display_text(0, 0, "Distance:")
            distance_string = f"{distance:.1f} cm"
            self.lcd_display_text(3, 1, distance_string)
            
            # Print status to console
            if distance >= SAFE_DISTANCE:
                print(f"✅ Safe distance: {distance:.2f} cm")
            elif distance > WARNING_DISTANCE:
                print(f"⚠️  Warning distance: {distance:.2f} cm")
            else:
                print(f"🚨 Danger distance: {distance:.2f} cm")
                
    def run(self):
        """Main program loop"""
        print("========================================")
        print("🎯 Smart Distance Measurement System")
        print("========================================")
        
        # Show startup message
        self.show_startup_message()
        print("🚀 System ready! Starting distance monitoring...")
        print("📏 Safe: >50cm | ⚠️ Warning: 20-50cm | 🚨 Danger: <20cm")
        print("💡 Press Ctrl+C to safely exit\n")
        
        # Main measurement loop
        while program_running.is_set():
            try:
                # Take distance measurement
                measured_distance = self.measure_distance()
                
                # Check if we should continue
                if not program_running.is_set():
                    break
                    
                # Display results on LCD and console
                self.display_distance_info(measured_distance)
                
                # Check again before playing sound
                if not program_running.is_set():
                    break
                    
                # Play appropriate sound alert
                self.play_proximity_alert(measured_distance)
                
                # Small delay before next measurement
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                time.sleep(1)

def main():
    """Main function - Program entry point"""
    try:
        sensor = UltrasonicDistanceSensor()
        sensor.run()
    except KeyboardInterrupt:
        print("\n🛑 Program interrupted")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        GPIO.cleanup()
        print("🧹 GPIO cleanup complete")

if __name__ == "__main__":
    main()
