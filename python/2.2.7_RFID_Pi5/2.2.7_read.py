#!/usr/bin/env python3
# -*- coding: utf8 -*-

# This script is designed to read data from an RFID card using the MFRC522 module.
# It features a user-friendly interface and runs in a continuous loop to read multiple cards.
# Inspired by the temple.py example for a better user experience.

import time
import signal
import MFRC522

# --- Configuration ---
# Define the default key for authentication.
# This should match the key used when writing to the card.
DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# Define the block number to read data from.
# This must match the block where data was written.
BLOCK_TO_READ = 8

# A flag to control the main reading loop. It's set to False on exit.
continue_reading = True

def end_read_handler(signal, frame):
    """
    Signal handler for Ctrl+C (SIGINT).
    This function will be called when the user presses Ctrl+C.
    It sets the `continue_reading` flag to False to gracefully exit the loop.
    """
    global continue_reading
    if continue_reading:
        print("\n\n⏹️  Program interruption detected. Shutting down...")
        continue_reading = False

def main():
    """
    Main function to handle the continuous card reading process.
    """
    # Register the signal handler for Ctrl+C.
    signal.signal(signal.SIGINT, end_read_handler)

    # Create an instance of the MFRC522 reader class.
    rfid_reader = MFRC522.MFRC522()
    
    # Counter for successful reads.
    read_count = 0

    # Display program title and instructions.
    print("=" * 50)
    print("    📖 RFID CARD READER 📖")
    print("=" * 50)
    print("This program reads data from RFID cards continuously.")
    print("Press Ctrl+C to exit the program.")
    print("=" * 50)

    # The main loop that continuously looks for cards to read.
    while continue_reading:
        # Display waiting message.
        print(f"\n🔍 Scan #{read_count + 1}")
        print("📡 Reading mode active... Please place an RFID card near the sensor.")

        # Step 1: Scan for RFID cards.
        (status, tag_type) = rfid_reader.request(rfid_reader.PICC_REQIDL)

        # If a card is found, the status will be MI_OK.
        if status == rfid_reader.MI_OK:
            print("✅ CARD DETECTED!")

            # Step 2: Get the Unique Identifier (UID) of the card.
            (status, uid) = rfid_reader.select_tag_sn()

            if status == rfid_reader.MI_OK:
                # Convert UID list to a readable hex string.
                uid_str = ''.join([f'{i:02X}' for i in uid])
                
                print("+" + "-" * 48 + "+")
                print(f"| 🆔 Card UID:   {uid_str:<32} |")

                # Step 3: Authenticate with the card.
                # This is required before you can read data from a block.
                auth_status = rfid_reader.auth(rfid_reader.PICC_AUTHENT1A, BLOCK_TO_READ, DEFAULT_KEY, uid)

                if auth_status == rfid_reader.MI_OK:
                    # Step 4: Read data from the specified block.
                    # The read() function returns a status and the data.
                    (read_status, read_data) = rfid_reader.read(BLOCK_TO_READ)

                    if read_status == rfid_reader.MI_OK and read_data:
                        # Step 5: Process and display the data.
                        # The data is a list of bytes. We convert it to a string.
                        # .rstrip('\x00') removes any trailing null characters used for padding.
                        text_read = ''.join(chr(byte) for byte in read_data).rstrip('\x00')
                        
                        # Calculate padding to align the output neatly.
                        # The total width for the content area is 32 characters.
                        padding = ' ' * (30 - len(text_read))
                        print(f"| 📄 Content:   '{text_read}'{padding} |")
                        read_count += 1
                    else:
                        print(f"| ❌ Failed to read data from Block {BLOCK_TO_READ}. Status: {read_status}")
                    
                    # Stop the encryption on the card to release it.
                    rfid_reader.stop_crypto1()
                else:
                    print(f"| ❌ Authentication failed. Status code: {auth_status}")

                print("+" + "-" * 48 + "+")
                print(f"📊 Total cards read: {read_count}")
                print("⏳ Waiting 3 seconds before next scan...")
                time.sleep(3) # Wait before the next scan.
            else:
                print("❌ Unable to get card UID.")
                time.sleep(1)

        # Wait a moment before the next scan if no card was found.
        time.sleep(0.5)

def destroy():
    """
    Cleanup message when the program exits.
    """
    print("✅ Program terminated gracefully. Goodbye!")

if __name__ == '__main__':
    main()
    destroy()
