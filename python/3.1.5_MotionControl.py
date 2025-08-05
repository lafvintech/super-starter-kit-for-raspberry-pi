#!/usr/bin/env python3
"""
Motion Control System
MPU6050 Accelerometer + Stepper Motor Control

This program reads tilt data from MPU6050 sensor and controls
a stepper motor based on the tilt angle threshold.
"""

import time
import math
import signal
import sys
try:
    import smbus
    import RPi.GPIO as GPIO
except ImportError:
    print("❌ Required libraries not found!")
    print("Please install: sudo apt-get install python3-smbus python3-rpi.gpio")
    sys.exit(1)

# --- Hardware Configuration ---
MPU6050_ADDR = 0x68
MPU6050_PWR_MGMT_1 = 0x6B
ACCEL_SCALE = 16384.0
TILT_THRESHOLD = 45.0

# --- Pin Configuration ---
STEPPER_PINS = [18, 23, 24, 25]  # GPIO pins for stepper motor

# --- Motor Parameters ---
RPM = 15
STEPS_PER_REVOLUTION = 2048

# --- Global Variables ---
bus = None
step_delay = 0
current_state = 's'  # 's' = stopped, 'c' = clockwise, 'a' = anti-clockwise

class MotionController:
    """Motion control system combining MPU6050 and stepper motor"""
    
    def __init__(self):
        """Initialize the motion controller"""
        self.setup_hardware()
    
    def read_mpu6050_word(self, reg_addr):
        """
        Read 16-bit value from MPU6050 register (two's complement)
        
        Args:
            reg_addr: Starting register address
            
        Returns:
            Signed 16-bit value
        """
        try:
            high_byte = bus.read_byte_data(MPU6050_ADDR, reg_addr)
            low_byte = bus.read_byte_data(MPU6050_ADDR, reg_addr + 1)
            
            value = (high_byte << 8) + low_byte
            
            # Convert to signed value if necessary
            if value >= 0x8000:
                value = -(65536 - value)
                
            return value
        except Exception as e:
            print(f"❌ Error reading MPU6050: {e}")
            return 0
    
    def calculate_distance(self, a, b):
        """
        Calculate distance for rotation calculation
        
        Args:
            a: First component
            b: Second component
            
        Returns:
            Distance value
        """
        return math.sqrt((a * a) + (b * b))
    
    def get_tilt_angle(self, x, y, z):
        """
        Calculate Y-axis rotation angle from accelerometer data
        
        Args:
            x: X-axis acceleration
            y: Y-axis acceleration
            z: Z-axis acceleration
            
        Returns:
            Y rotation angle in degrees
        """
        radians = math.atan2(x, self.calculate_distance(y, z))
        return -(radians * (180.0 / math.pi))
    
    def read_tilt_sensor(self):
        """
        Read MPU6050 and calculate tilt angle
        
        Returns:
            Current tilt angle in degrees
        """
        # Read raw accelerometer values
        raw_x = self.read_mpu6050_word(0x3B)
        raw_y = self.read_mpu6050_word(0x3D)
        raw_z = self.read_mpu6050_word(0x3F)
        
        # Convert to scaled values
        accel_x = raw_x / ACCEL_SCALE
        accel_y = raw_y / ACCEL_SCALE
        accel_z = raw_z / ACCEL_SCALE
        
        return self.get_tilt_angle(accel_x, accel_y, accel_z)
    
    def rotate_stepper(self, direction):
        """
        Rotate stepper motor one step
        
        Args:
            direction: 'c' for clockwise, 'a' for anti-clockwise
        """
        if direction == 'c':
            # Clockwise rotation sequence
            for step in range(4):
                for pin in range(4):
                    GPIO.output(STEPPER_PINS[pin], (0x99 >> step) & (0x08 >> pin))
                time.sleep(step_delay / 1000000.0)  # Convert microseconds to seconds
        elif direction == 'a':
            # Anti-clockwise rotation sequence
            for step in range(4):
                for pin in range(4):
                    GPIO.output(STEPPER_PINS[pin], (0x99 << step) & (0x80 >> pin))
                time.sleep(step_delay / 1000000.0)  # Convert microseconds to seconds
    
    def setup_hardware(self):
        """Initialize hardware components"""
        global bus, step_delay
        
        print("🔧 Initializing Motion Control System...")
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Setup stepper motor pins
        for pin in STEPPER_PINS:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        
        # Setup MPU6050
        try:
            bus = smbus.SMBus(1)  # I2C bus 1
            bus.write_byte_data(MPU6050_ADDR, MPU6050_PWR_MGMT_1, 0x00)  # Wake up MPU6050
            
            # Verify MPU6050 is responding
            reg_value = bus.read_byte_data(MPU6050_ADDR, MPU6050_PWR_MGMT_1)
            print(f"📊 MPU6050 initialized (Register 0x6B = 0x{reg_value:02X})")
            
        except Exception as e:
            print(f"❌ MPU6050 setup failed: {e}")
            self.cleanup_exit(None)
        
        # Calculate step delay for desired RPM
        step_delay = (60000000 // RPM) // STEPS_PER_REVOLUTION
        
        print(f"🔄 Stepper motor ready (RPM: {RPM}, Step delay: {step_delay} μs)")
        print(f"✅ System ready! Tilt threshold: ±{TILT_THRESHOLD} degrees\n")
    
    def motion_control_loop(self):
        """Main control loop"""
        global current_state
        
        print("🎮 Motion control active...")
        print("📱 Tilt device left/right to control stepper motor")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                tilt_angle = self.read_tilt_sensor()
                new_state = 's'  # Default to stopped
                
                if tilt_angle >= TILT_THRESHOLD:
                    new_state = 'a'
                    self.rotate_stepper('a')
                elif tilt_angle <= -TILT_THRESHOLD:
                    new_state = 'c'
                    self.rotate_stepper('c')
                
                # Only print when state changes
                if new_state != current_state:
                    if new_state == 'a':
                        print(f"➡️ Tilt: {tilt_angle:.1f}° → Rotating anti-clockwise")
                    elif new_state == 'c':
                        print(f"⬅️ Tilt: {tilt_angle:.1f}° → Rotating clockwise")
                    else:
                        print("⏹️ Centered → Motor stopped")
                    current_state = new_state
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            self.cleanup_exit(None)
    
    def cleanup_exit(self, signum):
        """Clean up and exit"""
        print("\n🧹 Shutting down motion control system...")
        
        # Turn off all motor pins
        for pin in STEPPER_PINS:
            GPIO.output(pin, GPIO.LOW)
        
        # Cleanup GPIO
        GPIO.cleanup()
        
        print("✅ Goodbye!")
        sys.exit(0)

def main():
    """Main function"""
    print("=== Motion Control System ===")
    print("MPU6050 + Stepper Motor Control\n")
    
    # Create motion controller
    controller = MotionController()
    
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, controller.cleanup_exit)
    
    # Start control loop
    controller.motion_control_loop()

if __name__ == '__main__':
    main()