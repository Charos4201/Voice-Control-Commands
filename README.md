# Voice-Control-Commands
Voice control commands for computer to Arduino. 

THIS IS A PROTOTYPE

- Uses laptop microphone to convert speech to text and then Arduino ide to convert text and commands into the OLED screen / passive speaker
- Final product will utilize a raspberry pi to better sort code / remove need for Visual Studio and Arduino to both run
- Must speak in a clear voice, otherwise it might not hear text correctly

- Uses Google's Web Speech API- free
- All Commands are hard coded, don't want to pay for an API

- Has command that kills code from the place the python part is running. Otherwise will run forever until manually killed.

COMMANDS IMPLEMENTED SO FAR
- Wake up: "Hey Homey Buddy"
- Reminders: "Remind me to ... in ... minutes / minute"
           | "Remind me to ... at (time wanted)"
- Current time: "What time is it"
- Thank you: "Thank you homey buddy"
- Shut off switch: "Goodbye"
