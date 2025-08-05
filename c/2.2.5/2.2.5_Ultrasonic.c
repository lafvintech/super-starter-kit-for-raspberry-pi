#include <wiringPi.h>
#include <stdio.h>
#include <stdlib.h> // Required for exit()
#include <sys/time.h>

// --- Pin Definitions ---
#define TRIGGER_PIN 4
#define ECHO_PIN    5

// --- Constants ---
// Speed of sound in cm/s (approx. 343 m/s).
const float SOUND_SPEED_CM_PER_S = 34300.0;
// Timeout for waiting for echo pin response in microseconds.
const int ECHO_TIMEOUT_US = 25000; // Corresponds to a max distance of ~4m.

/**
 * @brief Initializes GPIO pins for the ultrasonic sensor.
 */
void setup_ultrasonic() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }
    pinMode(ECHO_PIN, INPUT);
    pinMode(TRIGGER_PIN, OUTPUT);
    digitalWrite(TRIGGER_PIN, LOW); // Ensure trigger is low initially.
}

/**
 * @brief Measures distance using the ultrasonic sensor.
 * @return The measured distance in centimeters. Returns -1.0 on timeout.
 */
float get_distance_cm() {
    // Send a 10us pulse on the trigger pin to start the measurement.
    digitalWrite(TRIGGER_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIGGER_PIN, LOW);

    long start_time, end_time;
    struct timeval tv_start, tv_end;
    long timeout_start = micros();

    // Wait for the echo pin to go HIGH (start of the echo pulse).
    while (digitalRead(ECHO_PIN) == LOW) {
        if ((micros() - timeout_start) > ECHO_TIMEOUT_US) {
            return -1.0; // Timeout waiting for echo start
        }
    }
    gettimeofday(&tv_start, NULL);

    // Wait for the echo pin to go LOW (end of the echo pulse).
    while (digitalRead(ECHO_PIN) == HIGH) {
        if ((micros() - timeout_start) > ECHO_TIMEOUT_US * 2) { // Allow longer time for return
             return -1.0; // Timeout waiting for echo end
        }
    }
    gettimeofday(&tv_end, NULL);

    // Calculate the duration of the echo pulse in microseconds.
    start_time = tv_start.tv_sec * 1000000 + tv_start.tv_usec;
    end_time = tv_end.tv_sec * 1000000 + tv_end.tv_usec;
    long pulse_duration_us = end_time - start_time;

    // Calculate the distance. The sound travels to the object and back,
    // so we divide the total travel time by 2.
    // Distance = (Travel_Time / 2) * Speed_of_Sound
    float distance = (pulse_duration_us / 1000000.0) * SOUND_SPEED_CM_PER_S / 2.0;
    
    return distance;
}

/**
 * @brief Main loop to continuously measure and print the distance.
 */
void measurement_loop() {
    while (1) {
        float distance = get_distance_cm();
        if (distance > 0) {
            printf("Distance: %.2f cm\n", distance);
        } else {
            printf("Measurement failed (Timeout).\n");
        }
        delay(500); // Wait before the next measurement.
    }
}

/**
 * @brief Main function.
 * @return Integer status code.
 */
int main(void) {
    setup_ultrasonic();
    printf("Ultrasonic distance sensor ready.\n");
    measurement_loop();
    return 0; // Unreachable.
}