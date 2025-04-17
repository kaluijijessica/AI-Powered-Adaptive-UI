import pyaudio
import wave
import time
import os
import json
from test_framework import VoiceAssistantTester

class AudioTester:
    """Class for end-to-end audio testing of voice assistant"""
    
    def __init__(self, audio_directory="simulated_commands"):
        self.audio_directory = audio_directory
        self.tester = VoiceAssistantTester()
        
    def play_audio_file(self, filename):
        """Play an audio file through the system speakers"""
        # Open the audio file
        wf = wave.open(filename, 'rb')
        
        # Create PyAudio object
        p = pyaudio.PyAudio()
        
        # Open stream
        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)
        
        # Read data
        data = wf.readframes(1024)
        
        # Play
        while len(data) > 0:
            stream.write(data)
            data = wf.readframes(1024)
        
        # Stop stream
        stream.stop_stream()
        stream.close()
        
        # Close PyAudio
        p.terminate()
    
    def run_audio_tests(self, expected_responses, wait_time=5):
        """Run audio tests by playing files and waiting for responses"""
        if not self.tester.connect():
            print("Failed to connect to server!")
            return []
        
        results = []
        
        try:
            # Find all audio files
            audio_files = [f for f in os.listdir(self.audio_directory) if f.endswith('.wav')]
            audio_files.sort()  # Sort to maintain order
            
            for audio_file in audio_files:
                print(f"Testing audio file: {audio_file}")
                
                # Extract command name from filename
                # Format is: command_001_command_text.wav
                parts = audio_file.split('_', 2)[2].rsplit('.', 1)[0]
                command = parts.replace('_', ' ')
                
                # Look up expected response
                expected = next((er for er in expected_responses if er['command'] == command), None)
                
                if not expected:
                    print(f"No expected response found for command: {command}")
                    continue
                
                # Set up test
                self.tester.test_completed.clear()
                self.tester.current_test_command = command
                self.tester.current_test_expected = {
                    'action': expected['action'],
                    'direction': expected['direction']
                }
                self.tester.current_test_start_time = time.time()
                
                # Play the audio file
                full_path = os.path.join(self.audio_directory, audio_file)
                self.play_audio_file(full_path)
                
                # Wait for response with timeout
                success = self.tester.test_completed.wait(wait_time)
                
                if not success:
                    # Timeout occurred
                    result = {
                        'command': command,
                        'expected_action': expected['action'],
                        'expected_direction': expected['direction'],
                        'actual_action': 'timeout',
                        'actual_direction': None,
                        'latency': wait_time,
                        'success': False,
                        'error_message': 'Request timed out',
                        'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                    self.tester.results.append(result)
                    print(f"Test timeout for command: {command}")
                
                # Wait between tests
                time.sleep(2)
            
            results = self.tester.results
        
        finally:
            self.tester.disconnect()
        
        return results

def main():
    # Create audio tester
    tester = AudioTester()
    
    # Load expected responses from test cases
    from run_tests import TEST_CASES
    
    # Run audio tests
    results = tester.run_audio_tests(TEST_CASES)
    
    # Save results
    with open('audio_test_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Analyze results
    success_count = sum(1 for r in results if r.get('success', False))
    total_count = len(results)
    success_rate = (success_count / total_count) * 100 if total_count > 0 else 0
    
    avg_latency = sum(r.get('latency', 0) for r in results) / len(results) if results else 0
    
    print("\n===== AUDIO TEST RESULTS =====")
    print(f"Total Tests: {total_count}")
    print(f"Successful Tests: {success_count}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Average Latency: {avg_latency:.3f}s")

if __name__ == "__main__":
    main()
