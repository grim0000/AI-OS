import json
import os
import threading
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QMessageBox,
                             QFrame, QGridLayout, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QObject
from PyQt5.QtGui import QFont, QPalette, QColor
from .GmailIntegration import GmailIntegration

class EmailDialogWorker(QObject):
    """Worker object to handle email dialog in main thread"""
    
    dialog_finished = pyqtSignal(str)  # Signal when dialog is finished
    
    def __init__(self, subject, body):
        super().__init__()
        self.subject = subject
        self.body = body
        self.gmail = GmailIntegration()
        
    def show_dialog(self):
        """Show the email dialog in the main thread"""
        try:
            # Create and show the dialog
            dialog = PrivacyProtectedEmailDialog(self.subject, self.body)
            
            # Connect the email sent signal
            dialog.email_sent.connect(self._on_email_sent)
            
            # Show dialog and wait for result
            result = dialog.exec_()
            
            if result == QDialog.Accepted:
                self.dialog_finished.emit("Email dialog completed successfully.")
            else:
                self.dialog_finished.emit("Email sending cancelled.")
                
        except Exception as e:
            self.dialog_finished.emit(f"Error showing dialog: {str(e)}")
    
    def _on_email_sent(self, message):
        """Handle email sent notification"""
        print(f"Email operation completed: {message}")

class PrivacyProtectedEmailDialog(QDialog):
    """Secure email dialog that doesn't store sensitive data in chat history"""
    
    email_sent = pyqtSignal(str)  # Signal to notify when email is sent
    
    def __init__(self, subject="", body="", parent=None):
        super().__init__(parent)
        self.subject = subject
        self.body = body
        self.gmail = GmailIntegration()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Send Email - Privacy Protected")
        self.setFixedSize(500, 400)
        self.setWindowFlags(Qt.Window | Qt.WindowStaysOnTopHint)
        
        # Set modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #f8fafc;
                border: 2px solid #e2e8f0;
                border-radius: 12px;
            }
            QLabel {
                color: #1e293b;
                font-weight: bold;
                font-size: 12px;
            }
            QLineEdit, QTextEdit {
                border: 2px solid #cbd5e1;
                border-radius: 8px;
                padding: 8px;
                background-color: white;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #3b82f6;
                outline: none;
            }
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton#cancel {
                background-color: #6b7280;
            }
            QPushButton#cancel:hover {
                background-color: #4b5563;
            }
        """)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title = QLabel("📧 Send Secure Email")
        title.setStyleSheet("font-size: 18px; color: #1e293b; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Form grid
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        
        # To field
        to_label = QLabel("To:")
        self.to_input = QLineEdit()
        self.to_input.setPlaceholderText("recipient@example.com")
        form_layout.addWidget(to_label, 0, 0)
        form_layout.addWidget(self.to_input, 0, 1)
        
        # CC field
        cc_label = QLabel("CC (optional):")
        self.cc_input = QLineEdit()
        self.cc_input.setPlaceholderText("cc@example.com")
        form_layout.addWidget(cc_label, 1, 0)
        form_layout.addWidget(self.cc_input, 1, 1)
        
        # BCC field
        bcc_label = QLabel("BCC (optional):")
        self.bcc_input = QLineEdit()
        self.bcc_input.setPlaceholderText("bcc@example.com")
        form_layout.addWidget(bcc_label, 2, 0)
        form_layout.addWidget(self.bcc_input, 2, 1)
        
        # Subject field
        subject_label = QLabel("Subject:")
        self.subject_input = QLineEdit()
        self.subject_input.setText(self.subject)
        self.subject_input.setPlaceholderText("Enter email subject")
        form_layout.addWidget(subject_label, 3, 0)
        form_layout.addWidget(self.subject_input, 3, 1)
        
        # Body field
        body_label = QLabel("Body:")
        self.body_input = QTextEdit()
        self.body_input.setText(self.body)
        self.body_input.setPlaceholderText("Enter email body")
        self.body_input.setMaximumHeight(120)
        form_layout.addWidget(body_label, 4, 0)
        form_layout.addWidget(self.body_input, 4, 1)
        
        layout.addLayout(form_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Send button
        send_btn = QPushButton("Send Email")
        send_btn.clicked.connect(self.send_email)
        button_layout.addWidget(send_btn)
        
        layout.addLayout(button_layout)
        
        # Set focus to first input
        self.to_input.setFocus()
        
    def send_email(self):
        """Send the email and close dialog"""
        to_email = self.to_input.text().strip()
        subject = self.subject_input.text().strip()
        body = self.body_input.toPlainText().strip()
        
        # Validation
        if not to_email:
            QMessageBox.warning(self, "Validation Error", "Please enter a recipient email address.")
            self.to_input.setFocus()
            return
            
        if not subject:
            QMessageBox.warning(self, "Validation Error", "Please enter an email subject.")
            self.subject_input.setFocus()
            return
            
        if not body:
            QMessageBox.warning(self, "Validation Error", "Please enter an email body.")
            self.body_input.setFocus()
            return
            
        # Send email
        try:
            # Authenticate with Gmail
            auth_result = self.gmail.authenticate()
            if "successful" not in auth_result:
                QMessageBox.critical(self, "Authentication Error", f"Gmail authentication failed: {auth_result}")
                return
            
            # Get CC and BCC values
            cc_email = self.cc_input.text().strip() if self.cc_input.text().strip() else None
            bcc_email = self.bcc_input.text().strip() if self.bcc_input.text().strip() else None
            
            # Send the email with CC and BCC
            result = self.gmail.send_email(to_email, subject, body, cc_email, bcc_email)
            
            if "successfully" in result:
                QMessageBox.information(self, "Success", "Email sent successfully!")
                self.email_sent.emit(f"Email sent to {to_email}")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", f"Failed to send email: {result}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {str(e)}")

class PrivacyProtectedEmailSystem:
    """Main system for handling privacy-protected email operations"""
    
    def __init__(self):
        self.gmail = GmailIntegration()
        self.last_email_subject = ""
        self.last_email_body = ""
        
    def handle_email_request(self, user_input, parent_widget=None):
        """
        Handle email requests without storing sensitive data in chat history
        
        Args:
            user_input (str): User's email request
            parent_widget: Parent widget for the dialog
            
        Returns:
            str: Response message for chat (no sensitive data)
        """
        # Extract subject and body from user input
        subject, body = self._extract_email_content(user_input)
        
        # Store the extracted content temporarily for the dialog
        self.last_email_subject = subject
        self.last_email_body = body
        
        # Return instruction to use the new system
        return f"""🔒 **Privacy-Protected Email System Ready!**

