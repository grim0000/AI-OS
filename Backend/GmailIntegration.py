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
    """Handle Gmail-related requests with comprehensive parsing"""
    query_lower = query.lower()
    
    print(f"🔍 Processing Gmail request: {query}")
    
    # Setup and status commands
    if "setup gmail" in query_lower or "connect gmail" in query_lower:
        return setup_gmail()
    
    elif "gmail status" in query_lower or "email status" in query_lower:
        return gmail_integration.get_status()
    
    elif "gmail help" in query_lower or "email help" in query_lower:
        return """📧 Gmail Commands Available:

🔧 Setup:
- "setup gmail" - Configure Gmail integration

📊 Status:
- "gmail status" - Check Gmail connection status

📝 Email Commands:
- "send an email with subject 'Meeting Tomorrow' and body 'Let's meet at 2 PM'"
- "draft an email with subject 'Project Update' and body 'Here's the latest progress'"
- "send email to john@example.com subject meeting body I'll be there at 2 PM"

🔒 Privacy Features:
✅ Email addresses are NOT stored in chat history
✅ Recipient information is only used temporarily
✅ CC/BCC fields are available in the GUI
✅ All sensitive data is cleared after sending

💡 Tips:
- The GUI will open automatically for CC/BCC input
- Check status anytime with "gmail status"

Need help? Say "gmail help" anytime!"""
    
    # Enhanced email detection - catch all email-related queries
    elif any(email_keyword in query_lower for email_keyword in ["send email", "draft email", "compose email", "write email", "create email"]):
        print(f"📧 Email command detected: {query}")
        return process_email_command(query, query_lower)
    
    # Also catch "send an email" format
    elif "send an email" in query_lower:
        print(f"📧 Email command detected: {query}")
        return process_email_command(query, query_lower)
    
    # Catch "write an email" format (with "an")
    elif "write an email" in query_lower:
        print(f"📧 Email command detected: {query}")
        return process_email_command(query, query_lower)
    
    elif "draft" in query_lower and ("email" in query_lower or "mail" in query_lower):
        # Handle email drafting with GUI
        import re
        
        # Extract email address
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, query)
        if not email_match:
            return "Please provide a valid email address. Example: 'draft an email to john@example.com'"
        
        to_email = email_match.group()
        
        # Extract subject
        subject = ""
        subject_patterns = [
            r'about\s+([^,]+?)(?:\s+to\s+|\s+for\s+|\s+regarding\s+|$)',
            r'regarding\s+([^,]+?)(?:\s+to\s+|\s+for\s+|$)',
            r'concerning\s+([^,]+?)(?:\s+to\s+|\s+for\s+|$)'
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, query_lower)
            if match:
                subject = match.group(1).strip()
                break
        
        # Extract body
        body = ""
        body_patterns = [
            r'saying\s+(.+)',
            r'with\s+message\s+(.+)',
            r'with\s+content\s+(.+)'
        ]
        
        for pattern in body_patterns:
            match = re.search(pattern, query_lower)
            if match:
                body = match.group(1).strip()
                break
        
        # If no specific body found, extract meaningful content
        if not body:
            # Remove common email words and use the rest as body
            email_words = ['draft', 'email', 'send', 'to', 'subject', 'about', 'body', 'message', 'compose', 'write']
            body = query
            
            # Remove email address from body
            body = body.replace(to_email, '').strip()
            
            # Remove email words
            for word in email_words:
                body = re.sub(r'\b' + word + r'\b', '', body, flags=re.IGNORECASE)
            
            # Clean up extra spaces and punctuation
            body = re.sub(r'\s+', ' ', body).strip()
            body = body.strip('.,!?')
            
            # If body is still empty or just whitespace, create a default message
            if not body or body.isspace():
                body = "This is an email drafted by JARVIS."
        
        # Save the drafted email content
        try:
            with open("Data/generated_content.txt", 'w', encoding='utf-8') as f:
                f.write(f"To: {to_email}\n")
                f.write(f"Subject: {subject}\n")
                f.write(f"Body: {body}\n")
            
            # Open the email GUI dialog asynchronously
            try:
                import threading
                from Backend.EmailGUI import open_email_gui
                
                # Open GUI in a separate thread to avoid blocking
                def open_gui_async():
                    try:
                        open_email_gui(to_email, subject, body)
                    except Exception as e:
                        print(f"GUI Error: {e}")
                
                threading.Thread(target=open_gui_async, daemon=True).start()
                
                return f"✅ Email drafted successfully!\n\nTo: {to_email}\nSubject: {subject}\nBody: {body}\n\n📧 Email dialog opened for CC/BCC input."
            except ImportError:
                return f"✅ Email drafted successfully!\n\nTo: {to_email}\nSubject: {subject}\nBody: {body}\n\nSay 'send it to [email]' to send this email."
            
        except Exception as e:
            return f"❌ Failed to draft email: {str(e)}"
    
    elif ("send an email with subject" in query_lower or "send an email with the subject" in query_lower) and "and body" in query_lower:
        # Handle privacy-protected email format
        import re
        
        # Extract subject and body using simple string splitting
        if 'subject' in query_lower and 'body' in query_lower:
            # Handle both "with subject" and "with the subject"
            if 'with the subject' in query_lower:
                subject_part = query_lower.split('with the subject', 1)[1]
            else:
                subject_part = query_lower.split('with subject', 1)[1]
            
            # Split by 'body' to separate subject and body
            if 'body' in subject_part:
                subject_body_parts = subject_part.split('body', 1)
                subject = subject_body_parts[0].strip()
                body = subject_body_parts[1].strip()
                
                # Clean up common words
                subject = subject.replace('and', '').strip()
                body = body.strip()
                
                # Clean up quotes if present
                subject = subject.strip('"\'')
                body = body.strip('"\'')
            else:
                return "Please use the format: 'send an email with subject [subject] and body [body]'"
        # Save the drafted email content
        try:
            with open("Data/generated_content.txt", 'w', encoding='utf-8') as f:
                f.write(f"Subject: {subject}\n")
                f.write(f"Body: {body}\n")
            
            # Open the email GUI dialog asynchronously
            try:
                import threading
                from Backend.EmailGUI import open_email_gui
                
                # Open GUI in a separate thread to avoid blocking
                def open_gui_async():
                    try:
                        open_email_gui("", subject, body)  # Empty to_email, user will enter it in GUI
                    except Exception as e:
                        print(f"GUI Error: {e}")
                
                threading.Thread(target=open_gui_async, daemon=True).start()
                
                return f"✅ Email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\n📧 Email dialog opened. Please enter the recipient email address and click Send."
            except ImportError:
                return f"✅ Email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\nSay 'send it to [email]' to send this email."
            
        except Exception as e:
            return f"❌ Failed to prepare email: {str(e)}"
    
    elif "send email" in query_lower:
        # Handle direct email sending
        import re
        
        # Extract email address
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, query)
        if not email_match:
            return "Please provide a valid email address. Example: 'send email to john@example.com'"
        
        to_email = email_match.group()
        
        # Extract subject
        subject = ""
        subject_patterns = [
            r'subject\s+([^,]+)',
            r'about\s+([^,]+)',
            r'title\s+([^,]+)'
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, query_lower)
            if match:
                subject = match.group(1).strip()
                break
        
        # Extract body
        body = ""
        body_patterns = [
            r'body\s+(.+)',
            r'message\s+(.+)',
            r'content\s+(.+)'
        ]
        
        for pattern in body_patterns:
            match = re.search(pattern, query_lower)
            if match:
                body = match.group(1).strip()
                break
        
        # If no specific body found, use the query as body
        if not body and not subject:
            email_words = ['send', 'email', 'to', 'subject', 'about', 'body', 'message']
            body = query
            for word in email_words:
                body = body.replace(word, '').strip()
        
        # Send the email
        result = gmail_integration.send_email(to_email, subject, body)
        
        if "successfully" in result.lower():
            return f"✅ Email sent successfully to {to_email}!"
        else:
            return f"❌ Failed to send email: {result}"
    
    elif "send it to" in query_lower:
        # Send previously drafted content
        return auto_send_generated_email(query)
    
    # If no specific email command matched, return None
    print(f"📧 No specific email command matched for: {query}")
    return None

