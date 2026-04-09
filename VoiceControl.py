import speech_recognition as sr
from enum import Enum
import threading
import time
from datetime import datetime, timedelta
import re
import serial

# Initialize communication with Arduino
arduino = serial.Serial('COM4', 9600)
time.sleep(2)

# List to store reminders
reminders = []


# Enum for supported languages
class Language(Enum):
    ENGLISH = 'en-US'


# Define wake and kill words
WAKE_WORD = "hey homie buddy"
STOP_WORD = "goodbye"


# VoiceControl class, provides methods for voice control using speech recognition library
class VoiceControl():
    # Static method to print available microphone devices
    def print_mic_device_index():
        for index, name in enumerate(sr.Microphone.list_microphone_names()):
            print("{1}, device_index={0}".format(index, name))

    # Listens for wake word and then for commands, stops on stop word
    @staticmethod
    def voice_control_with_wake_word(device_index, language=Language.ENGLISH):
        recognizer = sr.Recognizer()

        with sr.Microphone(device_index=device_index) as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Waiting for wake word...")

            while True:
                try:
                    # Listen in short bursts
                    audio = recognizer.listen(
                        source, timeout=2, phrase_time_limit=10)
                    text = recognizer.recognize_google(
                        audio, language=language.value).lower()

                    print("Heard:", text)

                    # Checks for stop word
                    if STOP_WORD in text:
                        arduino.write(b"See you later!\n")
                        print("Stop word detected. Shutting down.")
                        break

                    if "thank you homey buddy" in text:
                        arduino.write(b"You're welcome!\n")
                        print("You're welcome!")
                        continue

                    # Check for wake word
                    if WAKE_WORD in text:
                        print("Wake word detected")
                        arduino.write(b"Wake word detected\nHow can I help?\n")

                        # Listens for actual command
                        audio = recognizer.listen(
                            source, timeout=2, phrase_time_limit=20)
                        command = recognizer.recognize_google(
                            audio, language=language.value)

                        print("Command:", command)
                        arduino.write((f"Command: {command}\n").encode())
                        time.sleep(0.1)

                        # Tries to take reminder details from command
                        task, remind_time = reminder(command)

                        # Check for time
                        if "what time is it" in command:
                            current_time = time_now()
                            print(f"The current time is {current_time}")
                            arduino.write(
                                (f"The current time is\n{current_time}").encode())
                            time.sleep(0.1)
                            continue

                        # Sets reminder if details were understood
                        if task:
                            reminders.append((task, remind_time))
                            print(
                                f"Reminder set for '{task}' at {remind_time}")
                            fullMessage = f"{task}\nTime: {remind_time.strftime('%I:%M %p')}"
                            arduino.write((fullMessage + "\n").encode())
                            time.sleep(0.1)
                        else:
                            print("Could not understand reminder format.")
                            arduino.write(
                                ("Could not understand reminder format.\n").encode())

                except sr.WaitTimeoutError:
                    # No speech detected, keep looping
                    continue
                except sr.UnknownValueError:
                    # Couldn't understand audio
                    continue
                except sr.RequestError as e:
                    print(f"API error: {e}")


# Function to create reminder details from command
def reminder(command):
    command = command.lower()

    # Pattern: "in X minutes"
    match_in = re.search(r"remind me to (.+) in (\d+) minutes", command)
    if match_in:
        task = match_in.group(1)
        minutes = int(match_in.group(2))
        remind_time = datetime.now() + timedelta(minutes=minutes)
        return task, remind_time

    match_in_two = re.search(r"remind me to (.+) in 1 minute", command)
    if match_in_two:
        task = match_in_two.group(1)
        remind_time = datetime.now() + timedelta(minutes=1)
        return task, remind_time

    # Pattern: "at HH:MM"
    match_at = re.search(r"remind me to (.+) at (\d{1,2}):(\d{2})", command)
    if match_at:
        task = match_at.group(1)
        hour = int(match_at.group(2))
        minute = int(match_at.group(3))

        remind_time = datetime.now().replace(hour=hour, minute=minute, second=0)

        # If time already passed today → schedule for tomorrow
        if remind_time < datetime():
            remind_time += timedelta(days=1)
        if hour > 12:
            remind_time = remind_time.replace(hour=hour - 12)

        return task, remind_time

    return None, None


# Prints current time in 12 hour format
def time_now():
    now = datetime.now()
    return now.strftime("%I:%M %p")


# Checks reminders every second and triggers when time is reached
# Sends reminder to Arduino and removes it from reminder list
def reminder_worker():
    while True:
        now = datetime.now()

        for reminder in reminders[:]:
            task, remind_time = reminder

            if now >= remind_time:
                print(f"Reminder: {task}")
                arduino.write((f"REMINDER!\n{task}\n").encode())
                reminders.remove(reminder)

        time.sleep(1)


# Runs Voice Control with specified device index
def run_voice_control(device_index):
    VoiceControl.voice_control_with_wake_word(device_index)


# Usage of the VoiceControl class to check microphone devices and run voice control in English
if __name__ == '__main__':
    threading.Thread(target=reminder_worker, daemon=True).start()
    run_voice_control(device_index=1)