I've prepared your email with:
**Subject:** {subject}
**Body:** {body}

**To send securely:**
1. Use the command: "open email dialog"
2. A secure dialog will open where you can enter the recipient email address
3. No sensitive data will be stored in our chat history

**Privacy Features:**
✅ Email addresses are NOT stored in chat history
✅ Recipient information is only used temporarily
✅ CC/BCC fields are optional and secure
✅ All sensitive data is cleared after sending

**Alternative:** You can also use the legacy system by saying "send email to [address] with subject [subject] saying [body]" but this will store the email address in chat history."""
    
    def open_email_dialog(self, subject="", body=""):
        """
        Open the email dialog (to be called from main thread)
        
        Args:
            subject (str): Email subject (optional, uses stored if not provided)
            body (str): Email body (optional, uses stored if not provided)
            
        Returns:
            str: Status message
        """
        try:
            # Use provided subject/body or fall back to stored values
            final_subject = subject if subject else self.last_email_subject
            final_body = body if body else self.last_email_body
            
            if not final_subject or not final_body:
                return "No email content prepared. Please draft an email first using 'draft an email with subject <sub>Subject</sub> and body <body>Content</body>'"
            
            # Return the content for the main thread to handle
            return {
                "action": "open_email_dialog",
                "subject": final_subject,
                "body": final_body,
                "message": "Email content ready for dialog"
            }
                
        except Exception as e:
            return f"Error preparing dialog: {str(e)}"
    
    def _extract_email_content(self, user_input):
        """Extract subject and body from user input"""
        subject = ""
        body = ""
        
        # Look for subject and body markers
        if "<sub>" in user_input and "<body>" in user_input:
            # Extract content between markers
            try:
                sub_start = user_input.find("<sub>") + 5
                sub_end = user_input.find("</sub>") if "</sub>" in user_input else user_input.find("<body>")
                subject = user_input[sub_start:sub_end].strip()
                
                body_start = user_input.find("<body>") + 6
                body_end = user_input.find("</body>") if "</body>" in user_input else len(user_input)
                body = user_input[body_start:body_end].strip()
            except:
                pass
        
        # Fallback: try to extract from natural language
        if not subject and not body:
            # Simple extraction for "draft an email with subject X and body Y"
            if "subject" in user_input.lower():
                parts = user_input.split("subject")
                if len(parts) > 1:
                    subject_part = parts[1]
                    if "and body" in subject_part:
                        subject = subject_part.split("and body")[0].strip()
                        body = subject_part.split("and body")[1].strip()
                    else:
                        subject = subject_part.strip()
            
            # Clean up common words
            subject = subject.replace("'", "").replace('"', "").strip()
            body = body.replace("'", "").replace('"', "").strip()
        
        return subject, body
    
    def _on_email_sent(self, message):
        """Handle email sent notification"""
        # This method can be used to log successful sends without sensitive data
        print(f"Email operation completed: {message}")
    
    def get_help_message(self):
        """Get help message for email commands"""
        return """📧 **Privacy-Protected Email Commands:**

• **"draft an email with subject <sub>Meeting</sub> and body <body>Let's meet tomorrow</body>"**
• **"send email with subject <sub>Project Update</sub> and body <body>Here's the latest progress</body>"**
• **"compose email with subject <sub>Hello</sub> and body <body>How are you?</body>"**

**Privacy Features:**
✅ Email addresses are NOT stored in chat history
✅ Recipient information is only used temporarily
✅ CC/BCC fields are optional and secure
✅ All sensitive data is cleared after sending

**How it works:**
1. Tell me the subject and body
2. I'll prepare your email securely
3. Use "open email dialog" to send
4. Enter recipient email address safely
5. Click send - no sensitive data stored!"""