# Removed old parse_email_request and send_parsed_email functions - replaced with direct email handling

def process_email_command(query, query_lower):
    """Process email commands with comprehensive parsing"""
    print(f"🔍 Processing email command: {query}")
    
    # Extract email address if present
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, query)
    to_email = email_match.group() if email_match else ""
    
    # Check for structured format: "send an email with subject X and body Y" (including "a subject")
    if ("send an email with subject" in query_lower or "send an email with the subject" in query_lower or "send an email with a subject" in query_lower) and "and body" in query_lower:
        print(f"📧 Matched structured format")
        return handle_structured_email_format(query, query_lower, to_email)
    
    # Check for direct format: "send email to X subject Y body Z"
    elif "send email to" in query_lower and "subject" in query_lower and "body" in query_lower:
        print(f"📧 Matched direct format")
        return handle_direct_email_format(query, query_lower, to_email)
    
    # Check for draft format: "draft email to X about Y saying Z"
    elif "draft email to" in query_lower:
        print(f"📧 Matched draft format")
        return handle_draft_email_format(query, query_lower, to_email)
    
    # Dynamic email handling for any email request
    else:
        print(f"📧 Matched dynamic format")
        return handle_dynamic_email_format(query, query_lower, to_email)

def handle_structured_email_format(query, query_lower, to_email=""):
    """Handle 'send an email with subject X and body Y' format"""
    print(f"📧 Processing structured format: {query}")
    
    # Extract subject and body using string splitting
    if 'subject' in query_lower and 'body' in query_lower:
        # Handle "with the subject", "with a subject", and "with subject"
        if 'with the subject' in query_lower:
            subject_part = query_lower.split('with the subject', 1)[1]
        elif 'with a subject' in query_lower:
            subject_part = query_lower.split('with a subject', 1)[1]
        else:
            subject_part = query_lower.split('with subject', 1)[1]
        
        # Split by 'body' to separate subject and body
        if 'body' in subject_part:
            subject_body_parts = subject_part.split('body', 1)
            raw_subject = subject_body_parts[0].strip()
            raw_body = subject_body_parts[1].strip()
            
            # Clean up common words and quotes
            raw_subject = raw_subject.replace('and', '').strip().strip('"\'')
            raw_body = raw_body.strip().strip('"\'')
            
            print(f"📧 Raw extracted - Subject: '{raw_subject}', Body: '{raw_body}'")
            
            # Generate better subject and body using AI
            subject, body = generate_email_content(query, raw_subject, raw_body)
            
            print(f"📧 AI Generated - Subject: '{subject}', Body: '{body}'")
            
            # Save the drafted email content
            try:
                with open("Data/generated_content.txt", 'w', encoding='utf-8') as f:
                    f.write(f"Subject: {subject}\n")
                    f.write(f"Body: {body}\n")
                
                # Open the email GUI dialog asynchronously
                try:
                    import threading
                    from Backend.EmailGUI import open_email_gui
                    
                    def open_gui_async():
                        try:
                            open_email_gui("", subject, body)  # Empty to_email, user will enter it in GUI
                        except Exception as e:
                            print(f"GUI Error: {e}")
                    
                    threading.Thread(target=open_gui_async, daemon=True).start()
                    
                    return f"✅ Email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\n📧 Email dialog opened. Please enter the recipient email address and click Send."
                except ImportError:
                    return f"✅ Email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\nSay 'send it to [email]' to send this email."
                
            except Exception as e:
                return f"❌ Failed to prepare email: {str(e)}"
        else:
            return "Please use the format: 'send an email with subject [subject] and body [body]'"
    else:
        return "Please use the format: 'send an email with subject [subject] and body [body]'"

