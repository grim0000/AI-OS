#!/usr/bin/env python3
"""
Debug Email System
Debug the email system step by step to identify the exact issue
"""

import sys
import traceback

def debug_email_system():
    """Debug the email system step by step"""
    
    print("🔍 DEBUGGING EMAIL SYSTEM STEP BY STEP")
    print("=" * 60)
    
    # Step 1: Test imports
    print("\n1️⃣ Testing Imports...")
    try:
        from Backend.PrivacyProtectedEmail import PrivacyProtectedEmailSystem
        print("✅ PrivacyProtectedEmail imported successfully")
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 2: Test system initialization
    print("\n2️⃣ Testing System Initialization...")
    try:
        email_system = PrivacyProtectedEmailSystem()
        print("✅ Email system initialized successfully")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 3: Test email drafting
    print("\n3️⃣ Testing Email Drafting...")
    try:
        test_input = "draft an email with subject <sub>Debug Test</sub> and body <body>This is a debug test</body>"
        response = email_system.handle_email_request(test_input)
        print("✅ Email drafting successful")
        print(f"   Response: {response[:100]}...")
        
        # Check stored content
        print(f"   Stored subject: '{email_system.last_email_subject}'")
        print(f"   Stored body: '{email_system.last_email_body}'")
        
    except Exception as e:
        print(f"❌ Email drafting failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 4: Test dialog preparation
    print("\n4️⃣ Testing Dialog Preparation...")
    try:
        response = email_system.open_email_dialog()
        print("✅ Dialog preparation successful")
        print(f"   Response type: {type(response)}")
        print(f"   Response: {response}")
        
        if isinstance(response, dict):
            print("   ✅ Response is dictionary format")
            print(f"   Action: {response.get('action')}")
            print(f"   Subject: {response.get('subject')}")
            print(f"   Body: {response.get('body')}")
        else:
            print("   ❌ Response is not dictionary format")
            
    except Exception as e:
        print(f"❌ Dialog preparation failed: {e}")
        traceback.print_exc()
        return False
    
    # Step 5: Test Main.py integration logic
    print("\n5️⃣ Testing Main.py Integration Logic...")
    try:
        # Simulate what Main.py does
        response = email_system.open_email_dialog()
        
        if isinstance(response, dict) and response.get("action") == "open_email_dialog":
            print("✅ Response format correct for Main.py")
            
            # Try to import the dialog class
            try:
                from Backend.PrivacyProtectedEmail import PrivacyProtectedEmailDialog
                print("✅ PrivacyProtectedEmailDialog imported successfully")
                
                # Check if we can create the dialog (without showing it)
                subject = response["subject"]
                body = response["body"]
                print(f"   Would create dialog with subject: '{subject}'")
                print(f"   Would create dialog with body: '{body}'")
                
            except Exception as e:
                print(f"❌ Dialog class import failed: {e}")
                traceback.print_exc()
                
        else:
            print("❌ Response format incorrect for Main.py")
            print(f"   Expected dict with action='open_email_dialog', got: {response}")
            
    except Exception as e:
        print(f"❌ Main.py integration test failed: {e}")
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("🎯 DEBUG COMPLETE")
    
    print("\n📋 **Summary of Issues Found:**")
    print("• Check the output above for any ❌ errors")
    print("• If all steps pass, the issue is in the GUI integration")
    print("• If any step fails, that's where the problem is")
    
    return True

if __name__ == "__main__":
    debug_email_system()
