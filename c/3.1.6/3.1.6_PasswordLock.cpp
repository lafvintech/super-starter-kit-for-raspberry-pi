#include <stdio.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>
#include <string.h>
#include <signal.h>
#include <stdlib.h>

// --- Hardware Configuration ---
#define LCD_ADDR        0x27
#define LCD_BACKLIGHT   0x08
#define KEYPAD_ROWS     4
#define KEYPAD_COLS     4
#define PASSWORD_LENGTH 4

// --- Pin Configuration ---
const int row_pins[KEYPAD_ROWS] = {1, 4, 5, 6};
const int col_pins[KEYPAD_COLS] = {12, 3, 2, 0};

// --- Keypad Layout ---
const char keypad_layout[KEYPAD_ROWS][KEYPAD_COLS] = {
    {'1', '2', '3', 'A'},
    {'4', '5', '6', 'B'},
    {'7', '8', '9', 'C'},
    {'*', '0', '#', 'D'}
};

// --- Password Configuration ---
const char correct_password[PASSWORD_LENGTH] = {'1', '9', '8', '4'};
char entered_password[PASSWORD_LENGTH] = {0};
int password_index = 0;

// --- Global Variables ---
int lcd_handle;

/**
 * @brief Write data to LCD via I2C
 * @param data Data byte to send
 */
void lcd_write_byte(int data) {
    int temp = data;
    if (LCD_BACKLIGHT) {
        temp |= 0x08;  // Turn on backlight
    } else {
        temp &= 0xF7;  // Turn off backlight
    }
    wiringPiI2CWrite(lcd_handle, temp);
}

/**
 * @brief Send command to LCD
 * @param command Command byte
 */
void lcd_send_command(int command) {
    // Send upper 4 bits
    int buffer = command & 0xF0;
    buffer |= 0x04;  // RS=0, RW=0, EN=1
    lcd_write_byte(buffer);
    delay(2);
    buffer &= 0xFB;  // EN=0
    lcd_write_byte(buffer);
    
    // Send lower 4 bits
    buffer = (command & 0x0F) << 4;
    buffer |= 0x04;  // RS=0, RW=0, EN=1
    lcd_write_byte(buffer);
    delay(2);
    buffer &= 0xFB;  // EN=0
    lcd_write_byte(buffer);
}

/**
 * @brief Send data to LCD
 * @param data Data byte
 */
void lcd_send_data(int data) {
    // Send upper 4 bits
    int buffer = data & 0xF0;
    buffer |= 0x05;  // RS=1, RW=0, EN=1
    lcd_write_byte(buffer);
    delay(2);
    buffer &= 0xFB;  // EN=0
    lcd_write_byte(buffer);
    
    // Send lower 4 bits
    buffer = (data & 0x0F) << 4;
    buffer |= 0x05;  // RS=1, RW=0, EN=1
    lcd_write_byte(buffer);
    delay(2);
    buffer &= 0xFB;  // EN=0
    lcd_write_byte(buffer);
}

/**
 * @brief Initialize LCD display
 */
void lcd_init() {
    printf("📺 Initializing LCD display...\n");
    
    lcd_send_command(0x33);  // Initialize to 8-bit mode
    delay(5);
    lcd_send_command(0x32);  // Switch to 4-bit mode
    delay(5);
    lcd_send_command(0x28);  // 2 lines, 5x7 dots
    delay(5);
    lcd_send_command(0x0C);  // Display on, cursor off
    delay(5);
    lcd_send_command(0x01);  // Clear screen
    wiringPiI2CWrite(lcd_handle, LCD_BACKLIGHT);
    
    printf("✅ LCD ready!\n");
}

/**
 * @brief Clear LCD screen
 */
void lcd_clear() {
    lcd_send_command(0x01);
}

/**
 * @brief Display text on LCD at specified position
 * @param x Column position (0-15)
 * @param y Row position (0-1)
 * @param text Text to display
 */
void lcd_display_text(int x, int y, const char* text) {
    // Boundary checks
    if (x < 0) x = 0;
    if (x > 15) x = 15;
    if (y < 0) y = 0;
    if (y > 1) y = 1;
    
    // Set cursor position
    int address = 0x80 + 0x40 * y + x;
    lcd_send_command(address);
    
    // Send text characters
    int length = strlen(text);
    for (int i = 0; i < length; i++) {
        lcd_send_data(text[i]);
    }
}

/**
 * @brief Initialize keypad pins
 */
void keypad_init() {
    printf("⌨️ Initializing keypad...\n");
    
    for (int i = 0; i < KEYPAD_ROWS; i++) {
        pinMode(row_pins[i], OUTPUT);
        digitalWrite(row_pins[i], LOW);
    }
    
    for (int i = 0; i < KEYPAD_COLS; i++) {
        pinMode(col_pins[i], INPUT);
        pullUpDnControl(col_pins[i], PUD_DOWN);
    }
    
    printf("✅ Keypad ready!\n");
}