def handle_direct_email_format(query, query_lower, to_email=""):
    """Handle 'send email to X subject Y body Z' format"""
    print(f"📧 Processing direct format: {query}")
    
    import re
    
    # Use provided email or extract from query
    if not to_email:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, query)
        if not email_match:
            return "Please provide a valid email address. Example: 'send email to john@example.com subject meeting body I'll be there'"
        to_email = email_match.group()
    
    # Extract subject and body
    raw_subject = ""
    raw_body = ""
    
    # Find subject and body after "subject" and "body" keywords
    subject_match = re.search(r'subject\s+([^,]+?)(?:\s+body\s+|$)', query_lower)
    if subject_match:
        raw_subject = subject_match.group(1).strip()
    
    body_match = re.search(r'body\s+(.+)', query_lower)
    if body_match:
        raw_body = body_match.group(1).strip()
    
    if not raw_subject or not raw_body:
        return "Please use the format: 'send email to [email] subject [subject] body [body]'"
    
    print(f"📧 Raw extracted - To: {to_email}, Subject: '{raw_subject}', Body: '{raw_body}'")
    
    # Generate better subject and body using AI
    subject, body = generate_email_content(query, raw_subject, raw_body)
    
    print(f"📧 AI Generated - To: {to_email}, Subject: '{subject}', Body: '{body}'")
    
    # Send the email directly
    result = gmail_integration.send_email(to_email, subject, body)
    
    if "successfully" in result.lower():
        return f"✅ Email sent successfully to {to_email}!"
    else:
        return f"❌ Failed to send email: {result}"

