#!/usr/bin/env python3

"""
RFID Card Reader Program
This program reads data from RFID/NFC cards using MFRC522 sensor.
"""

import time
from mfrc522 import SimpleMFRC522
import RPi.GPIO as GPIO

# Initialize the RFID reader
reader = SimpleMFRC522()

def main():
    """
    Main function that handles the card reading process
    """
    # Display program title and instructions
    print("=" * 50)
    print("    📖 RFID CARD READER 📖")
    print("=" * 50)
    print("This program reads data from RFID/NFC cards.")
    print("Press Ctrl+C to exit the program.")
    print("=" * 50)
    
    read_count = 0  # Counter for successful reads
    
    while True:
        # Display waiting message
        print(f"\n🔍 Scan #{read_count + 1}")
        print("📡 Reading mode active... Please place an RFID card near the sensor.")
        
        try:
            # Read data from the card (this will wait until a card is detected)
            id, text = reader.read()
            
            # Increment successful read counter
            read_count += 1
            
            # Display the read data in a formatted way
            print("✅ CARD DETECTED!")
            print("+" + "-" * 48 + "+")
            print(f"| 🆔 Card ID:   {id:<32} |")
            print(f"| 📄 Content:   {text.strip():<32} |")
            print("+" + "-" * 48 + "+")
            print(f"📊 Total cards read: {read_count}")
            
            # Wait before next scan
            print("⏳ Waiting 3 seconds before next scan...")
            time.sleep(3)
            
        except Exception as e:
            # Handle any reading errors
            print(f"❌ Error reading card: {e}")
            time.sleep(1)

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