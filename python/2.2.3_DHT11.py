#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DHT11 Temperature and Humidity Sensor Demo

This is a robust Python demo for reading the DHT11 sensor using a hybrid
Python + C library approach. The program features an intelligent retry
mechanism and clean output formatting.

Features:
- Hybrid Python + C architecture for optimal performance
- Silent retry mechanism with up to 15 attempts per cycle
- Clean, formatted output with cycle counting
- Robust error handling and user-friendly interface

Hardware Setup:
- Connect DHT11 data pin to BCM GPIO 17 (wiringPi pin 0)

Dependencies:
- dht_driver.py (Python wrapper for C library)
- dht_c_driver.so (Compiled C shared library)
- wiringPi library

Author: LAFVIN
Date: 2025/08/01
"""

import time
from dht_driver import DHT

# --- Configuration ---
DHT11_DATA_PIN = 0  # wiringPi pin number (corresponds to BCM GPIO 17)

def main():
    """The main function of the program."""
    print("Starting DHT11 sensor reading program (Python + C Library)...")
    print("--------------------------------------------------------------")
    print("Press Ctrl+C to exit.")
    print()

    # Initialize the DHT sensor driver
    try:
        dht = DHT()  # This will automatically load the C library and initialize wiringPi
        print("DHT11 driver initialized successfully.")
    except Exception as e:
        print(f"Error initializing DHT11 driver: {e}")
        return

    measurement_cycle = 0

    # --- Main Measurement Loop ---
    while True:
        measurement_cycle += 1
        max_retries = 15
        
        # --- Silent Retry Loop ---
        # This loop attempts to read the sensor up to 'max_retries' times.
        # It does so silently to provide a clean user experience.
        humidity = None
        temperature = None
        
        for attempt in range(max_retries):
            humidity, temperature = dht.read(DHT11_DATA_PIN)
            
            if humidity is not None and temperature is not None:
                break  # Exit loop on first successful read
            
            # If it failed, wait briefly before retrying.
            time.sleep(0.3)
        
        # --- Final, Clean Output ---
        # Print the result for this measurement cycle in a clean format.
        print(f"Cycle #{measurement_cycle}: ", end="")
        if humidity is not None and temperature is not None:
            print(f"Humidity = {humidity:.1f}%, Temperature = {temperature:.1f} C")
        else:
            # This message only appears if all retries fail.
            print("Failed to get a valid reading from the sensor.")

        # Wait for 2 seconds before the next major cycle.
        time.sleep(2)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")