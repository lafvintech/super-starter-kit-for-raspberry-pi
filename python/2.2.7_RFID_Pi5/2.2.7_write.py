#!/usr/bin/env python3
# -*- coding: utf8 -*-

# This script is designed to write data to an RFID card using the MFRC522 module.
# It provides a user-friendly interface to guide the user through the process.
# Inspired by the temple.py example for a better user experience.

import time
import MFRC522

# --- Configuration ---
# Define the default key for authentication.
# WARNING: Using a default key is insecure for real applications.
# This key is usually all 0xFF bytes.
DEFAULT_KEY = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

# Define the block number to write data to.
# Be careful not to use sector trailer blocks (like 3, 7, 11, ...). Block 8 is a safe choice.
BLOCK_TO_WRITE = 8

def main():
    """
    Main function to handle the card writing process.
    """
    # Create an instance of the MFRC522 reader class.
    rfid_reader = MFRC522.MFRC522()

    # Display program title and instructions.
    print("=" * 50)
    print("    ✍️  RFID CARD WRITER ✍️")
    print("=" * 50)
    print("This program writes user-provided data to an RFID card.")
    print("Press Ctrl+C at any time to exit the program.")
    print("=" * 50)

    # This loop will run once to find a card, write to it, and then exit.
    while True:
        print("\n📡 Waiting for card... Please place an RFID card near the sensor.")

        # Step 1: Scan for RFID cards.
        # The request() function looks for cards and returns the status and card type.
        (status, tag_type) = rfid_reader.request(rfid_reader.PICC_REQIDL)

        # If a card is found, the status will be MI_OK.
        if status == rfid_reader.MI_OK:
            print("✅ CARD DETECTED!")

            # Step 2: Get the Unique Identifier (UID) of the card.
            # The UID is a unique number that identifies the card.
            (status, uid) = rfid_reader.select_tag_sn()

            # If the UID was successfully read, proceed.
            if status == rfid_reader.MI_OK:
                # Convert the UID list to a readable hex string.
                uid_str = ''.join([f'{i:02X}' for i in uid])
                print(f"| 🆔 Card UID: {uid_str}")
                print("+" + "-" * 48 + "+")

                # Step 3: Get data from the user.
                # The data must be 16 characters or less to fit in one block.
                write_data = input("| 💬 Please enter data to write (max 16 chars): ")
                write_data = write_data[:16] # Truncate if longer than 16 chars.

                # Step 4: Prepare the data for writing.
                # Data must be a list of 16 bytes. We pad it with 0s if it's shorter.
                data_to_write = [0] * 16
                byte_data = write_data.encode('utf-8')
                for i, byte_val in enumerate(byte_data):
                    data_to_write[i] = byte_val
                
                print("| 📦 Preparing to write the following data:")
                print(f"|    - String: '{write_data}'")
                print(f"|    - Bytes:  {data_to_write}")

                # Step 5: Authenticate with the card.
                # Before reading or writing, you must authenticate with a key.
                # This proves you have permission to access the specified block.
                print(f"| 🔑 Authenticating Block {BLOCK_TO_WRITE}...")
                auth_status = rfid_reader.auth(rfid_reader.PICC_AUTHENT1A, BLOCK_TO_WRITE, DEFAULT_KEY, uid)

                if auth_status == rfid_reader.MI_OK:
                    print("|    Authentication successful!")

                    # Step 6: Write the data to the block.
                    print(f"| ✍️  Writing data to Block {BLOCK_TO_WRITE}...")
                    rfid_reader.write(BLOCK_TO_WRITE, data_to_write)
                    print("|    Data has been written to the card.")

                    # Step 7: Stop the encryption on the card.
                    # This is important to release the card for other operations.
                    rfid_reader.stop_crypto1()
                    print("| ✅ Write operation complete.")
                    
                    # Exit the loop and program after a successful write.
                    break 
                else:
                    print(f"| ❌ Authentication failed. Status code: {auth_status}")
                    rfid_reader.stop_crypto1()
                    break # Exit on failure as well.
            else:
                print("❌ Unable to get card UID.")
                time.sleep(1) # Wait a bit before trying to scan again.
        
        # Wait a moment before the next scan to reduce CPU usage.
        time.sleep(0.5)

def destroy():
    """
    Provides a clean exit message.
    """
    print("\n\n⏹️  Program interrupted. Goodbye!")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        # This block runs when the user presses Ctrl+C.
        # The 'pass' means we do nothing here and let finally handle the cleanup.
        pass
    finally:
        # This will always run, ensuring a clean exit message is displayed.
        destroy()
