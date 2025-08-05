#!/usr/bin/env python3

"""
2.2.6_mpu6050.py

This script provides a refactored, object-oriented version for reading data
from an MPU-6050 accelerometer and gyroscope sensor.

It is structured to be similar in clarity and organization to a well-written C
program, using a class to manage the sensor, a data structure to hold vector
information, and clear constants for configuration.
"""

import smbus
import math
import time

class MPU6050:
    """
    A class to interact with the MPU-6050 sensor, providing methods to
    read accelerometer, gyroscope, and rotation data.
    """

    # --- I2C and Register Constants ---
    I2C_ADDR = 0x68

    # Power Management Register
    REG_PWR_MGMT_1 = 0x6B

    # Accelerometer Registers
    REG_ACCEL_X_OUT = 0x3B
    REG_ACCEL_Y_OUT = 0x3D
    REG_ACCEL_Z_OUT = 0x3F

    # Gyroscope Registers
    REG_GYRO_X_OUT = 0x43
    REG_GYRO_Y_OUT = 0x45
    REG_GYRO_Z_OUT = 0x47

    # --- Scale Factors ---
    # From the MPU-6050 datasheet for default settings:
    # Gyroscope: FS_SEL=0 -> ±250 °/s -> Sensitivity: 131 LSB/°/s
    # Accelerometer: AFS_SEL=0 -> ±2g -> Sensitivity: 16384 LSB/g
    GYRO_SCALE_FACTOR = 131.0
    ACCEL_SCALE_FACTOR = 16384.0

    class Vector3D:
        """A simple data structure to hold 3D vector data (like a C struct)."""
        def __init__(self, x=0.0, y=0.0, z=0.0):
            self.x = x
            self.y = y
            self.z = z

        def __str__(self):
            # Formats the vector for clean printing.
            return f"X: {self.x:8.2f} | Y: {self.y:8.2f} | Z: {self.z:8.2f}"

    def __init__(self, bus_number=1):
        """
        Initializes the MPU-6050 sensor.
        Args:
            bus_number (int): The I2C bus number (1 for most Raspberry Pi models).
        """
        try:
            self.bus = smbus.SMBus(bus_number)
            # Wake up the sensor - it starts in sleep mode by default.
            self.bus.write_byte_data(self.I2C_ADDR, self.REG_PWR_MGMT_1, 0)
            print("MPU-6050 sensor initialized and woken up.")
        except IOError:
            print(f"Failed to initialize I2C device at address 0x{self.I2C_ADDR:X}.")
            print("Please check your connections and the I2C address.")
            exit(1) # Exit if sensor is not found

    def _read_word_2c(self, register):
        """
        Reads a 16-bit signed value (in two's complement format) from two
        adjacent 8-bit registers.
        Args:
            register (int): The starting register address.
        Returns:
            int: The signed 16-bit value.
        """
        high = self.bus.read_byte_data(self.I2C_ADDR, register)
        low = self.bus.read_byte_data(self.I2C_ADDR, register + 1)
        value = (high << 8) | low
        
        # Convert from two's complement
        if value >= 0x8000:
            return -((65535 - value) + 1)
        return value

    def get_gyro_data(self, scaled=True):
        """
        Reads gyroscope data (x, y, z axes).
        Args:
            scaled (bool): If True, returns scaled data in °/s. If False, returns raw integer data.
        Returns:
            Vector3D: A vector object containing the gyroscope data.
        """
        x = self._read_word_2c(self.REG_GYRO_X_OUT)
        y = self._read_word_2c(self.REG_GYRO_Y_OUT)
        z = self._read_word_2c(self.REG_GYRO_Z_OUT)

        if scaled:
            x /= self.GYRO_SCALE_FACTOR
            y /= self.GYRO_SCALE_FACTOR
            z /= self.GYRO_SCALE_FACTOR
        
        return self.Vector3D(x, y, z)

    def get_accel_data(self, scaled=True):
        """
        Reads accelerometer data (x, y, z axes).
        Args:
            scaled (bool): If True, returns scaled data in g's. If False, returns raw integer data.
        Returns:
            Vector3D: A vector object containing the accelerometer data.
        """
        x = self._read_word_2c(self.REG_ACCEL_X_OUT)
        y = self._read_word_2c(self.REG_ACCEL_Y_OUT)
        z = self._read_word_2c(self.REG_ACCEL_Z_OUT)

        if scaled:
            x /= self.ACCEL_SCALE_FACTOR
            y /= self.ACCEL_SCALE_FACTOR
            z /= self.ACCEL_SCALE_FACTOR

        return self.Vector3D(x, y, z)

    @staticmethod
    def _dist(a, b):
        """Calculates the Euclidean distance between two points (sqrt(a^2 + b^2))."""
        return math.sqrt(a*a + b*b)

    def get_rotation(self, accel_vector):
        """
        Calculates rotation around X and Y axes based on the gravity vector
        measured by the accelerometer.
        Args:
            accel_vector (Vector3D): The SCALED accelerometer data vector.
        Returns:
            dict: A dictionary with 'x' and 'y' rotation in degrees.
        """
        # Calculate rotation using atan2, which is robust and handles all quadrants.
        x_rad = math.atan2(accel_vector.y, self._dist(accel_vector.x, accel_vector.z))
        y_rad = math.atan2(accel_vector.x, self._dist(accel_vector.y, accel_vector.z))
        
        # Convert radians to degrees for human-readable output.
        x_deg = math.degrees(x_rad)
        y_deg = -math.degrees(y_rad)  # Y-rotation is often inverted depending on convention.
        
        return {'x': x_deg, 'y': y_deg}

def main():
    """Main function to initialize the sensor and run the data reading loop."""
    sensor = MPU6050()
    print("\nStarting sensor readings. Press Ctrl+C to exit.")
    
    try:
        while True:
            # Read data from the sensor
            gyro_data = sensor.get_gyro_data()
            accel_data = sensor.get_accel_data()
            rotation = sensor.get_rotation(accel_data)
            
            # Print the data in a clean, formatted block
            print("\n-----------------------------------------")
            print(f"--- Gyroscope (°/s) ---")
            print(gyro_data)
            
            print(f"--- Accelerometer (g) ---")
            print(accel_data)
            
            print("--- Calculated Rotation (°) ---")
            print(f"X-Rotation: {rotation['x']:6.1f} | Y-Rotation: {rotation['y']:6.1f}")
            
            # Wait before the next reading
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        print("Exiting.")

if __name__ == '__main__':
    # This ensures the main() function is called only when the script is executed directly.
    main()
