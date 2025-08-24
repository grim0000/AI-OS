from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, 
                             QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QSizePolicy, QGraphicsDropShadowEffect,
                             QComboBox)
from PyQt5.QtGui import (QIcon, QFont, QColor, QPainter, QMovie, QTextCharFormat, 
                         QPixmap, QTextBlockFormat, QTextCursor, QLinearGradient, QPalette)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect
from dotenv import dotenv_values
import sys
import os
import time

env_var = dotenv_values(".env")
Assistantname = env_var.get("AssistantName", "AI")
current_dir = os.getcwd()
old_chat_message = ""
last_processed_message = ""  # Track last processed message
TempDirPath = rf"{current_dir}\Frontend\Files"
GraphicsDirPath = rf"{current_dir}\Frontend\Graphics"

def AnswerModifier(Answer):
    lines = Answer.split('\n')
    non_empty_lines = [line for line in lines if line.strip()]
    modified_answer = '\n'.join(non_empty_lines)
    return modified_answer

def QueryModifier(Query):
    new_query = Query.lower().strip()
    query_words = new_query.split()
    question_words = ["how", "where", "what", "who", "when", "why", "which", "whose", "whom", "can you", "What's", "where's", "how's"]
    
    if any(word + " " in new_query for word in question_words):
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "?"
        else:
            new_query += "?"
    else:
        if query_words[-1][-1] in ['.', '?', '!']:
            new_query = new_query[:-1] + "."
        else:
            new_query += "."
            
    return new_query.capitalize()

def SetMicrophoneStatus(Command):
    with open(rf'{TempDirPath}\Mic.data', "w", encoding='utf-8') as file:
        file.write(Command)
        
def GetMicrophoneStatus():
    with open(rf'{TempDirPath}\Mic.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def SetAssistantStatus(Status):
    with open(rf'{TempDirPath}\Status.data', "w", encoding='utf-8') as file:
        file.write(Status)
        
def GetAssistantStatus():
    with open(rf'{TempDirPath}\Status.data', "r", encoding='utf-8') as file:
        Status = file.read()
    return Status

def MicButtonInitialed():
    SetMicrophoneStatus("False")
    
def MicButtonClosed():
    SetMicrophoneStatus("True")
    
def GraphicsDirectoryPath(Filename, width=None, height=None):
    Path = rf'{GraphicsDirPath}\{Filename}'
    return Path

def TempDirectoryPath(Filename):
    Path = rf'{TempDirPath}\{Filename}'
    return Path

def ShowTextToScreen(Text):
    with open(rf'{TempDirPath}\Responses.data', "w", encoding='utf-8') as file:
        file.write(Text)

class ChatScreen(QWidget):
    """Dedicated chat screen for text-based communication"""
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
            }
        """)
        
        # Header
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0ea5e9, stop:1 #0284c7);
                border-radius: 15px;
                border: 2px solid #0ea5e9;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        # Title
        title = QLabel("💬 AI Chat Assistant")
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        # Back button
        self.back_button = QPushButton("← Back to Main")
        self.back_button.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 10px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)
        self.back_button.clicked.connect(self.go_back)
        
        header_layout.addWidget(title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.back_button)
        
        main_layout.addWidget(header)

        # Ch
        #  at area
        chat_container = QWidget()
        chat_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                border: 2px solid #0ea5e9;
                border-radius: 15px;
            }
        """)
        
        chat_layout = QVBoxLayout(chat_container)
        chat_layout.setContentsMargins(20, 20, 20, 20)
        chat_layout.setSpacing(15)
        
        # Chat display area
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #020617);
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                border: 2px solid #1e293b;
                border-radius: 10px;
                padding: 15px;
                selection-background-color: #0ea5e9;
            }
            QTextEdit QScrollBar:vertical {
                background: #1e293b;
                width: 12px;
                border-radius: 6px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #0ea5e9;
                border-radius: 6px;
                min-height: 20px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: #38bdf8;
            }
        """)
        
        chat_layout.addWidget(self.chat_display)
        
        # Input area
        input_container = QWidget()
        input_container.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                border: 2px solid #0ea5e9;
                border-radius: 15px;
                padding: 15px;
            }
        """)
        
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(15, 15, 15, 15)
        input_layout.setSpacing(15)
        
        # Text input
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your message here...")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0f172a, stop:1 #020617);
                border: 2px solid #1e293b;
                border-radius: 10px;
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                padding: 15px 20px;
                min-height: 50px;
            }
            QLineEdit:focus {
                border: 2px solid #0ea5e9;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
            }
            QLineEdit::placeholder {
                color: #64748b;
                font-style: italic;
            }
        """)
        self.text_input.returnPressed.connect(self.send_message)
        
        # Send button
        self.send_button = QPushButton("📤 Send")
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                border: 2px solid #10b981;
                border-radius: 10px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 25px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34d399, stop:1 #10b981);
                border: 2px solid #34d399;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #059669, stop:1 #047857);
            }
        """)
        self.send_button.clicked.connect(self.send_message)
        
        # Clear button
        self.clear_button = QPushButton("🗑️ Clear")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef4444, stop:1 #dc2626);
                border: 2px solid #ef4444;
                border-radius: 10px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                padding: 15px 20px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f87171, stop:1 #ef4444);
                border: 2px solid #f87171;
            }
        """)
        self.clear_button.clicked.connect(self.clear_chat)
        
        input_layout.addWidget(self.text_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.clear_button)
        
        chat_layout.addWidget(input_container)
        main_layout.addWidget(chat_container)
        
        # Status bar
        self.status_label = QLabel("Ready to chat...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #0ea5e9;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: 300;
                padding: 10px;
                background: rgba(14, 165, 233, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(14, 165, 233, 0.3);
            }
        """)
        
        main_layout.addWidget(self.status_label)
        
        # Initialize chat
        self.load_chat_history()
        
        # Timer for updates
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_chat)
        self.update_timer.start(100)  # Update every 100ms for better performance
        
    def send_message(self):
        """Send a text message"""
        message = self.text_input.text().strip()
        if not message:
            return
            
        # Clear input
        self.text_input.clear()
        
        # Add user message to chat
        self.add_message_to_chat(f"{env_var.get('Username', 'User')}", message, "user")
        
        # Update status
        self.status_label.setText("Processing message...")
        
        # Process message in background
        import threading
        thread = threading.Thread(target=self.process_message, args=(message,), daemon=True)
        thread.start()
        
    def process_message(self, message):
        """Process the message using the AI system"""
        try:
            # Import and use the main execution system
            from Main import MainExecution
            
            # Process the message (this will update the responses file)
            result = MainExecution(use_text_input=True, text_query=message)
            
            # The response will be automatically loaded by the update_chat timer
            # No need to manually add it here since the timer will detect the change
            
        except Exception as e:
            print(f"Error processing message: {e}")
            self.add_message_to_chat(f"{env_var.get('AssistantName', 'AI')}", "Sorry, I encountered an error processing your message.", "ai")
        
        # Update status
        self.status_label.setText("Ready to chat...")
        
    def add_message_to_chat(self, sender, message, msg_type):
        """Add a message to the chat display"""
        cursor = self.chat_display.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        # Format based on message type
        if msg_type == "user":
            formatted_msg = f'<div style="margin: 10px 0; padding: 10px; background: rgba(14, 165, 233, 0.1); border-radius: 10px; border-left: 4px solid #0ea5e9;"><span style="color: #0ea5e9; font-weight: bold;">{sender}:</span> <span style="color: #e2e8f0;">{message}</span></div>'
        else:  # AI message
            formatted_msg = f'<div style="margin: 10px 0; padding: 10px; background: rgba(16, 185, 129, 0.1); border-radius: 10px; border-left: 4px solid #10b981;"><span style="color: #10b981; font-weight: bold;">{sender}:</span> <span style="color: #e2e8f0;">{message}</span></div>'
        
        cursor.insertHtml(formatted_msg + '<br>')
        self.chat_display.setTextCursor(cursor)
        
        # Auto-scroll to bottom
        self.chat_display.verticalScrollBar().setValue(
            self.chat_display.verticalScrollBar().maximum()
        )
        
    def load_chat_history(self):
        """Load existing chat history"""
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                content = file.read()
                if content.strip():
                    lines = content.split('\n')
                    for line in lines:
                        if line.strip() and ":" in line:
                            parts = line.split(":", 1)
                            if len(parts) == 2:
                                sender = parts[0].strip()
                                message = parts[1].strip()
                                msg_type = "user" if "User" in sender or env_var.get('Username', 'User') in sender else "ai"
                                self.add_message_to_chat(sender, message, msg_type)
        except:
            pass
            
    def update_chat(self):
        """Update chat display with new messages"""
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                content = file.read()
                if hasattr(self, 'last_content') and content != self.last_content:
                    # New content detected, reload chat
                    self.chat_display.clear()
                    self.load_chat_history()
                    # Auto-scroll to bottom
                    self.chat_display.verticalScrollBar().setValue(
                        self.chat_display.verticalScrollBar().maximum()
                    )
                self.last_content = content
        except:
            pass
            
    def clear_chat(self):
        """Clear the chat history"""
        self.chat_display.clear()
        try:
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write("")
        except:
            pass
            
    def go_back(self):
        """Return to main interface"""
        # Find the main window and switch back
        parent = self.parent()
        while parent and not hasattr(parent, 'show_main_interface'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'show_main_interface'):
            parent.show_main_interface()

