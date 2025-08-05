#!/usr/bin/env python3
"""
SG90 Servo Control - Optimized based on least-jitter version

Key principles from the most stable version:
1. 5-degree steps (not 1-degree) - reduces calculation frequency
2. Fast timing: 2ms forward, 1ms reverse - matches servo response
3. Minimal optimizations - less complexity = more stability
4. Clean, simple code structure
"""

import RPi.GPIO as GPIO
import time

SERVO_MIN_PULSE = 500
SERVO_MAX_PULSE = 2500
ServoPin = 18

# Sweep configuration - based on most stable version
SWEEP_START = 0      # Start angle (degrees)
SWEEP_END = 180      # End angle (degrees)  
SWEEP_STEP = 5       # 5-degree steps (proven most stable)
SWEEP_SPEED_FWD = 0.002  # Forward speed: 2ms (from stable version)
SWEEP_SPEED_REV = 0.001  # Reverse speed: 1ms (from stable version)

def map(value, inMin, inMax, outMin, outMax):
    """Simple linear mapping function - same as stable version"""
    return (outMax - outMin) * (value - inMin) / (inMax - inMin) + outMin

def setup():
    """Initialize servo - minimal setup based on stable version"""
    global p
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(ServoPin, GPIO.OUT)
    GPIO.output(ServoPin, GPIO.LOW)
    p = GPIO.PWM(ServoPin, 50)
    p.start(0)
    print("Servo initialized - using proven stable parameters")

def setAngle(angle):
    """Set servo angle - exact same calculation as stable version"""
    angle = max(0, min(180, angle))
    pulse_width = map(angle, 0, 180, SERVO_MIN_PULSE, SERVO_MAX_PULSE)
    pwm = map(pulse_width, 0, 20000, 0, 100)
    p.ChangeDutyCycle(pwm)
    # No settle time - stable version doesn't use it

def loop():
    """Main loop - exact timing from most stable version"""
    cycle_count = 0
    
    while True:
        cycle_count += 1
        
        # Forward sweep: 0° to 180° (same as stable version)
        for i in range(SWEEP_START, SWEEP_END + 1, SWEEP_STEP):
            setAngle(i)
            time.sleep(SWEEP_SPEED_FWD)  # 2ms - proven stable timing
        time.sleep(1)  # 1 second pause - same as stable version
        
        # Reverse sweep: 180° to 0° (same as stable version)  
        for i in range(SWEEP_END, SWEEP_START - 1, -SWEEP_STEP):
            setAngle(i)
            time.sleep(SWEEP_SPEED_REV)  # 1ms - proven stable timing
        time.sleep(1)  # 1 second pause - same as stable version
        
        # Minimal output to avoid interfering with PWM
        if cycle_count % 5 == 0:
            print(f"Completed {cycle_count} stable cycles")

def destroy():
    """Clean shutdown - same as stable version"""
    p.stop()
    GPIO.cleanup()
    print("Servo stopped")

if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        print("\nProgram interrupted")
        destroy()