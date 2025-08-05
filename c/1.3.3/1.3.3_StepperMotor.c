#include <stdio.h>
#include <stdlib.h> // Required for exit()
#include <wiringPi.h>
#include <termios.h> // For non-blocking getchar
#include <unistd.h>  // For STDIN_FILENO

// Define the GPIO pins connected to the ULN2003 driver for the stepper motor.
const int MOTOR_PINS[] = {1, 4, 5, 6};
const int NUM_MOTOR_PINS = sizeof(MOTOR_PINS) / sizeof(MOTOR_PINS[0]);

// This 8-step sequence corresponds to half-step mode for a 28BYJ-48 motor,
// which provides smoother rotation and more steps per revolution.
const int HALF_STEP_SEQUENCE[8][4] = {
    {1, 0, 0, 0},
    {1, 1, 0, 0},
    {0, 1, 0, 0},
    {0, 1, 1, 0},
    {0, 0, 1, 0},
    {0, 0, 1, 1},
    {0, 0, 0, 1},
    {1, 0, 0, 1}
};

/**
 * @brief Sets the motor pins to a specific step in the sequence.
 * @param step The step number (0-7) in the half-step sequence.
 */
void set_step(int step) {
    for (int i = 0; i < NUM_MOTOR_PINS; i++) {
        digitalWrite(MOTOR_PINS[i], HALF_STEP_SEQUENCE[step][i]);
    }
}

/**
 * @brief Rotates the motor by a given number of steps in a specified direction.
 * @param steps The number of steps to rotate.
 * @param clockwise If true, rotate clockwise; otherwise, anti-clockwise.
 * @param step_delay_us The delay in microseconds between each step, controls speed.
 */
void rotate_steps(int steps, int clockwise, int step_delay_us) {
    static int current_step = 0;
    int step_increment = clockwise ? 1 : -1;

    for (int i = 0; i < steps; i++) {
        current_step = (current_step + step_increment + 8) % 8;
        set_step(current_step);
        delayMicroseconds(step_delay_us);
    }
}

/**
 * @brief Initializes GPIO pins for the stepper motor.
 */
void setup_stepper() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }
    for (int i = 0; i < NUM_MOTOR_PINS; i++) {
        pinMode(MOTOR_PINS[i], OUTPUT);
    }
}

/**
 * @brief Main function to control the stepper motor.
 * @return Integer status code.
 */
int main(void) {
    setup_stepper();

    // The 28BYJ-48 motor has a gear ratio of ~64:1 and takes 32 steps per internal
    // revolution in full-step mode. In half-step mode (8 steps per sequence),
    // it's 64 steps. So, one full output revolution is 64 * 64 = 4096 steps.
    const int STEPS_PER_REVOLUTION = 4096;
    
    // Calculate delay for a target RPM (e.g., 15 RPM).
    const int TARGET_RPM = 15;
    const int step_delay_us = 60 * 1000 * 1000 / STEPS_PER_REVOLUTION / TARGET_RPM;

    printf("Stepper motor control initialized.\n");
    printf("Rotating one full revolution clockwise, then one anti-clockwise.\n");

    while (1) {
        // Rotate one full revolution clockwise.
        printf("-> Clockwise rotation...\n");
        rotate_steps(STEPS_PER_REVOLUTION, 1, step_delay_us);
        delay(1000); // Pause for 1 second.

        // Rotate one full revolution anti-clockwise.
        printf("<- Anti-clockwise rotation...\n");
        rotate_steps(STEPS_PER_REVOLUTION, 0, step_delay_us);
        delay(1000); // Pause for 1 second.
    }

    return 0; // Unreachable code.
}