/**
 * @brief Scan keypad for pressed key
 * @return Pressed key character, or 0 if no key pressed
 */
char scan_keypad() {
    for (int row = 0; row < KEYPAD_ROWS; row++) {
        // Activate current row
        digitalWrite(row_pins[row], HIGH);
        delayMicroseconds(100);  // Small delay for signal stability
        
        // Check each column
        for (int col = 0; col < KEYPAD_COLS; col++) {
            if (digitalRead(col_pins[col]) == HIGH) {
                digitalWrite(row_pins[row], LOW);  // Deactivate row
                return keypad_layout[row][col];
            }
        }
        
        // Deactivate current row
        digitalWrite(row_pins[row], LOW);
    }
    
    return 0;  // No key pressed
}

/**
 * @brief Check if entered password matches correct password
 * @return true if passwords match, false otherwise
 */
bool verify_password() {
    for (int i = 0; i < PASSWORD_LENGTH; i++) {
        if (entered_password[i] != correct_password[i]) {
            return false;
        }
    }
    return true;
}

/**
 * @brief Reset password entry
 */
void reset_password_entry() {
    password_index = 0;
    memset(entered_password, 0, PASSWORD_LENGTH);
}

/**
 * @brief Display password stars on LCD
 */
void display_password_stars() {
    char stars[PASSWORD_LENGTH + 1] = {0};
    for (int i = 0; i < password_index; i++) {
        stars[i] = '*';
    }
    lcd_display_text(16 - password_index, 1, stars);
}

/**
 * @brief Handle successful password entry
 */
void handle_success() {
    printf("✅ Password correct!\n");
    lcd_clear();
    lcd_display_text(4, 0, "CORRECT!");
    lcd_display_text(2, 1, "Welcome back");
    delay(3000);  // Show success message for 3 seconds
    reset_password_entry();
}

/**
 * @brief Handle failed password entry
 */
void handle_failure() {
    printf("❌ Wrong password!\n");
    lcd_clear();
    lcd_display_text(3, 0, "WRONG KEY!");
    lcd_display_text(0, 1, "Please try again");
    delay(2000);  // Show error message for 2 seconds
    reset_password_entry();
}

/**
 * @brief Display welcome screen
 */
void display_welcome_screen() {
    lcd_clear();
    lcd_display_text(0, 0, "Enter password:");
    display_password_stars();
}

/**
 * @brief Initialize hardware components
 */
void setup_hardware() {
    printf("🔧 Initializing Password Lock System...\n");
    
    // Initialize wiringPi
    if (wiringPiSetup() == -1) {
        printf("❌ wiringPi setup failed!\n");
        exit(1);
    }
    
    // Setup LCD
    lcd_handle = wiringPiI2CSetup(LCD_ADDR);
    lcd_init();
    
    // Setup keypad
    keypad_init();
    
    printf("🔐 Password Lock System ready!\n");
    printf("Default password: 1984\n\n");
}

/**
 * @brief Clean up and exit
 */
void cleanup_exit(int sig) {
    printf("\n🧹 Shutting down password lock system...\n");
    lcd_clear();
    lcd_display_text(4, 0, "GOODBYE!");
    delay(1000);
    printf("✅ Goodbye!\n");
    exit(0);
}

/**
 * @brief Main password lock loop
 */
void password_lock_loop() {
    char current_key = 0;
    char last_key = 0;
    
    // Display initial welcome screen
    lcd_clear();
    lcd_display_text(0, 0, "WELCOME!");
    lcd_display_text(2, 1, "Enter password");
    delay(2000);
    
    display_welcome_screen();
    
    printf("🔐 Password lock active...\n");
    printf("Enter 4-digit password using keypad\n");
    printf("Press Ctrl+C to exit\n\n");
    
    while (1) {
        current_key = scan_keypad();
        
        // Process key press (only on new press, not hold)
        if (current_key != 0 && current_key != last_key) {
            printf("🔑 Key pressed: %c\n", current_key);
            
            // Add character to password
            entered_password[password_index] = current_key;
            password_index++;
            
            // Update display
            display_welcome_screen();
            
            // Check if password is complete
            if (password_index >= PASSWORD_LENGTH) {
                if (verify_password()) {
                    handle_success();
                } else {
                    handle_failure();
                }
                display_welcome_screen();
            }
        }
        
        last_key = current_key;
        delay(50);  // Debounce delay
    }
}

/**
 * @brief Main function
 */
int main(void) {
    // Handle Ctrl+C
    signal(SIGINT, cleanup_exit);
    
    printf("=== Password Lock System ===\n");
    printf("4x4 Keypad + LCD1602 Display\n\n");
    
    // Initialize hardware
    setup_hardware();
    
    // Start password lock loop
    password_lock_loop();
    
    return 0;
}