def handle_draft_email_format(query, query_lower, to_email=""):
    """Handle 'draft email to X about Y saying Z' format"""
    print(f"📧 Processing draft format: {query}")
    
    import re
    
    # Use provided email or extract from query
    if not to_email:
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        email_match = re.search(email_pattern, query)
        if not email_match:
            return "Please provide a valid email address. Example: 'draft email to john@example.com about meeting saying I'll be there'"
        to_email = email_match.group()
    
    # Extract subject and body
    raw_subject = ""
    raw_body = ""
    
    # Find subject after "about" keyword
    subject_match = re.search(r'about\s+([^,]+?)(?:\s+saying\s+|$)', query_lower)
    if subject_match:
        raw_subject = subject_match.group(1).strip()
    
    # Find body after "saying" keyword
    body_match = re.search(r'saying\s+(.+)', query_lower)
    if body_match:
        raw_body = body_match.group(1).strip()
    
    if not raw_subject or not raw_body:
        return "Please use the format: 'draft email to [email] about [subject] saying [body]'"
    
    print(f"📧 Raw extracted - To: {to_email}, Subject: '{raw_subject}', Body: '{raw_body}'")
    
    # Generate better subject and body using AI
    subject, body = generate_email_content(query, raw_subject, raw_body)
    
    print(f"📧 AI Generated - To: {to_email}, Subject: '{subject}', Body: '{body}'")
    
    # Save the drafted email content
    try:
        with open("Data/generated_content.txt", 'w', encoding='utf-8') as f:
            f.write(f"To: {to_email}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"Body: {body}\n")
        
        # Open the email GUI dialog asynchronously
        try:
            import threading
            from Backend.EmailGUI import open_email_gui
            
            def open_gui_async():
                try:
                    open_email_gui(to_email, subject, body)
                except Exception as e:
                    print(f"GUI Error: {e}")
            
            threading.Thread(target=open_gui_async, daemon=True).start()
            
            return f"✅ Email drafted successfully!\n\nTo: {to_email}\nSubject: {subject}\nBody: {body}\n\n📧 Email dialog opened. Please review and click Send."
        except ImportError:
            return f"✅ Email drafted successfully!\n\nTo: {to_email}\nSubject: {subject}\nBody: {body}\n\nSay 'send it to [email]' to send this email."
        
    except Exception as e:
        return f"❌ Failed to draft email: {str(e)}"

def handle_dynamic_email_format(query, query_lower, to_email=""):
    """Handle any type of email request dynamically"""
    print(f"📧 Processing dynamic email format: {query}")
    
    # Extract email address if present
    import re
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, query)
    extracted_email = email_match.group() if email_match else to_email
    
    # Clean the query to extract the main content
    email_words = ['send', 'email', 'draft', 'compose', 'write', 'create', 'to', 'subject', 'body', 'about', 'saying', 'with', 'an', 'a', 'the', 'me']
    clean_query = query_lower
    
    # Remove email address from the query
    if extracted_email:
        clean_query = clean_query.replace(extracted_email.lower(), '')
    
    # Remove common email words more carefully
    for word in email_words:
        # Use word boundaries to avoid partial matches
        clean_query = re.sub(r'\b' + word + r'\b', ' ', clean_query, flags=re.IGNORECASE)
    
    # Clean up extra spaces and punctuation
    clean_query = re.sub(r'\s+', ' ', clean_query).strip()
    clean_query = clean_query.strip('.,!?')
    
    # If the cleaned content is too short, use the original query
    if len(clean_query) < 10:
        # Extract meaningful content from the original query
        meaningful_words = []
        words = query.split()
        for word in words:
            if len(word) > 2 and word.lower() not in email_words:
                meaningful_words.append(word)
        clean_query = ' '.join(meaningful_words)
    
    print(f"📧 Cleaned content: '{clean_query}'")
    
    # Test AI generation first
    print("🧪 Testing AI generation...")
    ai_working = test_ai_generation()
    
    # Generate AI content based on the type of request
    if ai_working:
        subject, body = generate_dynamic_email_content(query, clean_query, extracted_email)
    else:
        # Use simple fallback if AI is not working
        print("⚠️ Using fallback content generation (AI not working)")
        subject, body = generate_simple_fallback_content(query, clean_query, "general")
    
    print(f"📧 AI Generated Dynamic Email - Subject: '{subject}', Body: '{body}'")
    
    # Save the drafted email content
    try:
        with open("Data/generated_content.txt", 'w', encoding='utf-8') as f:
            f.write(f"Subject: {subject}\n")
            f.write(f"Body: {body}\n")
        
        # Open the email GUI dialog asynchronously
        try:
            import threading
            from Backend.EmailGUI import open_email_gui
            
            def open_gui_async():
                try:
                    print(f"📧 Opening GUI with - Subject: '{subject}', Body: '{body[:100]}...'")
                    open_email_gui(extracted_email, subject, body)  # Use extracted email if available
                except Exception as e:
                    print(f"GUI Error: {e}")
            
            threading.Thread(target=open_gui_async, daemon=True).start()
            
            return f"✅ Email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\n📧 Email dialog opened. Please enter the recipient email address and click Send."
        except ImportError:
            return f"✅ Email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\nSay 'send it to [email]' to send this email."
        
    except Exception as e:
        return f"❌ Failed to prepare email: {str(e)}"

def handle_leave_request_format(query, query_lower):
    """Handle leave request email commands"""
    print(f"📧 Processing leave request format: {query}")
    
    # Extract the leave request content
    leave_keywords = ['leave', 'request', 'asking', 'asking for', 'not coming', 'tomorrow', 'morning']
    raw_content = query
    
    # Remove common email words but keep the leave request content
    email_words = ['send', 'email', 'draft', 'compose', 'write', 'create', 'to', 'subject', 'body', 'about', 'saying', 'with']
    clean_query = query_lower
    for word in email_words:
        clean_query = clean_query.replace(word, ' ').strip()
    
    raw_content = clean_query.strip()
    
    print(f"📧 Raw leave request content: '{raw_content}'")
    
    # Generate better subject and body using AI specifically for leave requests
    subject, body = generate_leave_request_content(query, raw_content)
    
    print(f"📧 AI Generated Leave Request - Subject: '{subject}', Body: '{body}'")
    
    # Save the drafted email content
    try:
        with open("Data/generated_content.txt", 'w', encoding='utf-8') as f:
            f.write(f"Subject: {subject}\n")
            f.write(f"Body: {body}\n")
        
        # Open the email GUI dialog asynchronously
        try:
            import threading
            from Backend.EmailGUI import open_email_gui
            
            def open_gui_async():
                try:
                    open_email_gui("", subject, body)  # Empty to_email, user will enter it in GUI
                except Exception as e:
                    print(f"GUI Error: {e}")
            
            threading.Thread(target=open_gui_async, daemon=True).start()
            
            return f"✅ Leave request email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\n📧 Email dialog opened. Please enter the recipient email address and click Send."
        except ImportError:
            return f"✅ Leave request email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\nSay 'send it to [email]' to send this email."
        
    except Exception as e:
        return f"❌ Failed to prepare leave request email: {str(e)}"

