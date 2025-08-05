/**
 * @file ultrasonic_distance_sensor.c
 * @brief Smart Distance Measurement System
 * @description Uses ultrasonic sensor to measure distance and displays results on LCD
 *              with audio alerts based on proximity
 * @author LAFVIN (Refactored for better readability)
 */

 #include <wiringPi.h>
 #include <stdio.h>
 #include <sys/time.h>
 #include <wiringPiI2C.h>
 #include <string.h>
 #include <stdlib.h>
 #include <unistd.h>
 #include <signal.h>    // 添加信号处理
 
 // ========== PIN DEFINITIONS ==========
 #define TRIGGER_PIN     4    // Ultrasonic sensor trigger pin
 #define ECHO_PIN        5    // Ultrasonic sensor echo pin  
 #define BUZZER_PIN      0    // Active buzzer pin
 
 // ========== LCD CONFIGURATION ==========
 #define LCD_I2C_ADDRESS 0x27  // I2C address of LCD display
 #define LCD_BACKLIGHT_ON  1   // Backlight control flag
 #define LCD_BACKLIGHT_OFF 0
 
 // ========== DISTANCE THRESHOLDS ==========
 #define SAFE_DISTANCE    50.0  // Distance > 50cm (safe zone)
 #define WARNING_DISTANCE 20.0  // Distance 20-50cm (warning zone)
 #define DANGER_DISTANCE  20.0  // Distance < 20cm (danger zone)
 #define MAX_VALID_DISTANCE 400.0  // Maximum sensor range
 
 // ========== GLOBAL VARIABLES ==========
 int lcd_file_descriptor;      // I2C file descriptor for LCD
 int backlight_status = LCD_BACKLIGHT_ON;
 volatile int program_running = 1;  // 程序运行标志
 
 // Function declarations (函数声明)
 void lcd_clear_screen(void);
 void lcd_display_text(int column, int row, char text[]);
 
 // ========== EXIT HANDLER ==========
 
 /**
  * @brief Handle Ctrl+C signal - turn off buzzer and exit
  * @param signal_num The signal number received
  */
 void handle_exit(int signal_num) {
	 printf("\n🛑 Ctrl+C pressed! Shutting down...\n");
	 
	 // Turn off buzzer immediately
	 digitalWrite(BUZZER_PIN, LOW);
	 printf("🔇 Buzzer turned off\n");
 
	 // Clear LCD and show goodbye message
	 lcd_clear_screen();
	 lcd_display_text(3, 0, "Goodbye!");
	 lcd_display_text(1, 1, "See you later");
	 delay(2000);  // Show message for 2 seconds
 
	 // Clear screen completely
	 lcd_clear_screen();
	 
	 // Set program flag to stop main loop
	 program_running = 0;
	 
	 printf("👋 Thank you for using Distance Sensor! Goodbye!\n");
	 exit(0);
 }
 
 /**
  * @brief Setup signal handler for Ctrl+C
  */
 void setup_exit_handler(void) {
	 signal(SIGINT, handle_exit);  // Handle Ctrl+C
	 printf("🛡️  Press Ctrl+C to safely exit\n");
 }
 
 // ========== LCD CONTROL FUNCTIONS ==========
 
 /**
  * @brief Send raw data to LCD via I2C
  * @param data_byte The byte to send to LCD
  */
 void lcd_write_byte(int data_byte) {
	 int temp_data = data_byte;
	 
	 // Add backlight control bit if needed
	 if (backlight_status == LCD_BACKLIGHT_ON) {
		 temp_data |= 0x08;  // Set backlight bit
	 } else {
		 temp_data &= 0xF7;  // Clear backlight bit
	 }
	 
	 wiringPiI2CWrite(lcd_file_descriptor, temp_data);
 }
 
 /**
  * @brief Send command to LCD (4-bit mode)
  * @param command The command byte to send
  */
 void lcd_send_command(int command) {
	 int buffer;
	 
	 // Send upper 4 bits first
	 buffer = command & 0xF0;        // Keep upper 4 bits
	 buffer |= 0x04;                 // Set Enable bit (RS=0, RW=0, EN=1)
	 lcd_write_byte(buffer);
	 delayMicroseconds(100);
	 
	 buffer &= 0xFB;                 // Clear Enable bit (EN=0)
	 lcd_write_byte(buffer);
	 
	 // Send lower 4 bits
	 buffer = (command & 0x0F) << 4; // Shift lower 4 bits to upper position
	 buffer |= 0x04;                 // Set Enable bit
	 lcd_write_byte(buffer);
	 delayMicroseconds(100);
	 
	 buffer &= 0xFB;                 // Clear Enable bit
	 lcd_write_byte(buffer);
 }
 
 /**
  * @brief Send data (character) to LCD
  * @param character The character to display
  */
 void lcd_send_character(int character) {
	 int buffer;
	 
	 // Send upper 4 bits first
	 buffer = character & 0xF0;      // Keep upper 4 bits
	 buffer |= 0x05;                 // Set RS and Enable bits (RS=1, RW=0, EN=1)
	 lcd_write_byte(buffer);
	 delayMicroseconds(100);
	 
	 buffer &= 0xFB;                 // Clear Enable bit
	 lcd_write_byte(buffer);
	 
	 // Send lower 4 bits
	 buffer = (character & 0x0F) << 4; // Shift lower 4 bits to upper position
	 buffer |= 0x05;                 // Set RS and Enable bits
	 lcd_write_byte(buffer);
	 delayMicroseconds(100);
	 
	 buffer &= 0xFB;                 // Clear Enable bit
	 lcd_write_byte(buffer);
 }
 
 /**
  * @brief Initialize LCD display
  */
 void lcd_initialize(void) {
	 printf("🔧 Initializing LCD display...\n");
	 
	 // LCD initialization sequence for 4-bit mode
	 lcd_send_command(0x33);         // Initialize to 8-bit mode first
	 delay(5);
	 lcd_send_command(0x32);         // Switch to 4-bit mode
	 delay(5);
	 lcd_send_command(0x28);         // 4-bit mode, 2 lines, 5x7 character font
	 delay(5);
	 lcd_send_command(0x0C);         // Display ON, cursor OFF, blink OFF
	 delay(5);
	 lcd_send_command(0x01);         // Clear display
	 delay(5);
	 
	 wiringPiI2CWrite(lcd_file_descriptor, 0x08); // Turn on backlight
	 
	 printf("✅ LCD initialization complete!\n");
 }
 
 /**
  * @brief Clear LCD screen
  */
 void lcd_clear_screen(void) {
	 lcd_send_command(0x01);         // Clear display command
	 delay(2);
 }
 
 /**
  * @brief Display text at specific position on LCD
  * @param column Column position (0-15)
  * @param row Row position (0-1)
  * @param text Text string to display
  */
 void lcd_display_text(int column, int row, char text[]) {
	 int cursor_address;
	 int text_length = strlen(text);
	 
	 // Validate and limit input parameters
	 if (column < 0) column = 0;
	 if (column > 15) column = 15;
	 if (row < 0) row = 0;
	 if (row > 1) row = 1;
	 
	 // Calculate cursor position (LCD memory address)
	 cursor_address = 0x80 + (0x40 * row) + column;
	 lcd_send_command(cursor_address);
	 
	 // Send each character of the text
	 for (int i = 0; i < text_length; i++) {
		 lcd_send_character(text[i]);
	 }
 }
 
 // ========== ULTRASONIC SENSOR FUNCTIONS ==========
 
 /**
  * @brief Initialize ultrasonic sensor pins
  */
 void ultrasonic_sensor_setup(void) {
	 printf("🔧 Setting up ultrasonic sensor...\n");
	 
	 pinMode(ECHO_PIN, INPUT);       // Echo pin receives signal
	 pinMode(TRIGGER_PIN, OUTPUT);   // Trigger pin sends signal
	 
	 // Ensure trigger starts LOW
	 digitalWrite(TRIGGER_PIN, LOW);
	 
	 printf("✅ Ultrasonic sensor ready!\n");
 }
 
 /**
  * @brief Measure distance using ultrasonic sensor
  * @return Distance in centimeters (float)
  */
 float measure_distance(void) {
	 struct timeval start_time, end_time;
	 long start_microseconds, end_microseconds;
	 float distance_cm;
	 
	 // Send trigger pulse
	 digitalWrite(TRIGGER_PIN, LOW);
	 delayMicroseconds(2);           // Ensure clean LOW pulse
	 
	 digitalWrite(TRIGGER_PIN, HIGH);
	 delayMicroseconds(10);          // 10µs HIGH pulse
	 digitalWrite(TRIGGER_PIN, LOW);
	 
	 // Wait for echo to go HIGH (start of return signal)
	 while (digitalRead(ECHO_PIN) == 0 && program_running) {
		 // Wait for echo start (with exit check)
	 }
	 
	 if (!program_running) return 0;  // Exit if Ctrl+C pressed
	 
	 gettimeofday(&start_time, NULL); // Record start time
	 
	 // Wait for echo to go LOW (end of return signal)  
	 while (digitalRead(ECHO_PIN) == 1 && program_running) {
		 // Wait for echo end (with exit check)
	 }
	 
	 if (!program_running) return 0;  // Exit if Ctrl+C pressed
	 
	 gettimeofday(&end_time, NULL);   // Record end time
	 
	 // Calculate time difference in microseconds
	 start_microseconds = start_time.tv_sec * 1000000 + start_time.tv_usec;
	 end_microseconds = end_time.tv_sec * 1000000 + end_time.tv_usec;
	 
	 // Convert time to distance
	 // Formula: Distance = (Time × Speed_of_Sound) / 2
	 // Speed of sound = 34000 cm/s = 0.034 cm/µs
	 distance_cm = (float)(end_microseconds - start_microseconds) * 0.034 / 2.0;
	 
	 return distance_cm;
 }
 
 // ========== BUZZER CONTROL FUNCTIONS ==========
 
 /**
  * @brief Setup buzzer pin
  */
 void buzzer_setup(void) {
	 pinMode(BUZZER_PIN, OUTPUT);
	 digitalWrite(BUZZER_PIN, LOW);  // Start with buzzer OFF
 }
 
 /**
  * @brief Play buzzer pattern based on distance (with exit check)
  * @param distance Current measured distance
  */
 void play_proximity_alert(float distance) {
	 digitalWrite(BUZZER_PIN, LOW);  // Ensure buzzer starts OFF
	 
	 if (!program_running) return;   // Exit if Ctrl+C pressed
	 
	 if (distance >= SAFE_DISTANCE) {
		 // Safe zone: No sound, longer delay
		 for (int i = 0; i < 50 && program_running; i++) {
			 delay(10);  // Break delay into smaller chunks for responsiveness
		 }
		 
	 } else if (distance > WARNING_DISTANCE && distance < SAFE_DISTANCE) {
		 // Warning zone: Slow beeping
		 printf("⚠️  WARNING: Object approaching!\n");
		 for (int beep = 0; beep < 2 && program_running; beep++) {
			 digitalWrite(BUZZER_PIN, HIGH);
			 for (int i = 0; i < 10 && program_running; i++) delay(10);  // 100ms
			 digitalWrite(BUZZER_PIN, LOW);
			 for (int i = 0; i < 30 && program_running; i++) delay(10);  // 300ms
		 }
		 
	 } else if (distance <= WARNING_DISTANCE) {
		 // Danger zone: Fast beeping
		 printf("🚨 DANGER: Object very close!\n");  
		 for (int beep = 0; beep < 5 && program_running; beep++) {
			 digitalWrite(BUZZER_PIN, HIGH);
			 for (int i = 0; i < 8 && program_running; i++) delay(10);   // 80ms
			 digitalWrite(BUZZER_PIN, LOW);
			 for (int i = 0; i < 8 && program_running; i++) delay(10);   // 80ms
		 }
	 }
 }
 
 // ========== DISPLAY FUNCTIONS ==========
 
 /**
  * @brief Display welcome message
  */
 void show_startup_message(void) {
	 lcd_clear_screen();
	 lcd_display_text(0, 0, "Distance Sensor");
	 lcd_display_text(2, 1, "Starting Up...");
	 delay(2000);
	 
	 lcd_clear_screen();
	 lcd_display_text(1, 0, "LAFVIN Project");
	 lcd_display_text(0, 1, "Ready to measure");
	 delay(2000);
 }
 
 /**
  * @brief Display distance measurement results
  * @param distance Measured distance value
  */
 void display_distance_info(float distance) {
	 char distance_string[16];
	 
	 lcd_clear_screen();
	 
	 if (distance > MAX_VALID_DISTANCE) {
		 // Out of range error
		 lcd_display_text(3, 0, "ERROR!");
		 lcd_display_text(1, 1, "Out of Range");
		 printf("❌ Measurement error: Distance too far (%.2f cm)\n", distance);
		 
	 } else {
		 // Valid measurement - display distance
		 lcd_display_text(0, 0, "Distance:");
		 sprintf(distance_string, "%.1f cm", distance);
		 lcd_display_text(3, 1, distance_string);
		 
		 // Print status to console
		 if (distance >= SAFE_DISTANCE) {
			 printf("✅ Safe distance: %.2f cm\n", distance);
		 } else if (distance > WARNING_DISTANCE) {
			 printf("⚠️  Warning distance: %.2f cm\n", distance);
		 } else {
			 printf("🚨 Danger distance: %.2f cm\n", distance);
		 }
	 }
 }
 
 // ========== MAIN PROGRAM ==========
 
 /**
  * @brief Main function - Program entry point
  */
 int main(void) {
	 float measured_distance;
	 
	 printf("========================================\n");
	 printf("🎯 Smart Distance Measurement System\n");
	 printf("========================================\n");
	 
	 // Setup exit handler FIRST
	 setup_exit_handler();
	 
	 // Initialize wiringPi library
	 if (wiringPiSetup() == -1) {
		 printf("❌ ERROR: Failed to initialize wiringPi!\n");
		 printf("💡 Try running with: sudo ./ultrasonic_distance_sensor\n");
		 return 1;
	 }
	 printf("✅ WiringPi initialization successful\n");
	 
	 // Setup all hardware components
	 buzzer_setup();
	 lcd_file_descriptor = wiringPiI2CSetup(LCD_I2C_ADDRESS);
	 
	 if (lcd_file_descriptor < 0) {
		 printf("❌ ERROR: Failed to initialize I2C for LCD!\n");
		 return 1;
	 }
	 
	 lcd_initialize();
	 ultrasonic_sensor_setup();
	 
	 // Show startup message
	 show_startup_message();
	 printf("🚀 System ready! Starting distance monitoring...\n");
	 printf("📏 Safe: >50cm | ⚠️ Warning: 20-50cm | 🚨 Danger: <20cm\n");
	 printf("💡 Press Ctrl+C to safely exit\n\n");
	 
	 // Main measurement loop with program_running check
	 while (program_running) {
		 // Take distance measurement
		 measured_distance = measure_distance();
		 
		 // Check if we should continue
		 if (!program_running) break;
		 
		 // Display results on LCD and console
		 display_distance_info(measured_distance);
		 
		 // Check again before playing sound
		 if (!program_running) break;
		 
		 // Play appropriate sound alert
		 play_proximity_alert(measured_distance);
		 
		 // Small delay before next measurement (with exit check)
		 for (int i = 0; i < 10 && program_running; i++) {
			 delay(10);
		 }
	 }
	 
	 return 0;
 }
 