#!/usr/bin/env python3
"""
Test Email Parsing
Tests different email formats to see which ones work
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_email_parsing():
    """Test different email parsing formats"""
    
    print("📧 TESTING EMAIL PARSING")
    print("=" * 50)
    
    try:
        from Backend.GmailIntegration import parse_email_request
        
        # Test different email formats
        test_formats = [
            "send email to banubb2005@gmail.com with subject 'meeting' saying 'lets meet up'",
            "send email to banubb2005@gmail.com with subject \"meeting\" saying \"lets meet up\"",
            "send email to banubb2005@gmail.com subject 'meeting' content 'lets meet up'",
            "email banubb2005@gmail.com about 'meeting' saying 'lets meet up'",
            "send to banubb2005@gmail.com subject 'meeting' message 'lets meet up'",
            "send email to banubb2005@gmail.com about 'meeting' with message 'lets meet up'"
        ]
        
        for i, format_test in enumerate(test_formats, 1):
            print(f"\n{i}️⃣ Testing: {format_test}")
            result = parse_email_request(format_test)
            if result:
                print(f"     ✅ SUCCESS!")
                print(f"        To: {result['to_email']}")
                print(f"        Subject: {result['subject']}")
                print(f"        Body: {result['body']}")
            else:
                print(f"     ❌ FAILED - Not recognized")
        
        print("\n🎯 RECOMMENDED FORMAT:")
        print("Use single quotes: send email to email@domain.com with subject 'Subject' saying 'Content'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_email_parsing()
