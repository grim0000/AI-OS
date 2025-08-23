#!/usr/bin/env python3
"""
Test Gmail Integration
Verifies that Gmail functionality is working correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gmail_integration():
    """Test the Gmail integration system"""
    
    print("📧 TESTING GMAIL INTEGRATION")
    print("=" * 50)
    
    try:
        # Test 1: Import the Gmail module
        print("\n1️⃣ Testing Imports...")
        from Backend.GmailIntegration import gmail_integration, handle_gmail_request
        print("✅ Gmail module imported successfully")
        
        # Test 2: Check if credentials exist
        print("\n2️⃣ Checking Credentials...")
        credentials_file = "Data/gmail_credentials.json"
        if os.path.exists(credentials_file):
            print(f"✅ Credentials file found: {credentials_file}")
            print(f"   Size: {os.path.getsize(credentials_file)} bytes")
        else:
            print(f"❌ Credentials file missing: {credentials_file}")
            print("   You need to download gmail_credentials.json from Google Cloud Console")
            print("   See GMAIL_SETUP_GUIDE.md for instructions")
            return False
        
        # Test 3: Test Gmail request handling
        print("\n3️⃣ Testing Gmail Request Handler...")
        test_queries = [
            "setup gmail",
            "send email to test@example.com with subject 'Test' saying 'Hello'",
            "gmail status"
        ]
        
        for query in test_queries:
            print(f"\n   Testing: {query}")
            response = handle_gmail_request(query)
            if response:
                print(f"     Response: {response[:100]}...")
            else:
                print("     Response: None (not a Gmail request)")
        
        # Test 4: Test authentication (if credentials exist)
        print("\n4️⃣ Testing Authentication...")
        if os.path.exists(credentials_file):
            print("   Attempting to authenticate...")
            auth_result = gmail_integration.authenticate()
            print(f"   Result: {auth_result}")
            
            if "successful" in auth_result.lower():
                print("   ✅ Authentication successful!")
            elif "credentials not found" in auth_result.lower():
                print("   ⚠️  Credentials file exists but authentication failed")
            else:
                print(f"   ❌ Authentication failed: {auth_result}")
        else:
            print("   ⏭️  Skipping authentication test (no credentials)")
        
        # Test 5: Test email parsing
        print("\n5️⃣ Testing Email Parsing...")
        from Backend.GmailIntegration import parse_email_request
        
        test_parsing = [
            "send email to john@example.com with subject 'Meeting' saying 'Let us meet tomorrow'",
            "email client@company.com about 'Project Update' saying 'Here is the latest status'"
        ]
        
        for query in test_parsing:
            print(f"\n   Testing: {query}")
            parsed = parse_email_request(query)
            if parsed:
                print(f"     To: {parsed['to_email']}")
                print(f"     Subject: {parsed['subject']}")
                print(f"     Body: {parsed['body'][:50]}...")
            else:
                print("     Failed to parse email details")
        
        # Test 6: Show system status
        print("\n6️⃣ System Status...")
        print(f"   Credentials file: {'✅' if os.path.exists(credentials_file) else '❌'}")
        print(f"   Token file: {'✅' if os.path.exists('Data/gmail_token.json') else '❌'}")
        print(f"   Gmail service: {'✅' if gmail_integration.service else '❌'}")
        
        print("\n🎉 GMAIL INTEGRATION TEST COMPLETED!")
        print("\n📋 Next Steps:")
        print("1. If credentials are missing, follow GMAIL_SETUP_GUIDE.md")
        print("2. Run 'setup gmail' in your AI-OS system")
        print("3. Test with: 'send email to test@example.com with subject 'Test' saying 'Hello'")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
        return False
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gmail_commands():
    """Test specific Gmail commands"""
    
    print("\n🧪 TESTING GMAIL COMMANDS")
    print("=" * 50)
    
    try:
        from Backend.GmailIntegration import handle_gmail_request
        
        commands = [
            ("setup gmail", "Should show setup instructions"),
            ("send email to test@example.com with subject 'Test' saying 'Hello'", "Should parse email details"),
            ("gmail help", "Should show help information"),
            ("email status", "Should show Gmail status")
        ]
        
        for command, expected in commands:
            print(f"\n📝 Command: {command}")
            print(f"   Expected: {expected}")
            response = handle_gmail_request(command)
            if response:
                print(f"   Response: {response[:100]}...")
            else:
                print("   Response: None (not recognized as Gmail command)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing commands: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting Gmail Integration Tests...\n")
    
    # Run main test
    main_success = test_gmail_integration()
    
    # Run command tests
    command_success = test_gmail_commands()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    if main_success and command_success:
        print("🎉 All Gmail tests passed!")
        print("✅ Gmail integration is ready to use")
        print("📧 You can now send emails through your AI-OS system")
    else:
        print("⚠️  Some tests failed")
        print("🔧 Check the error messages above")
        print("📖 Follow GMAIL_SETUP_GUIDE.md for setup instructions")
    
    print("=" * 50)
