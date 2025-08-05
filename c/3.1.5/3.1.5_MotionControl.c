#include <wiringPiI2C.h>
#include <wiringPi.h>
#include <stdio.h>
#include <math.h>
#include <signal.h>
#include <stdlib.h>

// --- Hardware Configuration ---
#define MPU6050_ADDR        0x68
#define MPU6050_PWR_MGMT_1  0x6B
#define ACCEL_SCALE         16384.0
#define TILT_THRESHOLD      45.0

// --- Pin Configuration ---
const int stepper_pins[4] = {1, 4, 5, 6};

// --- Motor Parameters ---
const int rpm = 15;
const int steps_per_revolution = 2048;

// --- Global Variables ---
int i2c_handle;
int step_delay;
char current_state = 's';  // 's' = stopped, 'c' = clockwise, 'a' = anti-clockwise

/**
 * @brief Read 16-bit value from MPU6050 register (two's complement)
 * @param reg_addr Starting register address
 * @return Signed 16-bit value
 */
int read_mpu6050_word(int reg_addr) {
    int high_byte = wiringPiI2CReadReg8(i2c_handle, reg_addr);
    int low_byte = wiringPiI2CReadReg8(i2c_handle, reg_addr + 1);
    
    int value = (high_byte << 8) + low_byte;
    
    // Convert to signed value if necessary
    if (value >= 0x8000) {
        value = -(65536 - value);
    }
    
    return value;
}

/**
 * @brief Calculate distance for rotation calculation
 * @param a First component
 * @param b Second component
 * @return Distance value
 */
double calculate_distance(double a, double b) {
    return sqrt((a * a) + (b * b));
}

/**
 * @brief Calculate Y-axis rotation angle from accelerometer data
 * @param x X-axis acceleration
 * @param y Y-axis acceleration  
 * @param z Z-axis acceleration
 * @return Y rotation angle in degrees
 */
double get_tilt_angle(double x, double y, double z) {
    double radians = atan2(x, calculate_distance(y, z));
    return -(radians * (180.0 / M_PI));
}

/**
 * @brief Read MPU6050 and calculate tilt angle
 * @return Current tilt angle in degrees
 */
double read_tilt_sensor() {
    // Read raw accelerometer values
    int raw_x = read_mpu6050_word(0x3B);
    int raw_y = read_mpu6050_word(0x3D);
    int raw_z = read_mpu6050_word(0x3F);
    
    // Convert to scaled values
    double accel_x = raw_x / ACCEL_SCALE;
    double accel_y = raw_y / ACCEL_SCALE;
    double accel_z = raw_z / ACCEL_SCALE;
    
    return get_tilt_angle(accel_x, accel_y, accel_z);
}

/**
 * @brief Rotate stepper motor one step
 * @param direction 'c' for clockwise, 'a' for anti-clockwise
 */
void rotate_stepper(char direction) {
    if (direction == 'c') {
        // Clockwise rotation sequence
        for (int step = 0; step < 4; step++) {
            for (int pin = 0; pin < 4; pin++) {
                digitalWrite(stepper_pins[pin], (0x99 >> step) & (0x08 >> pin));
            }
            delayMicroseconds(step_delay);
        }
    } else if (direction == 'a') {
        // Anti-clockwise rotation sequence
        for (int step = 0; step < 4; step++) {
            for (int pin = 0; pin < 4; pin++) {
                digitalWrite(stepper_pins[pin], (0x99 << step) & (0x80 >> pin));
            }
            delayMicroseconds(step_delay);
        }
    }
}

/**
 * @brief Initialize hardware components
 */
void setup_hardware() {
    printf("🔧 Initializing Motion Control System...\n");
    
    // Initialize wiringPi
    if (wiringPiSetup() == -1) {
        printf("❌ wiringPi setup failed!\n");
        exit(1);
    }
    
    // Setup MPU6050
    i2c_handle = wiringPiI2CSetup(MPU6050_ADDR);
    wiringPiI2CWriteReg8(i2c_handle, MPU6050_PWR_MGMT_1, 0x00);  // Wake up MPU6050
    printf("📊 MPU6050 initialized (Register 0x6B = 0x%02X)\n", 
           wiringPiI2CReadReg8(i2c_handle, MPU6050_PWR_MGMT_1));
    
    // Setup stepper motor pins
    for (int i = 0; i < 4; i++) {
        pinMode(stepper_pins[i], OUTPUT);
    }
    
    // Calculate step delay for desired RPM
    step_delay = (60000000 / rpm) / steps_per_revolution;
    
    printf("🔄 Stepper motor ready (RPM: %d, Step delay: %d μs)\n", rpm, step_delay);
    printf("✅ System ready! Tilt threshold: ±%.1f degrees\n\n", TILT_THRESHOLD);
}

/**
 * @brief Clean up and exit
 */
void cleanup_exit(int sig) {
    printf("\n🧹 Shutting down motion control system...\n");
    
    // Turn off all motor pins
    for (int i = 0; i < 4; i++) {
        digitalWrite(stepper_pins[i], LOW);
    }
    
    printf("✅ Goodbye!\n");
    exit(0);
}

/**
 * @brief Main control loop
 */
void motion_control_loop() {
    printf("🎮 Motion control active...\n");
    printf("📱 Tilt device left/right to control stepper motor\n");
    printf("Press Ctrl+C to exit\n\n");
    
    while (1) {
        double tilt_angle = read_tilt_sensor();
        char new_state = 's';  // Default to stopped
        
        if (tilt_angle >= TILT_THRESHOLD) {
            new_state = 'a';
            rotate_stepper('a');
        } else if (tilt_angle <= -TILT_THRESHOLD) {
            new_state = 'c';
            rotate_stepper('c');
        }
        
        // Only print when state changes
        if (new_state != current_state) {
            if (new_state == 'a') {
                printf("➡️ Tilt: %.1f° → Rotating anti-clockwise\n", tilt_angle);
            } else if (new_state == 'c') {
                printf("⬅️ Tilt: %.1f° → Rotating clockwise\n", tilt_angle);
            } else {
                printf("⏹️ Centered → Motor stopped\n");
            }
            current_state = new_state;
        }
    }
}

/**
 * @brief Main function
 */
int main(void) {
    // Handle Ctrl+C
    signal(SIGINT, cleanup_exit);
    
    printf("=== Motion Control System ===\n");
    printf("MPU6050 + Stepper Motor Control\n\n");
    
    // Initialize hardware
    setup_hardware();
    
    // Start control loop
    motion_control_loop();
    
    return 0;
}
