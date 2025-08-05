#!/usr/bin/env python3

"""
RFID Card Writer Program
This program allows you to write text data to RFID/NFC cards using MFRC522 sensor.
"""

from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

# Initialize the RFID reader/writer
reader = SimpleMFRC522()

def main():
    """
    Main function that handles the card writing process
    """
    # Display program title and instructions
    print("=" * 50)
    print("    🔖 RFID CARD WRITER 🔖")
    print("=" * 50)
    print("This program writes text data to RFID/NFC cards.")
    print("Press Ctrl+C to exit the program.")
    print("=" * 50)
    
    while True:
        # Get text input from user
        print("\n📝 Step 1: Enter your data")
        text = input('💬 Please type the text you want to write to the card: ')
        
        if not text.strip():  # Check if input is empty
            print("⚠️  Warning: Empty input detected. Please enter some text.")
            continue
        
        # Instruct user to place the card
        print("\n📡 Step 2: Place your card")
        print("🔄 Please place the RFID card near the sensor to write data...")
        
        try:
            # Write data to the card (this will wait until a card is detected)
            reader.write(text)
            
            # Success message
            print("✅ SUCCESS! Data written successfully!")
            print(f"📄 Written content: '{text}'")
            print("-" * 50)
            
        except Exception as e:
            # Handle any writing errors
            print(f"❌ Error writing to card: {e}")

def destroy():
    """
    Cleanup function to release GPIO resources
    """
    print("\n🧹 Cleaning up GPIO resources...")
    GPIO.cleanup()
    print("✅ Cleanup complete. Goodbye!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:  # When 'Ctrl+C' is pressed
        print("\n\n⏹️  Program interrupted by user.")
        destroy()