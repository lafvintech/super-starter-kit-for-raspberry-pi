#include <wiringPiI2C.h>
#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h> // Required for exit()
#include <math.h>

// --- MPU6050 Constants ---
#define MPU6050_I2C_ADDR 0x68

// Register Addresses
#define REG_PWR_MGMT_1   0x6B
#define REG_ACCEL_X_OUT  0x3B
#define REG_ACCEL_Y_OUT  0x3D
#define REG_ACCEL_Z_OUT  0x3F
#define REG_GYRO_X_OUT   0x43
#define REG_GYRO_Y_OUT   0x45
#define REG_GYRO_Z_OUT   0x47

// Sensitivity Scale Factors from datasheet
// Gyroscope: ±250 °/s => 131 LSB/°/s
// Accelerometer: ±2g => 16384 LSB/g
const double GYRO_SCALE_FACTOR = 131.0;
const double ACCEL_SCALE_FACTOR = 16384.0;

// Struct to hold 3D vector data (raw and scaled)
typedef struct {
    int x_raw, y_raw, z_raw;
    double x_scaled, y_scaled, z_scaled;
} Vector3D;

/**
 * @brief Reads a 16-bit word (two 8-bit registers) from the I2C device.
 * MPU6050 stores values in two's complement format.
 * @param fd The file descriptor for the I2C device.
 * @param addr The starting register address.
 * @return The signed 16-bit integer value.
 */
int read_sensor_word(int fd, int addr) {
    int high = wiringPiI2CReadReg8(fd, addr);
    int low = wiringPiI2CReadReg8(fd, addr + 1);
    int value = (high << 8) | low;
    
    // Convert from two's complement
    if (value >= 0x8000) {
        value = -(65536 - value);
    }
    return value;
}

/**
 * @brief Initializes the MPU6050 sensor.
 * @return The file descriptor for the I2C device.
 */
int setup_mpu6050() {
    int fd = wiringPiI2CSetup(MPU6050_I2C_ADDR);
    if (fd == -1) {
        printf("Failed to setup I2C device at address 0x%X.\n", MPU6050_I2C_ADDR);
        exit(1);
    }
    // Wake up the MPU6050 by writing 0x00 to the power management register.
    wiringPiI2CWriteReg8(fd, REG_PWR_MGMT_1, 0x00);
    return fd;
}

/**
 * @brief Reads all raw data from the gyroscope and populates the Vector3D struct.
 * @param fd File descriptor for the I2C device.
 * @param gyro A pointer to the Vector3D struct to fill.
 */
void read_gyro_data(int fd, Vector3D* gyro) {
    gyro->x_raw = read_sensor_word(fd, REG_GYRO_X_OUT);
    gyro->y_raw = read_sensor_word(fd, REG_GYRO_Y_OUT);
    gyro->z_raw = read_sensor_word(fd, REG_GYRO_Z_OUT);
    gyro->x_scaled = gyro->x_raw / GYRO_SCALE_FACTOR;
    gyro->y_scaled = gyro->y_raw / GYRO_SCALE_FACTOR;
    gyro->z_scaled = gyro->z_raw / GYRO_SCALE_FACTOR;
}

/**
 * @brief Reads all raw data from the accelerometer and populates the Vector3D struct.
 * @param fd File descriptor for the I2C device.
 * @param accel A pointer to the Vector3D struct to fill.
 */
void read_accel_data(int fd, Vector3D* accel) {
    accel->x_raw = read_sensor_word(fd, REG_ACCEL_X_OUT);
    accel->y_raw = read_sensor_word(fd, REG_ACCEL_Y_OUT);
    accel->z_raw = read_sensor_word(fd, REG_ACCEL_Z_OUT);
    accel->x_scaled = accel->x_raw / ACCEL_SCALE_FACTOR;
    accel->y_scaled = accel->y_raw / ACCEL_SCALE_FACTOR;
    accel->z_scaled = accel->z_raw / ACCEL_SCALE_FACTOR;
}

/**
 * @brief Calculates the distance between two points in 2D space.
 */
double dist(double a, double b) {
    return sqrt(a * a + b * b);
}

/**
 * @brief Calculates rotation around the X and Y axes based on accelerometer data.
 * @param accel A pointer to the accelerometer data.
 * @param x_rotation A pointer to store the calculated X-axis rotation.
 * @param y_rotation A pointer to store the calculated Y-axis rotation.
 */
void calculate_rotation(const Vector3D* accel, double* x_rotation, double* y_rotation) {
    *x_rotation = atan2(accel->y_scaled, dist(accel->x_scaled, accel->z_scaled)) * 180.0 / M_PI;
    *y_rotation = -atan2(accel->x_scaled, dist(accel->y_scaled, accel->z_scaled)) * 180.0 / M_PI;
}

/**
 * @brief Main function.
 */
int main() {
    int fd = setup_mpu6050();
    Vector3D gyroscope, accelerometer;
    double x_rot, y_rot;

    printf("MPU6050 sensor reading started.\n\n");

    while (1) {
        read_gyro_data(fd, &gyroscope);
        read_accel_data(fd, &accelerometer);
        calculate_rotation(&accelerometer, &x_rot, &y_rot);
        
        printf("--- Gyroscope (°/s) ---\n");
        printf("X: %8.2f | Y: %8.2f | Z: %8.2f\n", gyroscope.x_scaled, gyroscope.y_scaled, gyroscope.z_scaled);
        
        printf("--- Accelerometer (g) ---\n");
        printf("X: %8.2f | Y: %8.2f | Z: %8.2f\n", accelerometer.x_scaled, accelerometer.y_scaled, accelerometer.z_scaled);
        
        printf("--- Calculated Rotation (°) ---\n");
        printf("X-Rotation: %6.1f | Y-Rotation: %6.1f\n", x_rot, y_rot);

        printf("\n----------------------------------\n\n");
        delay(500);
    }

    return 0; // Unreachable
}
