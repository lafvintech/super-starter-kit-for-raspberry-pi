#!/usr/bin/env python3
"""
Morse Code Generator
LED + Buzzer Morse Code Output

This program converts text messages to Morse code and outputs them
using an LED and buzzer for visual and audio feedback.
"""

import time
import signal
import sys
try:
    import RPi.GPIO as GPIO
except ImportError:
    print("❌ Required libraries not found!")
    print("Please install: sudo apt-get install python3-rpi.gpio")
    sys.exit(1)

# --- Hardware Configuration ---
BUZZER_PIN = 22        # GPIO pin for buzzer
LED_PIN =  17          # GPIO pin for LED
DOT_DURATION = 0.125   # Duration for dot (seconds)
DASH_DURATION = 0.250  # Duration for dash (seconds)
MAX_INPUT_SIZE = 100   # Maximum input string length

# --- Morse Code Dictionary ---
MORSE_DICTIONARY = {
    # Letters A-Z
    'A': '.-',   'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
    'F': '..-.', 'G': '--.',  'H': '....', 'I': '..',  'J': '.---',
    'K': '-.-',  'L': '.-..', 'M': '--',   'N': '-.',  'O': '---',
    'P': '.--.', 'Q': '--.-', 'R': '.-.',  'S': '...', 'T': '-',
    'U': '..-',  'V': '...-', 'W': '.--',  'X': '-..-', 'Y': '-.--',
    'Z': '--..',
    
    # Numbers 0-9
    '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
    '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
    
    # Special characters
    '?': '..--..', '/': '-..-.', ',': '--..--', '.': '.-.-.-',
    ';': '-.-.-.', '!': '-.-.--', '@': '.--.-.',  ':': '---...'
}

class MorseCodeGenerator:
    """Morse code generator using LED and buzzer output"""
    
    def __init__(self):
        """Initialize the Morse code generator"""
        self.setup_hardware()
    
    def find_morse_pattern(self, character):
        """
        Find Morse code pattern for a character
        
        Args:
            character: Character to look up
            
        Returns:
            Morse code pattern string, or None if not found
        """
        return MORSE_DICTIONARY.get(character.upper())
    
    def signal_on(self):
        """Turn on LED and buzzer"""
        GPIO.output(LED_PIN, GPIO.HIGH)
        GPIO.output(BUZZER_PIN, GPIO.HIGH)
    
    def signal_off(self):
        """Turn off LED and buzzer"""
        GPIO.output(LED_PIN, GPIO.LOW)
        GPIO.output(BUZZER_PIN, GPIO.LOW)
    
    def play_signal(self, duration):
        """
        Play a dot or dash signal
        
        Args:
            duration: Signal duration in seconds
        """
        self.signal_on()
        time.sleep(duration)
        self.signal_off()
        time.sleep(DOT_DURATION)  # Short pause between dots/dashes
    
    def play_morse_character(self, character):
        """
        Convert and play a single character as Morse code
        
        Args:
            character: Character to convert and play
        """
        # Skip spaces (use as word separator)
        if character == ' ':
            time.sleep(DASH_DURATION * 2)  # Long pause for word separation
            return
        
        # Find Morse pattern
        pattern = self.find_morse_pattern(character)
        if pattern is None:
            print(f"⚠️ Character '{character}' not supported")
            return
        
        print(f"📡 {character.upper()} → {pattern}")
        
        # Play each dot/dash in the pattern
        for symbol in pattern:
            if symbol == '.':
                self.play_signal(DOT_DURATION)
            elif symbol == '-':
                self.play_signal(DASH_DURATION)
        
        # Pause between characters
        time.sleep(DASH_DURATION)
    
    def play_morse_message(self, message):
        """
        Convert and play entire message as Morse code
        
        Args:
            message: Text message to convert
        """
        print(f"\n🎵 Playing Morse code for: \"{message}\"")
        print("--- Morse Code Output ---")
        
        for character in message:
            self.play_morse_character(character)
        
        print("✅ Transmission complete!\n")
    
    def setup_hardware(self):
        """Initialize hardware pins"""
        print("🔧 Initializing Morse Code Generator...")
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup output pins
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        GPIO.setup(LED_PIN, GPIO.OUT)
        
        # Ensure outputs are off initially
        self.signal_off()
        
        print(f"📻 Buzzer pin: {BUZZER_PIN}")
        print(f"💡 LED pin: {LED_PIN}")
        print(f"⏱️ Dot duration: {DOT_DURATION*1000:.0f}ms, Dash duration: {DASH_DURATION*1000:.0f}ms")
        print("✅ Hardware ready!\n")
    
    def display_supported_characters(self):
        """Display available characters"""
        print("📝 Supported characters:")
        print("   Letters: A-Z")
        print("   Numbers: 0-9")
        print("   Special: ? / , . ; ! @ :")
        print("   Spaces are used as word separators\n")
    
    def display_morse_chart(self):
        """Display complete Morse code chart"""
        print("📊 Morse Code Reference Chart:")
        print("=" * 50)
        
        # Letters
        print("LETTERS:")
        for i, (char, code) in enumerate(sorted(MORSE_DICTIONARY.items())[:26]):
            print(f"{char}: {code:<6}", end="")
            if (i + 1) % 6 == 0:
                print()
        print()
        
        # Numbers
        print("\nNUMBERS:")
        numbers = {k: v for k, v in MORSE_DICTIONARY.items() if k.isdigit()}
        for i, (char, code) in enumerate(sorted(numbers.items())):
            print(f"{char}: {code:<6}", end="")
            if (i + 1) % 5 == 0:
                print()
        print()
        
        # Special characters
        print("\nSPECIAL:")
        special = {k: v for k, v in MORSE_DICTIONARY.items() if not k.isalnum()}
        for i, (char, code) in enumerate(sorted(special.items())):
            print(f"{char}: {code:<8}", end="")
            if (i + 1) % 4 == 0:
                print()
        print("\n" + "=" * 50 + "\n")
    
    def morse_generator_loop(self):
        """Main program loop"""
        print("🎯 Morse Code Generator active!")
        print("Commands:")
        print("  - Type your message and press Enter to convert to Morse code")
        print("  - Type 'chart' to display the Morse code reference")
        print("  - Type 'help' to show supported characters")
        print("  - Press Ctrl+C to exit\n")
        
        self.display_supported_characters()
        
        try:
            while True:
                try:
                    message = input("💬 Enter message (or 'chart'/'help'): ").strip()
                    
                    # Handle special commands
                    if message.lower() == 'chart':
                        self.display_morse_chart()
                        continue
                    elif message.lower() == 'help':
                        self.display_supported_characters()
                        continue
                    elif message == '':
                        print("⚠️ Empty message. Please enter some text.\n")
                        continue
                    
                    # Play the Morse code
                    self.play_morse_message(message)
                    
                except EOFError:
                    # Handle Ctrl+D
                    self.cleanup_exit(None)
                    
        except KeyboardInterrupt:
            self.cleanup_exit(None)
    
    def cleanup_exit(self, signum):
        """Clean up and exit"""
        print("\n🧹 Shutting down Morse code generator...")
        
        # Turn off all outputs
        self.signal_off()
        
        # Cleanup GPIO
        GPIO.cleanup()
        
        print("✅ Goodbye!")
        sys.exit(0)

def main():
    """Main function"""
    print("=== Morse Code Generator ===")
    print("LED + Buzzer Morse Code Output\n")
    
    # Create Morse code generator
    generator = MorseCodeGenerator()
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, generator.cleanup_exit)
    
    # Start main loop
    generator.morse_generator_loop()

if __name__ == '__main__':
    main()