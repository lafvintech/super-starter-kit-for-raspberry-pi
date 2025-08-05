#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time
import sys

# Define the GPIO pin connected to the passive buzzer
BUZZER_PIN = 11

# Define PWM initial frequency and duty cycle
INITIAL_FREQUENCY = 440
PWM_DUTY_CYCLE = 50

# Define note duration multiplier (beat * NOTE_DURATION = actual duration)
NOTE_DURATION = 0.5

# Frequency definitions for musical notes in C major scale
# CL = Bass tone frequencies, CM = Midrange tone frequencies, CH = Treble tone frequencies
FREQ_BASS = [0, 131, 147, 165, 175, 196, 211, 248]    # C Low octave
FREQ_MID = [0, 262, 294, 330, 350, 393, 441, 495]     # C Middle octave  
FREQ_HIGH = [0, 525, 589, 661, 700, 786, 882, 990]    # C High octave

# Song 1: Musical notes and beats
SONG_1_NOTES = [
    FREQ_MID[3], FREQ_MID[5], FREQ_MID[6], FREQ_MID[3], FREQ_MID[2], FREQ_MID[3], FREQ_MID[5], FREQ_MID[6],
    FREQ_HIGH[1], FREQ_MID[6], FREQ_MID[5], FREQ_MID[1], FREQ_MID[3], FREQ_MID[2], FREQ_MID[2], FREQ_MID[3],
    FREQ_MID[5], FREQ_MID[2], FREQ_MID[3], FREQ_MID[3], FREQ_BASS[6], FREQ_BASS[6], FREQ_BASS[6], FREQ_MID[1],
    FREQ_MID[2], FREQ_MID[3], FREQ_MID[2], FREQ_BASS[7], FREQ_BASS[6], FREQ_MID[1], FREQ_BASS[5]
]

SONG_1_BEATS = [
    1, 1, 3, 1, 1, 3, 1, 1,  # 1 means 1/8 beat
    1, 1, 1, 1, 1, 1, 3, 1,
    1, 3, 1, 1, 1, 1, 1, 1,
    1, 2, 1, 1, 1, 1, 1, 1,
    1, 1, 3
]

# Song 2: Musical notes and beats  
SONG_2_NOTES = [
    FREQ_MID[1], FREQ_MID[1], FREQ_MID[1], FREQ_BASS[5], FREQ_MID[3], FREQ_MID[3], FREQ_MID[3], FREQ_MID[1],
    FREQ_MID[1], FREQ_MID[3], FREQ_MID[5], FREQ_MID[5], FREQ_MID[4], FREQ_MID[3], FREQ_MID[2], FREQ_MID[2],
    FREQ_MID[3], FREQ_MID[4], FREQ_MID[4], FREQ_MID[3], FREQ_MID[2], FREQ_MID[3], FREQ_MID[1], FREQ_MID[1],
    FREQ_MID[3], FREQ_MID[2], FREQ_BASS[5], FREQ_BASS[7], FREQ_MID[2], FREQ_MID[1]
]

SONG_2_BEATS = [
    1, 1, 2, 2, 1, 1, 2, 2,  # 1 means 1/8 beat
    1, 1, 2, 2, 1, 1, 3, 1,
    1, 2, 2, 1, 1, 2, 2, 1,
    1, 2, 2, 1, 1, 3
]

# Global PWM object for buzzer control
buzzer_pwm = None

def setup_buzzer():
    """
    Initializes GPIO and configures the passive buzzer with PWM.
    Returns: 0 on success, 1 on failure.
    """
    global buzzer_pwm
    
    try:
        # Set GPIO mode to BOARD numbering (physical pin numbers)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setwarnings(False)
        
        # Configure buzzer pin as output
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        
        # Initialize PWM on buzzer pin with initial frequency
        buzzer_pwm = GPIO.PWM(BUZZER_PIN, INITIAL_FREQUENCY)
        buzzer_pwm.start(PWM_DUTY_CYCLE)  # Start PWM with specified duty cycle
        
        print("Passive buzzer PWM setup successful!")
        return 0
        
    except Exception as e:
        print(f"Failed to setup buzzer PWM: {e}")
        return 1

def play_song(notes, beats, song_name):
    """
    Plays a song using the provided notes and beats arrays.
    Parameters:
        notes: Array of frequency values for each note
        beats: Array of beat durations for each note  
        song_name: Name of the song for display purposes
    """
    print(f"\n    Playing {song_name}...")
    
    try:
        # Play each note in the song (starting from index 1, skipping index 0)
        for i in range(1, len(notes)):
            # Change PWM frequency to play the current note
            buzzer_pwm.ChangeFrequency(notes[i])
            
            # Hold the note for the specified beat duration
            time.sleep(beats[i] * NOTE_DURATION)
            
    except Exception as e:
        print(f"Error playing {song_name}: {e}")

def music_loop():
    """
    Main music loop that continuously plays both songs.
    This function runs indefinitely until interrupted.
    """
    try:
        while True:
            # Play song 1
            play_song(SONG_1_NOTES, SONG_1_BEATS, "Song 1")
            
            # Wait between songs
            time.sleep(1)
            
            # Play song 2  
            play_song(SONG_2_NOTES, SONG_2_BEATS, "Song 2")
            
            # Wait before repeating the cycle
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\nMusic loop interrupted by user")
        raise  # Re-raise to be handled by main()

def destroy():
    """
    Clean up function for PWM and GPIO resources.
    Ensures buzzer is stopped and GPIO is properly cleaned up.
    """
    global buzzer_pwm
    
    try:
        if buzzer_pwm:
            buzzer_pwm.stop()  # Stop PWM signal
            
        GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Set buzzer pin to High (off)
        GPIO.cleanup()  # Release all GPIO resources
        
        print("PWM stopped and GPIO cleanup completed")
        
    except Exception as e:
        print(f"Error during cleanup: {e}")

def main():
    """
    Main function.
    Returns: Integer status code. 0 for success, 1 for error.
    """
    # Initialize the buzzer PWM
    if setup_buzzer() != 0:
        return 1  # Exit if setup fails
    
    try:
        # Start the main music loop
        music_loop()
        
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
        destroy()
        return 0
        
    except Exception as e:
        print(f"An error occurred: {e}")
        destroy()
        return 1

# If run this script directly, do:
if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
