#!/usr/bin/env python3
"""
4x4 Keypad Scanner - Python version matching C++ implementation

This implementation replicates the C++ code's features:
1. Professional class-based design with encapsulation
2. Clear constant definitions and initialization
3. State change detection to reduce output noise
4. Professional function naming and structure
5. Enhanced error handling and resource management
"""

import RPi.GPIO as GPIO
import time
import sys

# Define the layout of the keypad (matching C++ constants)
NUM_ROWS = 4
NUM_COLS = 4

class Keypad:
    """
    Encapsulates all keypad functionality with professional design.
    """
    
    def __init__(self, row_pins, col_pins, key_map):
        """
        Constructor: Initializes the keypad with specified pins and key map.
        Parameters:
            row_pins: List of GPIO pins connected to keypad rows
            col_pins: List of GPIO pins connected to keypad columns  
            key_map: List of characters representing the keypad layout
        """
        self.row_pins = row_pins
        self.col_pins = col_pins
        self.key_map = key_map
        self.last_pressed_keys = []
        
        try:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)
            self._initialize_pins()
            print("Keypad GPIO initialization successful!")
            
        except Exception as e:
            print(f"Failed to initialize keypad: {e}")
            raise

    def _initialize_pins(self):
        """
        Private method: Initializes GPIO pins for keypad scanning.
        """
        # Setup row pins as outputs, initially LOW
        for pin in self.row_pins:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            
        # Setup column pins as inputs with pull-down resistors
        for pin in self.col_pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def get_pressed_keys(self):
        """
        Scans the keypad and returns a list of currently pressed keys.
        Returns: List of characters representing pressed keys
        """
        pressed_keys = []
        
        try:
            for r in range(NUM_ROWS):
                # Activate one row at a time
                GPIO.output(self.row_pins[r], GPIO.HIGH)
                
                # Small delay to ensure signal stabilization
                time.sleep(0.001)
                
                # Scan all columns for this active row
                for c in range(NUM_COLS):
                    if GPIO.input(self.col_pins[c]) == GPIO.HIGH:
                        key_index = r * NUM_COLS + c
                        pressed_keys.append(self.key_map[key_index])
                
                # Deactivate the row before moving to the next one
                GPIO.output(self.row_pins[r], GPIO.LOW)
                
        except Exception as e:
            print(f"Error reading keypad: {e}")
            
        return pressed_keys

def print_keys(keys):
    """
    Prints the currently pressed keys to the console.
    Parameters: keys - List of characters representing the pressed keys
    """
    if not keys:
        print("No key pressed")
    else:
        key_str = ", ".join(keys)
        print(f"Pressed: {key_str}")

def setup_keypad():
    """
    Initializes the keypad hardware and configuration.
    Returns: Keypad object on success, None on failure
    """
    try:
        # Define the physical pin connections (C++ wiringPi pins mapped to BCM)
        # C++: ROW_PINS[4] = {1, 4, 5, 6} -> BCM equivalents
        # C++: COL_PINS[4] = {12, 3, 2, 0} -> BCM equivalents
        # Using original working BCM pins from Python code
        row_pins = [18, 23, 24, 25]  # Original working row pins
        col_pins = [10, 22, 27, 17]  # Original working column pins
        
        # Define the character map for the keys (matching C++)
        key_map = [
            '1', '2', '3', 'A',
            '4', '5', '6', 'B', 
            '7', '8', '9', 'C',
            '*', '0', '#', 'D'
        ]
        
        keypad = Keypad(row_pins, col_pins, key_map)
        
        print("4x4 Keypad Scanner initialized")
        print(f"Row pins: {row_pins}")
        print(f"Column pins: {col_pins}")
        print("Keypad layout:")
        print("  1 2 3 A")
        print("  4 5 6 B")
        print("  7 8 9 C")
        print("  * 0 # D")
        print("-" * 30)
        
        return keypad
        
    except Exception as e:
        print(f"Failed to setup keypad: {e}")
        return None

def keypad_scan_loop(keypad):
    """
    Main keypad scanning loop - matches C++ main loop logic.
    This function runs indefinitely until interrupted.
    """
    try:
        last_pressed = []
        
        print("Keypad scanner ready. Press any key...")
        
        while True:
            currently_pressed = keypad.get_pressed_keys()
            
            # Only print if the state has changed (matching C++ logic)
            if currently_pressed != last_pressed:
                print_keys(currently_pressed)
                last_pressed = currently_pressed[:]  # Make a copy
            
            # Poll every 100ms (matching C++ delay)
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nKeypad scanning interrupted by user")
        raise  # Re-raise to be handled by main()

def destroy():
    """
    Clean up function for GPIO resources.
    Ensures all pins are properly released.
    """
    try:
        GPIO.cleanup()
        print("Keypad GPIO resources cleaned up")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """
    Main function - matches C++ code structure.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    print("4x4 Matrix Keypad Scanner")
    print("Professional scanning with state change detection")
    print("Press Ctrl+C to stop...")
    print("=" * 50)
    
    # Initialize the keypad
    keypad = setup_keypad()
    if keypad is None:
        return 1  # Exit if setup fails
    
    try:
        # Start the main scanning loop
        keypad_scan_loop(keypad)
        
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