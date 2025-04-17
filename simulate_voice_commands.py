import pyttsx3
import os
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
from test_framework import VoiceAssistantTester

class VoiceCommandSimulator:
    """Class to simulate voice commands using text-to-speech"""
    
    def __init__(self, rate=150, voice_id=None):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', rate)  # Speed of speech
        
        # Set voice if specified
        if voice_id:
            self.engine.setProperty('voice', voice_id)
        
        # Create output directory
        os.makedirs("simulated_commands", exist_ok=True)
    
    def list_available_voices(self):
        """List all available voices"""
        voices = self.engine.getProperty('voices')
        for i, voice in enumerate(voices):
            print(f"Voice #{i}: {voice.name} ({voice.id})")
        return voices
    
    def set_voice(self, voice_id):
        """Set the voice to use"""
        self.engine.setProperty('voice', voice_id)
    
    def text_to_speech(self, text, output_file=None):
        """Convert text to speech and optionally save to file"""
        if output_file:
            # Save speech to file
            self.engine.save_to_file(text, output_file)
            self.engine.runAndWait()
            return output_file
        else:
            # Just speak it
            self.engine.say(text)
            self.engine.runAndWait()
            return None
    
    def simulate_commands(self, commands):
        """Simulate a list of voice commands"""
        results = []
        
        for i, command in enumerate(commands):
            print(f"Simulating command {i+1}/{len(commands)}: {command}")
            
            # Create filename
            filename = f"simulated_commands/command_{i+1:03d}_{command.replace(' ', '_')}.wav"
            
            # Generate speech
            self.text_to_speech(command, filename)
            
            results.append({
                'command': command,
                'audio_file': filename
            })
            
            # Wait a bit between commands
            time.sleep(0.5)
        
        return results

def main():
    # Initialize simulator
    simulator = VoiceCommandSimulator()
    
    # Print available voices
    print("Available voices:")
    voices = simulator.list_available_voices()
    
    # Optionally set a different voice
    # simulator.set_voice(voices[1].id)
    
    # Define commands to simulate (from our test cases)
    from run_tests import TEST_CASES
    commands = [tc['command'] for tc in TEST_CASES]
    
    # Simulate commands
    results = simulator.simulate_commands(commands)
    
    print(f"\nSimulated {len(results)} commands. Audio files saved to simulated_commands/")

if __name__ == "__main__":
    main()
