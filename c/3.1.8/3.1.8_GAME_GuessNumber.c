/**
 * Guess Number Game
 * Using 4x4 Keypad and LCD1602 Display
 * 
 * A number guessing game where players try to guess a random number
 * between 0-99 using a 4x4 keypad for input and LCD for display.
 */

#include <stdio.h>
#include <stdlib.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <string.h>
#include <time.h>
#include <stdbool.h>
#include <signal.h>

// --- Hardware Configuration ---
#define KEYPAD_ROWS         4         // Number of keypad rows
#define KEYPAD_COLS         4         // Number of keypad columns  
#define TOTAL_KEYS          (KEYPAD_ROWS * KEYPAD_COLS)
#define LCD_I2C_ADDR        0x27      // LCD I2C address
#define MAX_NUMBER          99        // Maximum guessable number
#define INPUT_BUFFER_SIZE   3         // Maximum digits for input

// --- Game Constants ---
#define GAME_MIN_VALUE      0         // Minimum random number
#define GAME_MAX_VALUE      99        // Maximum random number
#define TWO_DIGIT_THRESHOLD 10        // Threshold for two-digit detection

// --- Hardware Pin Configuration ---
static const unsigned char KEYPAD_LAYOUT[TOTAL_KEYS] = {  
    '1','2','3','A',
    '4','5','6','B',
    '7','8','9','C',
    '*','0','#','D'
};

static const unsigned char ROW_PINS[KEYPAD_ROWS] = {1, 4, 5, 6}; 
static const unsigned char COL_PINS[KEYPAD_COLS] = {12, 3, 2, 0};

// --- Game State Structure ---
typedef struct {
    int target_number;        // The number to guess
    int current_input;        // Current player input
    int range_lower;          // Lower bound of valid range
    int range_upper;          // Upper bound of valid range
    int lcd_handle;           // I2C handle for LCD
    bool backlight_enabled;   // LCD backlight state
} GameState;

// --- Global Game State ---
static GameState game;

// --- LCD Control Functions ---

/**
 * Write a byte to LCD with backlight control
 * @param data: Data byte to write
 */
static void lcd_write_byte(int data) {
    int temp = data;
    if (game.backlight_enabled) {
        temp |= 0x08;  // Enable backlight
    } else {
        temp &= 0xF7;  // Disable backlight
    }
    wiringPiI2CWrite(game.lcd_handle, temp);
}

/**
 * Send command to LCD
 * @param command: LCD command byte
 */
static void lcd_send_command(int command) {
    int buffer;
    
    // Send upper 4 bits first
    buffer = command & 0xF0;
    buffer |= 0x04;  // RS=0, RW=0, EN=1
    lcd_write_byte(buffer);
    delay(2);
    buffer &= 0xFB;  // EN=0
    lcd_write_byte(buffer);

    // Send lower 4 bits second
    buffer = (command & 0x0F) << 4;
    buffer |= 0x04;  // RS=0, RW=0, EN=1
    lcd_write_byte(buffer);
    delay(2);
    buffer &= 0xFB;  // EN=0
    lcd_write_byte(buffer);
}

/**
 * Send data to LCD
 * @param data: Data byte to display
 */
static void lcd_send_data(int data) {
    int buffer;
    
    // Send upper 4 bits first
    buffer = data & 0xF0;
    buffer |= 0x05;  // RS=1, RW=0, EN=1
    lcd_write_byte(buffer);
    delay(2);
    buffer &= 0xFB;  // EN=0
    lcd_write_byte(buffer);

    // Send lower 4 bits second
    buffer = (data & 0x0F) << 4;
    buffer |= 0x05;  // RS=1, RW=0, EN=1
    lcd_write_byte(buffer);
    delay(2);
    buffer &= 0xFB;  // EN=0
    lcd_write_byte(buffer);
}

/**
 * Initialize LCD display
 */
static void lcd_initialize(void) {
    lcd_send_command(0x33);  // Initialize to 8-bit mode first
    delay(5);
    lcd_send_command(0x32);  // Switch to 4-bit mode
    delay(5);
    lcd_send_command(0x28);  // 2 lines, 5x7 dots
    delay(5);
    lcd_send_command(0x0C);  // Display on, cursor off
    delay(5);
    lcd_send_command(0x01);  // Clear display
    wiringPiI2CWrite(game.lcd_handle, 0x08);
}

/**
 * Clear LCD display
 */
static void lcd_clear_display(void) {
    lcd_send_command(0x01);  // Clear screen command
}

/**
 * Display text at specified position
 * @param col: Column position (0-15)
 * @param row: Row position (0-1)
 * @param text: Text string to display
 */
