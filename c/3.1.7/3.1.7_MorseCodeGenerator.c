#include <stdio.h>
#include <wiringPi.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <signal.h>

// --- Hardware Configuration ---
#define BUZZER_PIN      3
#define LED_PIN         0
#define DOT_DURATION    125   // Duration for dot (milliseconds)
#define DASH_DURATION   250   // Duration for dash (milliseconds)
#define MAX_INPUT_SIZE  100   // Maximum input string length

// --- Morse Code Dictionary ---
typedef struct {
    char character;
    const char* morse_pattern;
} MorseCode;

const MorseCode morse_dictionary[] = {
    // Letters A-Z
    {'A', ".-"},   {'B', "-..."}, {'C', "-.-."}, {'D', "-.."},  {'E', "."},
    {'F', "..-."}, {'G', "--."},  {'H', "...."}, {'I', ".."},   {'J', ".---"},
    {'K', "-.-"},  {'L', ".-.."}, {'M', "--"},   {'N', "-."},   {'O', "---"},
    {'P', ".--."}, {'Q', "--.-"}, {'R', ".-."},  {'S', "..."},  {'T', "-"},
    {'U', "..-"},  {'V', "...-"}, {'W', ".--"},  {'X', "-..-"}, {'Y', "-.--"},
    {'Z', "--.."},
    
    // Numbers 0-9
    {'0', "-----"}, {'1', ".----"}, {'2', "..---"}, {'3', "...--"}, {'4', "....-"},
    {'5', "....."}, {'6', "-...."}, {'7', "--..."}, {'8', "---.."}, {'9', "----."},
    
    // Special characters
    {'?', "..--.."}, {'/', "-..-."}, {',', "--..--"}, {'.', ".-.-.-"},
    {';', "-.-.-."}, {'!', "-.-.--"}, {'@', ".--.-."}, {':', "---..."}
};

const int dictionary_size = sizeof(morse_dictionary) / sizeof(morse_dictionary[0]);

/**
 * @brief Find Morse code pattern for a character
 * @param character Character to look up
 * @return Morse code pattern string, or NULL if not found
 */
const char* find_morse_pattern(char character) {
    for (int i = 0; i < dictionary_size; i++) {
        if (morse_dictionary[i].character == character) {
            return morse_dictionary[i].morse_pattern;
        }
    }
    return NULL;  // Character not found
}

/**
 * @brief Turn on LED and buzzer
 */
void signal_on() {
    digitalWrite(LED_PIN, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);
}

/**
 * @brief Turn off LED and buzzer
 */
void signal_off() {
    digitalWrite(LED_PIN, LOW);
    digitalWrite(BUZZER_PIN, LOW);
}

/**
 * @brief Play a dot or dash signal
 * @param duration Signal duration in milliseconds
 */
void play_signal(int duration) {
    signal_on();
    delay(duration);
    signal_off();
    delay(DOT_DURATION);  // Short pause between dots/dashes
}

/**
 * @brief Convert and play a single character as Morse code
 * @param character Character to convert and play
 */
void play_morse_character(char character) {
    // Skip spaces (use as word separator)
    if (character == ' ') {
        delay(DASH_DURATION * 2);  // Long pause for word separation
        return;
    }
    
    // Convert to uppercase
    character = toupper(character);
    
    // Find Morse pattern
    const char* pattern = find_morse_pattern(character);
    if (pattern == NULL) {
        printf("⚠️ Character '%c' not supported\n", character);
        return;
    }
    
    printf("📡 %c → %s\n", character, pattern);
    
    // Play each dot/dash in the pattern
    for (int i = 0; pattern[i] != '\0'; i++) {
        if (pattern[i] == '.') {
            play_signal(DOT_DURATION);
        } else if (pattern[i] == '-') {
            play_signal(DASH_DURATION);
        }
    }
    
    // Pause between characters
    delay(DASH_DURATION);
}

/**
 * @brief Convert and play entire message as Morse code
 * @param message Text message to convert
 */
void play_morse_message(const char* message) {
    printf("\n🎵 Playing Morse code for: \"%s\"\n", message);
    printf("--- Morse Code Output ---\n");
    
    for (int i = 0; message[i] != '\0'; i++) {
        play_morse_character(message[i]);
    }
    
    printf("✅ Transmission complete!\n\n");
}

/**
 * @brief Initialize hardware pins
 */
void setup_hardware() {
    printf("🔧 Initializing Morse Code Generator...\n");
    
    if (wiringPiSetup() == -1) {
        printf("❌ wiringPi setup failed!\n");
        exit(1);
    }
    
    // Setup output pins
    pinMode(BUZZER_PIN, OUTPUT);
    pinMode(LED_PIN, OUTPUT);
    
    // Ensure outputs are off initially
    signal_off();
    
    printf("📻 Buzzer pin: %d\n", BUZZER_PIN);
    printf("💡 LED pin: %d\n", LED_PIN);
    printf("⏱️ Dot duration: %dms, Dash duration: %dms\n", DOT_DURATION, DASH_DURATION);
    printf("✅ Hardware ready!\n\n");
}

/**
 * @brief Display available characters
 */
void display_supported_characters() {
    printf("📝 Supported characters:\n");
    printf("   Letters: A-Z\n");
    printf("   Numbers: 0-9\n");
    printf("   Special: ? / , . ; ! @ :\n");
    printf("   Spaces are used as word separators\n\n");
}

/**
 * @brief Clean up and exit
 */
void cleanup_exit(int sig) {
    printf("\n🧹 Shutting down Morse code generator...\n");
    
    // Turn off all outputs
    signal_off();
    
    printf("✅ Goodbye!\n");
    exit(0);
}

/**
 * @brief Main program loop
 */
void morse_generator_loop() {
    char input_message[MAX_INPUT_SIZE];
    
    printf("🎯 Morse Code Generator active!\n");
    printf("Type your message and press Enter to convert to Morse code.\n");
    printf("Press Ctrl+C to exit\n\n");
    
    display_supported_characters();
    
    while (1) {
        printf("💬 Enter message: ");
        fflush(stdout);
        
        // Read input message
        if (fgets(input_message, sizeof(input_message), stdin) != NULL) {
            // Remove newline character
            input_message[strcspn(input_message, "\n")] = '\0';
            
            // Check for empty input
            if (strlen(input_message) == 0) {
                printf("⚠️ Empty message. Please enter some text.\n\n");
                continue;
            }
            
            // Play the Morse code
            play_morse_message(input_message);
        }
    }
}

/**
 * @brief Main function
 */
int main(void) {
    // Handle Ctrl+C
    signal(SIGINT, cleanup_exit);
    
    printf("=== Morse Code Generator ===\n");
    printf("LED + Buzzer Morse Code Output\n\n");
    
    // Initialize hardware
    setup_hardware();
    
    // Start main loop
    morse_generator_loop();
    
    return 0;
}