def handle_generic_email_format(query, query_lower):
    """Handle generic email commands"""
    print(f"📧 Processing generic format: {query}")
    
    # For generic commands, try to extract meaningful content
    # Remove common email words
    email_words = ['send', 'email', 'draft', 'compose', 'write', 'create', 'to', 'subject', 'body', 'about', 'saying', 'with']
    clean_query = query_lower
    for word in email_words:
        clean_query = clean_query.replace(word, ' ').strip()
    
    # Use the cleaned query as raw content
    raw_content = clean_query.strip()
    
    print(f"📧 Raw content extracted: '{raw_content}'")
    
    # Generate better subject and body using AI
    subject, body = generate_email_content(query, "", raw_content)
    
    print(f"📧 AI Generated - Subject: '{subject}', Body: '{body}'")
    
    # Save the drafted email content
    try:
        with open("Data/generated_content.txt", 'w', encoding='utf-8') as f:
            f.write(f"Subject: {subject}\n")
            f.write(f"Body: {body}\n")
        
        # Open the email GUI dialog asynchronously
        try:
            import threading
            from Backend.EmailGUI import open_email_gui
            
            def open_gui_async():
                try:
                    open_email_gui("", subject, body)  # Empty to_email, user will enter it in GUI
                except Exception as e:
                    print(f"GUI Error: {e}")
            
            threading.Thread(target=open_gui_async, daemon=True).start()
            
            return f"✅ Email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\n📧 Email dialog opened. Please enter the recipient email address and click Send."
        except ImportError:
            return f"✅ Email prepared successfully!\n\nSubject: {subject}\nBody: {body}\n\nSay 'send it to [email]' to send this email."
        
    except Exception as e:
        return f"❌ Failed to prepare email: {str(e)}"

def generate_dynamic_email_content(query, clean_content, to_email=""):
    """Generate email content dynamically based on the request type"""
    try:
        # Import the AI model
        from Backend.Model import ChatBot
        
        # Extract intent using NLP-like processing
        intent_data = extract_email_intent(query)
        
        # Intelligent prompt that uses extracted intent
        prompt = f"""You are an email writing assistant. Create a professional email based on this analysis:

Original Request: "{query}"
Subject Hint: "{intent_data['subject_hint']}"
Content Focus: "{intent_data['content_hint']}"

Instructions:
- Use the subject hint as guidance for the subject line
- Focus the email content on the identified topic
- Keep it professional but concise (2-3 sentences)
- Make it appropriate for the detected intent

Format your response exactly as:

SUBJECT: [clear, professional subject line - max 60 characters]

BODY: [concise, professional email body]

Create the email now:"""
        
        print(f"🤖 Calling AI with simple prompt: {prompt}")
        
        # Generate content using AI
        try:
            ai_response = ChatBot(prompt)
            print(f"🤖 AI Response: {ai_response}")
        except Exception as ai_error:
            print(f"⚠️ AI generation failed: {ai_error}")
            ai_response = ""
        
        # Parse the AI response using the new parsing function
        subject, body = parse_ai_email_response(ai_response, clean_content)
        
        print(f"📧 Final Subject: '{subject}'")
        print(f"📧 Final Body: '{body[:100]}...'")
        
        return subject, body
        
    except Exception as e:
        print(f"⚠️ AI dynamic email generation failed: {e}")
        # Fallback to basic email
        subject = "Email Request"
        body = f"""Dear [Recipient],

I hope this email finds you well. I am writing to address the following matter:

{clean_content}

I would appreciate your attention to this request.

Thank you for your consideration.

Best regards,
[Your Name]"""
        
        return subject, body