static void lcd_display_text(int col, int row, const char *text) {
    int address;
    
    // Boundary checks
    if (col < 0) col = 0;
    if (col > 15) col = 15;
    if (row < 0) row = 0;
    if (row > 1) row = 1;

    // Calculate cursor position
    address = 0x80 + 0x40 * row + col;
    lcd_send_command(address);
    
    // Send each character
    for (int i = 0; i < strlen(text); i++) {
        lcd_send_data(text[i]);
    }
}


// --- Keypad Control Functions ---

/**
 * Clear keypad buffer
 * @param buffer: Key buffer to clear
 */
static void keypad_clear_buffer(unsigned char *buffer) {
    for (int i = 0; i < TOTAL_KEYS; i++) {
        buffer[i] = 0;
    }
}

/**
 * Read pressed keys from keypad
 * @param result: Buffer to store pressed keys
 */
static void keypad_read_keys(unsigned char *result) {
    int key_index;
    int found_keys = 0;
    
    keypad_clear_buffer(result);
    
    // Scan each row
    for (int row = 0; row < KEYPAD_ROWS; row++) {
        digitalWrite(ROW_PINS[row], HIGH);
        
        // Check each column in current row
        for (int col = 0; col < KEYPAD_COLS; col++) {
            key_index = row * KEYPAD_ROWS + col;
            if (digitalRead(COL_PINS[col]) == HIGH) {
                result[found_keys] = KEYPAD_LAYOUT[key_index];
                found_keys++;
            }
        }
        
        delay(1);  // Small delay for stability
        digitalWrite(ROW_PINS[row], LOW);
    }
}

/**
 * Compare two key buffers
 * @param buffer_a: First buffer
 * @param buffer_b: Second buffer
 * @return: true if buffers are identical
 */
static bool keypad_compare_buffers(const unsigned char *buffer_a, const unsigned char *buffer_b) {
    for (int i = 0; i < TOTAL_KEYS; i++) {
        if (buffer_a[i] != buffer_b[i]) {
            return false;
        }
    }
    return true;
}

/**
 * Copy key buffer contents
 * @param destination: Destination buffer
 * @param source: Source buffer
 */
static void keypad_copy_buffer(unsigned char *destination, const unsigned char *source) {
    for (int i = 0; i < TOTAL_KEYS; i++) {
        destination[i] = source[i];
    }
}

/**
 * Find index of specific key in layout
 * @param key: Key character to find
 * @return: Index of key, or -1 if not found
 */
static int keypad_find_key_index(char key) {
    for (int i = 0; i < TOTAL_KEYS; i++) {
        if (KEYPAD_LAYOUT[i] == key) {
            return i;
        }
    }
    return -1;
}

// --- Utility Functions ---

/**
 * Convert integer to string for LCD display
 * @param str: Output string buffer
 * @param number: Integer to convert
 */
static void number_to_string(char *str, int number) {
    if (number == 0) {
        str[0] = '0';
        str[1] = '\0';
        return;
    }
    
    sprintf(str, "%d", number);
}

// --- Game Logic Functions ---

/**
 * Initialize hardware components
 */
static void setup_hardware(void) {
    printf("🎮 Initializing Guess Number Game...\n");
    
    // Setup LCD
    game.lcd_handle = wiringPiI2CSetup(LCD_I2C_ADDR);
    game.backlight_enabled = true;
    lcd_initialize();
    lcd_clear_display();
    
    // Setup keypad pins
    for (int i = 0; i < KEYPAD_ROWS; i++) {
        pinMode(ROW_PINS[i], OUTPUT);
        pinMode(COL_PINS[i], INPUT);
    }
    
    // Display welcome message
    lcd_clear_display();
    lcd_display_text(0, 0, "Welcome!");
    lcd_display_text(0, 1, "Press A to start");
    
    printf("✅ Hardware setup complete!\n");
}

/**
 * Generate new random target number
 */
static void generate_new_target(void) {
    srand(time(NULL));
    game.target_number = rand() % (GAME_MAX_VALUE + 1);
    game.range_upper = GAME_MAX_VALUE;
    game.range_lower = GAME_MIN_VALUE;
    game.current_input = 0;
    
    printf("🎯 New target generated: %d\n", game.target_number);
}

/**
 * Check if guessed number matches target
 * @return: true if guess is correct
 */
