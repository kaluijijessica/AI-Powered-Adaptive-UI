from json.tool import main
import time
import threading
import socketio
import random
import json
import matplotlib.pyplot as plt
import numpy as np
from concurrent.futures import ThreadPoolExecutor

class LoadTester:
    """Class for load testing the voice assistant"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.results = []
        self.active_clients = 0
        self.max_active_clients = 0
        self.lock = threading.Lock()
        
    def client_session(self, commands, delay=0):
        """Simulate a client session with multiple commands"""
        # Create socket client
        sio = socketio.Client()
        client_results = []
        
        try:
            # Connect to server
            sio.connect(self.base_url)
            
            # Update active client count
            with self.lock:
                self.active_clients += 1
                self.max_active_clients = max(self.max_active_clients, self.active_clients)
            
            # Initial delay to stagger clients
            if delay > 0:
                time.sleep(delay)
            
            # Process each command
            for command in commands:
                result = {
                    'command': command,
                    'timestamp': time.time(),
                    'start_time': time.time(),
                    'end_time': None,
                    'latency': None,
                    'success': False,
                    'error': None
                }
                
                # Event to track completion
                completed = threading.Event()
                
                # Set up response handlers
                @sio.on('action_update')
                def on_action_update(data):
                    end_time = time.time()
                    result['end_time'] = end_time
                    result['latency'] = end_time - result['start_time']
                    result['success'] = True
                    result['response'] = data
                    completed.set()
                
                @sio.on('error')
                def on_error(data):
                    end_time = time.time()
                    result['end_time'] = end_time
                    result['latency'] = end_time - result['start_time']
                    result['success'] = False
                    result['error'] = data.get('message', 'Unknown error')
                    completed.set()
                
                # Send the command
                sio.emit('process_command', {'text': command})
                
                # Wait for response with timeout
                if completed.wait(10):  # 10 second timeout
                    client_results.append(result)
                else:
                    # Timeout
                    result['end_time'] = time.time()
                    result['latency'] = result['end_time'] - result['start_time']
                    result['success'] = False
                    result['error'] = 'Timeout'
                    client_results.append(result)
                
                # Wait between commands
                time.sleep(1)
            
            # Save results
            with self.lock:
                self.results.extend(client_results)
            
        except Exception as e:
            print(f"Client error: {e}")
        finally:
            # Update active client count
            with self.lock:
                self.active_clients -= 1
            
            # Disconnect
            try:
                sio.disconnect()
            except:
                pass
    
    def run_load_test(self, num_clients, commands_per_client, command_pool):
        """Run a load test with multiple clients"""
        # Reset results
        self.results = []
        self.active_clients = 0
        self.max_active_clients = 0
        
        # Prepare client commands
        client_commands = []
        for i in range(num_clients):
            # Choose random commands from the pool
            commands = random.choices(command_pool, k=commands_per_client)
            client_commands.append(commands)
        
        # Start client threads
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=num_clients) as executor:
            for i, commands in enumerate(client_commands):
                # Stagger client starts
                delay = i * 0.5  # 500ms between client starts
                executor.submit(self.client_session, commands, delay)
        
        # Wait for all clients to complete
        total_time = time.time() - start_time
        
        # Analyze results
        return self.analyze_results(total_time, num_clients)
    
    def analyze_results(self, total_time, num_clients):
        """Analyze load test results"""
        if not self.results:
            return {
                'total_commands': 0,
                'success_rate': 0,
                'average_latency': 0,
                'throughput': 0,
                'max_concurrent': 0
            }
        
        total_commands = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        success_rate = (successful / total_commands) * 100
        
        latencies = [r['latency'] for r in self.results if r['latency'] is not None]
        avg_latency = sum(latencies) / len(latencies) if latencies else 0
        
        throughput = total_commands / total_time if total_time > 0 else 0
        
        analysis = {
            'total_commands': total_commands,
            'successful_commands': successful,
            'success_rate': success_rate,
            'average_latency': avg_latency,
            'throughput': throughput,
            'max_concurrent': self.max_active_clients,
            'total_time': total_time,
            'clients': num_clients
        }
        
        return analysis
    
    def visualize_load_test(self, analyses, output_file='load_test_results.png'):
        """Visualize load test results"""
        # Extract data
        clients = [a['clients'] for a in analyses if 'clients' in a]

    def main():
        from run_tests import TEST_CASES
        command_pool = [tc['command'] for tc in TEST_CASES]
    
    # Create load tester
        tester = LoadTester()
    
    # Run tests with different client counts
        results = []
        for clients in [1, 2, 5]:  # Start with smaller numbers first
         print(f"Running load test with {clients} simultaneous clients...")
         analysis = tester.run_load_test(
            num_clients=clients,
            commands_per_client=3,
            command_pool=command_pool
        )
        results.append(analysis)
        
        print(f"Results for {clients} clients:")
        print(f"  Success rate: {analysis['success_rate']:.2f}%")
        print(f"  Average latency: {analysis['average_latency']:.3f}s")
        print(f"  Throughput: {analysis['throughput']:.2f} requests/sec")
        print()
    
    # Save detailed results
        with open('load_test_details.json', 'w') as f:
            json.dump(results, f, indent=2)
    
    print("Load testing completed. Results saved to load_test_details.json")

if __name__ == "__main__":
    main()