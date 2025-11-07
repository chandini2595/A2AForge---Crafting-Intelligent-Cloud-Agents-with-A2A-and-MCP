#!/usr/bin/env python3
"""
AWS Multi-Agent Chat Interface
Simple CLI for interacting with EC2 and S3 agents
"""

import json
from agents.coordinator import CoordinatorAgent

def print_response(response: dict):
    """Pretty print the agent response"""
    if 'error' in response:
        print(f"\n❌ Error: {response['error']}\n")
    elif 'success' in response and response['success']:
        print(f"\n✅ Success!")
        for key, value in response.items():
            if key != 'success':
                if isinstance(value, (list, dict)):
                    print(f"{key}:")
                    print(json.dumps(value, indent=2))
                else:
                    print(f"{key}: {value}")
        print()
    else:
        print(f"\n💬 {response.get('message', json.dumps(response, indent=2))}\n")

def main():
    print("=" * 60)
    print("AWS Multi-Agent System")
    print("=" * 60)
    print("\nType your commands or 'help' for examples")
    print("Type 'quit' or 'exit' to stop\n")
    
    coordinator = CoordinatorAgent()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!\n")
                break
            
            if user_input.lower() == 'help':
                print("\n📚 Example Commands:")
                print("  - create ec2 instance")
                print("  - create ec2 instance t2.small")
                print("  - list instances")
                print("  - stop instance i-1234567890abcdef0")
                print("  - terminate instance i-1234567890abcdef0")
                print("  - create s3 bucket my-unique-bucket-name")
                print("  - create s3 bucket my-bucket in us-west-2")
                print("  - list buckets")
                print("  - list objects in my-bucket")
                print("  - delete bucket my-bucket")
                print()
                continue
            
            print("\n🤖 Processing...")
            response = coordinator.process_request(user_input)
            print_response(response)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}\n")

if __name__ == "__main__":
    main()
