#!/usr/bin/env python3
"""
Password Lock System
4x4 Keypad + LCD1602 Display

This program creates a password lock system using a 4x4 matrix keypad
for input and an LCD1602 display for user interface.
"""

import time
import signal
import sys
try:
    import smbus
    import RPi.GPIO as GPIO
except ImportError:
    print("❌ Required libraries not found!")
    print("Please install: sudo apt-get install python3-smbus python3-rpi.gpio")
    sys.exit(1)

# --- Hardware Configuration ---
LCD_ADDR = 0x27
LCD_BACKLIGHT = 0x08
PASSWORD_LENGTH = 4

# --- Pin Configuration ---
ROW_PINS = [18, 23, 24, 25]      # GPIO pins for keypad rows
COL_PINS = [10, 22, 27, 17]      # GPIO pins for keypad columns

# --- Keypad Layout ---
KEYPAD_LAYOUT = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]

# --- Password Configuration ---
CORRECT_PASSWORD = "1984"
entered_password = ""

# --- Global Variables ---
bus = None

class PasswordLock:
    """Password lock system combining 4x4 keypad and LCD1602 display"""
    
    def __init__(self):
        """Initialize the password lock system"""
        self.setup_hardware()
    
    def lcd_write_byte(self, data):
        """Write data to LCD via I2C"""
        temp = data | LCD_BACKLIGHT  # Keep backlight on
        bus.write_byte(LCD_ADDR, temp)
    
    def lcd_send_command(self, command):
        """Send command to LCD"""
        # Send upper 4 bits
        buffer = command & 0xF0
        buffer |= 0x04  # RS=0, RW=0, EN=1
        self.lcd_write_byte(buffer)
        time.sleep(0.002)
        buffer &= 0xFB  # EN=0
        self.lcd_write_byte(buffer)
        
        # Send lower 4 bits
        buffer = (command & 0x0F) << 4
        buffer |= 0x04  # RS=0, RW=0, EN=1
        self.lcd_write_byte(buffer)
        time.sleep(0.002)
        buffer &= 0xFB  # EN=0
        self.lcd_write_byte(buffer)
    
    def lcd_send_data(self, data):
        """Send data to LCD"""
        # Send upper 4 bits
        buffer = data & 0xF0
        buffer |= 0x05  # RS=1, RW=0, EN=1
        self.lcd_write_byte(buffer)
        time.sleep(0.002)
        buffer &= 0xFB  # EN=0
        self.lcd_write_byte(buffer)
        
        # Send lower 4 bits
        buffer = (data & 0x0F) << 4
        buffer |= 0x05  # RS=1, RW=0, EN=1
        self.lcd_write_byte(buffer)
        time.sleep(0.002)
        buffer &= 0xFB  # EN=0
        self.lcd_write_byte(buffer)
    
    def lcd_init(self):
        """Initialize LCD display"""
        print("📺 Initializing LCD display...")
        
        try:
            self.lcd_send_command(0x33)  # Initialize to 8-bit mode
            time.sleep(0.005)
            self.lcd_send_command(0x32)  # Switch to 4-bit mode
            time.sleep(0.005)
            self.lcd_send_command(0x28)  # 2 lines, 5x7 dots
            time.sleep(0.005)
            self.lcd_send_command(0x0C)  # Display on, cursor off
            time.sleep(0.005)
            self.lcd_send_command(0x01)  # Clear screen
            time.sleep(0.002)
            bus.write_byte(LCD_ADDR, LCD_BACKLIGHT)
            
            print("✅ LCD ready!")
        except Exception as e:
            print(f"❌ LCD initialization failed: {e}")
            self.cleanup_exit(None)
    
    def lcd_clear(self):
        """Clear LCD screen"""
        self.lcd_send_command(0x01)
        time.sleep(0.002)
    
    def lcd_display_text(self, x, y, text):
        """Display text on LCD at specified position"""
        # Set cursor position
        address = 0x80 + (0x40 * y) + x
        self.lcd_send_command(address)
        
        # Send text characters
        for char in text:
            self.lcd_send_data(ord(char))
    
    def keypad_init(self):
        """Initialize keypad pins"""
        print("⌨️ Initializing keypad...")
        
        # Setup row pins as outputs
        for pin in ROW_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        
        # Setup column pins as inputs with pull-down resistors
        for pin in COL_PINS:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        print("✅ Keypad ready!")
    
    def scan_keypad(self):
        """Scan keypad for pressed key"""
        for row in range(4):
            # Activate current row
            GPIO.output(ROW_PINS[row], GPIO.HIGH)
            time.sleep(0.001)  # Small delay for signal stability
            
            # Check each column
            for col in range(4):
                if GPIO.input(COL_PINS[col]) == GPIO.HIGH:
                    GPIO.output(ROW_PINS[row], GPIO.LOW)  # Deactivate row
                    return KEYPAD_LAYOUT[row][col]
            
            # Deactivate current row
            GPIO.output(ROW_PINS[row], GPIO.LOW)
        
        return None  # No key pressed
    
    def verify_password(self):
        """Check if entered password matches correct password"""
        return entered_password == CORRECT_PASSWORD
    
    def reset_password_entry(self):
        """Reset password entry"""
        global entered_password
        entered_password = ""
    
    def display_password_entry(self):
        """Display password entry screen"""
        self.lcd_clear()
        self.lcd_display_text(0, 0, "Enter password:")
        # Show entered digits
        for i in range(len(entered_password)):
            self.lcd_display_text(i, 1, entered_password[i])
    
    def handle_success(self):
        """Handle successful password entry"""
        print("✅ Password correct!")
        self.lcd_clear()
        self.lcd_display_text(4, 0, "CORRECT!")
        self.lcd_display_text(2, 1, "welcome back")
        time.sleep(3)
        self.reset_password_entry()
    
    def handle_failure(self):
        """Handle failed password entry"""
        print("❌ Wrong password!")
        self.lcd_clear()
        self.lcd_display_text(3, 0, "WRONG KEY!")
        self.lcd_display_text(0, 1, "please try again")
        time.sleep(2)
        self.reset_password_entry()
    
    def setup_hardware(self):
        """Initialize hardware components"""
        global bus
        
        print("🔧 Initializing Password Lock System...")
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup I2C for LCD
        try:
            bus = smbus.SMBus(1)  # I2C bus 1
            self.lcd_init()
        except Exception as e:
            print(f"❌ LCD setup failed: {e}")
            self.cleanup_exit(None)
        
        # Setup keypad
        self.keypad_init()
        
        print("🔐 Password Lock System ready!")
        print(f"Default password: {CORRECT_PASSWORD}\n")
    
    def password_lock_loop(self):
        """Main password lock loop"""
        global entered_password
        
        last_key = None
        
        # Display welcome screen
        self.lcd_clear()
        self.lcd_display_text(0, 0, "WELCOME!")
        self.lcd_display_text(2, 1, "Enter password")
        time.sleep(2)
        
        self.display_password_entry()
        
        print("🔐 Password lock active...")
        print("Enter 4-digit password using keypad")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                current_key = self.scan_keypad()
                
                # Process key press (only on new press, not hold)
                if current_key and current_key != last_key:
                    print(f"🔑 Key pressed: {current_key}")
                    
                    # Add key to password if there's room
                    if len(entered_password) < PASSWORD_LENGTH:
                        entered_password += current_key
                        self.display_password_entry()
                    
                    # Check if password is complete
                    if len(entered_password) == PASSWORD_LENGTH:
                        if self.verify_password():
                            self.handle_success()
                        else:
                            self.handle_failure()
                        self.display_password_entry()
                
                last_key = current_key
                time.sleep(0.1)  # Debounce delay
                
        except KeyboardInterrupt:
            self.cleanup_exit(None)
    
    def cleanup_exit(self, signum):
        """Clean up and exit"""
        print("\n🧹 Shutting down password lock system...")
        
        try:
            self.lcd_clear()
            self.lcd_display_text(4, 0, "GOODBYE!")
            time.sleep(1)
            self.lcd_clear()
        except:
            pass
        
        # Cleanup GPIO
        GPIO.cleanup()
        
        print("✅ Goodbye!")
        sys.exit(0)

def main():
    """Main function"""
    print("=== Password Lock System ===")
    print("4x4 Keypad + LCD1602 Display\n")
    
    # Create password lock system
    password_lock = PasswordLock()
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, password_lock.cleanup_exit)
    
    # Start password lock loop
    password_lock.password_lock_loop()

if __name__ == '__main__':
    main()