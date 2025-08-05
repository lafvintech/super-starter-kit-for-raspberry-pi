#!/usr/bin/env python3

"""
2.2.4_PIR.py

This script provides a refactored, object-oriented version of a program that
uses a PIR (Passive Infrared) motion sensor to control the color of an RGB LED.

- When motion is detected, the LED turns yellow.
- When there is no motion, the LED is blue.

This version maintains the exact same functionality and pin configuration as the
original but features a cleaner, more modular structure and detailed comments.
"""

import RPi.GPIO as GPIO
import time

class MotionActivatedLight:
    """
    A class to manage a PIR motion sensor and a connected RGB LED.

    This class encapsulates the hardware setup, motion detection loop,
    color control, and cleanup operations.
    """
    
    # Define colors for different states (as 24-bit hex values)
    MOTION_DETECTED_COLOR = 0xFFFF00  # Yellow
    IDLE_COLOR = 0x0000FF              # Blue

    def __init__(self, pir_pin, red_pin, green_pin, blue_pin):
        """
        Initializes the motion sensor and RGB LED.
        
        Args:
            pir_pin (int): The BCM pin number for the PIR sensor.
            red_pin (int): The BCM pin number for the red channel of the LED.
            green_pin (int): The BCM pin number for the green channel of the LED.
            blue_pin (int): The BCM pin number for the blue channel of the LED.
        """
        self.pir_pin = pir_pin
        self.rgb_pins = {'red': red_pin, 'green': green_pin, 'blue': blue_pin}
        
        # PWM objects for each color channel
        self.pwm_channels = {}

        self._setup_gpio()

    def _setup_gpio(self):
        """Sets up the GPIO mode and configures the pins."""
        GPIO.setmode(GPIO.BCM)  # Use Broadcom SOC channel numbering
        
        # Setup PIR sensor pin as input
        GPIO.setup(self.pir_pin, GPIO.IN)
        
        # Setup RGB LED pins as outputs and initialize PWM
        for color, pin in self.rgb_pins.items():
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.LOW)
            # Create a PWM instance for the pin with a frequency of 2000 Hz
            self.pwm_channels[color] = GPIO.PWM(pin, 2000)
            self.pwm_channels[color].start(0)  # Start with 0% duty cycle (off)

    def _map_value(self, value, from_min, from_max, to_min, to_max):
        """Maps a value from one range to another."""
        return (value - from_min) * (to_max - to_min) / (from_max - from_min) + to_min

    def set_color(self, color_hex):
        """
        Sets the RGB LED to a specific color.
        
        Args:
            color_hex (int): A 24-bit integer representing the color (e.g., 0xFF0000 for red).
        """
        # Extract the 8-bit R, G, B values from the 24-bit color hex
        r_val = (color_hex & 0xFF0000) >> 16
        g_val = (color_hex & 0x00FF00) >> 8
        b_val = (color_hex & 0x0000FF)
        
        # Map the 0-255 color values to 0-100 PWM duty cycle
        r_duty = self._map_value(r_val, 0, 255, 0, 100)
        g_duty = self._map_value(g_val, 0, 255, 0, 100)
        b_duty = self._map_value(b_val, 0, 255, 0, 100)
        
        # Change the duty cycle for each color channel
        self.pwm_channels['red'].ChangeDutyCycle(r_duty)
        self.pwm_channels['green'].ChangeDutyCycle(g_duty)
        self.pwm_channels['blue'].ChangeDutyCycle(b_duty)

    def run(self):
        """Starts the main loop to detect motion and control the light."""
        print("Motion detection active. Press Ctrl+C to exit.")
        last_pir_state = None # To avoid unnecessary color changes
        
        while True:
            pir_state = GPIO.input(self.pir_pin)
            
            # Only update the color if the state has changed
            if pir_state != last_pir_state:
                if pir_state == GPIO.HIGH:
                    print("Motion Detected! -> LED Yellow")
                    self.set_color(self.MOTION_DETECTED_COLOR)
                else:
                    print("No Motion.       -> LED Blue")
                    self.set_color(self.IDLE_COLOR)
                last_pir_state = pir_state
            
            # A short delay to reduce CPU usage
            time.sleep(0.1)

    def cleanup(self):
        """Stops the PWM channels and cleans up GPIO resources."""
        print("\nCleaning up resources.")
        # The explicit pwm.stop() calls are redundant because GPIO.cleanup()
        # handles shutting down all channels used by the script.
        # Removing them prevents a race condition during script termination.
        GPIO.cleanup()

def main():
    """
    The main function to set up and run the motion-activated light.
    """
    # Pin numbers must be kept the same to match the hardware.
    # Using BCM numbering as in the original script.
    PIR_PIN = 17
    RED_PIN = 18
    GREEN_PIN = 27
    BLUE_PIN = 22

    # Create an instance of the motion light system.
    motion_light = MotionActivatedLight(
        pir_pin=PIR_PIN,
        red_pin=RED_PIN,
        green_pin=GREEN_PIN,
        blue_pin=BLUE_PIN
    )

    try:
        # Start the continuous operation.
        motion_light.run()
    except KeyboardInterrupt:
        # Gracefully handle Ctrl+C to exit.
        print("\nProgram terminated by user.")
    finally:
        # This block ensures that cleanup is always called, even if an error occurs.
        motion_light.cleanup()

if __name__ == '__main__':
    # This ensures the main() function is called only when the script is executed directly.
    main()

