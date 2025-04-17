import requests
import time
import json
import csv
import os
import threading
import socketio
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

class VoiceAssistantTester:
    """Framework for testing voice assistant accuracy and latency"""
    
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url
        self.socket = socketio.Client()
        self.results = []
        self.current_test_start_time = None
        self.current_test_command = None
        self.test_completed = threading.Event()
        
        # Set up socket event handlers
        self.socket.on('connect', self.on_connect)
        self.socket.on('action_update', self.on_action_update)
        self.socket.on('error', self.on_error)
        
    def on_connect(self):
        print("Connected to server")
    
    def on_action_update(self, data):
        latency = time.time() - self.current_test_start_time
        
        # Record the result
        result = {
            'command': self.current_test_command,
            'expected_action': self.current_test_expected['action'],
            'expected_direction': self.current_test_expected['direction'],
            'actual_action': data.get('action'),
            'actual_direction': data.get('direction'),
            'latency': latency,
            'success': (data.get('action') == self.current_test_expected['action'] and
                        data.get('direction') == self.current_test_expected['direction']),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        print(f"Test completed: {result['success']}, Latency: {latency:.3f}s")
        self.test_completed.set()
    
    def on_error(self, data):
        latency = time.time() - self.current_test_start_time
        
        # Record error result
        result = {
            'command': self.current_test_command,
            'expected_action': self.current_test_expected['action'],
            'expected_direction': self.current_test_expected['direction'],
            'actual_action': 'error',
            'actual_direction': None,
            'latency': latency,
            'success': False,
            'error_message': data.get('message', 'Unknown error'),
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        print(f"Test error: {data.get('message', 'Unknown error')}, Latency: {latency:.3f}s")
        self.test_completed.set()
    
    def connect(self):
        """Connect to the socket server"""
        try:
            self.socket.connect(self.base_url)
            return True
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the socket server"""
        if self.socket.connected:
            self.socket.disconnect()
    
    def test_command(self, command, expected_action, expected_direction, timeout=10):
        """Test a single voice command"""
        self.test_completed.clear()
        self.current_test_command = command
        self.current_test_expected = {
            'action': expected_action,
            'direction': expected_direction
        }
        self.current_test_start_time = time.time()
        
        # Emit the command
        self.socket.emit('process_command', {'text': command})
        
        # Wait for response with timeout
        success = self.test_completed.wait(timeout)
        
        if not success:
            # Timeout occurred
            result = {
                'command': command,
                'expected_action': expected_action,
                'expected_direction': expected_direction,
                'actual_action': 'timeout',
                'actual_direction': None,
                'latency': timeout,
                'success': False,
                'error_message': 'Request timed out',
                'timestamp': datetime.now().isoformat()
            }
            self.results.append(result)
            print(f"Test timeout for command: {command}")
        
        return success
    
    def run_test_suite(self, test_cases, parallel=False, max_workers=4):
        """Run a suite of tests"""
        if not self.socket.connected:
            if not self.connect():
                return False
        
        self.results = []
        
        if parallel:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for test_case in test_cases:
                    executor.submit(self.test_command, 
                                   test_case['command'], 
                                   test_case['action'], 
                                   test_case['direction'])
        else:
            for test_case in test_cases:
                self.test_command(
                    test_case['command'],
                    test_case['action'],
                    test_case['direction']
                )
                # Add a small delay between tests
                time.sleep(0.5)
        
        return self.results
    
    def export_results(self, filename='test_results.csv'):
        """Export test results to CSV"""
        if not self.results:
            print("No results to export")
            return
        
        fieldnames = self.results[0].keys()
        
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.results)
        
        print(f"Results exported to {filename}")
    
    def analyze_results(self):
        """Analyze test results"""
        if not self.results:
            return {
                'total_tests': 0,
                'success_rate': 0,
                'average_latency': 0,
                'min_latency': 0,
                'max_latency': 0
            }
        
        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        success_rate = (successful / total) * 100
        
        latencies = [r['latency'] for r in self.results]
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        # Group by command type
        by_action = {}
        for r in self.results:
            action = r['expected_action']
            if action not in by_action:
                by_action[action] = {
                    'total': 0,
                    'success': 0,
                    'latency': []
                }
            
            by_action[action]['total'] += 1
            by_action[action]['success'] += 1 if r['success'] else 0
            by_action[action]['latency'].append(r['latency'])
        
        # Calculate per-action metrics
        action_metrics = {}
        for action, data in by_action.items():
            action_metrics[action] = {
                'success_rate': (data['success'] / data['total']) * 100,
                'avg_latency': sum(data['latency']) / len(data['latency'])
            }
        
        analysis = {
            'total_tests': total,
            'successful_tests': successful,
            'success_rate': success_rate,
            'average_latency': avg_latency,
            'min_latency': min_latency,
            'max_latency': max_latency,
            'action_metrics': action_metrics
        }
        
        return analysis
    
    def print_analysis(self):
        """Print analysis to console"""
        analysis = self.analyze_results()
        
        print("\n===== TEST RESULTS ANALYSIS =====")
        print(f"Total Tests: {analysis['total_tests']}")
        print(f"Success Rate: {analysis['success_rate']:.2f}%")
        print(f"Average Latency: {analysis['average_latency']:.3f}s")
        print(f"Min Latency: {analysis['min_latency']:.3f}s")
        print(f"Max Latency: {analysis['max_latency']:.3f}s")
        
        print("\n=== Results by Action Type ===")
        for action, metrics in analysis['action_metrics'].items():
            print(f"Action: {action}")
            print(f"  Success Rate: {metrics['success_rate']:.2f}%")
            print(f"  Avg Latency: {metrics['avg_latency']:.3f}s")

        return analysis
