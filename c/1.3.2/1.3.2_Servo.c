#include <wiringPi.h>
#include <softPwm.h>
#include <stdio.h>
#include <stdlib.h> // Required for exit()

// Define the GPIO pin for the servo motor.
#define SERVO_PIN 1

// --- Servo PWM Configuration ---
// These values are typical for SG90 servos and may need calibration for others.
// The PWM period is 20ms (50Hz), so the total range is 200 ticks for softPwm.
#define PWM_PERIOD      200 // 200 * 100us = 20ms period
#define PWM_MIN_PULSE   5   // Minimum pulse width for 0 degrees (0.5ms)
#define PWM_MAX_PULSE   25  // Maximum pulse width for 180 degrees (2.5ms)
#define ANGLE_MIN       0
#define ANGLE_MAX       180

/**
 * @brief Converts an angle (0-180) to a corresponding PWM value for the servo.
 * @param angle The desired angle in degrees.
 * @return The calculated PWM value.
 */
int angle_to_pwm(int angle) {
    // Constrain the angle to the valid range.
    if (angle < ANGLE_MIN) angle = ANGLE_MIN;
    if (angle > ANGLE_MAX) angle = ANGLE_MAX;
    
    // Linearly map the angle (0-180) to the PWM pulse range (5-25).
    return (int)(((double)(angle - ANGLE_MIN) / (ANGLE_MAX - ANGLE_MIN)) * (PWM_MAX_PULSE - PWM_MIN_PULSE) + PWM_MIN_PULSE);
}

/**
 * @brief Sets the servo to a specific angle.
 * @param angle The target angle (0 to 180 degrees).
 */
void set_servo_angle(int angle) {
    int pwm_value = angle_to_pwm(angle);
    softPwmWrite(SERVO_PIN, pwm_value);
}

/**
 * @brief Initializes wiringPi and creates a software PWM pin for the servo.
 */
void setup_servo() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }
    // Create a software PWM pin with a 0-200 range (20ms period).
    if (softPwmCreate(SERVO_PIN, 0, PWM_PERIOD) != 0) {
        printf("Failed to create softPwm pin!\n");
        exit(1);
    }
}

/**
 * @brief Main application loop to sweep the servo back and forth.
 */
void servo_sweep_loop() {
    while (1) {
        printf("Sweeping from %d to %d degrees...\n", ANGLE_MIN, ANGLE_MAX);
        for (int angle = ANGLE_MIN; angle <= ANGLE_MAX; angle++) {
            set_servo_angle(angle);
            delay(10); // A small delay to control the speed of the sweep.
        }
        delay(1000); // Pause at the end position.

        printf("Sweeping from %d to %d degrees...\n", ANGLE_MAX, ANGLE_MIN);
        for (int angle = ANGLE_MAX; angle >= ANGLE_MIN; angle--) {
            set_servo_angle(angle);
            delay(10);
        }
        delay(1000); // Pause at the start position.
    }
}

/**
 * @brief Main function.
 * @return Integer status code.
 */
int main(void) {
    setup_servo();
    servo_sweep_loop();
    return 0; // Unreachable code.
}

