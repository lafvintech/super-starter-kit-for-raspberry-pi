#ifndef DHT_C_DRIVER_H
#define DHT_C_DRIVER_H

#include <stdint.h> // Required for uint8_t

// Define the possible return codes from the read function.
// Using an enum for better type safety and readability in C.
typedef enum {
    DHT_SUCCESS = 0,
    DHT_ERROR_TIMEOUT = -1,
    DHT_ERROR_CHECKSUM = -2
} DHT_Status;

// A structure to hold the sensor data.
// This makes it easy to return both temperature and humidity from one function call.
typedef struct {
    float temperature_celsius;
    float humidity_percent;
} DHT_Data;

/**
 * @brief Reads data from a DHT11 sensor.
 *
 * This function handles the complete communication with the DHT11 sensor,
 * including sending the start signal, waiting for a response, reading the 40 bits
 * of data, and performing a checksum validation. It's a pure C implementation.
 *
 * @param pin The wiringPi pin number connected to the DHT11 data line.
 * @param sensor_data A pointer to a DHT_Data struct where the successfully
 *                    read temperature and humidity will be stored.
 *
 * @return A DHT_Status enum value:
 *         - DHT_SUCCESS on a successful read.
 *         - DHT_ERROR_TIMEOUT if the sensor fails to respond in time.
 *         - DHT_ERROR_CHECKSUM if the received data is corrupt.
 */
DHT_Status dht11_read(int pin, DHT_Data *sensor_data);

#endif // DHT_C_DRIVER_H
