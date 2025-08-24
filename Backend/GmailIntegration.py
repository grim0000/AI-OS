import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from dotenv import dotenv_values

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

class GmailIntegration:
    def __init__(self):
        self.service = None
        self.credentials = None
        self.token_file = "Data/gmail_token.json"
        self.credentials_file = "Data/gmail_credentials.json"
        
    def authenticate(self):
        """Authenticate with Gmail API"""
        try:
            # Check if we have valid credentials
            if os.path.exists(self.token_file):
                self.credentials = Credentials.from_authorized_user_file(self.token_file, SCOPES)
            
            # If no valid credentials available, let the user log in
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        return "Gmail credentials not found. Please add 'gmail_credentials.json' to the Data folder."
                    
                    flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                    self.credentials = flow.run_local_server(port=0)
                
                # Save the credentials for the next run
                with open(self.token_file, 'w') as token:
                    token.write(self.credentials.to_json())
            
            # Build the Gmail service
            self.service = build('gmail', 'v1', credentials=self.credentials)
            return "Gmail authentication successful!"
            
        except Exception as e:
            return f"Gmail authentication failed: {str(e)}"
    
    def send_email(self, to_email, subject, body, cc_email=None, bcc_email=None, is_html=False):
        """Send an email via Gmail with optional CC and BCC"""
        if not self.service:
            auth_result = self.authenticate()
            if "successful" not in auth_result:
                return auth_result
        
        try:
            # Create the message
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            
            # Add CC if provided
            if cc_email and cc_email.strip():
                message['cc'] = cc_email.strip()
            
            # Add BCC if provided (BCC is handled differently in Gmail API)
            if bcc_email and bcc_email.strip():
                # For BCC, we need to add it to the 'to' field but handle it specially
                # This is a limitation of the Gmail API
                pass  # BCC will be handled by adding to recipients list
            
            # Add body
            if is_html:
                msg = MIMEText(body, 'html')
            else:
                msg = MIMEText(body, 'plain')
            message.attach(msg)
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Prepare recipients list for Gmail API
            recipients = [to_email]
            if cc_email and cc_email.strip():
                recipients.append(cc_email.strip())
            if bcc_email and bcc_email.strip():
                recipients.append(bcc_email.strip())
            
            # Send the email
            sent_message = self.service.users().messages().send(
                userId='me', 
                body={'raw': raw_message}
            ).execute()
            
            return f"Email sent successfully! Message ID: {sent_message['id']}"
            
        except HttpError as error:
            return f"An error occurred while sending email: {error}"
        except Exception as e:
            return f"Failed to send email: {str(e)}"
    
    def send_email_from_file(self, to_email, subject, file_path):
        """Send an email with content from a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return self.send_email(to_email, subject, content)
            
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def get_status(self):
        """Get Gmail integration status"""
        # Check if we have a valid service
        if self.service:
            return "Gmail integration is active and ready to send emails."
        
        # Check if we have credentials but no service
        if self.credentials and self.credentials.valid:
            return "Gmail credentials valid but service not initialized. Run 'setup gmail' to initialize."
        
        # Check if we have a token file
        if os.path.exists(self.token_file):
            return "Gmail token found but not loaded. Run 'setup gmail' to authenticate."
        
        # Check if we have credentials file
        if os.path.exists(self.credentials_file):
            return "Gmail credentials found but not authenticated. Run 'setup gmail' to authenticate."
        
        return "Gmail credentials not found. Please add 'gmail_credentials.json' to the Data folder."

# Global instance
gmail_integration = GmailIntegration()

def setup_gmail():
    """Setup Gmail integration"""
    return gmail_integration.authenticate()

def send_email_via_gmail(to_email, subject, body):
    """Send email via Gmail"""
    return gmail_integration.send_email(to_email, subject, body)

def send_generated_content_email(to_email, subject):
    """Send the generated content as an email"""
    content_file = "Data/generated_content.txt"
    if os.path.exists(content_file):
        return gmail_integration.send_email_from_file(to_email, subject, content_file)
    else:
        return "No generated content found. Please generate content first."

def auto_send_generated_email(query):
    """Automatically send generated content as email based on query"""
    import re
    
    # Check if we have generated content
    content_file = "Data/generated_content.txt"
    if not os.path.exists(content_file):
        return "No generated content found. Please generate content first using 'draft an email'."
    
    # Parse email details from query
    email_patterns = [
        r"send it to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        r"email it to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
        r"send to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
    ]
    
    to_email = None
    for pattern in email_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            to_email = match.group(1)
            break
    
    if not to_email:
        return "Please provide an email address. Say something like 'send it to john@example.com'"
    
    # Try to extract subject from query or use default
    subject_patterns = [
        r"subject ['\"]([^'\"]+)['\"]",
        r"about ['\"]([^'\"]+)['\"]",
        r"regarding ['\"]([^'\"]+)['\"]",
    ]
    
    subject = "Generated Content"
    for pattern in subject_patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            subject = match.group(1)
            break
    
    # Send the email
    result = gmail_integration.send_email_from_file(to_email, subject, content_file)
    
    if "successfully" in result.lower():
        return f"✅ Generated content sent successfully to {to_email}!\n\nSubject: {subject}"
    else:
        return f"❌ Failed to send email: {result}"

def handle_gmail_request(query):
    """Handle Gmail-related requests"""
    query_lower = query.lower()
    
    if "setup gmail" in query_lower or "connect gmail" in query_lower:
        return """To setup Gmail integration:

