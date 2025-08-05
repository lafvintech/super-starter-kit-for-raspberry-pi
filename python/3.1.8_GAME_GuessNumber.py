#!/usr/bin/env python3
"""
Guess Number Game
Using 4x4 Keypad and LCD1602 Display

A number guessing game where players try to guess a random number
between 0-99 using a 4x4 keypad for input and LCD for display.
"""

import RPi.GPIO as GPIO
import time
import random
import signal
import sys
try:
    import smbus
except ImportError:
    print("❌ Required libraries not found!")
    print("Please install: sudo apt-get install python3-smbus")
    sys.exit(1)

# --- Hardware Configuration ---
LCD_ADDR = 0x27
LCD_BACKLIGHT = 0x08
KEYPAD_ROWS = 4
KEYPAD_COLS = 4

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

# --- Game Constants ---
GAME_MIN_VALUE = 0
GAME_MAX_VALUE = 99
TWO_DIGIT_THRESHOLD = 10

# --- Global Variables ---
bus = None
target_number = 0
current_input = 0
range_lower = 0
range_upper = 99

class GuessNumberGame:
    """Number guessing game with keypad and LCD display"""
    
    def __init__(self):
        """Initialize the game system"""
        self.setup_hardware()
    
    # --- LCD Control Functions ---
    
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
    
    # --- Keypad Control Functions ---
    
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
        for row in range(KEYPAD_ROWS):
            # Activate current row
            GPIO.output(ROW_PINS[row], GPIO.HIGH)
            time.sleep(0.001)  # Small delay for signal stability
            
            # Check each column
            for col in range(KEYPAD_COLS):
                if GPIO.input(COL_PINS[col]) == GPIO.HIGH:
                    GPIO.output(ROW_PINS[row], GPIO.LOW)  # Deactivate row
                    return KEYPAD_LAYOUT[row][col]
            
            # Deactivate current row
            GPIO.output(ROW_PINS[row], GPIO.LOW)
        
        return None  # No key pressed
    
    # --- Game Logic Functions ---
    
    def generate_new_target(self):
        """Generate new random target number"""
        global target_number, range_lower, range_upper, current_input
        
        target_number = random.randint(GAME_MIN_VALUE, GAME_MAX_VALUE)
        range_upper = GAME_MAX_VALUE
        range_lower = GAME_MIN_VALUE
        current_input = 0
        
        print(f"🎯 New target generated: {target_number}")
    
    def check_guess_result(self):
        """Check if guessed number matches target"""
        global current_input, range_lower, range_upper
        
        if current_input > target_number:
            # Guess too high - update upper bound
            if current_input < range_upper:
                range_upper = current_input
        elif current_input < target_number:
            # Guess too low - update lower bound
            if current_input > range_lower:
                range_lower = current_input
        else:
            # Correct guess!
            current_input = 0
            return True
        
        current_input = 0
        return False
    
    def update_game_display(self, is_correct):
        """Update LCD display with current game state"""
        self.lcd_clear()
        
        if is_correct:
            self.lcd_display_text(0, 0, "Congratulations!")
            self.lcd_display_text(0, 1, "You got it!")
            time.sleep(3)
            self.generate_new_target()
            self.update_game_display(False)
            return
        
        # Display input prompt and current number
        self.lcd_display_text(0, 0, "Enter number:")
        self.lcd_display_text(13, 0, str(current_input))
        
        # Display range information
        self.lcd_display_text(0, 1, str(range_lower))
        self.lcd_display_text(3, 1, "<Target<")
        self.lcd_display_text(12, 1, str(range_upper))
    
    def setup_hardware(self):
        """Initialize hardware components"""
        global bus
        
        print("🎮 Initializing Guess Number Game...")
        
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
        
        # Display welcome screen
        self.lcd_clear()
        self.lcd_display_text(0, 0, "Welcome!")
        self.lcd_display_text(0, 1, "Press A to start")
        
        print("✅ Hardware setup complete!")
    
    def run_game_loop(self):
        """Main game execution function"""
        global current_input
        
        last_key = None
        
        print("🎮 Starting game loop...")
        print("🎯 Try to guess the secret number!")
        print("A: New Game, D: Submit Guess, *: Clear Input")
        print("Press Ctrl+C to exit\n")
        
        # Generate first target
        self.generate_new_target()
        self.update_game_display(False)
        
        try:
            while True:
                current_key = self.scan_keypad()
                
                # Process key press (only on new press, not hold)
                if current_key and current_key != last_key:
                    print(f"🔹 Key pressed: {current_key}")
                    
                    is_correct_guess = False
                    
                    if current_key == 'A':
                        # Start new game
                        print("🔄 Starting new game...")
                        self.generate_new_target()
                        self.update_game_display(False)
                        
                    elif current_key == 'D':
                        # Submit current guess
                        print(f"✅ Submitting guess: {current_input}")
                        is_correct_guess = self.check_guess_result()
                        self.update_game_display(is_correct_guess)
                        
                    elif current_key == '*':
                        # Clear current input
                        print("🔄 Clearing input...")
                        current_input = 0
                        self.update_game_display(False)
                        
                    elif current_key.isdigit():
                        # Handle number input (0-9)
                        digit = int(current_key)
                        current_input = current_input * 10 + digit
                        
                        # Auto-submit if two digits entered
                        if current_input >= TWO_DIGIT_THRESHOLD:
                            print(f"✅ Auto-submitting two-digit guess: {current_input}")
                            is_correct_guess = self.check_guess_result()
                        
                        self.update_game_display(is_correct_guess)
                        
                    else:
                        print(f"⚠️ Invalid key: {current_key}")
                
                last_key = current_key
                time.sleep(0.1)  # Debounce delay
                
        except KeyboardInterrupt:
            self.cleanup_exit(None)
    
    def cleanup_exit(self, signum):
        """Clean up and exit"""
        print("\n🧹 Shutting down game...")
        
        try:
            self.lcd_clear()
            self.lcd_display_text(0, 0, "Game Over!")
            self.lcd_display_text(0, 1, "Goodbye!")
            time.sleep(2)
            self.lcd_clear()
        except:
            pass
        
        # Cleanup GPIO
        GPIO.cleanup()
        
        print("✅ Cleanup complete. Goodbye!")
        sys.exit(0)

def main():
    """Main function"""
    print("=== Guess Number Game ===")
    print("🎯 Try to guess the secret number!\n")
    
    # Create game instance
    game = GuessNumberGame()
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, game.cleanup_exit)
    
    # Start game loop
    game.run_game_loop()

if __name__ == '__main__':
    main()