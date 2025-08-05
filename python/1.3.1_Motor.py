#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# Motor control pin definitions (BCM numbering)
MOTOR_PIN1 = 17    # Motor direction pin 1
MOTOR_PIN2 = 27    # Motor direction pin 2  
MOTOR_ENABLE = 22  # Motor enable pin (speed control)

# Timing constants
RUN_DURATION = 3.0   # Motor run time in seconds (3 seconds)
STOP_DURATION = 3.0  # Motor stop time in seconds (3 seconds)
SHORT_DELAY = 0.1    # Short delay for state transitions

# Motor direction definitions
CLOCKWISE = 1
ANTI_CLOCKWISE = -1
STOP = 0

def setupHardware():
    """
    Initializes GPIO pins for motor control.
    Returns: 0 on success, 1 on failure.
    """
    try:
        # Set the GPIO modes to BCM Numbering
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Configure motor control pins as outputs
        GPIO.setup(MOTOR_PIN1, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(MOTOR_PIN2, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(MOTOR_ENABLE, GPIO.OUT, initial=GPIO.LOW)
        
        print("Motor control hardware initialized successfully!")
        return 0
        
    except Exception as e:
        print(f"Failed to setup GPIO: {e}")
        return 1

def setMotorDirection(direction):
    """
    Controls motor direction and enable state.
    Parameters: direction - Motor direction (CLOCKWISE, ANTI_CLOCKWISE, or STOP)
    """
    if direction == CLOCKWISE:
        print("Motor: Clockwise rotation")
        # Set direction
        GPIO.output(MOTOR_PIN1, GPIO.HIGH)
        GPIO.output(MOTOR_PIN2, GPIO.LOW)
        # Enable the motor
        GPIO.output(MOTOR_ENABLE, GPIO.HIGH)
        
    elif direction == ANTI_CLOCKWISE:
        print("Motor: Anti-clockwise rotation")
        # Set direction
        GPIO.output(MOTOR_PIN1, GPIO.LOW)
        GPIO.output(MOTOR_PIN2, GPIO.HIGH)
        # Enable the motor
        GPIO.output(MOTOR_ENABLE, GPIO.HIGH)
        
    elif direction == STOP:
        print("Motor: Stop")
        # Disable the motor
        GPIO.output(MOTOR_ENABLE, GPIO.LOW)
    
    time.sleep(SHORT_DELAY)  # Small delay for state transition

def motorControlLoop():
    """
    Main motor control loop.
    """
    # Define a dictionary to make the script more readable
    # CW as clockwise, CCW as counterclockwise, STOP as stop
    directions = {'CW': CLOCKWISE, 'CCW': ANTI_CLOCKWISE, 'STOP': STOP}
    
    while True:
        # Run motor clockwise for 3 seconds
        setMotorDirection(directions['CW'])
        time.sleep(RUN_DURATION)
        
        # Stop motor for 3 seconds
        setMotorDirection(directions['STOP'])
        time.sleep(STOP_DURATION)
        
        # Run motor anti-clockwise for 3 seconds
        setMotorDirection(directions['CCW'])
        time.sleep(RUN_DURATION)
        
        # Stop motor for 3 seconds
        setMotorDirection(directions['STOP'])
        time.sleep(STOP_DURATION)

def destroy():
    """
    Clean up function for GPIO resources.
    """
    # Stop the motor
    GPIO.output(MOTOR_ENABLE, GPIO.LOW)
    print("Motor stopped")
    
    # Release resource
    GPIO.cleanup()
    print("GPIO cleanup completed")

def main():
    """
    Main function.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    # Initialize hardware
    if setupHardware() != 0:
        return 1  # Exit if setup fails
    
    try:
        # Start motor control loop
        motorControlLoop()
    except KeyboardInterrupt:
        # When 'Ctrl+C' is pressed, the program destroy() will be executed
        print("\nProgram interrupted by user")
        destroy()
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        destroy()
        return 1

# If run this script directly, do:
if __name__ == '__main__':
    main()