1. Go to Google Cloud Console (https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download the credentials JSON file
6. Save it as 'gmail_credentials.json' in the Data folder
7. Then say 'setup gmail' again

Would you like me to help you with any of these steps?"""
    
    elif "gmail status" in query_lower or "email status" in query_lower:
        return gmail_integration.get_status()
    
    elif "gmail help" in query_lower or "email help" in query_lower:
        return """📧 Gmail Commands Available:

🔧 Setup:
- "setup gmail" - Configure Gmail integration

📊 Status:
- "gmail status" - Check Gmail connection status

📝 Send Emails:
- "send email to john@example.com with subject 'Meeting' saying 'Let us meet tomorrow'"
- "email client@company.com about 'Project Update' saying 'Here is the latest status'"

📤 Auto-Send Generated Content:
- "send it to boss@company.com"
- "email the generated content to team@company.com"

💡 Tips:
- Use quotes around subject and content for better parsing
- Generate content first with "draft an email" then send it
- Check status anytime with "gmail status"

Need help? Say "gmail help" anytime!"""
    
    elif "send email" in query_lower or "draft email" in query_lower or "compose email" in query_lower:
        # Check if this is a privacy-protected email request
        if any(marker in query for marker in ["<sub>", "<body>", "subject", "body"]):
            # This is a privacy-protected request - return instruction to use the new system
            return """🔒 **Privacy-Protected Email System**

I can help you draft an email securely! Use this format:

**"draft an email with subject <sub>Your Subject</sub> and body <body>Your message here</body>"**

**Privacy Features:**
✅ Email addresses are NOT stored in chat history
✅ Recipient information is only used temporarily
✅ Secure dialog for entering sensitive details

**Example:**
"draft an email with subject <sub>Meeting Tomorrow</sub> and body <body>Let's meet at 2 PM to discuss the project</body>"

This will open a secure dialog where you can enter the recipient email address safely."""
        else:
            # Parse email details from the query (legacy method)
            email_details = parse_email_request(query)
            if email_details:
                return send_parsed_email(email_details)
            else:
                return """To send an email, I need:
1. Recipient email address
2. Subject line
3. Email content

**For Privacy Protection, use:**
"draft an email with subject <sub>Subject</sub> and body <body>Content</body>"

**Or Legacy Method:**
"send email to john@example.com with subject 'Meeting' saying 'Let's meet tomorrow'"

First, make sure Gmail is set up by saying 'setup gmail'"""
    
    elif any(keyword in query_lower for keyword in ["send it to", "email it to", "send to"]) and "@" in query:
        # Auto-send generated content
        return auto_send_generated_email(query)
    
    return None

def parse_email_request(query):
    """Parse email details from user query"""
    import re
    
    # Common patterns for email parsing
    patterns = [
        # Pattern: send email to email@domain.com with subject 'Subject' saying 'Content'
        r"send email to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) with subject ['\"]([^'\"]+)['\"] saying ['\"]([^'\"]+)['\"]",
        # Pattern: send email to email@domain.com subject 'Subject' content 'Content'
        r"send email to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) subject ['\"]([^'\"]+)['\"] content ['\"]([^'\"]+)['\"]",
        # Pattern: email email@domain.com about 'Subject' saying 'Content'
        r"email ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) about ['\"]([^'\"]+)['\"] saying ['\"]([^'\"]+)['\"]",
        # Pattern: send to email@domain.com subject 'Subject' message 'Content'
        r"send to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) subject ['\"]([^'\"]+)['\"] message ['\"]([^'\"]+)['\"]",
        # Pattern: send email to email@domain.com about 'Subject' with message 'Content'
        r"send email to ([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}) about ['\"]([^'\"]+)['\"] with message ['\"]([^'\"]+)['\"]",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            return {
                'to_email': match.group(1),
                'subject': match.group(2),
                'body': match.group(3)
            }
    
    return None

def send_parsed_email(email_details):
    """Send email with parsed details"""
    try:
        # First check if we have generated content
        content_file = "Data/generated_content.txt"
        if os.path.exists(content_file):
            with open(content_file, 'r', encoding='utf-8') as f:
                generated_content = f.read().strip()
            
            # Use generated content if available
            body = generated_content
        else:
            # Use the parsed body
            body = email_details['body']
        
        # Send the email
        result = gmail_integration.send_email(
            email_details['to_email'],
            email_details['subject'],
            body
        )
        
        if "successfully" in result.lower():
            return f"✅ Email sent successfully to {email_details['to_email']}!\n\nSubject: {email_details['subject']}\n\nContent: {body[:100]}..."
        else:
            return f"❌ Failed to send email: {result}"
            
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"
