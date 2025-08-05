/*
 * LED Matrix Control Program using 74HC595 Shift Register - FINAL VERSION
 * This program creates animated patterns on an 8x8 LED matrix
 * Hardware: Raspberry Pi + 74HC595 + 8x8 LED Matrix
 */

 #include <wiringPi.h>
 #include <stdio.h>
 
 // Pin definitions for 74HC595 shift register
 #define SDI     0   // Serial Data Input (DS pin on 74HC595)
 #define RCLK    1   // Register Clock (ST_CP pin) - latches data to output
 #define SRCLK   2   // Shift Register Clock (SH_CP pin) - shifts data
 
 #define DISPLAY_DELAY   100  // Delay between pattern changes (ms)
 
 // Animation pattern data
 unsigned char scan_down_high[8] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80};
 unsigned char scan_down_low[8]  = {0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00};
 
 unsigned char scan_right_high[8] = {0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff};
 unsigned char scan_right_low[8]  = {0x7f, 0xbf, 0xdf, 0xef, 0xf7, 0xfb, 0xfd, 0xfe};
 
 // Arrow patterns
 unsigned char arrow_up_high[8] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80};
 unsigned char arrow_up_low[8]  = {0xe7, 0xc3, 0x81, 0x00, 0xe7, 0xe7, 0xe7, 0xe7};
 
 unsigned char arrow_right_high[8] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80};
 unsigned char arrow_right_low[8]  = {0xef, 0xcf, 0x8f, 0x00, 0x00, 0x8f, 0xcf, 0xef};
 
 unsigned char arrow_down_high[8] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80};
 unsigned char arrow_down_low[8]  = {0xe7, 0xe7, 0xe7, 0xe7, 0x00, 0x81, 0xc3, 0xe7};
 
 unsigned char arrow_left_high[8] = {0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80};
 unsigned char arrow_left_low[8]  = {0xf7, 0xf3, 0xf1, 0x00, 0x00, 0xf1, 0xf3, 0xf7};
 
 void initPins(void) {
	 pinMode(SDI, OUTPUT);
	 pinMode(RCLK, OUTPUT);
	 pinMode(SRCLK, OUTPUT);
	 digitalWrite(SDI, LOW);
	 digitalWrite(RCLK, LOW);
	 digitalWrite(SRCLK, LOW);
 }
 
 /*
  * Send one byte of data to the 74HC595 shift register
  */
 void shiftOutByte(unsigned char data) {
	 for (int bit = 0; bit < 8; bit++) {
		 digitalWrite(SDI, (data & 0x80) ? HIGH : LOW);
		 data <<= 1;
		 
		 digitalWrite(SRCLK, HIGH);
		 delayMicroseconds(10);
		 digitalWrite(SRCLK, LOW);
	 }
 }
 
 /*
  * Latch the data from shift register to output pins
  */
 void latchOutput(void) {
	 digitalWrite(RCLK, HIGH);
	 delayMicroseconds(10);
	 digitalWrite(RCLK, LOW);
 }
 
 /*
  * 🆕 Clear the entire LED matrix display
  * Turns off all LEDs by sending zeros to both shift registers
  */
 void clearDisplay(void) {
	 shiftOutByte(0x00);  // Clear column data (all columns OFF)
	 shiftOutByte(0x00);  // Clear row data (all rows OFF)
	 latchOutput();       // Apply the changes
 }
 
 void displayPattern(unsigned char low_byte, unsigned char high_byte) {
	 shiftOutByte(low_byte);
	 shiftOutByte(high_byte);
	 latchOutput();
	 delay(DISPLAY_DELAY);
 }
 
 /*
  * Display a complete 8x8 pattern using row scanning
  */
 void displayCompletePattern(unsigned char* row_data, unsigned char* col_data, int duration_ms) {
	 unsigned long start_time = millis();
	 
	 while ((millis() - start_time) < duration_ms) {
		 for (int row = 0; row < 8; row++) {
			 shiftOutByte(col_data[row]);
			 shiftOutByte(row_data[row]);
			 latchOutput();
			 delayMicroseconds(500);
			 
			 if ((millis() - start_time) >= duration_ms) {
				 break;
			 }
		 }
	 }
 }
 
 void playTopToBottomScan(void) {
	 printf("Playing: Top-to-bottom scan...\n");
	 for (int i = 0; i < 8; i++) {
		 displayPattern(scan_down_low[i], scan_down_high[i]);
	 }
	 delay(200);
 }
 
 void playLeftToRightScan(void) {
	 printf("Playing: Left-to-right scan...\n");
	 for (int i = 0; i < 8; i++) {
		 displayPattern(scan_right_low[i], scan_right_high[i]);
	 }
	 delay(200);
 }
 
 /*
  * Stage 3: Arrow animation (clockwise rotation)
  * 🔧 ADDED: Clear display after each arrow and at the end
  */
 void playArrowAnimation(void) {
	 printf("Playing: Arrow rotation...\n");
	 
	 printf("  ↑ UP\n");
	 displayCompletePattern(arrow_up_high, arrow_up_low, 1000);
	 clearDisplay();  // 🆕 Clear after UP arrow
	 delay(100);      // Brief pause to see the clear
	 
	 printf("  → RIGHT\n");  
	 displayCompletePattern(arrow_right_high, arrow_right_low, 1000);
	 clearDisplay();  // 🆕 Clear after RIGHT arrow
	 delay(100);
	 
	 printf("  ↓ DOWN\n");
	 displayCompletePattern(arrow_down_high, arrow_down_low, 1000);
	 clearDisplay();  // 🆕 Clear after DOWN arrow
	 delay(100);
	 
	 printf("  ← LEFT\n");
	 displayCompletePattern(arrow_left_high, arrow_left_low, 1000);
	 clearDisplay();  // 🆕 Clear after LEFT arrow - THIS FIXES THE ISSUE!
	 
	 printf("Arrow sequence completed, clearing display...\n");
	 delay(500);      // Pause before next cycle
 }
 
 int main(void) {
	 if (wiringPiSetup() == -1) {
		 printf("Error: Failed to initialize wiringPi!\n");
		 return 1;
	 }
 
	 printf("LED Matrix Animation Started...\n");
	 printf("Animation sequence: Top-to-bottom → Left-to-right → Arrow rotation\n");
	 printf("Display clears between animations for clean transitions\n");
	 printf("Press Ctrl+C to exit\n");
 
	 initPins();
	 
	 // 🆕 Clear display at startup
	 clearDisplay();
	 printf("Display initialized and cleared\n");
 
	 while (1) {
		 playTopToBottomScan();
		 clearDisplay();        // 🆕 Clear after top-to-bottom scan
		 delay(100);
		 
		 playLeftToRightScan();
		 clearDisplay();        // 🆕 Clear after left-to-right scan  
		 delay(100);
		 
		 playArrowAnimation();  // Already has clear after each arrow
		 
		 printf("=== Starting new animation cycle ===\n");
	 }
 
	 return 0;
 }
 