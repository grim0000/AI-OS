#!/usr/bin/env python3
"""
Test Sending Email to sunillal360@gmail.com
Tests sending an email with the urgent meeting subject
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_send_email():
    """Test sending an email"""
    
    print("📧 TESTING EMAIL SENDING")
    print("=" * 50)
    
    try:
        from Backend.GmailIntegration import handle_gmail_request
        
        # Test the exact command you want to use
        test_command = "send email to sunillal360@gmail.com with subject 'urgent meeting' saying 'lets meet up test this now'"
        
        print(f"Testing command: {test_command}")
        print("\nSending email...")
        
        response = handle_gmail_request(test_command)
        print(f"\nResponse: {response}")
        
        if "successfully" in response.lower():
            print("\n🎉 EMAIL SENT SUCCESSFULLY!")
        else:
            print("\n❌ Email sending failed")
            print("Check the response above for details")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_send_email()