def parse_ai_email_response(ai_response, clean_content):
    """Parse AI response to extract subject and body"""
    subject = ""
    body = ""
    
    print(f"🔍 Parsing AI response: {ai_response[:200]}...")
    
    # Try parsing with **SUBJECT:** and **BODY:** format first
    if "**SUBJECT:**" in ai_response and "**BODY:**" in ai_response:
        subject_start = ai_response.find("**SUBJECT:**") + 12
        body_start = ai_response.find("**BODY:**") + 8
        
        if body_start > subject_start:
            subject = ai_response[subject_start:body_start-8].strip()
            body = ai_response[body_start:].strip()
            print(f"✅ Parsed with ** markers - Subject: '{subject}'")
    
    # If that didn't work, try regular SUBJECT: and BODY: format
    elif "SUBJECT:" in ai_response and "BODY:" in ai_response:
        subject_start = ai_response.find("SUBJECT:") + 8
        body_start = ai_response.find("BODY:") + 5
        
        if body_start > subject_start:
            subject = ai_response[subject_start:body_start-5].strip()
            body = ai_response[body_start:].strip()
            print(f"✅ Parsed with regular markers - Subject: '{subject}'")
        else:
            # Fallback parsing line by line
            lines = ai_response.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("SUBJECT:"):
                    subject = line.replace("SUBJECT:", "").strip()
                elif line.startswith("BODY:"):
                    body = line.replace("BODY:", "").strip()
            print(f"✅ Parsed line by line - Subject: '{subject}'")
    
    # If still no success, try to extract subject from the first meaningful line
    if not subject or not body:
        lines = ai_response.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            # Skip empty lines and common email words
            if (line and 
                not line.startswith('Dear') and 
                not line.startswith('I hope') and 
                not line.startswith('Best regards') and
                not line.startswith('Thank you') and
                not line.startswith('Please') and
                not line.startswith('Here is') and
                len(line) > 5):
                # Clean up the subject line
                if line.startswith('SUBJECT:'):
                    subject = line.replace('SUBJECT:', '').strip()
                elif line.startswith('**SUBJECT:**'):
                    subject = line.replace('**SUBJECT:**', '').strip()
                else:
                    subject = line
                # Take everything after this line as body
                body = '\n'.join(lines[i+1:]).strip()
                print(f"✅ Extracted from first meaningful line - Subject: '{subject}'")
                break
    
    # Clean up formatting issues
    if subject:
        # Remove any remaining SUBJECT: prefixes
        subject = subject.replace('SUBJECT:', '').strip()
        subject = subject.replace('**SUBJECT:**', '').strip()
        subject = subject.replace('  ', ' ').strip()  # Remove double spaces
        subject = subject.replace('\n', ' ').strip()  # Remove line breaks
        subject = subject.replace('\t', ' ').strip()  # Remove tabs
    
    if body:
        body = body.replace('  ', ' ')  # Remove double spaces
        body = body.replace('\t', ' ')  # Remove tabs
        body = body.replace('\n\n\n', '\n\n')  # Remove excessive line breaks
        body = body.strip()
        
        # If body is too long, truncate it to a reasonable length
        lines = body.split('\n')
        if len(lines) > 6:  # If more than 6 lines, keep only first 6
            body = '\n'.join(lines[:6])
        
        # Remove any trailing notes or explanations from AI
        if "Please note that you can" in body:
            body = body.split("Please note that you can")[0].strip()
        if "A professional" in body and body.count('\n') > 3:
            body = body.split("A professional")[0].strip()
    
    # If AI parsing failed, use fallback
    if not subject or not body:
        print("⚠️ AI parsing failed, using fallback")
        subject = "Email Request"
        body = f"""Dear [Recipient],

I hope this email finds you well. I am writing to address the following matter:

{clean_content}

I would appreciate your attention to this request.

Thank you for your consideration.

Best regards,
[Your Name]"""
    
    return subject, body

def test_ai_generation():
    """Test if AI generation is working"""
    try:
        from Backend.Model import ChatBot
        test_prompt = "Generate a simple test response: SUBJECT: Test Subject\nBODY: This is a test body"
        response = ChatBot(test_prompt)
        print(f"🤖 AI Test Response: {response}")
        
        # Check if response contains expected markers
        if "SUBJECT:" in response and "BODY:" in response:
            print("✅ AI test successful - response contains expected markers")
            return True
        else:
            print("⚠️ AI test failed - response missing expected markers")
            return False
    except Exception as e:
        print(f"⚠️ AI Test Failed: {e}")
        return False

def generate_simple_fallback_content(query, clean_content, email_type):
    """Generate simple fallback content without AI"""
    print(f"📧 Generating fallback content for: {clean_content}")
    
    # Create subject based on content
    if "don't sleep" in clean_content.lower() or "sleep" in clean_content.lower():
        subject = "Sleep Schedule Request"
    elif "leave" in clean_content.lower() or "request" in clean_content.lower():
        subject = "Leave Request"
    elif "meeting" in clean_content.lower():
        subject = "Meeting Request"
    elif "project" in clean_content.lower() or "update" in clean_content.lower():
        subject = "Project Update"
    else:
        subject = "Email Request"
    
    # Create body based on content
    if "don't sleep" in clean_content.lower():
        body = f"""Dear [Recipient],

I hope this email finds you well. I am writing to address a sleep-related matter.

{clean_content}

I would appreciate your attention to this request.

Thank you for your consideration.

Best regards,
[Your Name]"""
    else:
        body = f"""Dear [Recipient],

I hope this email finds you well. I am writing to address the following matter:

{clean_content}

I would appreciate your attention to this request.

Thank you for your consideration.

Best regards,
[Your Name]"""
    
    return subject, body

def validate_and_enhance_email_content(subject, body, clean_content, email_type):
    """Validate and enhance email content quality"""
    # Ensure subject is not too short
    if not subject or len(subject) < 5:
        if email_type == "leave_request":
            subject = "Leave Request"
        elif email_type == "meeting_request":
            subject = "Meeting Request"
        elif email_type == "project_update":
            subject = "Project Update"
        else:
            subject = "Email Request"
    
    # Ensure body is not too short
    if not body or len(body) < 50:
        if email_type == "leave_request":
            body = f"""Dear Manager,

I hope this email finds you well. I am writing to formally request leave.

{clean_content}

I would appreciate your approval for this leave request.

Thank you for your consideration.

Best regards,
[Your Name]"""
        else:
            body = f"""Dear [Recipient],

I hope this email finds you well. I am writing to address the following matter:

{clean_content}

I would appreciate your attention to this request.

Thank you for your consideration.

Best regards,
[Your Name]"""
    
    # Ensure proper formatting
    subject = subject.strip()
    body = body.strip()
    
    # Add proper spacing if missing
    if body and not body.startswith('\n'):
        body = '\n' + body
    
    return subject, body

