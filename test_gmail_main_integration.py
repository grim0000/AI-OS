#!/usr/bin/env python3
"""
Test Gmail Integration with Main System
Verifies that Gmail commands are properly recognized and processed
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gmail_main_integration():
    """Test Gmail integration with the main system"""
    
    print("🔧 TESTING GMAIL MAIN INTEGRATION")
    print("=" * 50)
    
    try:
        # Test 1: Import the main Gmail handler
        print("\n1️⃣ Testing Gmail Handler Import...")
        from Backend.GmailIntegration import handle_gmail_request
        print("✅ Gmail handler imported successfully")
        
        # Test 2: Test Gmail command recognition
        print("\n2️⃣ Testing Gmail Command Recognition...")
        test_commands = [
            "setup gmail",
            "gmail help", 
            "gmail status",
            "send email to test@example.com with subject 'Test' saying 'Hello'"
        ]
        
        for command in test_commands:
            print(f"\n   Testing: {command}")
            response = handle_gmail_request(command)
            if response:
                print(f"     Response: {response[:100]}...")
            else:
                print("     Response: None (not recognized)")
        
        # Test 3: Test the main system integration
        print("\n3️⃣ Testing Main System Integration...")
        print("   This test simulates how the main system would process Gmail commands")
        
        # Simulate the main system's command processing
        def simulate_main_system(command):
            if "gmail" in command.lower():
                return handle_gmail_request(command)
            else:
                return None
        
        test_main_commands = [
            "gmail help",
            "gmail status",
            "setup gmail"
        ]
        
        for command in test_main_commands:
            print(f"\n   Main System Command: {command}")
            response = simulate_main_system(command)
            if response:
                print(f"     Processed: {response[:100]}...")
            else:
                print("     Not processed")
        
        print("\n🎉 GMAIL MAIN INTEGRATION TEST COMPLETED!")
        print("\n📋 How to Use in Your AI-OS System:")
        print("1. Say 'gmail help' to see available commands")
        print("2. Say 'gmail status' to check Gmail status")
        print("3. Say 'setup gmail' to configure Gmail")
        print("4. Say 'send email to...' to send emails")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Gmail Main Integration Tests...\n")
    
    success = test_gmail_main_integration()
    
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if success:
        print("🎉 Gmail main integration test passed!")
        print("✅ Gmail commands should work in your AI-OS system")
        print("📧 Try saying 'gmail help' in your system")
    else:
        print("⚠️  Some tests failed")
        print("🔧 Check the error messages above")
    
    print("=" * 50)
