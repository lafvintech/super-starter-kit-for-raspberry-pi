#!/usr/bin/env python3
"""
28BYJ-48 Stepper Motor Control - Python version matching C implementation

This implementation replicates the C code's features:
1. 8-step half-step sequence for smoother rotation
2. Accurate step calculations (4096 steps per revolution)
3. Automatic continuous rotation
4. Precise speed control based on target RPM
"""

import RPi.GPIO as GPIO
import time

# Define the GPIO pins connected to the ULN2003 driver for the stepper motor
MOTOR_PINS = [18, 23, 24, 25]
NUM_MOTOR_PINS = len(MOTOR_PINS)

# 8-step half-step sequence for 28BYJ-48 motor (smoother rotation)
# This provides smoother rotation and more steps per revolution than 4-step mode
HALF_STEP_SEQUENCE = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

# Motor specifications
# The 28BYJ-48 motor has a gear ratio of ~64:1 and takes 64 steps per internal
# revolution in half-step mode. So, one full output revolution is 64 * 64 = 4096 steps.
STEPS_PER_REVOLUTION = 4096

# Speed configuration
TARGET_RPM = 15
# Calculate delay for target RPM (converted from microseconds to seconds)
STEP_DELAY = (60.0 / STEPS_PER_REVOLUTION / TARGET_RPM)

# Global step tracking
current_step = 0

def set_step(step):
    """
    Sets the motor pins to a specific step in the sequence.
    Parameters: step - The step number (0-7) in the half-step sequence.
    """
    for i in range(NUM_MOTOR_PINS):
        GPIO.output(MOTOR_PINS[i], HALF_STEP_SEQUENCE[step][i])

def rotate_steps(steps, clockwise):
    """
    Rotates the motor by a given number of steps in a specified direction.
    Parameters:
        steps - The number of steps to rotate
        clockwise - True for clockwise, False for anti-clockwise
    """
    global current_step
    step_increment = 1 if clockwise else -1
    
    for i in range(steps):
        current_step = (current_step + step_increment) % 8
        set_step(current_step)
        time.sleep(STEP_DELAY)

def setup_stepper():
    """
    Initializes GPIO pins for the stepper motor.
    Returns: 0 on success, 1 on failure.
    """
    try:
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        
        for pin in MOTOR_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)  # Initialize all pins to LOW
        
        print("Stepper motor GPIO setup successful!")
        print(f"Motor pins: {MOTOR_PINS}")
        print(f"Steps per revolution: {STEPS_PER_REVOLUTION}")
        print(f"Target RPM: {TARGET_RPM}")
        print(f"Step delay: {STEP_DELAY:.6f} seconds")
        return 0
        
    except Exception as e:
        print(f"Failed to setup stepper motor: {e}")
        return 1

def continuous_rotation():
    """
    Main rotation loop - automatically alternates between clockwise and anti-clockwise.
    This function runs indefinitely until interrupted.
    """
    try:
        cycle_count = 0
        
        while True:
            cycle_count += 1
            print(f"\n=== Rotation Cycle {cycle_count} ===")
            
            # Rotate one full revolution clockwise
            print("-> Clockwise rotation...")
            rotate_steps(STEPS_PER_REVOLUTION, True)
            print("Clockwise rotation complete")
            time.sleep(1)  # Pause for 1 second
            
            # Rotate one full revolution anti-clockwise  
            print("<- Anti-clockwise rotation...")
            rotate_steps(STEPS_PER_REVOLUTION, False)
            print("Anti-clockwise rotation complete")
            time.sleep(1)  # Pause for 1 second
            
    except KeyboardInterrupt:
        print("\nStepper motor rotation interrupted by user")
        raise  # Re-raise to be handled by main()

def destroy():
    """
    Clean up function for GPIO resources.
    Ensures all motor pins are turned off and GPIO is properly cleaned up.
    """
    try:
        # Turn off all motor pins
        for pin in MOTOR_PINS:
            GPIO.output(pin, GPIO.LOW)
        
        GPIO.cleanup()
        print("Stepper motor stopped and GPIO cleaned up")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """
    Main function - matches C code structure.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    print("28BYJ-48 Stepper Motor Control")
    print("Rotating one full revolution clockwise, then one anti-clockwise")
    print("Press Ctrl+C to stop...")
    
    # Initialize the stepper motor
    if setup_stepper() != 0:
        return 1  # Exit if setup fails
    
    try:
        # Start continuous rotation
        continuous_rotation()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        destroy()
        return 0
        
    except Exception as e:
        print(f"An error occurred: {e}")
        destroy()
        return 1

if __name__ == '__main__':
    exit_code = main()
    exit(exit_code)