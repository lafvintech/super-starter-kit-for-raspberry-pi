#!/usr/bin/env python3

"""
1.3.5_LedBarGraph.py

Simple LED Bar Graph Controller
This program controls 10 LEDs with different animation patterns.
本程序控制10个LED灯条，具有不同的动画模式。

Animation patterns:
- Odd LEDs (奇数位置LED): 0, 2, 4, 6, 8
- Even LEDs (偶数位置LED): 1, 3, 5, 7, 9  
- All LEDs sequence (所有LED序列)
"""

import RPi.GPIO as GPIO
import time
import signal
import sys

class LedBarGraph:
    """
    A class to control a 10-LED bar graph with various animation patterns.
    """
    
    def __init__(self):
        """
        Initialize the LED bar graph controller.
        """
        # Pin configuration - these must match your hardware setup
        # Using BCM numbering that corresponds to wiringPi pins 0-10
        self.led_pins = [17, 18, 27, 22, 23, 24, 25, 2, 3, 8]  # BCM pins corresponding to wiringPi 0,1,2,3,4,5,6,8,9,10
        
        # Setup GPIO and LEDs
        self._setup_gpio()
        self._setup_leds()
        
        # Setup signal handler for graceful exit
        signal.signal(signal.SIGINT, self._cleanup_exit)

    def _setup_gpio(self):
        """
        Configure GPIO settings.
        """
        GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
        GPIO.setwarnings(False)  # Disable GPIO warnings

    def _setup_leds(self):
        """
        Initialize LED pins and turn them all off.
        """
        print("🔧 Setting up LED bar graph...")
        
        for pin in self.led_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Turn off LEDs (assuming common anode setup)
        
        print("✅ LED setup complete! Ready to start animations.")
        print()

    def light_odd_leds(self):
        """
        Light odd-positioned LEDs (positions 0, 2, 4, 6, 8).
        """
        print("🔸 Lighting odd pattern LEDs...")
        
        for i in range(0, 10, 2):  # 0, 2, 4, 6, 8
            GPIO.output(self.led_pins[i], GPIO.LOW)   # Turn ON
            time.sleep(0.3)
            GPIO.output(self.led_pins[i], GPIO.HIGH)  # Turn OFF

    def light_even_leds(self):
        """
        Light even-positioned LEDs (positions 1, 3, 5, 7, 9).
        """
        
        for i in range(1, 10, 2):  # 1, 3, 5, 7, 9
            GPIO.output(self.led_pins[i], GPIO.LOW)   # Turn ON
            time.sleep(0.3)
            GPIO.output(self.led_pins[i], GPIO.HIGH)  # Turn OFF

    def light_all_leds(self):
        """
        Light all LEDs in sequence from 0 to 9.
        """
        print("🔸 Lighting all LEDs in sequence...")
        
        for i in range(10):
            GPIO.output(self.led_pins[i], GPIO.LOW)   # Turn ON
            time.sleep(0.3)
            GPIO.output(self.led_pins[i], GPIO.HIGH)  # Turn OFF

    def run_animation_cycle(self):
        """
        Run one complete animation cycle with all patterns.
        """
        # Execute animation patterns in sequence
        self.light_odd_leds()
        time.sleep(0.3)
        
        self.light_even_leds()
        time.sleep(0.3)
        
        self.light_all_leds()
        time.sleep(0.3)
        
        print("--- Animation cycle complete ---")
        print()

    def run(self):
        """
        Start the main animation loop.
        """
        print("🚀 Starting LED bar graph animations...")
        print("Press Ctrl+C to stop and exit.")
        print()
        
        try:
            while True:
                self.run_animation_cycle()
                
        except KeyboardInterrupt:
            # This should be caught by the signal handler, but just in case
            self._cleanup_exit(None)

    def _cleanup_exit(self, signal_num):
        """
        Clean up GPIO resources and exit gracefully.
        
        Args:
            signal_num: The signal number (for signal handler compatibility)
        """
        print("\n🧹 Turning off all LEDs...")
        
        # Turn off all LEDs
        for pin in self.led_pins:
            GPIO.output(pin, GPIO.HIGH)  # Turn OFF
        
        # Clean up GPIO resources
        GPIO.cleanup()
        
        print("✅ Cleanup complete. Goodbye!")
        sys.exit(0)

def main():
    """
    Main function to initialize and run the LED bar graph controller.
    """
    print("=" * 40)
    print("=" * 40)
    print("This program controls 10 LEDs with animation patterns.")
    print("=" * 40)
    print()
    
    try:
        # Create and run the LED controller
        led_controller = LedBarGraph()
        led_controller.run()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        GPIO.cleanup()
        sys.exit(1)

if __name__ == '__main__':
    # Execute the main function when the script is run directly
    main()