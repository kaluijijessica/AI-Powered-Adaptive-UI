from test_framework import VoiceAssistantTester
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime

# Define your test cases
TEST_CASES = [
    # Contrast tests
    {'command': 'dark mode', 'action': 'adjust_contrast', 'direction': 'dark'},
    {'command': 'make it darker', 'action': 'adjust_contrast', 'direction': 'dark'},
    {'command': 'too bright', 'action': 'adjust_contrast', 'direction': 'dark'},
    {'command': 'night mode', 'action': 'adjust_contrast', 'direction': 'dark'},
    {'command': 'light mode', 'action': 'adjust_contrast', 'direction': 'light'},
    {'command': 'make it brighter', 'action': 'adjust_contrast', 'direction': 'light'},
    {'command': 'too dark', 'action': 'adjust_contrast', 'direction': 'light'},
    {'command': 'day mode', 'action': 'adjust_contrast', 'direction': 'light'},
    
    # Text size tests
    {'command': 'bigger text', 'action': 'adjust_text', 'direction': 'increase'},
    {'command': 'increase text size', 'action': 'adjust_text', 'direction': 'increase'},
    {'command': 'make text bigger', 'action': 'adjust_text', 'direction': 'increase'},
    {'command': 'text is too small', 'action': 'adjust_text', 'direction': 'increase'},
    {'command': 'smaller text', 'action': 'adjust_text', 'direction': 'decrease'},
    {'command': 'decrease text size', 'action': 'adjust_text', 'direction': 'decrease'},
    {'command': 'make text smaller', 'action': 'adjust_text', 'direction': 'decrease'},
    {'command': 'text is too big', 'action': 'adjust_text', 'direction': 'decrease'},
    
    # Identity tests
    {'command': 'who am i', 'action': 'show_identity', 'direction': None},
    {'command': 'what is my name', 'action': 'show_identity', 'direction': None},
    {'command': 'show my identity', 'action': 'show_identity', 'direction': None},
    {'command': 'where do i live', 'action': 'show_identity', 'direction': None},
    
    # Edge cases
    {'command': 'switch to dark', 'action': 'adjust_contrast', 'direction': 'dark'},
    {'command': 'i can barely read this', 'action': 'adjust_text', 'direction': 'increase'},
    {'command': 'the screen is too bright for me', 'action': 'adjust_contrast', 'direction': 'dark'},
    {'command': 'my emergency contact', 'action': 'show_identity', 'direction': None}
]

# Add some negative test cases (commands that should be rejected)
NEGATIVE_TEST_CASES = [
    {'command': 'what time is it', 'action': 'error', 'direction': None},
    {'command': 'call my daughter', 'action': 'error', 'direction': None},
    {'command': 'play some music', 'action': 'error', 'direction': None}
]

def create_test_directory():
    """Create a directory for test results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dirname = f"test_results_{timestamp}"
    os.makedirs(dirname, exist_ok=True)
    return dirname

def create_visualizations(results, output_dir):
    """Create visualization charts from test results"""
    # Convert results to DataFrame
    df = pd.DataFrame(results)
    
    # Success rate by command type
    plt.figure(figsize=(12, 6))
    success_rates = df.groupby('expected_action')['success'].mean() * 100
    success_rates.plot(kind='bar', color='skyblue')
    plt.title('Success Rate by Command Type')
    plt.xlabel('Command Type')
    plt.ylabel('Success Rate (%)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/success_rate_by_command.png")
    
    # Latency by command type
    plt.figure(figsize=(12, 6))
    latency_by_command = df.groupby('expected_action')['latency'].mean()
    latency_by_command.plot(kind='bar', color='lightgreen')
    plt.title('Average Latency by Command Type')
    plt.xlabel('Command Type')
    plt.ylabel('Latency (seconds)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/latency_by_command.png")
    
    # Success vs. Failure distribution
    plt.figure(figsize=(8, 8))
    success_counts = df['success'].value_counts()
    plt.pie(success_counts, labels=['Success', 'Failure'] if True in success_counts.index else ['Failure', 'Success'],
            autopct='%1.1f%%', colors=['#5cb85c', '#d9534f'] if True in success_counts.index else ['#d9534f', '#5cb85c'])
    plt.title('Success vs. Failure Distribution')
    plt.savefig(f"{output_dir}/success_failure_pie.png")
    
    # Latency distribution
    plt.figure(figsize=(12, 6))
    plt.hist(df['latency'], bins=20, color='lightblue', edgecolor='black')
    plt.title('Latency Distribution')
    plt.xlabel('Latency (seconds)')
    plt.ylabel('Frequency')
    plt.axvline(df['latency'].mean(), color='red', linestyle='dashed', linewidth=1)
    plt.text(df['latency'].mean() + 0.05, plt.ylim()[1] * 0.9, f'Mean: {df["latency"].mean():.3f}s')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/latency_distribution.png")
    
    return {
        'success_rate_by_command': success_rates.to_dict(),
        'latency_by_command': latency_by_command.to_dict(),
        'overall_success_rate': df['success'].mean() * 100,
        'overall_latency': df['latency'].mean()
    }

def main():
    # Set up test directory
    output_dir = create_test_directory()
    print(f"Test results will be saved to: {output_dir}")
    
    # Initialize tester
    tester = VoiceAssistantTester()
    
    # Connect to server
    if not tester.connect():
        print("Failed to connect to server. Make sure the app is running.")
        return
    
    try:
        # Run positive test cases
        print(f"Running {len(TEST_CASES)} positive test cases...")
        results = tester.run_test_suite(TEST_CASES)
        
        # Run negative test cases
        print(f"Running {len(NEGATIVE_TEST_CASES)} negative test cases...")
        negative_results = tester.run_test_suite(NEGATIVE_TEST_CASES)
        results.extend(negative_results)
        
        # Export raw results
        tester.export_results(f"{output_dir}/test_results.csv")
        
        # Analyze and print results
        analysis = tester.print_analysis()
        
        # Save analysis as JSON
        with open(f"{output_dir}/analysis.json", 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Create and save visualizations
        viz_data = create_visualizations(results, output_dir)
        
        # Save visualization data
        with open(f"{output_dir}/visualization_data.json", 'w') as f:
            json.dump(viz_data, f, indent=2)
        
        print(f"\nAll tests completed. Results saved to {output_dir}/")
        
    finally:
        # Disconnect from server
        tester.disconnect()

if __name__ == "__main__":
    main()
