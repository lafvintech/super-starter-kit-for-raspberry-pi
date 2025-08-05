#include <wiringPi.h>
#include <softTone.h>
#include <stdio.h>
#include <stdlib.h> // Required for exit()

// Define the GPIO pin for the passive buzzer.
#define BUZZER_PIN 0

// Define the base duration for one beat in milliseconds.
#define BEAT_DURATION_MS 500

// Define note frequencies for three octaves.
// C (Do), D (Re), E (Mi), F (Fa), G (Sol), A (La), B (Si)
#define NOTE_C_LOW  131
#define NOTE_D_LOW  147
#define NOTE_E_LOW  165
#define NOTE_F_LOW  175
#define NOTE_G_LOW  196
#define NOTE_A_LOW  221
#define NOTE_B_LOW  248

#define NOTE_C_MID  262
#define NOTE_D_MID  294
#define NOTE_E_MID  330
#define NOTE_F_MID  350
#define NOTE_G_MID  393
#define NOTE_A_MID  441
#define NOTE_B_MID  495

#define NOTE_C_HIGH 525
#define NOTE_D_HIGH 589
#define NOTE_E_HIGH 661
#define NOTE_F_HIGH 700
#define NOTE_G_HIGH 786
#define NOTE_A_HIGH 882
#define NOTE_B_HIGH 990

// Structure to represent a musical note (frequency and duration).
typedef struct {
    int frequency;
    int duration_beats;
} Note;

// First song: An array of Notes.
const Note SONG_1[] = {
    {NOTE_E_MID, 1}, {NOTE_G_MID, 1}, {NOTE_A_MID, 3}, {NOTE_E_MID, 1}, {NOTE_D_MID, 1},
    {NOTE_E_MID, 3}, {NOTE_G_MID, 1}, {NOTE_A_MID, 1}, {NOTE_C_HIGH, 1}, {NOTE_A_MID, 1},
    {NOTE_G_MID, 1}, {NOTE_C_MID, 1}, {NOTE_E_MID, 1}, {NOTE_D_MID, 1}, {NOTE_D_MID, 3},
    {NOTE_E_MID, 1}, {NOTE_G_MID, 1}, {NOTE_D_MID, 3}, {NOTE_E_MID, 1}, {NOTE_E_MID, 1},
    {NOTE_A_LOW, 1}, {NOTE_A_LOW, 1}, {NOTE_A_LOW, 1}, {NOTE_C_MID, 1}, {NOTE_D_MID, 1},
    {NOTE_E_MID, 2}, {NOTE_D_MID, 1}, {NOTE_B_LOW, 1}, {NOTE_A_LOW, 1}, {NOTE_C_MID, 1},
    {NOTE_G_LOW, 3}
};
const int SONG_1_LENGTH = sizeof(SONG_1) / sizeof(SONG_1[0]);

// Second song: An array of Notes.
const Note SONG_2[] = {
    {NOTE_C_MID, 1}, {NOTE_C_MID, 1}, {NOTE_C_MID, 1}, {NOTE_G_LOW, 3}, {NOTE_E_MID, 1},
    {NOTE_E_MID, 1}, {NOTE_E_MID, 1}, {NOTE_C_MID, 3}, {NOTE_C_MID, 1}, {NOTE_E_MID, 1},
    {NOTE_G_MID, 1}, {NOTE_G_MID, 1}, {NOTE_F_MID, 1}, {NOTE_E_MID, 1}, {NOTE_D_MID, 3},
    {NOTE_D_MID, 1}, {NOTE_E_MID, 1}, {NOTE_F_MID, 1}, {NOTE_F_MID, 2}, {NOTE_E_MID, 1},
    {NOTE_D_MID, 1}, {NOTE_E_MID, 1}, {NOTE_C_MID, 3}, {NOTE_C_MID, 1}, {NOTE_E_MID, 1},
    {NOTE_D_MID, 1}, {NOTE_G_LOW, 3}, {NOTE_B_LOW, 3}, {NOTE_D_MID, 2}, {NOTE_C_MID, 3}
};
const int SONG_2_LENGTH = sizeof(SONG_2) / sizeof(SONG_2[0]);

/**
 * @brief Initializes wiringPi and the softTone library for the buzzer.
 */
void setup_passive_buzzer() {
    if (wiringPiSetup() == -1) {
        printf("Failed to setup wiringPi!\n");
        exit(1);
    }
    if (softToneCreate(BUZZER_PIN) == -1) {
        printf("Failed to setup softTone on pin %d!\n", BUZZER_PIN);
        exit(1);
    }
}

/**
 * @brief Plays a song on the buzzer.
 * @param song An array of Note structures representing the song.
 * @param length The number of notes in the song.
 */
void play_song(const Note song[], int length) {
    for (int i = 0; i < length; i++) {
        softToneWrite(BUZZER_PIN, song[i].frequency);
        delay(song[i].duration_beats * BEAT_DURATION_MS);
    }
    // Stop the tone after the song is finished.
    softToneWrite(BUZZER_PIN, 0);
}

/**
 * @brief Main function.
 * @return Integer status code.
 */
int main(void) {         
    setup_passive_buzzer();

    while (1) {
        printf("Playing the first song...\n");
        play_song(SONG_1, SONG_1_LENGTH);
        delay(1000); // Pause between songs

        printf("Playing the second song...\n");
        play_song(SONG_2, SONG_2_LENGTH);
        delay(1000); // Pause before repeating
    }

    return 0; // This is unreachable.
