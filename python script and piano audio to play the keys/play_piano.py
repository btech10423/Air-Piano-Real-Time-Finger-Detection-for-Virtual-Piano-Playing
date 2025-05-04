import serial
import pygame
import time

# Initialize pygame mixer
pygame.mixer.init()

# Load welcome message sound
welcome_sound = pygame.mixer.Sound("welcome_message.wav")

# Load piano sounds (assuming note_0.wav to note_7.wav correspond to piano keys)
sounds = {i: pygame.mixer.Sound(f"note_{i}.wav") for i in range(8)}

# Open serial port (adjust the port name based on our system)
ser = serial.Serial('COM23', 115200)  
print("Listening for piano commands...")

while True:
    line = ser.readline().decode().strip()
    if line == "WELCOME":
        welcome_sound.play()
        # Wait for the welcome message to finish before processing further commands
        time.sleep(welcome_sound.get_length())
    elif line.startswith("PLAY"):
        key = int(line.split()[1])
        sounds[key].play()
        print(f"Playing key {key}")
    elif line.startswith("RELEASE"):
        key = int(line.split()[1])
        sounds[key].stop()
        print(f"Released key {key}")