static bool check_guess_result(void) {
    if (game.current_input > game.target_number) {
        // Guess too high - update upper bound
        if (game.current_input < game.range_upper) {
            game.range_upper = game.current_input;
        }
    } else if (game.current_input < game.target_number) {
        // Guess too low - update lower bound
        if (game.current_input > game.range_lower) {
            game.range_lower = game.current_input;
        }
    } else {
        // Correct guess!
        game.current_input = 0;
        return true;
    }
    
    game.current_input = 0;
    return false;
}

/**
 * Update LCD display with current game state
 * @param is_correct: true if last guess was correct
 */
static void update_game_display(bool is_correct) {
    char number_str[INPUT_BUFFER_SIZE + 1];
    
    lcd_clear_display();
    
    if (is_correct) {
        lcd_display_text(0, 0, "Congratulations!");
        lcd_display_text(0, 1, "You got it!");
        delay(3000);
        generate_new_target();
        update_game_display(false);
        return;
    }
    
    // Display input prompt and current number
    lcd_display_text(0, 0, "Enter number:");
    number_to_string(number_str, game.current_input);
    lcd_display_text(13, 0, number_str);
    
    // Display range information
    number_to_string(number_str, game.range_lower);
    lcd_display_text(0, 1, number_str);
    lcd_display_text(3, 1, "<Target<");
    number_to_string(number_str, game.range_upper);
    lcd_display_text(12, 1, number_str);
}

// --- Signal Handler ---

/**
 * Clean shutdown on signal
 */
static void cleanup_and_exit(int signum) {
    printf("\n🧹 Shutting down game...\n");
    lcd_clear_display();
    lcd_display_text(0, 0, "Game Over!");
    lcd_display_text(0, 1, "Goodbye!");
    delay(2000);
    printf("✅ Cleanup complete. Goodbye!\n");
    exit(0);
}

// --- Main Game Loop ---

/**
 * Main game execution function
 */
static void run_game_loop(void) {
    unsigned char current_keys[TOTAL_KEYS];
    unsigned char previous_keys[TOTAL_KEYS];
    bool is_correct_guess;
    
    printf("🎮 Starting game loop...\n");
    
    // Initialize key buffers
    keypad_clear_buffer(current_keys);
    keypad_clear_buffer(previous_keys);
    
    // Generate first target
    generate_new_target();
    update_game_display(false);
    
    while (true) {
        // Read current keypad state
        keypad_read_keys(current_keys);
        
        // Check if keys changed (debouncing)
        if (!keypad_compare_buffers(current_keys, previous_keys)) {
            if (current_keys[0] != 0) {  // Key was pressed
                char pressed_key = current_keys[0];
                is_correct_guess = false;
                
                printf("🔹 Key pressed: %c\n", pressed_key);
                
                switch (pressed_key) {
                    case 'A':
                        // Start new game
                        printf("🔄 Starting new game...\n");
                        generate_new_target();
                        update_game_display(false);
                        break;
                        
                    case 'D':
                        // Submit current guess
                        printf("✅ Submitting guess: %d\n", game.current_input);
                        is_correct_guess = check_guess_result();
                        update_game_display(is_correct_guess);
                        break;
                        
                    case '*':
                        // Clear current input
                        printf("🔄 Clearing input...\n");
                        game.current_input = 0;
                        update_game_display(false);
                        break;
                        
                    default:
                        // Handle number input (0-9)
                        if (pressed_key >= '0' && pressed_key <= '9') {
                            int digit = pressed_key - '0';
                            game.current_input = game.current_input * 10 + digit;
                            
                            // Auto-submit if two digits entered
                            if (game.current_input >= TWO_DIGIT_THRESHOLD) {
                                printf("✅ Auto-submitting two-digit guess: %d\n", game.current_input);
                                is_correct_guess = check_guess_result();
                            }
                            
                            update_game_display(is_correct_guess);
                        } else {
                            printf("⚠️ Invalid key: %c\n", pressed_key);
                        }
                        break;
                }
            }
            
            // Update key state for next iteration
            keypad_copy_buffer(previous_keys, current_keys);
        }
        
        delay(100);  // Main loop delay
    }
}

/**
 * Main function
 */
int main(void) {
    printf("=== Guess Number Game ===\n");
    printf("🎯 Try to guess the secret number!\n\n");
    
    // Initialize wiringPi
    if (wiringPiSetup() == -1) {
        printf("❌ Failed to initialize wiringPi!\n");
        return 1;
    }
    
    // Setup signal handler for graceful exit
    signal(SIGINT, cleanup_and_exit);
    signal(SIGTERM, cleanup_and_exit);
    
    // Initialize hardware
    setup_hardware();
    
    // Run main game loop
    run_game_loop();
    
    return 0;
}

