#include "DHT.h"
#include <wiringPi.h>
#include <stdio.h>

// Define a timeout for waiting for sensor responses.
// This is a loop counter to precisely match the original library's logic.
#define DHT_TIMEOUT_LOOPS 10000

// The core function to read from the sensor. It's kept private to this file
// by not being declared in the header. It contains the precise timing logic.
static DHT_Status read_sensor_raw(int pin, uint8_t data_buffer[5]);

// This is the public function defined in the header file.
DHT_Status dht11_read(int pin, DHT_Data *sensor_data) {
    uint8_t bits[5]; // A buffer to store the 5 bytes of data from the sensor.

    // Call the internal raw reading function.
    DHT_Status status = read_sensor_raw(pin, bits);
    if (status != DHT_SUCCESS) {
        // On failure, ensure the data struct holds invalid values, similar to C++ version.
        sensor_data->humidity_percent = -999;
        sensor_data->temperature_celsius = -999;
        return status; // Return on timeout or other errors.
    }

    // --- Checksum Validation ---
    // The 5th byte sent by the sensor is a checksum, which is the sum of the
    // first four bytes. This helps to ensure data integrity.
    uint8_t checksum = (uint8_t)(bits[0] + bits[1] + bits[2] + bits[3]);
    if (bits[4] != checksum) {
        return DHT_ERROR_CHECKSUM; // Data is corrupt.
    }

    // --- Data Conversion ---
    // If checksum is OK, convert the raw data into temperature and humidity.
    // For DHT11:
    // - The first byte is the integer part of humidity.
    // - The second byte is the decimal part of humidity (always 0 for DHT11).
    // - The third byte is the integer part of temperature.
    // - The fourth byte is the decimal part of temperature.
    sensor_data->humidity_percent = (float)bits[0];
    sensor_data->temperature_celsius = (float)bits[2];

    return DHT_SUCCESS;
}


// --- Private Helper Function ---

static DHT_Status read_sensor_raw(int pin, uint8_t data_buffer[5]) {
    // Initialize the data buffer to zeros.
    uint8_t mask = 128;
    uint8_t idx = 0;
    for (int i = 0; i < 5; i++) {
        data_buffer[i] = 0;
    }

    // --- Step 1: Send Start Signal ---
    // To wake up the sensor, we pull the data pin LOW for 20ms, then HIGH.
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    delay(20); // Wakeup call for DHT11 must be >= 18ms
    digitalWrite(pin, HIGH);
    delayMicroseconds(40); // Wait for the sensor to respond
    pinMode(pin, INPUT);   // Set pin back to input to read the response

    // --- Step 2: Wait for Sensor's Response Signal ---
    // The sensor responds by pulling the line LOW for ~80us, then HIGH for ~80us.
    unsigned int loop_count;

    // Wait for the pin to go LOW (start of response)
    loop_count = DHT_TIMEOUT_LOOPS;
    while (digitalRead(pin) == HIGH) {
        if (loop_count-- == 0) return DHT_ERROR_TIMEOUT;
    }

    // Wait for the pin to go HIGH (end of response)
    loop_count = DHT_TIMEOUT_LOOPS;
    while (digitalRead(pin) == LOW) {
        if (loop_count-- == 0) return DHT_ERROR_TIMEOUT;
    }

    // Wait for pin to go LOW again (start of actual data transmission)
    loop_count = DHT_TIMEOUT_LOOPS;
    while (digitalRead(pin) == HIGH) {
        if (loop_count-- == 0) return DHT_ERROR_TIMEOUT;
    }

    // --- Step 3: Read the 40 Bits of Data using the bitmasking technique ---
    for (int i = 0; i < 40; i++) {
        loop_count = DHT_TIMEOUT_LOOPS;
        while (digitalRead(pin) == LOW) {
            if (loop_count-- == 0) return DHT_ERROR_TIMEOUT;
        }

        unsigned long high_pulse_start = micros();
        loop_count = DHT_TIMEOUT_LOOPS;
        while (digitalRead(pin) == HIGH) {
            if (loop_count-- == 0) return DHT_ERROR_TIMEOUT;
        }
        
        // If the HIGH pulse was longer than 40us, it's a '1'.
        if ((micros() - high_pulse_start) > 40) {
            data_buffer[idx] |= mask;
        }

        // Shift the mask to the next bit.
        mask >>= 1;
        // If the mask is 0, we've filled a byte, so reset mask and move to next byte.
        if (mask == 0) {
            mask = 128;
            idx++;
        }
    }

    // --- Final Step: Leave pin in a clean state ---
    // This matches the original library's behavior.
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);

    return DHT_SUCCESS;
}
