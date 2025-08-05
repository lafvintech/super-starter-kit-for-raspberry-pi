/**
 * @file digital_counter_display.c
 * @brief 4-Digit Digital Counter with Sensor Input
 * @description This program creates a digital counter that increments when a sensor
 *              detects an object. The count is displayed on a 4-digit 7-segment display
 *              using a 74HC595 shift register for multiplexing.
 * @author Enhanced version for beginners
 */

 #include <wiringPi.h>
 #include <stdio.h>
 #include <wiringShift.h>
 #include <signal.h>
 #include <unistd.h>
 #include <stdlib.h>
 
 // ========== PIN CONFIGURATION ==========
 #define SENSOR_INPUT_PIN    25    // Pin connected to the sensor (detects objects)
 
 // 74HC595 Shift Register Control Pins
 #define DATA_PIN           5     // SDI - Serial Data Input to shift register
 #define LATCH_PIN          4     // RCLK - Register Clock (latch data to output)
 #define CLOCK_PIN          1     // SRCLK - Shift Register Clock
 
 // 4-Digit Display Control Pins (digit selection)
 const int digit_control_pins[] = {12, 3, 2, 0};  // Controls which digit is active
 #define TOTAL_DIGITS       4     // Number of digits in the display
 
 // ========== 7-SEGMENT DISPLAY PATTERNS ==========
 // Each number represents the LED segments to light up for digits 0-9
 // Format: 0bGFEDCBA (where A-G are the 7 segments of the display)
 const unsigned char digit_patterns[] = {
     0x3F,  // 0: segments A,B,C,D,E,F
     0x06,  // 1: segments B,C
     0x5B,  // 2: segments A,B,D,E,G
     0x4F,  // 3: segments A,B,C,D,G
     0x66,  // 4: segments B,C,F,G
     0x6D,  // 5: segments A,C,D,F,G
     0x7D,  // 6: segments A,C,D,E,F,G
     0x07,  // 7: segments A,B,C
     0x7F,  // 8: segments A,B,C,D,E,F,G
     0x6F   // 9: segments A,B,C,D,F,G
 };
 
 // ========== GLOBAL VARIABLES ==========
 volatile int object_count = 0;           // Counter for detected objects
 volatile int program_active = 1;         // Flag to control program execution
 int previous_sensor_state = 1;           // Previous state of sensor (for edge detection)
 
 // ========== FUNCTION DECLARATIONS ==========
 void initialize_hardware(void);
 void activate_digit_position(int digit_number);
 void send_data_to_shift_register(unsigned char data);
 void clear_all_segments(void);
 void update_display_output(void);
 void detect_sensor_changes(void);
 void handle_program_exit(int signal_number);
 void setup_exit_handler(void);
 
 // ========== HARDWARE INITIALIZATION ==========
 
 /**
  * @brief Initialize all GPIO pins and hardware components
  * @description Sets up wiringPi library and configures all pins for input/output
  */
 void initialize_hardware(void) {
     printf("🔧 Initializing Digital Counter System...\n");
     
     // Initialize wiringPi library
     if (wiringPiSetup() == -1) { 
         printf("❌ ERROR: Failed to initialize wiringPi library!\n");
         printf("💡 Try running with: sudo ./digital_counter\n");
         exit(1);
     }
     printf("✅ WiringPi library initialized successfully\n");
     
     // Configure shift register control pins as outputs
     pinMode(DATA_PIN, OUTPUT);    // Data line to shift register
     pinMode(LATCH_PIN, OUTPUT);   // Latch pin to update display
     pinMode(CLOCK_PIN, OUTPUT);   // Clock pin for shifting data
     printf("✅ Shift register pins configured\n");
     
     // Configure digit control pins as outputs (for multiplexing)
     for (int i = 0; i < TOTAL_DIGITS; i++) {
         pinMode(digit_control_pins[i], OUTPUT);
         digitalWrite(digit_control_pins[i], HIGH);  // Start with all digits OFF
     }
     printf("✅ Display digit control pins configured\n");
     
     // Configure sensor pin as input
     pinMode(SENSOR_INPUT_PIN, INPUT);
     printf("✅ Sensor input pin configured\n");
     
     printf("🚀 Hardware initialization complete!\n\n");
 }
 
 // ========== DISPLAY CONTROL FUNCTIONS ==========
 
 /**
  * @brief Activate a specific digit position on the 4-digit display
  * @param digit_number Which digit to activate (0=rightmost, 3=leftmost)
  * @description Turns OFF all digits first, then turns ON the selected digit
  */
 void activate_digit_position(int digit_number) {
     // Turn OFF all digits first (HIGH = OFF for common cathode display)
     for (int i = 0; i < TOTAL_DIGITS; i++) {
         digitalWrite(digit_control_pins[i], HIGH);
     }
     
     // Turn ON the selected digit (LOW = ON for common cathode display)
     if (digit_number >= 0 && digit_number < TOTAL_DIGITS) {
         digitalWrite(digit_control_pins[digit_number], LOW);
     }
 }
 
 /**
  * @brief Send 8-bit data to the 74HC595 shift register
  * @param data The 8-bit pattern to send (represents which LED segments to light)
  * @description Shifts data bit by bit into the register, then latches it to output
  */
 void send_data_to_shift_register(unsigned char data) {
     // Send each bit of data, starting from the most significant bit (MSB)
     for (int bit_position = 0; bit_position < 8; bit_position++) {
         // Extract the current bit (starting from MSB)
         int current_bit = (data & (0x80 >> bit_position)) ? 1 : 0;
         
         // Send the bit to the shift register
         digitalWrite(DATA_PIN, current_bit);
         
         // Pulse the clock to shift the bit into the register
         digitalWrite(CLOCK_PIN, HIGH);
         delayMicroseconds(1);  // Small delay for reliable timing
         digitalWrite(CLOCK_PIN, LOW);
     }
     
     // Latch the data to the output (make it visible on display)
     digitalWrite(LATCH_PIN, HIGH);
     delayMicroseconds(1);
     digitalWrite(LATCH_PIN, LOW);
 }
 
 /**
  * @brief Clear all segments on the display
  * @description Sends all zeros to turn off all LED segments
  */
 void clear_all_segments(void) {
     send_data_to_shift_register(0x00);  // Send all zeros (all segments OFF)
 }
 
 /**
  * @brief Update the 4-digit display with current counter value
  * @description Uses multiplexing to display each digit sequentially
  *              Human eye sees all digits due to persistence of vision
  */
 void update_display_output(void) {
     // Extract individual digits from the counter value
     int ones_digit      = object_count % 10;           // Rightmost digit
     int tens_digit      = (object_count / 10) % 10;    // Second digit
     int hundreds_digit  = (object_count / 100) % 10;   // Third digit  
     int thousands_digit = (object_count / 1000) % 10;  // Leftmost digit
     
     // Display each digit for a brief moment (multiplexing)
     
     // Display ones digit (position 0 - rightmost)
     clear_all_segments();
     activate_digit_position(0);
     send_data_to_shift_register(digit_patterns[ones_digit]);
     delayMicroseconds(100);  // Brief delay to make digit visible
     
     // Display tens digit (position 1)
     clear_all_segments();
     activate_digit_position(1);
     send_data_to_shift_register(digit_patterns[tens_digit]);
     delayMicroseconds(100);
     
     // Display hundreds digit (position 2)
     clear_all_segments();
     activate_digit_position(2);
     send_data_to_shift_register(digit_patterns[hundreds_digit]);
     delayMicroseconds(100);
     
     // Display thousands digit (position 3 - leftmost)
     clear_all_segments();
     activate_digit_position(3);
     send_data_to_shift_register(digit_patterns[thousands_digit]);
     delayMicroseconds(100);
 }
 
 // ========== SENSOR PROCESSING ==========
 
 /**
  * @brief Detect changes in sensor state and increment counter
  * @description Uses edge detection to count objects passing the sensor
  *              Increments counter on falling edge (HIGH to LOW transition)
  */
 void detect_sensor_changes(void) {
     int current_sensor_state = digitalRead(SENSOR_INPUT_PIN);
     
     // Check for falling edge (object detected)
     // Falling edge = previous state was HIGH(1) and current state is LOW(0)
     if ((previous_sensor_state == 1) && (current_sensor_state == 0)) {
         object_count++;  // Increment the counter
         
         // Print status to console
         printf("🎯 Object detected! Count: %d\n", object_count);
         
         // Prevent counter overflow (reset at 10000)
         if (object_count >= 10000) {
             object_count = 0;
             printf("🔄 Counter reset to 0\n");
         }
     }
     
     // Update previous state for next comparison
     previous_sensor_state = current_sensor_state;
 }
 
 // ========== EXIT HANDLING ==========
 
 /**
  * @brief Handle program exit (Ctrl+C)
  * @param signal_number The signal number received
  */
 void handle_program_exit(int signal_number) {
     printf("\n🛑 Ctrl+C pressed! Shutting down...\n");
     
     // Clear the display
     clear_all_segments();
     for (int i = 0; i < TOTAL_DIGITS; i++) {
         digitalWrite(digit_control_pins[i], HIGH);
     }
     
     printf("📺 Display cleared\n");
     printf("📊 Final count: %d objects detected\n", object_count);
     printf("👋 Digital Counter program terminated!\n");
     
     program_active = 0;
     exit(0);
 }
 
 /**
  * @brief Setup signal handler for graceful exit
  */
 void setup_exit_handler(void) {
     signal(SIGINT, handle_program_exit);
     printf("🛡️  Press Ctrl+C to safely exit\n");
 }
 
 // ========== MAIN PROGRAM LOOP ==========
 
 /**
  * @brief Main program execution loop
  * @description Continuously updates display and checks sensor input
  */
 void run_counter_program(void) {
     printf("🚀 Starting Digital Counter...\n");
     printf("📊 Current count: %d\n", object_count);
     printf("👁️  Monitoring sensor for object detection...\n");
     printf("💡 Press Ctrl+C to exit\n\n");
     
     // Main program loop
     while (program_active) {
         // Update the 4-digit display with current count
         update_display_output();
         
         // Check sensor for object detection
         detect_sensor_changes();
         
         // Small delay to prevent excessive CPU usage
         delayMicroseconds(50);
     }
 }
 
 // ========== MAIN FUNCTION ==========
 
 /**
  * @brief Main function - Program entry point
  * @return Exit status code
  */
 int main(void) {
     printf("========================================\n");
     printf("🔢 4-Digit Digital Counter System\n");
     printf("========================================\n");
     printf("📝 This program counts objects detected by a sensor\n");
     printf("📺 Count is displayed on a 4-digit 7-segment display\n");
     printf("⚡ Uses 74HC595 shift register for multiplexing\n\n");
     
     // Setup exit handler first
     setup_exit_handler();
     
     // Initialize all hardware components
     initialize_hardware();
     
     // Start the main program
     run_counter_program();
     
     return 0;
 }
 