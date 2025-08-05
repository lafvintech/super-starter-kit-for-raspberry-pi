#!/usr/bin/env python3

"""
2.2.5_Ultrasonic.py

This script provides a refactored, object-oriented version for measuring distance
using an HC-SR04 ultrasonic sensor with a Raspberry Pi.

It maintains the exact same functionality as the original script but with
a cleaner structure, improved readability, and extensive comments.
"""

import RPi.GPIO as GPIO
import time

class UltrasonicSensor:
    """
    A class to represent and interact with an HC-SR04 ultrasonic sensor.
    
    This class encapsulates the GPIO setup, distance measurement logic,
    and cleanup operations for the sensor.
    """

    def __init__(self, trigger_pin, echo_pin):
        """
        Initializes the UltrasonicSensor.
        
        Args:
            trigger_pin (int): The GPIO pin number (using BOARD numbering) for the TRIG pin.
            echo_pin (int): The GPIO pin number (using BOARD numbering) for the ECHO pin.
        """
        self.trigger_pin = trigger_pin
        self.echo_pin = echo_pin
        # Speed of sound in cm/s. The original script uses 340 m/s.
        # (340 m/s * 100 cm/m = 34000 cm/s)
        self.speed_of_sound_cm = 34000
        
        # Set up the GPIO pins
        self._setup_gpio()

    def _setup_gpio(self):
        """Sets up the GPIO mode and pin configurations."""
        GPIO.setmode(GPIO.BOARD)  # Use physical pin numbering
        GPIO.setup(self.trigger_pin, GPIO.OUT)
        GPIO.setup(self.echo_pin, GPIO.IN)
        
        # Ensure the trigger pin is low to start
        GPIO.output(self.trigger_pin, False)
        
        # Allow the sensor to settle for a moment
        print("Sensor warming up...")
        time.sleep(2)

    def measure_distance(self):
        """
        Measures the distance to an object and returns it in centimeters.
        
        Returns:
            float: The measured distance in cm. Returns -1 if the measurement times out.
        """
        # Send a 10 microsecond pulse to the trigger pin to start the measurement.
        GPIO.output(self.trigger_pin, True)
        time.sleep(0.00001)
        GPIO.output(self.trigger_pin, False)

        pulse_start_time = time.time()
        
        # The measurement loop can get stuck if no echo is received (e.g., object is
        # too far or sensor is disconnected). A timeout prevents this.
        # Max sensor range is ~400-500cm, which takes ~0.025s round trip.
        # A timeout of 0.1s is safe.
        timeout_start = time.time()

        # Wait for the echo pin to go high, marking the start of the echo pulse.
        while GPIO.input(self.echo_pin) == 0:
            pulse_start_time = time.time()
            if pulse_start_time > timeout_start + 0.1:
                return -1 # Timeout error

        pulse_end_time = pulse_start_time
        # Wait for the echo pin to go low, marking the end of the echo pulse.
        while GPIO.input(self.echo_pin) == 1:
            pulse_end_time = time.time()
            if pulse_end_time > timeout_start + 0.1:
                return -1 # Timeout error

        # Calculate the duration of the echo pulse.
        pulse_duration = pulse_end_time - pulse_start_time
        
        # Calculate the distance.
        # Distance = (Pulse Duration * Speed of Sound) / 2
        # We divide by 2 because the sound wave travels to the object and back.
        distance = (pulse_duration * self.speed_of_sound_cm) / 2
        
        return distance

    def cleanup(self):
        """Resets the GPIO pins to their default state."""
        print("Cleaning up GPIO.")
        GPIO.cleanup()

def main():
    """
    Main function to run the distance measurement loop.
    """
    # Define the GPIO pins connected to the sensor.
    # These pin numbers MUST NOT be changed to match the hardware setup.
    TRIGGER_PIN = 16
    ECHO_PIN = 18

    # Create an instance of the sensor.
    sensor = UltrasonicSensor(trigger_pin=TRIGGER_PIN, echo_pin=ECHO_PIN)

    try:
        print("Starting measurements. Press Ctrl+C to exit.")
        while True:
            # Get the distance from the sensor.
            distance = sensor.measure_distance()
            
            # Check for a valid measurement.
            if distance != -1:
                # Print the distance, formatted to two decimal places.
                print(f"Distance: {distance:.2f} cm")
            else:
                # Inform the user that the measurement failed.
                print("Measurement failed (timeout). Please check sensor connections.")
            
            # Wait for a short period before the next measurement.
            time.sleep(0.3)

    except KeyboardInterrupt:
        # This block is executed when the user presses Ctrl+C.
        print("\nMeasurement stopped by user.")
    finally:
        # This block is always executed, ensuring GPIO cleanup happens.
        sensor.cleanup()

if __name__ == '__main__':
    # This ensures the main() function is called only when the script is executed directly.
    main()
	