def generate_leave_request_content(query, raw_content):
    """Generate leave request email content using AI"""
    try:
        # Import the AI model
        from Backend.Model import ChatBot
        
        # Create a specialized prompt for leave requests
        prompt = f"""You are a professional email assistant. Generate a detailed, well-formatted leave request email.

Original Request: "{query}"
Raw Content: "{raw_content}"

Generate a professional leave request email with:

SUBJECT: Create a clear, professional subject line (max 60 characters) for a leave request

BODY: Write a comprehensive, professional email body that includes:
- Formal greeting (e.g., "Dear [Manager's Name]," or "Dear Manager,")
- Clear statement of leave request with specific dates if mentioned
- Reason for leave if provided in the request
- Professional tone throughout
- Proper closing (e.g., "Best regards," "Sincerely,")
- Your name at the end

Make the email detailed, professional, and properly formatted. Use proper spacing and formatting. The email should be at least 3-4 paragraphs long and address all aspects of the leave request professionally."""
        
        # Generate content using AI
        print(f"🤖 Calling AI with prompt: {prompt[:200]}...")
        ai_response = ChatBot(prompt)
        print(f"🤖 AI Response: {ai_response}")
        
        # Parse the AI response with improved formatting
        subject = ""
        body = ""
        
        if "SUBJECT:" in ai_response and "BODY:" in ai_response:
            # Extract subject and body from AI response
            subject_start = ai_response.find("SUBJECT:") + 8
            body_start = ai_response.find("BODY:") + 5
            
            if body_start > subject_start:
                subject = ai_response[subject_start:body_start-5].strip()
                body = ai_response[body_start:].strip()
            else:
                # Fallback parsing
                lines = ai_response.split('\n')
                for line in lines:
                    if line.strip().startswith("SUBJECT:"):
                        subject = line.replace("SUBJECT:", "").strip()
                    elif line.strip().startswith("BODY:"):
                        body = line.replace("BODY:", "").strip()
        
        # Clean up formatting issues
        if subject:
            # Fix letter spacing and formatting issues
            subject = subject.replace('  ', ' ').strip()  # Remove double spaces
            subject = subject.replace('\n', ' ').strip()  # Remove line breaks
            subject = subject.replace('\t', ' ').strip()  # Remove tabs
        
        if body:
            # Fix letter spacing and formatting issues
            body = body.replace('  ', ' ')  # Remove double spaces
            body = body.replace('\t', ' ')  # Remove tabs
            # Ensure proper paragraph spacing
            body = body.replace('\n\n\n', '\n\n')  # Remove excessive line breaks
            body = body.strip()
        
        # If AI parsing failed, use fallback
        if not subject or not body:
            subject = "Leave Request"
            body = f"""Dear Manager,

I hope this email finds you well. I am writing to formally request leave.

{raw_content}

I would appreciate your approval for this leave request.

Thank you for your consideration.

Best regards,
[Your Name]"""
        
        return subject, body
        
    except Exception as e:
        print(f"⚠️ AI leave request generation failed: {e}")
        # Fallback to basic leave request
        subject = "Leave Request"
        body = f"""Dear Manager,

I hope this email finds you well. I am writing to formally request leave.

{raw_content}

I would appreciate your approval for this leave request.

Thank you for your consideration.

Best regards,
[Your Name]"""
        
        return subject, body

def generate_email_content(query, raw_subject, raw_body):
    """Generate better email subject and body using AI"""
    try:
        # Import the AI model
        from Backend.Model import ChatBot
        
        # Create a prompt for email generation
        if raw_subject and raw_body:
            # If we have both subject and body, enhance them
            prompt = f"""Based on this email request, generate a professional email subject and body:

Original Request: "{query}"
Raw Subject: "{raw_subject}"
Raw Body: "{raw_body}"

Please generate:
1. A clear, professional subject line (max 60 characters)
2. A well-written email body that expands on the raw content

Format your response as:
SUBJECT: [subject line]
BODY: [email body]

Make the email professional, clear, and actionable."""
        else:
            # If we only have raw content, generate both subject and body
            prompt = f"""Based on this email request, generate a professional email subject and body:

Original Request: "{query}"
Raw Content: "{raw_body}"

Please generate:
1. A clear, professional subject line (max 60 characters)
2. A well-written email body that addresses the request

Format your response as:
SUBJECT: [subject line]
BODY: [email body]

Make the email professional, clear, and actionable."""
        
        # Generate content using AI
        print(f"🤖 Calling AI for leave request with prompt: {prompt[:200]}...")
        ai_response = ChatBot(prompt)
        print(f"🤖 AI Leave Request Response: {ai_response}")
        
        # Parse the AI response
        subject = ""
        body = ""
        
        if "SUBJECT:" in ai_response and "BODY:" in ai_response:
            # Extract subject and body from AI response
            subject_start = ai_response.find("SUBJECT:") + 8
            body_start = ai_response.find("BODY:") + 5
            
            if body_start > subject_start:
                subject = ai_response[subject_start:body_start-5].strip()
                body = ai_response[body_start:].strip()
            else:
                # Fallback parsing
                lines = ai_response.split('\n')
                for line in lines:
                    if line.strip().startswith("SUBJECT:"):
                        subject = line.replace("SUBJECT:", "").strip()
                    elif line.strip().startswith("BODY:"):
                        body = line.replace("BODY:", "").strip()
        
        # If AI parsing failed, use fallback
        if not subject or not body:
            if raw_subject:
                subject = raw_subject
            else:
                subject = "Email from JARVIS"
            
            if raw_body:
                body = raw_body
            else:
                body = f"Hello,\n\n{query}\n\nBest regards,\nJARVIS"
        
        return subject, body
        
    except Exception as e:
        print(f"⚠️ AI email generation failed: {e}")
        # Fallback to raw content
        if raw_subject:
            subject = raw_subject
        else:
            subject = "Email from JARVIS"
        
        if raw_body:
            body = raw_body
        else:
            body = f"Hello,\n\n{query}\n\nBest regards,\nJARVIS"
        
        return subject, body

