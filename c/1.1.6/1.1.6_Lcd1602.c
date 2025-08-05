#include <stdio.h>
#include <stdlib.h> // Required for exit()
#include <string.h>
#include <wiringPi.h>
#include <wiringPiI2C.h>

// --- Constants ---

// I2C Address of the PCF8574A chip on the LCD's I2C backpack.
#define I2C_ADDR   0x27

// LCD Command and Character constants.
#define LCD_CHR  1 // Mode: Sending data (characters)
#define LCD_CMD  0 // Mode: Sending command

// LCD Line addresses.
#define LINE1  0x80 // Address for the 1st line.
#define LINE2  0xC0 // Address for the 2nd line.

// Bitmask for the backlight. On: 0x08, Off: 0x00.
#define LCD_BACKLIGHT 0x08

// Enable bit.
#define ENABLE 0x04

// --- Function Prototypes ---
void lcd_init(int* fd_ptr);
void lcd_write_byte(int fd, int bits, int mode);
void lcd_toggle_enable(int fd, int bits);
void lcd_clear(int fd);
void lcd_set_cursor(int fd, int col, int row);
void lcd_print(int fd, const char* message);
void lcd_print_at(int fd, int col, int row, const char* message);

/**
 * @brief Toggles the Enable (EN) pin to latch data into the LCD.
 * @param fd File descriptor for the I2C device.
 * @param bits The data packet to send.
 */
void lcd_toggle_enable(int fd, int bits) {
    delayMicroseconds(500);
    wiringPiI2CWrite(fd, (bits | ENABLE));
    delayMicroseconds(500);
    wiringPiI2CWrite(fd, (bits & ~ENABLE));
    delayMicroseconds(500);
}

/**
 * @brief Writes a single byte to the LCD in 4-bit mode.
 * @param fd File descriptor for the I2C device.
 * @param bits The byte to write.
 * @param mode LCD_CMD for commands, LCD_CHR for data.
 */
void lcd_write_byte(int fd, int bits, int mode) {
    // Send the high nibble (4 bits).
    int bits_high = mode | (bits & 0xF0) | LCD_BACKLIGHT;
    wiringPiI2CWrite(fd, bits_high);
    lcd_toggle_enable(fd, bits_high);

    // Send the low nibble (4 bits).
    int bits_low = mode | ((bits << 4) & 0xF0) | LCD_BACKLIGHT;
    wiringPiI2CWrite(fd, bits_low);
    lcd_toggle_enable(fd, bits_low);
}

/**
 * @brief Initializes the LCD display in 4-bit mode.
 * @param fd_ptr Pointer to an integer where the file descriptor will be stored.
 */
void lcd_init(int* fd_ptr) {
    *fd_ptr = wiringPiI2CSetup(I2C_ADDR);
    if (*fd_ptr == -1) {
        printf("Failed to initialize I2C device with address %d.\n", I2C_ADDR);
        exit(1);
    }
    
    // Initialization sequence for 4-bit mode.
    lcd_write_byte(*fd_ptr, 0x33, LCD_CMD); // Must be sent to ensure 8-bit mode for init
    lcd_write_byte(*fd_ptr, 0x32, LCD_CMD); // Now set to 4-bit mode
    lcd_write_byte(*fd_ptr, 0x06, LCD_CMD); // Entry mode: cursor moves to the right
    lcd_write_byte(*fd_ptr, 0x0C, LCD_CMD); // Display control: display on, cursor off, no blink
    lcd_write_byte(*fd_ptr, 0x28, LCD_CMD); // Function set: 2 lines, 5x8 dots
    lcd_write_byte(*fd_ptr, 0x01, LCD_CMD); // Clear display
    delay(1);
}

/**
 * @brief Clears the LCD screen and returns the cursor to home.
 * @param fd File descriptor for the I2C device.
 */
void lcd_clear(int fd) {
    lcd_write_byte(fd, 0x01, LCD_CMD); // Clear display command
    delay(1);
}

/**
 * @brief Positions the cursor at a specified column and row.
 * @param fd File descriptor for the I2C device.
 * @param col The column (0-15).
 * @param row The row (0-1).
 */
void lcd_set_cursor(int fd, int col, int row) {
    if (row == 0) {
        lcd_write_byte(fd, LINE1 + col, LCD_CMD);
    } else {
        lcd_write_byte(fd, LINE2 + col, LCD_CMD);
    }
}

/**
 * @brief Prints a string to the LCD at the current cursor position.
 * @param fd File descriptor for the I2C device.
 * @param message The string to print.
 */
void lcd_print(int fd, const char* message) {
    while (*message) {
        lcd_write_byte(fd, *message++, LCD_CHR);
    }
}

/**
 * @brief A utility function to set the cursor and print a string.
 * @param fd File descriptor for the I2C device.
 * @param col The column (0-15).
 * @param row The row (0-1).
 * @param message The string to print.
 */
void lcd_print_at(int fd, int col, int row, const char* message) {
    lcd_set_cursor(fd, col, row);
    lcd_print(fd, message);
}

/**
 * @brief Main function.
 * @return 0 on success, 1 on failure.
 */
int main(void) {
    int lcd_fd;

    // wiringPiSetup is essential for delay functions and I2C.
    if (wiringPiSetup() == -1) {
        printf("wiringPiSetup failed!\n");
        return 1;
    }

    lcd_init(&lcd_fd);

    lcd_print_at(lcd_fd, 0, 0, "Hello World!");
    lcd_print_at(lcd_fd, 1, 1, "From LAFVIN");

    return 0;
}
