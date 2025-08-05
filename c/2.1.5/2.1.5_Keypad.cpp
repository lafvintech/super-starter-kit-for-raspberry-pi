#include <wiringPi.h>
#include <stdio.h>
#include <vector>
#include <string>
#include <iostream>
#include <stdlib.h> // Required for exit()

// Define the layout of the keypad.
const int NUM_ROWS = 4;
const int NUM_COLS = 4;

// Define a class to encapsulate all keypad functionality.
class Keypad {
public:
    // Constructor: Initializes the keypad with specified pins and key map.
    Keypad(const int* rowPins, const int* colPins, const char* keyMap);

    // Scans the keypad and returns a vector of currently pressed keys.
    std::vector<char> getPressedKeys();

private:
    // Initializes GPIO pins.
    void initialize_pins();
    
    const int* row_pins;
    const int* col_pins;
    const char* key_map;
    std::vector<char> last_pressed_keys;
};

Keypad::Keypad(const int* rowPins, const int* colPins, const char* keyMap)
    : row_pins(rowPins), col_pins(colPins), key_map(keyMap) {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }
    initialize_pins();
}

void Keypad::initialize_pins() {
    for (int i = 0; i < NUM_ROWS; ++i) {
        pinMode(row_pins[i], OUTPUT);
        digitalWrite(row_pins[i], LOW); // Set rows low initially.
    }
    for (int i = 0; i < NUM_COLS; ++i) {
        pinMode(col_pins[i], INPUT);
        pullUpDnControl(col_pins[i], PUD_DOWN); // Use internal pull-down resistors.
    }
}

std::vector<char> Keypad::getPressedKeys() {
    std::vector<char> pressed_keys;
    for (int r = 0; r < NUM_ROWS; ++r) {
        // Activate one row at a time.
        digitalWrite(row_pins[r], HIGH);

        // Scan all columns for this active row.
        for (int c = 0; c < NUM_COLS; ++c) {
            if (digitalRead(col_pins[c]) == HIGH) {
                pressed_keys.push_back(key_map[r * NUM_COLS + c]);
            }
        }
        
        // Deactivate the row before moving to the next one.
        digitalWrite(row_pins[r], LOW);
    }
    return pressed_keys;
}

// --- Main Application ---

// Define the physical pin connections.
const int ROW_PINS[NUM_ROWS] = {1, 4, 5, 6};
const int COL_PINS[NUM_COLS] = {12, 3, 2, 0};

// Define the character map for the keys.
const char KEY_MAP[NUM_ROWS * NUM_COLS] = {
    '1', '2', '3', 'A',
    '4', '5', '6', 'B',
    '7', '8', '9', 'C',
    '*', '0', '#', 'D'
};

/**
 * @brief Prints the currently pressed keys to the console.
 * @param keys A vector of characters representing the pressed keys.
 */
void print_keys(const std::vector<char>& keys) {
    if (keys.empty()) {
        std::cout << "No key pressed" << std::endl;
    } else {
        std::cout << "Pressed: ";
        for (size_t i = 0; i < keys.size(); ++i) {
            std::cout << keys[i] << (i == keys.size() - 1 ? "" : ", ");
        }
        std::cout << std::endl;
    }
}

/**
 * @brief Main function.
 * @return Integer status code.
 */
int main(void) {
    Keypad keypad(ROW_PINS, COL_PINS, KEY_MAP);
    std::vector<char> last_pressed;

    printf("Keypad scanner initialized. Press any key.\n");

    while (1) {
        std::vector<char> currently_pressed = keypad.getPressedKeys();
        
        // Only print if the state has changed.
        if (currently_pressed != last_pressed) {
            print_keys(currently_pressed);
            last_pressed = currently_pressed;
        }
        
        delay(100); // Poll every 100ms.
    }

    return 0; // Unreachable.
}