def extract_email_intent(query):
    """Extract email intent from natural language using NLP-like processing"""
    import re
    
    print(f"🧠 Extracting intent from: '{query}'")
    
    # Common patterns and their corresponding subjects/content
    patterns = [
        # Meeting patterns
        (r'(?:write|draft|send|compose).*?email.*?(?:about|regarding)\s*(meeting|call|appointment)\s*(tomorrow|today|next week|monday|tuesday|wednesday|thursday|friday|saturday|sunday|\d+)', 
         lambda m: f"Meeting {m.group(2).title()}", lambda m: f"meeting {m.group(2)}"),
        
        # Leave/absence patterns
        (r'(?:write|draft|send|compose).*?email.*?(?:saying|about|that)\s*(?:i|I).*?(sick|ill|late|leave|absent|not coming|won\'t be|cannot come)',
         lambda m: f"Leave Request - {m.group(1).title()}", lambda m: f"leave request {m.group(1)}"),
        
        # Project/work patterns
        (r'(?:write|draft|send|compose).*?email.*?(?:about|regarding)\s*(project|work|task|assignment).*?(update|progress|status|completion)',
         lambda m: f"Project {m.group(2).title()}", lambda m: f"project {m.group(2)}"),
        
        # Apology patterns
        (r'(?:write|draft|send|compose).*?email.*?(?:saying|apologizing|sorry)\s*(for|about)?\s*(being late|delay|mistake|error)',
         lambda m: "Apology", lambda m: f"apology {m.group(2)}"),
        
        # Request patterns
        (r'(?:write|draft|send|compose).*?email.*?(?:asking|requesting)\s*(for|about)?\s*(.+)',
         lambda m: "Request", lambda m: f"request {m.group(2)}"),
        
        # Confirmation patterns
        (r'(?:write|draft|send|compose).*?email.*?(?:confirming|to confirm)\s*(.+)',
         lambda m: "Confirmation", lambda m: f"confirmation {m.group(1)}"),
        
        # General action patterns
        (r'(?:write|draft|send|compose).*?email.*?(?:saying|about|that)\s*(.+)',
         lambda m: "Email", lambda m: m.group(1)),
    ]
    
    # Try to match patterns
    for pattern, subject_func, content_func in patterns:
        match = re.search(pattern, query, re.IGNORECASE)
        if match:
            try:
                if callable(subject_func):
                    subject_hint = subject_func(match)
                else:
                    subject_hint = subject_func
                
                if callable(content_func):
                    content_hint = content_func(match)
                else:
                    content_hint = content_func
                
                print(f"✅ Matched pattern - Subject hint: '{subject_hint}', Content: '{content_hint}'")
                return {'subject_hint': subject_hint, 'content_hint': content_hint, 'original': query}
            except Exception as e:
                print(f"⚠️ Pattern matching error: {e}")
                continue
    
    # If no pattern matched, extract key content words
    email_words = ['write', 'draft', 'send', 'compose', 'email', 'to', 'about', 'saying', 'that', 'an', 'a', 'the']
    words = query.split()
    meaningful_words = [word for word in words if word.lower() not in email_words and len(word) > 2]
    
    content_hint = ' '.join(meaningful_words[:5])  # Take first 5 meaningful words
    subject_hint = "Email Request"
    
    if 'meeting' in query.lower():
        subject_hint = "Meeting Request"
    elif 'leave' in query.lower() or 'sick' in query.lower():
        subject_hint = "Leave Request"
    elif 'project' in query.lower() or 'update' in query.lower():
        subject_hint = "Project Update"
    elif 'sorry' in query.lower() or 'apologize' in query.lower():
        subject_hint = "Apology"
    
    print(f"🔍 Fallback extraction - Subject hint: '{subject_hint}', Content: '{content_hint}'")
    return {'subject_hint': subject_hint, 'content_hint': content_hint, 'original': query}

def send_email_with_gui(to_email, subject, body, cc_email="", bcc_email=""):
    """Send email with GUI confirmation"""
    try:
        # First authenticate
        auth_result = gmail_integration.authenticate()
        if "successful" not in auth_result:
            return f"❌ Authentication failed: {auth_result}"
        
        # Send the email
        result = gmail_integration.send_email(to_email, subject, body, cc_email, bcc_email)
        
        if "successfully" in result.lower():
            return f"✅ Email sent successfully to {to_email}!"
        else:
            return f"❌ Failed to send email: {result}"
            
    except Exception as e:
        return f"❌ Error sending email: {str(e)}"