class ModernChatSection(QWidget):
    def __init__(self):
        super(ModernChatSection, self).__init__()
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Main horizontal layout with chat on left, main interface on right
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Left side - Chat Panel (35% width)
        chat_panel = QWidget()
        chat_panel.setFixedWidth(int(screen_width * 0.35))
        chat_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e1e2e, stop:1 #181825);
                border-right: 3px solid #89b4fa;
            }
        """)
        
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(15, 15, 15, 15)
        chat_layout.setSpacing(15)
        
        # Chat title with better colors
        chat_title = QLabel("💬 Chat History")
        chat_title.setStyleSheet("""
            QLabel {
                color: #89b4fa;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background: rgba(137, 180, 250, 0.1);
                border-radius: 10px;
                border: 2px solid rgba(137, 180, 250, 0.3);
            }
        """)
        chat_layout.addWidget(chat_title)
        
        # Chat text area with better colors and larger fonts
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #313244, stop:1 #1e1e2e);
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                border: 2px solid #89b4fa;
                border-radius: 15px;
                padding: 15px;
                selection-background-color: #89b4fa;
            }
            QTextEdit QScrollBar:vertical {
                background: #1e1e2e;
                width: 12px;
                border-radius: 6px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #89b4fa;
                border-radius: 6px;
                min-height: 20px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: #b4befe;
            }
        """)
        chat_layout.addWidget(self.chat_text_edit)
        
        # Device selection section
        device_layout = QVBoxLayout()
        device_layout.setSpacing(10)
        
        # Input device dropdown
        input_label = QLabel("🎤 Input Device:")
        input_label.setStyleSheet("""
            QLabel {
                color: #89b4fa;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        device_layout.addWidget(input_label)
        
        self.input_device_combo = QComboBox()
        self.input_device_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #313244, stop:1 #1e1e2e);
                border: 2px solid #89b4fa;
                border-radius: 8px;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                padding: 8px 12px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #89b4fa;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #1e1e2e;
                border: 2px solid #89b4fa;
                border-radius: 8px;
                color: #cdd6f4;
                selection-background-color: #89b4fa;
            }
        """)
        self.populate_input_devices()
        device_layout.addWidget(self.input_device_combo)
        
        # Output device dropdown
        output_label = QLabel("🔊 Output Device:")
        output_label.setStyleSheet("""
            QLabel {
                color: #89b4fa;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        device_layout.addWidget(output_label)
        
        self.output_device_combo = QComboBox()
        self.output_device_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #313244, stop:1 #1e1e2e);
                border: 2px solid #89b4fa;
                border-radius: 8px;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                padding: 8px 12px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #89b4fa;
                margin-right: 5px;
            }
            QComboBox QAbstractItemView {
                background: #1e1e2e;
                border: 2px solid #89b4fa;
                border-radius: 8px;
                color: #cdd6f4;
                selection-background-color: #89b4fa;
            }
        """)
        self.populate_output_devices()
        device_layout.addWidget(self.output_device_combo)
        
        chat_layout.addLayout(device_layout)
        
        # Control buttons row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Reset button with better colors
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f38ba8, stop:1 #eba0ac);
                border: 2px solid #f38ba8;
                border-radius: 10px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f5c2e7, stop:1 #f38ba8);
                border: 2px solid #f5c2e7;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #eba0ac, stop:1 #f38ba8);
            }
        """)
        self.reset_button.clicked.connect(self.reset_assistant)
        
        # Clear chat button with better colors
        self.clear_chat_button = QPushButton("🗑️ Clear")
        self.clear_chat_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fab387, stop:1 #f9e2af);
                border: 2px solid #fab387;
                border-radius: 10px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fef3c7, stop:1 #fab387);
                border: 2px solid #fef3c7;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f9e2af, stop:1 #fab387);
            }
        """)
        self.clear_chat_button.clicked.connect(self.clear_chat)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.clear_chat_button)
        chat_layout.addLayout(button_layout)
        
        # Right side - Main Interface (65% width)
        main_interface = QWidget()
        main_interface.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #11111b, stop:1 #1e1e2e);
            }
        """)
        main_interface_layout = QVBoxLayout(main_interface)
        main_interface_layout.setContentsMargins(0, 0, 0, 0)
        main_interface_layout.setSpacing(0)
        
        # Create animated background with GIF
        self.background_label = QLabel()
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.setStyleSheet("background: transparent;")
        
        # Load and display the 7ZN3.gif as background
        try:
            gif_path = GraphicsDirectoryPath("7ZN3.gif")
            if os.path.exists(gif_path):
                movie = QMovie(gif_path)
                movie.setScaledSize(QSize(400, 400))  # Restored original size
                self.background_label.setMovie(movie)
                movie.start()
        except Exception as e:
            print(f"Error loading background GIF: {e}")
        
        # Status label with better colors
        self.status_label = QLabel("Ready to assist you...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #89b4fa;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: 300;
                margin: 20px;
                padding: 10px;
                background: rgba(137, 180, 250, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(137, 180, 250, 0.3);
            }
        """)
        
        # Layout setup for main interface
        main_interface_layout.addStretch(1)
        main_interface_layout.addWidget(self.background_label, alignment=Qt.AlignCenter)
        main_interface_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        main_interface_layout.addStretch(1)
        
        # Add both panels to main layout
        main_layout.addWidget(chat_panel)
        main_layout.addWidget(main_interface)
        
        # Set default text color
        text_color = QColor("#ffffff")
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        
    def loadMessage(self):
        global last_processed_message
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                
            if messages != last_processed_message and messages.strip():
                # Clear the chat and display all messages to maintain history
                self.chat_text_edit.clear()
                
                lines = messages.split('\n')
                new_lines = []
                
                for line in lines:
                    if line.strip():
                        if ":" in line:
                            parts = line.split(":", 1)
                            if len(parts) == 2:
                                speaker = parts[0].strip()
                                message = parts[1].strip()
                                
                                if "Sunil" in speaker or "User" in speaker:
                                    new_lines.append(f"👤 {message}")
                                else:
                                    new_lines.append(f"🤖 {message}")
                        else:
                            new_lines.append(line)
                
                # Display all messages with proper colors
                for line in new_lines:
                    if "👤" in line:
                        self.addMessages(line, "#89b4fa")  # Blue for user
                    elif "🤖" in line:
                        self.addMessages(line, "#a6e3a1")  # Green for AI
                    else:
                        self.addMessages(line, "#cdd6f4")  # White for other
                
                # Update the last processed message
                last_processed_message = messages
                            
        except Exception as e:
            print(f"Error loading messages: {e}")
            
    def SpeechRecogText(self):
        self.loadMessage()
        
    def addMessages(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        format.setFontWeight(QFont.Bold if color == "#4a90e2" else QFont.Normal)
        
        formatm = QTextBlockFormat()
        formatm.setLineHeight(150, QTextBlockFormat.ProportionalHeight)
        formatm.setTopMargin(10)
        formatm.setBottomMargin(10)
        
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        
        # Auto-scroll to bottom to show latest messages
        self.chat_text_edit.verticalScrollBar().setValue(
            self.chat_text_edit.verticalScrollBar().maximum()
        )
    
    def reset_assistant(self):
        """Reset the assistant to listening state and clear any ongoing operations"""
        try:
            # Set microphone to listening state
            SetMicrophoneStatus("True")
            SetAssistantStatus("Listening...")
            
            # Clear any ongoing operations by writing empty status
            with open(TempDirectoryPath('Status.data'), "w", encoding='utf-8') as file:
                file.write("Listening...")
            
            # Update UI
            self.status_label.setText("Listening...")
            
            print("🔄 Assistant reset to listening state")
            
        except Exception as e:
            print(f"Error resetting assistant: {e}")
    
    def clear_chat(self):
        """Clear the chat history"""
        try:
            # Clear the chat display
            self.chat_text_edit.clear()
            
            # Clear the chat data file
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write("")
            
            print("🗑️ Chat history cleared")
            
        except Exception as e:
            print(f"Error clearing chat: {e}")
    
    def populate_input_devices(self):
        """Populate input device dropdown with currently available microphones"""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            self.input_device_combo.clear()
            self.input_device_combo.addItem("Default Microphone")
            
            # Get default input device
            try:
                default_input = p.get_default_input_device_info()
                if default_input:
                    self.input_device_combo.addItem(f"🎤 {default_input['name']} (Default)")
            except:
                pass
            
            # Get currently available input devices
            available_devices = []
            for i in range(p.get_device_count()):
                try:
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:  # Input device
                        # Check if device is currently available
                        if device_info['hostApi'] == 0:  # Windows DirectSound
                            device_name = device_info['name']
                            # Filter out virtual devices and duplicates
                            if not any(keyword in device_name.lower() for keyword in 
                                      ['virtual', 'cable', 'loopback', 'stereo mix']):
                                available_devices.append(device_name)
                except:
                    continue
            
            # Add unique available devices
            seen_devices = set()
            for device_name in available_devices:
                if device_name not in seen_devices:
                    self.input_device_combo.addItem(f"🎤 {device_name}")
                    seen_devices.add(device_name)
            
            p.terminate()
            
        except Exception as e:
            print(f"Error populating input devices: {e}")
            self.input_device_combo.addItem("Default Microphone")
    
    def populate_output_devices(self):
        """Populate output device dropdown with currently available speakers"""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            self.output_device_combo.clear()
            self.output_device_combo.addItem("Default Speakers")
            
            # Get default output device
            try:
                default_output = p.get_default_output_device_info()
                if default_output:
                    self.output_device_combo.addItem(f"🔊 {default_output['name']} (Default)")
            except:
                pass
            
            # Get currently available output devices
            available_devices = []
            for i in range(p.get_device_count()):
                try:
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxOutputChannels'] > 0:  # Output device
                        # Check if device is currently available
                        if device_info['hostApi'] == 0:  # Windows DirectSound
                            device_name = device_info['name']
                            # Filter out virtual devices and duplicates
                            if not any(keyword in device_name.lower() for keyword in 
                                      ['virtual', 'cable', 'loopback', 'stereo mix']):
                                available_devices.append(device_name)
                except:
                    continue
            
            # Add unique available devices
            seen_devices = set()
            for device_name in available_devices:
                if device_name not in seen_devices:
                    self.output_device_combo.addItem(f"🔊 {device_name}")
                    seen_devices.add(device_name)
            
            p.terminate()
            
        except Exception as e:
            print(f"Error populating output devices: {e}")
            self.output_device_combo.addItem("Default Speakers")

class ModernIntegratedScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.heartbeat_animation = None
        self.is_responding = False
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Main horizontal layout with chat on left, main interface on right
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create pitch black background
        self.setStyleSheet("""
            QWidget {
                background: #000000;
            }
        """)
        
        # Left side - Chat Panel (40% width) - Enhanced design
        chat_panel = QWidget()
        chat_panel.setFixedWidth(int(screen_width * 0.40))
        chat_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-right: 3px solid #0ea5e9;
            }
        """)
        
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(20, 20, 20, 20)
        chat_layout.setSpacing(20)
        
        # Enhanced chat title with larger font
        chat_title = QLabel("💬 Chat History")
        chat_title.setStyleSheet("""
            QLabel {
                color: #0ea5e9;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
                background: rgba(14, 165, 233, 0.15);
                border-radius: 15px;
                border: 2px solid rgba(14, 165, 233, 0.4);
            }
        """)
        chat_layout.addWidget(chat_title)
        
        # Enhanced chat text area with larger fonts and better styling
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                border: 2px solid #0ea5e9;
                border-radius: 20px;
                padding: 20px;
                selection-background-color: #0ea5e9;
            }
            QTextEdit QScrollBar:vertical {
                background: #0f172a;
                width: 14px;
                border-radius: 7px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #0ea5e9;
                border-radius: 7px;
                min-height: 30px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: #38bdf8;
            }
        """)
        chat_layout.addWidget(self.chat_text_edit)
        
        # Enhanced device selection section with refresh button
        device_layout = QVBoxLayout()
        device_layout.setSpacing(15)
        
        # Device section header with refresh button
        device_header_layout = QHBoxLayout()
        
        device_header_label = QLabel("🎛️ Audio Devices")
        device_header_label.setStyleSheet("""
            QLabel {
                color: #0ea5e9;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: bold;
            }
        """)
        device_header_layout.addWidget(device_header_label)
        
        # Refresh devices button
        self.refresh_devices_btn = QPushButton("🔄 Refresh")
        self.refresh_devices_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6366f1, stop:1 #4f46e5);
                border: 2px solid #6366f1;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #818cf8, stop:1 #6366f1);
                border: 2px solid #818cf8;}
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4f46e5, stop:1 #3730a3);}
        """)
        self.refresh_devices_btn.clicked.connect(self.refresh_devices)
        device_header_layout.addWidget(self.refresh_devices_btn)
        device_header_layout.addStretch(1)
        
        device_layout.addLayout(device_header_layout)
        
        # Input device dropdown with larger font
        input_label = QLabel("🎤 Input Device:")
        input_label.setStyleSheet("""
            QLabel {
                color: #0ea5e9;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        device_layout.addWidget(input_label)
        
        self.input_device_combo = QComboBox()
        self.input_device_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                border: 2px solid #0ea5e9;
                border-radius: 12px;
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                padding: 12px 16px;
                min-width: 250px;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #0ea5e9;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: #0f172a;
                border: 2px solid #0ea5e9;
                border-radius: 12px;
                color: #e2e8f0;
                selection-background-color: #0ea5e9;
                font-size: 16px;
            }
            QComboBox:hover {
                border: 2px solid #38bdf8;}
        """)
        self.populate_input_devices()
        device_layout.addWidget(self.input_device_combo)
        
        # Output device dropdown with larger font
        output_label = QLabel("🔊 Output Device:")
        output_label.setStyleSheet("""
            QLabel {
                color: #0ea5e9;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        device_layout.addWidget(output_label)
        
        self.output_device_combo = QComboBox()
        self.output_device_combo.setStyleSheet("""
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1e293b, stop:1 #0f172a);
                border: 2px solid #0ea5e9;
                border-radius: 12px;
                color: #e2e8f0;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                padding: 12px 16px;
                min-width: 250px;
            }
            QComboBox::drop-down {
                border: none;
                width: 25px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 6px solid transparent;
                border-right: 6px solid transparent;
                border-top: 6px solid #0ea5e9;
                margin-right: 8px;
            }
            QComboBox QAbstractItemView {
                background: #0f172a;
                border: 2px solid #0ea5e9;
                border-radius: 12px;
                color: #e2e8f0;
                selection-background-color: #0ea5e9;
                font-size: 16px;
            }
            QComboBox:hover {
                border: 2px solid #38bdf8;}
        """)
        self.populate_output_devices()
        device_layout.addWidget(self.output_device_combo)
        
        chat_layout.addLayout(device_layout)
        
        # Right side - Main Interface (60% width)
        main_interface = QWidget()
        main_interface.setStyleSheet("""
            QWidget {
                background: #000000;
            }
        """)
        main_interface_layout = QVBoxLayout(main_interface)
        main_interface_layout.setContentsMargins(0, 0, 0, 0)
        main_interface_layout.setSpacing(0)
        
        # Create animated background with GIF and heartbeat effect
        self.background_label = QLabel()
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.setStyleSheet("background: transparent;")
        
        # Load and display the 7ZN3.gif as background
        try:
            gif_path = GraphicsDirectoryPath("7ZN3.gif")
            if os.path.exists(gif_path):
                self.movie = QMovie(gif_path)
                self.movie.setScaledSize(QSize(450, 450))  # Larger size
                self.background_label.setMovie(self.movie)
                self.movie.start()
        except Exception as e:
            print(f"Error loading background GIF: {e}")
        
        # Enhanced status label with larger font
        self.status_label = QLabel("Ready to assist you...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #0ea5e9;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 22px;
                font-weight: 300;
                margin: 25px;
                padding: 15px;
                background: rgba(14, 165, 233, 0.15);
                border-radius: 15px;
                border: 1px solid rgba(14, 165, 233, 0.4);
            }
        """)
        
        # Enhanced microphone button with animations
        self.mic_button = QPushButton()
        self.mic_button.setFixedSize(140, 140)  # Larger button
        self.mic_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0ea5e9, stop:1 #0284c7);
                border: none;
                border-radius: 70px;
                color: white;
                font-size: 32px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #38bdf8, stop:1 #0ea5e9);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0284c7, stop:1 #0ea5e9);
            }
        """)
        self.mic_button.setText("🎤")
        self.mic_button.clicked.connect(self.toggle_mic)
        
        # Enhanced drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(14, 165, 233, 100))
        shadow.setOffset(0, 8)
        self.mic_button.setGraphicsEffect(shadow)
        
        self.mic_active = False
        self.update_mic_button()
        
        # Enhanced control buttons row with animations
        button_layout = QHBoxLayout()
        button_layout.setSpacing(25)
        button_layout.setAlignment(Qt.AlignCenter)
        
        # Enhanced reset button with animations
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ef4444, stop:1 #dc2626);
                border: 2px solid #ef4444;
                border-radius: 15px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 25px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f87171, stop:1 #ef4444);
                border: 2px solid #f87171;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #dc2626, stop:1 #b91c1c);
            }
        """)
        self.reset_button.clicked.connect(self.reset_assistant)
        
        # Enhanced clear chat button with animations
        self.clear_chat_button = QPushButton("🗑️ Clear")
        self.clear_chat_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f59e0b, stop:1 #d97706);
                border: 2px solid #f59e0b;
                border-radius: 15px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 25px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fbbf24, stop:1 #f59e0b);
                border: 2px solid #fbbf24;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #d97706, stop:1 #b45309);
            }
        """)
        self.clear_chat_button.clicked.connect(self.clear_chat)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.clear_chat_button)
        
        # Chat button placeholder - will be replaced by actual button
        self.chat_button_placeholder = QWidget()
        self.chat_button_placeholder.setFixedHeight(80)
        
        # Layout setup for main interface
        main_interface_layout.addStretch(1)
        main_interface_layout.addWidget(self.background_label, alignment=Qt.AlignCenter)
        main_interface_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        main_interface_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        main_interface_layout.addLayout(button_layout)
        main_interface_layout.addWidget(self.chat_button_placeholder, alignment=Qt.AlignCenter)
        main_interface_layout.addStretch(1)
        
        # Add both panels to main layout
        main_layout.addWidget(chat_panel)
        main_layout.addWidget(main_interface)
        
        # Set default text color
        text_color = QColor("#ffffff")
        text_color_text = QTextCharFormat()
        text_color_text.setForeground(text_color)
        self.chat_text_edit.setCurrentCharFormat(text_color_text)
        
        # Timer for chat updates - ultra fast updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loadMessage)
        self.timer.start(25)  # Ultra fast updates
        
        # Timer for checking AI response status
        self.response_timer = QTimer(self)
        self.response_timer.timeout.connect(self.check_ai_response)
        self.response_timer.start(100)  # Check every 100ms
        
        # Initialize assistant state
        self.initialize_assistant_state()
        
        self.last_processed_message = ""
        
    def add_chat_button(self, chat_button):
        """Add chat button to the main interface"""
        # Replace the placeholder with the actual chat button
        if hasattr(self, 'chat_button_placeholder'):
            # Remove placeholder from layout
            layout = self.chat_button_placeholder.parent().layout()
            layout.removeWidget(self.chat_button_placeholder)
            self.chat_button_placeholder.deleteLater()
            
            # Add the chat button
            layout.addWidget(chat_button, alignment=Qt.AlignCenter)
    
    def initialize_assistant_state(self):
        """Initialize the assistant to proper listening state"""
        try:
            # Set initial microphone state
            self.mic_active = True
            SetMicrophoneStatus("True")
            SetAssistantStatus("Listening...")
            
            # Initialize response detection state
            self.is_responding = False
            self.last_mp3_time = None
            self.last_mp3_size = None
            
            # Update UI to show listening state
            self.status_label.setText("🎧 Listening...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #0ea5e9;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 22px;
                    font-weight: 300;
                    margin: 25px;
                    padding: 15px;
                    background: rgba(14, 165, 233, 0.15);
                    border-radius: 15px;
                    border: 1px solid rgba(14, 165, 233, 0.4);
                }
            """)
            
            # Update microphone button
            self.mic_button.setText("🎤")
            self.update_mic_button()
            
            # Clear any existing status files and ensure listening state
            with open(TempDirectoryPath('Status.data'), "w", encoding='utf-8') as file:
                file.write("Listening...")
            
            # Stop any existing heartbeat effect
            if hasattr(self, 'heartbeat_animation') and self.heartbeat_animation:
                self.heartbeat_animation.stop()
            
        except Exception as e:
            print(f"Error initializing assistant state: {e}")
        
    def check_ai_response(self):
        """Improved AI response detection - only trigger when actually processing"""
        try:
            # Skip detection for first few seconds after startup
            if not hasattr(self, 'startup_time'):
                self.startup_time = time.time()
            
            # Don't detect AI responses for first 5 seconds after startup
            if time.time() - self.startup_time < 5:
                return
            
            # Check if assistant is actually processing (not just listening)
            current_status = GetAssistantStatus()
            
            # Only trigger AI response animation if status indicates processing
            processing_statuses = ["Processing...", "Searching...", "Executing...", "Answering..."]
            
            if current_status in processing_statuses and self.mic_active and not self.is_responding:
                self.start_heartbeat_effect()
                self.is_responding = True
            elif current_status == "Ready" or current_status == "Listening...":
                # Stop the animation when not processing
                if self.is_responding:
                    self.stop_heartbeat_effect()
                    self.is_responding = False
                
        except Exception as e:
            pass
    
    def start_heartbeat_effect(self):
        """Start the heartbeat animation for the GIF"""
        # Don't start heartbeat if we're not actually listening
        if not self.mic_active:
            return
            
        if not hasattr(self, 'heartbeat_animation') or not self.heartbeat_animation:
            # Create a more sophisticated heartbeat animation
            self.heartbeat_animation = QPropertyAnimation(self.background_label, b"geometry")
            self.heartbeat_animation.setDuration(800)  # 800ms for one heartbeat cycle
            self.heartbeat_animation.setLoopCount(-1)  # Infinite loop
            
            # Get current geometry
            current_geometry = self.background_label.geometry()
            
            # Create a more realistic heartbeat effect (double beat)
            # First beat: scale up to 115%
            first_beat_width = int(current_geometry.width() * 1.15)
            first_beat_height = int(current_geometry.height() * 1.15)
            x_offset_1 = (first_beat_width - current_geometry.width()) // 2
            y_offset_1 = (first_beat_height - current_geometry.height()) // 2
            
            first_beat_geometry = QRect(
                current_geometry.x() - x_offset_1,
                current_geometry.y() - y_offset_1,
                first_beat_width,
                first_beat_height
            )
            
            # Second beat: scale up to 120%
            second_beat_width = int(current_geometry.width() * 1.20)
            second_beat_height = int(current_geometry.height() * 1.20)
            x_offset_2 = (second_beat_width - current_geometry.width()) // 2
            y_offset_2 = (second_beat_height - current_geometry.height()) // 2
            
            second_beat_geometry = QRect(
                current_geometry.x() - x_offset_2,
                current_geometry.y() - y_offset_2,
                second_beat_width,
                second_beat_height
            )
            
            # Create keyframe animation for realistic heartbeat
            self.heartbeat_animation.setStartValue(current_geometry)
            self.heartbeat_animation.setKeyValueAt(0.3, first_beat_geometry)  # First beat
            self.heartbeat_animation.setKeyValueAt(0.5, current_geometry)     # Return to normal
            self.heartbeat_animation.setKeyValueAt(0.7, second_beat_geometry) # Second beat
            self.heartbeat_animation.setEndValue(current_geometry)           # Return to normal
            
            # Use a more natural easing curve
            self.heartbeat_animation.setEasingCurve(QEasingCurve.OutBounce)
            self.heartbeat_animation.start()
            
            # Add pulsing glow effect to the status label
            self.status_label.setText("🤖 AI is responding...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #10b981;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 22px;
                    font-weight: 300;
                    margin: 25px;
                    padding: 15px;
                    background: rgba(16, 185, 129, 0.2);
                    border-radius: 15px;
                    border: 2px solid rgba(16, 185, 129, 0.6);
                    /* Pulsing effect handled by PyQt5 animations */
                }
            """)
            
            # Add pulsing effect to microphone button
            if hasattr(self, 'mic_button'):
                self.mic_button.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #10b981, stop:1 #059669);
                        border: none;
                        border-radius: 70px;
                        color: white;
                        font-size: 32px;
                        font-weight: bold;
                        /* Pulsing effect handled by PyQt5 animations */
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #34d399, stop:1 #10b981);}
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #059669, stop:1 #047857);}
                """)
    
    def stop_heartbeat_effect(self):
        """Stop the heartbeat animation and reset all effects"""
        if self.heartbeat_animation:
            self.heartbeat_animation.stop()
            self.heartbeat_animation = None
            
            # Reset GIF to original size
            if hasattr(self, 'movie'):
                self.background_label.setMovie(self.movie)
            
            # Update status
            self.status_label.setText("Ready to assist you...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #0ea5e9;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 22px;
                    font-weight: 300;
                    margin: 25px;
                    padding: 15px;
                    background: rgba(14, 165, 233, 0.15);
                    border-radius: 15px;
                    border: 1px solid rgba(14, 165, 233, 0.4);
                }
            """)
            
            # Reset microphone button to normal state
            if hasattr(self, 'mic_button'):
                if self.mic_active:
                    self.mic_button.setStyleSheet("""
                        QPushButton {
                            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #10b981, stop:1 #059669);
                            border: none;
                            border-radius: 70px;
                            color: white;
                            font-size: 32px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #34d399, stop:1 #10b981);}
                        QPushButton:pressed {
                            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #059669, stop:1 #047857);}
                    """)
                else:
                    self.mic_button.setStyleSheet("""
                        QPushButton {
                            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #ef4444, stop:1 #dc2626);
                            border: none;
                            border-radius: 70px;
                            color: white;
                            font-size: 32px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #f87171, stop:1 #ef4444);}
                        QPushButton:pressed {
                            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                stop:0 #dc2626, stop:1 #b91c1c);}
                    """)
    
    def loadMessage(self):
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                messages = file.read()
                
            if messages != self.last_processed_message and messages.strip():
                # Clear the chat and display all messages to maintain history
                self.chat_text_edit.clear()
                
                lines = messages.split('\n')
                new_lines = []
                
                for line in lines:
                    if line.strip():
                        if ":" in line:
                            parts = line.split(":", 1)
                            if len(parts) == 2:
                                speaker = parts[0].strip()
                                message = parts[1].strip()
                                
                                if "Sunil" in speaker or "User" in speaker:
                                    new_lines.append(f"👤 {message}")
                                else:
                                    new_lines.append(f"🤖 {message}")
                        else:
                            new_lines.append(line)
                
                # Display all messages with proper colors
                for line in new_lines:
                    if "👤" in line:
                        self.addMessages(line, "#0ea5e9")  # Blue for user
                    elif "🤖" in line:
                        self.addMessages(line, "#10b981")  # Green for AI
                    else:
                        self.addMessages(line, "#e2e8f0")  # White for other
                
                # Update the last processed message
                self.last_processed_message = messages
                            
        except Exception as e:
            print(f"Error loading messages: {e}")
        
    def addMessages(self, message, color):
        cursor = self.chat_text_edit.textCursor()
        cursor.movePosition(QTextCursor.End)
        
        format = QTextCharFormat()
        format.setForeground(QColor(color))
        format.setFontWeight(QFont.Bold if color == "#0ea5e9" else QFont.Normal)
        
        formatm = QTextBlockFormat()
        formatm.setLineHeight(150, QTextBlockFormat.ProportionalHeight)
        formatm.setTopMargin(10)
        formatm.setBottomMargin(10)
        
        cursor.setCharFormat(format)
        cursor.setBlockFormat(formatm)
        cursor.insertText(message + "\n")
        self.chat_text_edit.setTextCursor(cursor)
        
        # Auto-scroll to bottom to show latest messages
        self.chat_text_edit.verticalScrollBar().setValue(
            self.chat_text_edit.verticalScrollBar().maximum()
        )
    
    def reset_assistant(self):
        """Reset the assistant to listening state and clear any ongoing operations"""
        try:
            # Set microphone to listening state
            SetMicrophoneStatus("True")
            SetAssistantStatus("Listening...")
            
            # Clear any ongoing operations by writing empty status
            with open(TempDirectoryPath('Status.data'), "w", encoding='utf-8') as file:
                file.write("Listening...")
            
            # Update UI
            self.status_label.setText("Listening...")
            
            print("🔄 Assistant reset to listening state")
            
        except Exception as e:
            print(f"Error resetting assistant: {e}")
    
    def clear_chat(self):
        """Clear the chat history"""
        try:
            # Clear the chat display
            self.chat_text_edit.clear()
            
            # Clear the chat data file
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write("")
            
            print("🗑️ Chat history cleared")
            
        except Exception as e:
            print(f"Error clearing chat: {e}")
    
    def populate_input_devices(self):
        """Populate input device dropdown with currently available microphones"""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            self.input_device_combo.clear()
            self.input_device_combo.addItem("Default Microphone")
            
            # Get default input device
            try:
                default_input = p.get_default_input_device_info()
                if default_input:
                    self.input_device_combo.addItem(f"🎤 {default_input['name']} (Default)")
            except:
                pass
            
            # Get currently available input devices
            available_devices = []
            for i in range(p.get_device_count()):
                try:
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxInputChannels'] > 0:  # Input device
                        # Check if device is currently available
                        if device_info['hostApi'] == 0:  # Windows DirectSound
                            device_name = device_info['name']
                            # Filter out virtual devices and duplicates
                            if not any(keyword in device_name.lower() for keyword in 
                                      ['virtual', 'cable', 'loopback', 'stereo mix']):
                                available_devices.append(device_name)
                except:
                    continue
            
            # Add unique available devices
            seen_devices = set()
            for device_name in available_devices:
                if device_name not in seen_devices:
                    self.input_device_combo.addItem(f"🎤 {device_name}")
                    seen_devices.add(device_name)
            
            p.terminate()
            
        except Exception as e:
            print(f"Error populating input devices: {e}")
            self.input_device_combo.addItem("Default Microphone")
    
    def populate_output_devices(self):
        """Populate output device dropdown with currently available speakers"""
        try:
            import pyaudio
            p = pyaudio.PyAudio()
            
            self.output_device_combo.clear()
            self.output_device_combo.addItem("Default Speakers")
            
            # Get default output device
            try:
                default_output = p.get_default_output_device_info()
                if default_output:
                    self.output_device_combo.addItem(f"🔊 {default_output['name']} (Default)")
            except:
                pass
            
            # Get currently available output devices
            available_devices = []
            for i in range(p.get_device_count()):
                try:
                    device_info = p.get_device_info_by_index(i)
                    if device_info['maxOutputChannels'] > 0:  # Output device
                        # Check if device is currently available
                        if device_info['hostApi'] == 0:  # Windows DirectSound
                            device_name = device_info['name']
                            # Filter out virtual devices and duplicates
                            if not any(keyword in device_name.lower() for keyword in 
                                      ['virtual', 'cable', 'loopback', 'stereo mix']):
                                available_devices.append(device_name)
                except:
                    continue
            
            # Add unique available devices
            seen_devices = set()
            for device_name in available_devices:
                if device_name not in seen_devices:
                    self.output_device_combo.addItem(f"🔊 {device_name}")
                    seen_devices.add(device_name)
            
            p.terminate()
            
        except Exception as e:
            print(f"Error populating output devices: {e}")
            self.output_device_combo.addItem("Default Speakers")
    
    def refresh_devices(self):
        """Refresh the device dropdowns with currently available devices"""
        try:
            print("🔄 Refreshing audio devices...")
            
            # Add a brief animation to the refresh button
            self.refresh_devices_btn.setText("⏳ Refreshing...")
            self.refresh_devices_btn.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f59e0b, stop:1 #d97706);
                    border: 2px solid #f59e0b;
                    border-radius: 8px;
                    color: white;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 8px 12px;
                    min-width: 80px;
                }
            """)
            
            # Refresh both dropdowns
            self.populate_input_devices()
            self.populate_output_devices()
            
            # Reset button after a short delay
            QTimer.singleShot(1000, self.reset_refresh_button)
            
        except Exception as e:
            print(f"Error refreshing devices: {e}")
            self.reset_refresh_button()
    
    def reset_refresh_button(self):
        """Reset the refresh button to normal state"""
        self.refresh_devices_btn.setText("🔄 Refresh")
        self.refresh_devices_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6366f1, stop:1 #4f46e5);
                border: 2px solid #6366f1;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #818cf8, stop:1 #6366f1);
                border: 2px solid #818cf8;}
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4f46e5, stop:1 #3730a3);}
        """)
            
    def toggle_mic(self):
        """Toggle microphone on/off with improved state management"""
        try:
            if self.mic_active:
                # Turn off microphone
                SetMicrophoneStatus("False")
                self.mic_active = False
                self.mic_button.setText("🔇")
                self.status_label.setText("🔇 Microphone OFF")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #ef4444;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        font-size: 22px;
                        font-weight: 300;
                        margin: 25px;
                        padding: 15px;
                        background: rgba(239, 68, 68, 0.15);
                        border-radius: 15px;
                        border: 1px solid rgba(239, 68, 68, 0.4);
                    }
                """)
                print("🎤 Microphone turned OFF")
            else:
                # Turn on microphone
                SetMicrophoneStatus("True")
                self.mic_active = True
                self.mic_button.setText("🎤")
                self.status_label.setText("🎧 Listening...")
                self.status_label.setStyleSheet("""
                    QLabel {
                        color: #0ea5e9;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        font-size: 22px;
                        font-weight: 300;
                        margin: 25px;
                        padding: 15px;
                        background: rgba(14, 165, 233, 0.15);
                        border-radius: 15px;
                        border: 1px solid rgba(14, 165, 233, 0.4);
                    }
                """)
                print("🎤 Microphone turned ON")
            
            self.update_mic_button()
            
        except Exception as e:
            print(f"Error toggling microphone: {e}")
    
    def update_mic_button(self):
        """Update microphone button appearance based on status with enhanced animations"""
        try:
            if self.mic_active:
                self.mic_button.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #10b981, stop:1 #059669);
                        border: none;
                        border-radius: 70px;
                        color: white;
                        font-size: 32px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #34d399, stop:1 #10b981);}
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #059669, stop:1 #047857);}
                """)
                self.mic_button.setText("⏹️")
            else:
                self.mic_button.setStyleSheet("""
                    QPushButton {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #ef4444, stop:1 #dc2626);
                        border: none;
                        border-radius: 70px;
                        color: white;
                        font-size: 32px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #f87171, stop:1 #ef4444);}
                    QPushButton:pressed {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                            stop:0 #dc2626, stop:1 #b91c1c);}
                """)
                self.mic_button.setText("🎤")
        except Exception as e:
            print(f"Error updating mic button: {e}")

class ModernInitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Main horizontal layout with chat on left, main interface on right
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create pitch black background
        self.setStyleSheet("""
            QWidget {
                background: #000000;
            }
        """)
        
        # Left side - Chat Panel (35% width) - Restored original design
        chat_panel = QWidget()
        chat_panel.setFixedWidth(int(screen_width * 0.35))
        chat_panel.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-right: 3px solid #4a90e2;
            }
        """)
        
        chat_layout = QVBoxLayout(chat_panel)
        chat_layout.setContentsMargins(15, 15, 15, 15)
        chat_layout.setSpacing(15)
        
        # Chat title with original styling
        chat_title = QLabel("💬 Chat History")
        chat_title.setStyleSheet("""
            QLabel {
                color: #4a90e2;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 20px;
                font-weight: bold;
                padding: 15px;
                background: rgba(74, 144, 226, 0.1);
                border-radius: 10px;
                border: 2px solid rgba(74, 144, 226, 0.3);
            }
        """)
        chat_layout.addWidget(chat_title)
        
        # Chat text area with original styling and larger fonts
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34495e, stop:1 #2c3e50);
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                border: 2px solid #4a90e2;
                border-radius: 15px;
                padding: 15px;
                selection-background-color: #4a90e2;
            }
            QTextEdit QScrollBar:vertical {
                background: #2c3e50;
                width: 12px;
                border-radius: 6px;
            }
            QTextEdit QScrollBar::handle:vertical {
                background: #4a90e2;
                border-radius: 6px;
                min-height: 20px;
            }
            QTextEdit QScrollBar::handle:vertical:hover {
                background: #5ba0f2;
            }
        """)
        self.chat_text_edit.setReadOnly(True)
        chat_layout.addWidget(self.chat_text_edit)
        
        # Control buttons row
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Reset button with original styling
        self.reset_button = QPushButton("🔄 Reset")
        self.reset_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                border: 2px solid #e74c3c;
                border-radius: 10px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f75c4c, stop:1 #e74c3c);
                border: 2px solid #f75c4c;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c0392b, stop:1 #a93226);
            }
        """)
        self.reset_button.clicked.connect(self.reset_assistant)
        
        # Clear chat button
        self.clear_chat_button = QPushButton("🗑️ Clear")
        self.clear_chat_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f39c12, stop:1 #e67e22);
                border: 2px solid #f39c12;
                border-radius: 10px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
                padding: 12px 20px;
                min-width: 100px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f4ac22, stop:1 #f39c12);
                border: 2px solid #f4ac22;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e67e22, stop:1 #d35400);
            }
        """)
        self.clear_chat_button.clicked.connect(self.clear_chat)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.clear_chat_button)
        chat_layout.addLayout(button_layout)
        
        # Right side - Main Interface (65% width)
        main_interface = QWidget()
        main_interface_layout = QVBoxLayout(main_interface)
        main_interface_layout.setContentsMargins(0, 0, 0, 0)
        main_interface_layout.setSpacing(0)
        
        # AI Assistant Logo/Animation with GIF - Restored original size
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Load and display the 7ZN3.gif animation
        try:
            gif_path = GraphicsDirectoryPath("7ZN3.gif")
            if os.path.exists(gif_path):
                movie = QMovie(gif_path)
                movie.setScaledSize(QSize(400, 400))  # Restored original size
                logo_label.setMovie(movie)
                movie.start()
            else:
                # Fallback to text if GIF not found
                logo_label.setStyleSheet("""
                    QLabel {
                        color: #ffffff;
                        font-family: 'Segoe UI', Arial, sans-serif;
                        font-size: 48px;
                        font-weight: bold;
                        margin: 40px;
                    }
                """)
                logo_label.setText("🤖  AI")
        except Exception as e:
            print(f"Error loading GIF: {e}")
            # Fallback to text
            logo_label.setStyleSheet("""
                QLabel {
                    color: #ffffff;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 48px;
                    font-weight: bold;
                    margin: 40px;
                }
            """)
            logo_label.setText("🤖  AI")
        
        # Status label with original styling
        self.status_label = QLabel("Ready to assist you...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                color: #4a90e2;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: 300;
                margin: 20px;
                padding: 10px;
                background: rgba(74, 144, 226, 0.1);
                border-radius: 10px;
                border: 1px solid rgba(74, 144, 226, 0.3);
            }
        """)
        
        # Modern microphone button - Restored original size
        self.mic_button = QPushButton()
        self.mic_button.setFixedSize(120, 120)
        self.mic_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4a90e2, stop:1 #357abd);
                border: none;
                border-radius: 60px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #5ba0f2, stop:1 #4a90e2);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #357abd, stop:1 #2a5f9e);
            }
        """)
        self.mic_button.setText("🎤")
        self.mic_button.clicked.connect(self.toggle_mic)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 80))
        shadow.setOffset(0, 4)
        self.mic_button.setGraphicsEffect(shadow)
        
        self.mic_active = False
        self.last_chat_content = ""
        self.update_mic_button()
        
        # Text input area (ChatGPT style)
        text_input_container = QWidget()
        text_input_container.setFixedHeight(120)
        text_input_container.setStyleSheet("""
            QWidget {
                background: transparent;
                margin: 20px;
            }
        """)
        
        text_input_layout = QVBoxLayout(text_input_container)
        text_input_layout.setContentsMargins(50, 10, 50, 10)
        text_input_layout.setSpacing(10)
        
        # Text input field
        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Type your message here... (Press Enter to send)")
        self.text_input.setStyleSheet("""
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #313244, stop:1 #1e1e2e);
                border: 2px solid #89b4fa;
                border-radius: 15px;
                color: #cdd6f4;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                padding: 15px 20px;
                min-height: 50px;
            }
            QLineEdit:focus {
                border: 2px solid #b4befe;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #45475a, stop:1 #313244);
            }
            QLineEdit::placeholder {
                color: #6c7086;
                font-style: italic;
            }
        """)
        self.text_input.returnPressed.connect(self.send_text_message)
        
        # Send button
        self.send_button = QPushButton("📤 Send")
        self.send_button.setFixedSize(100, 50)
        self.send_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a6e3a1, stop:1 #94e2d5);
                border: 2px solid #a6e3a1;
                border-radius: 15px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b6f3b1, stop:1 #a4f2e5);
                border: 2px solid #b6f3b1;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #94e2d5, stop:1 #a6e3a1);
            }
        """)
        self.send_button.clicked.connect(self.send_text_message)
        
        # Input row with text field and send button
        input_row = QHBoxLayout()
        input_row.addWidget(self.text_input)
        input_row.addWidget(self.send_button)
        input_row.setSpacing(15)
        
        text_input_layout.addLayout(input_row)
        
        # Layout setup for main interface
        main_interface_layout.addStretch(1)
        main_interface_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        main_interface_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        main_interface_layout.addWidget(text_input_container, alignment=Qt.AlignCenter)
        main_interface_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        
        # Chat button will be added here if provided
        self.chat_button_placeholder = QWidget()
        self.chat_button_placeholder.setFixedHeight(80)
        main_interface_layout.addWidget(self.chat_button_placeholder, alignment=Qt.AlignCenter)
        
        main_interface_layout.addStretch(1)
        
        # Add both panels to main layout
        main_layout.addWidget(chat_panel)
        main_layout.addWidget(main_interface)
        
        self.setLayout(main_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        
        # Timer for status updates - ultra fast updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(25)  # Ultra fast updates
        
        # Timer for chat updates
        self.chat_timer = QTimer(self)
        self.chat_timer.timeout.connect(self.update_chat)
        self.chat_timer.start(25)  # Ultra fast updates
        
    def toggle_mic(self):
        self.mic_active = not self.mic_active
        if self.mic_active:
            MicButtonClosed()
        else:
            MicButtonInitialed()
        self.update_mic_button()
        
    def update_mic_button(self):
        if self.mic_active:
            self.mic_button.setText("⏹️")
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e74c3c, stop:1 #c0392b);
                    border: none;
                    border-radius: 60px;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f75c4c, stop:1 #e74c3c);
                }
            """)
        else:
            self.mic_button.setText("🎤")
            self.mic_button.setStyleSheet("""
                QPushButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #4a90e2, stop:1 #357abd);
                    border: none;
                    border-radius: 60px;
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #5ba0f2, stop:1 #4a90e2);
                }
            """)
            
    def reset_assistant(self):
        """Reset the assistant to listening state and clear any ongoing operations"""
        try:
            # Stop any ongoing heartbeat animation
            if hasattr(self, 'heartbeat_animation') and self.heartbeat_animation:
                self.heartbeat_animation.stop()
                self.heartbeat_animation = None
            
            # Reset response state
            self.is_responding = False
            
            # Set microphone to listening state
            SetMicrophoneStatus("True")
            SetAssistantStatus("Listening...")
            
            # Clear any ongoing operations by writing empty status
            with open(TempDirectoryPath('Status.data'), "w", encoding='utf-8') as file:
                file.write("Listening...")
            
            # Update UI
            self.mic_active = True
            self.update_mic_button()
            self.status_label.setText("🎧 Listening...")
            self.status_label.setStyleSheet("""
                QLabel {
                    color: #0ea5e9;
                    font-family: 'Segoe UI', Arial, sans-serif;
                    font-size: 22px;
                    font-weight: 300;
                    margin: 25px;
                    padding: 15px;
                    background: rgba(14, 165, 233, 0.15);
                    border-radius: 15px;
                    border: 1px solid rgba(14, 165, 233, 0.4);
                }
            """)
            
            # Reset background to normal state
            if hasattr(self, 'movie'):
                self.background_label.setMovie(self.movie)
            
            print("🔄 Assistant reset to listening state")
            
        except Exception as e:
            print(f"Error resetting assistant: {e}")
    
    def clear_chat(self):
        """Clear the chat history"""
        try:
            # Clear the chat display
            self.chat_text_edit.clear()
            self.last_chat_content = ""
            
            # Clear the chat data file
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write("")
            
            print("🗑️ Chat history cleared")
            
        except Exception as e:
            print(f"Error clearing chat: {e}")
    
    def send_text_message(self):
        """Handle text message sending from the input field"""
        try:
            # Get the text from input field
            message = self.text_input.text().strip()
            
            if not message:
                return  # Don't send empty messages
            
            # Clear the input field
            self.text_input.clear()
            
            # Update status
            self.status_label.setText("Processing text message...")
            
            # Write the user message to the responses file to show in chat
            current_content = ""
            try:
                with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                    current_content = file.read()
            except:
                pass
            
            # Add user message to chat
            user_message = f"{env_var.get('Username', 'User')} : {message}"
            updated_content = current_content + "\n" + user_message if current_content else user_message
            
            with open(TempDirectoryPath('Responses.data'), "w", encoding='utf-8') as file:
                file.write(updated_content)
            
            # Process the message using the main execution system
            self.process_text_message(message)
            
        except Exception as e:
            print(f"Error sending text message: {e}")
            self.status_label.setText("Error processing message")
    
    def process_text_message(self, message):
        """Process text message using the main execution system"""
        try:
            # Import the main execution function
            from Main import MainExecution
            
            # Create a thread to process the message without blocking UI
            import threading
            
            def process_in_thread():
                try:
                    # Set status
                    SetAssistantStatus("Processing...")
                    
                    # Call the main execution function with text input
                    print(f"📝 Processing text message: {message}")
                    
                    # Use the modified MainExecution function
                    result = MainExecution(use_text_input=True, text_query=message)
                    
                    # Update status
                    if result:
                        SetAssistantStatus("Ready")
                    else:
                        SetAssistantStatus("Error")
                    
                except Exception as e:
                    print(f"Error processing text message in thread: {e}")
                    SetAssistantStatus("Error")
            
            # Start the processing thread
            thread = threading.Thread(target=process_in_thread, daemon=True)
            thread.start()
            
        except Exception as e:
            print(f"Error in process_text_message: {e}")
            self.status_label.setText("Error processing message")
            
    def update_status(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                status = file.read()
                if status.strip():
                    self.status_label.setText(status)
        except:
            pass
    
    def update_chat(self):
        """Update the chat display with latest messages"""
        try:
            with open(TempDirectoryPath('Responses.data'), "r", encoding='utf-8') as file:
                content = file.read()
                if content.strip() and content != self.last_chat_content:
                    # Format the chat content with better styling
                    formatted_content = self.format_chat_content(content)
                    self.chat_text_edit.setHtml(formatted_content)
                    self.last_chat_content = content
                    
                    # Auto-scroll to bottom
                    self.chat_text_edit.verticalScrollBar().setValue(
                        self.chat_text_edit.verticalScrollBar().maximum()
                    )
        except Exception as e:
            print(f"Error updating chat: {e}")
    
    def format_chat_content(self, content):
        """Format chat content with HTML styling"""
        try:
            lines = content.split('\n')
            formatted_lines = []
            
            for line in lines:
                if line.strip():
                    if line.startswith(f"{env_var.get('Username', 'User')} :"):
                        # User message styling
                        formatted_lines.append(f'<p style="margin: 5px 0; padding: 8px; background: rgba(74, 144, 226, 0.1); border-radius: 8px; border-left: 3px solid #4a90e2;"><span style="color: #4a90e2; font-weight: bold;">{line}</span></p>')
                    elif line.startswith(f"{env_var.get('AssistantName', 'AI')} :"):
                        # Assistant message styling
                        formatted_lines.append(f'<p style="margin: 5px 0; padding: 8px; background: rgba(46, 204, 113, 0.1); border-radius: 8px; border-left: 3px solid #2ecc71;"><span style="color: #2ecc71; font-weight: bold;">{line}</span></p>')
                    else:
                        # Regular message styling
                        formatted_lines.append(f'<p style="margin: 3px 0; color: #ffffff;">{line}</p>')
            
            return '<br>'.join(formatted_lines)
        except Exception as e:
            print(f"Error formatting chat content: {e}")
            return content

class ModernMessagesScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Modern chat section
        self.chat_section = ModernChatSection()
        layout.addWidget(self.chat_section)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            QWidget {
                background: #000000;
            }
        """)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        
        # Timer for chat updates - ultra fast updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.chat_section.SpeechRecogText)
        self.timer.start(25)  # Ultra fast updates

class ModernTopBar(QWidget):
    def __init__(self, parent, stacked_widget):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.initUI()
        
    def initUI(self):
        self.setFixedHeight(70)  # Increased height
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border-bottom: 3px solid #0ea5e9;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(25, 15, 25, 15)
        layout.setSpacing(20)
        
        # Enhanced title with larger font
        title_label = QLabel(f"🤖  OSAIMA")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 24px;
                font-weight: bold;

            }
        """)
        
        # Enhanced window control buttons
        minimize_btn = self.create_control_button("─", self.minimize_window)
        maximize_btn = self.create_control_button("□", self.maximize_window)
        close_btn = self.create_control_button("✕", self.close_window, "#ef4444")
        
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(minimize_btn)
        layout.addWidget(maximize_btn)
        layout.addWidget(close_btn)
        
        # Dragging functionality
        self.draggable = True
        self.offset = None
        
    def create_nav_button(self, text, index):
        button = QPushButton(text)
        button.setStyleSheet("""
            QPushButton {
                background: rgba(74, 144, 226, 0.2);
                border: 1px solid rgba(74, 144, 226, 0.5);
                border-radius: 8px;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: 500;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: rgba(74, 144, 226, 0.4);
                border: 1px solid rgba(74, 144, 226, 0.8);
            }
            QPushButton:pressed {
                background: rgba(74, 144, 226, 0.6);
            }
        """)
        button.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(index))
        return button
        
    def create_control_button(self, text, callback, color="#0ea5e9"):
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                border: none;
                border-radius: 8px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                padding: 8px 16px;
                min-width: 35px;
            }}
            QPushButton:hover {{
                background: {color.replace('e9', 'f8') if 'e9' in color else color.replace('44', '55')};}}
            QPushButton:pressed {{}}
        """)
        button.clicked.connect(callback)
        return button
        
    def minimize_window(self):
        self.parent().showMinimized()
        
    def maximize_window(self):
        if self.parent().isMaximized():
            self.parent().showNormal()
        else:
            self.parent().showMaximized()
            
    def close_window(self):
        self.parent().close()
        
    def mousePressEvent(self, event):
        if self.draggable:
            self.offset = event.pos()
            
    def mouseMoveEvent(self, event):
        if self.draggable and self.offset:
            new_pos = event.globalPos() - self.offset
            self.parent().move(new_pos)

class ModernMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Set window properties with enhanced styling
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("""
            QMainWindow {
                background: #000000;
                border: 2px solid #0ea5e9;
                border-radius: 10px;
            }
        """)
        
        # Create stacked widget for multiple screens
        self.stacked_widget = QStackedWidget()
        
        # Create integrated main screen
        self.main_screen = ModernIntegratedScreen()
        
        # Create chat screen
        self.chat_screen = ChatScreen()
        
        # Add screens to stacked widget
        self.stacked_widget.addWidget(self.main_screen)
        self.stacked_widget.addWidget(self.chat_screen)
        
        # Create modern top bar with stacked widget reference
        self.top_bar = ModernTopBar(self, self.stacked_widget)
        self.setMenuWidget(self.top_bar)
        self.setCentralWidget(self.stacked_widget)
        
        # Add chat button to main screen
        self.add_chat_button_to_main_screen()
        
    def add_chat_button_to_main_screen(self):
        """Add a chat button to the main screen"""
        # Create chat button
        chat_button = QPushButton("💬 Chat")
        chat_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #8b5cf6, stop:1 #7c3aed);
                border: 2px solid #8b5cf6;
                border-radius: 15px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                font-weight: bold;
                padding: 15px 30px;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #a78bfa, stop:1 #8b5cf6);
                border: 2px solid #a78bfa;
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #7c3aed, stop:1 #6d28d9);
            }
        """)
        chat_button.clicked.connect(self.show_chat_screen)
        
        # Add button to main screen (you'll need to modify ModernIntegratedScreen to accept this)
        if hasattr(self.main_screen, 'add_chat_button'):
            self.main_screen.add_chat_button(chat_button)
        
    def show_chat_screen(self):
        """Switch to chat screen"""
        self.stacked_widget.setCurrentIndex(1)
        
    def show_main_interface(self):
        """Switch to main interface"""
        self.stacked_widget.setCurrentIndex(0)

def ModernGraphicalUserInterface():
    app = QApplication(sys.argv)
    
    # Set application-wide font with larger size
    font = QFont("Segoe UI", 11)
    app.setFont(font)
    
    # Add error handling for GUI
    def handle_exception(exc_type, exc_value, exc_traceback):
        print(f"⚠️ GUI Error: {exc_type.__name__}: {exc_value}")
        import traceback
        traceback.print_exception(exc_type, exc_value, exc_traceback)
    
    # Set up exception handler
    sys.excepthook = handle_exception
    
    window = ModernMainWindow()
    window.show()
    
    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"⚠️ GUI execution error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    ModernGraphicalUserInterface() 