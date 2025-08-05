#include <stdio.h>
#include <wiringPi.h>
#include "DHT.h" // Include our C driver header

// Define the wiringPi pin number connected to the DHT11 data line.
#define DHT11_DATA_PIN 0

int main(void) {
    // --- Initialization ---
    printf("Starting DHT11 sensor reading program (Pure C Version)...\n");
    printf("--------------------------------------------------------\n");

    // Initialize the wiringPi library.
    if (wiringPiSetup() == -1) {
        fprintf(stderr, "Error: Failed to initialize wiringPi.\n");
        return 1; // Exit with an error code
    }

    // This structure will hold the data read from the sensor.
    DHT_Data sensor_data = {0.0f, 0.0f};

    long measurement_cycle = 0;

    // --- Main Loop ---
    while (1) {
        measurement_cycle++;
        
        int max_retries = 15;
        DHT_Status status = DHT_ERROR_TIMEOUT; // Assume failure initially

        // --- Silent Retry Loop ---
        // This loop attempts to read the sensor up to 'max_retries' times.
        // It does so silently to provide a clean user experience.
        for (int attempt = 1; attempt <= max_retries; attempt++) {
            status = dht11_read(DHT11_DATA_PIN, &sensor_data);
            if (status == DHT_SUCCESS) {
                break; // Exit loop on first successful read
            }
            // If it failed, wait briefly before retrying.
            delay(300); 
        }

        // --- Final, Clean Output ---
        // Print the result for this measurement cycle in a clean format.
        printf("Cycle #%ld: ", measurement_cycle);
        if (status == DHT_SUCCESS) {
            printf("Humidity = %.1f%%, Temperature = %.1f C\n",
                   sensor_data.humidity_percent, sensor_data.temperature_celsius);
        } else {
            // This message only appears if all 15 retries fail.
            printf("Failed to get a valid reading from the sensor.\n");
        }

        // Wait for 2 seconds before the next major cycle.
        delay(2000);
    }
    return 0;
}
