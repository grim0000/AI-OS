from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QStackedWidget, 
                             QWidget, QLineEdit, QGridLayout, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QFrame, QSizePolicy, QGraphicsDropShadowEffect)
from PyQt5.QtGui import (QIcon, QFont, QColor, QPainter, QMovie, QTextCharFormat, 
                         QPixmap, QTextBlockFormat, QTextCursor, QLinearGradient, QPalette)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QEasingCurve, QRect
from dotenv import dotenv_values
import sys
import os

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

class ModernChatSection(QWidget):
    def __init__(self):
        super(ModernChatSection, self).__init__()
        self.initUI()
        
    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        # Create animated background with GIF
        self.background_label = QLabel()
        self.background_label.setAlignment(Qt.AlignCenter)
        self.background_label.setStyleSheet("background: transparent;")
        
        # Load and display the 7ZN3.gif as background
        try:
            gif_path = GraphicsDirectoryPath("7ZN3.gif")
            if os.path.exists(gif_path):
                movie = QMovie(gif_path)
                movie.setScaledSize(QSize(400, 300))  # Scale the GIF for background
                self.background_label.setMovie(movie)
                movie.start()
        except Exception as e:
            print(f"Error loading background GIF: {e}")
        
        # Modern chat text edit with gradient background
        self.chat_text_edit = QTextEdit()
        self.chat_text_edit.setReadOnly(True)
        self.chat_text_edit.setTextInteractionFlags(Qt.NoTextInteraction)
        self.chat_text_edit.setFrameStyle(QFrame.NoFrame)
        
        # Apply modern styling
        self.chat_text_edit.setStyleSheet("""
            QTextEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #1a1a2e, stop:1 #16213e);
                border: none;
                border-radius: 15px;
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                padding: 20px;
                selection-background-color: #4a90e2;
            }
        """)
        
        # Add background and chat text edit
        layout.addWidget(self.background_label)
        layout.addWidget(self.chat_text_edit)
        self.setStyleSheet("background: transparent;")
        layout.setSizeConstraint(QVBoxLayout.SetDefaultConstraint)
        layout.setStretch(1, 1)
        self.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding))
        
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
                # Don't clear the chat, just append new messages
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
                
                # Only add new messages that aren't already displayed - optimized
                current_text = self.chat_text_edit.toPlainText()
                added_count = 0
                for line in new_lines:
                    if line not in current_text and added_count < 10:  # Limit to prevent lag
                        if "👤" in line:
                            self.addMessages(line, "#4a90e2")
                        elif "🤖" in line:
                            self.addMessages(line, "#50c878")
                        else:
                            self.addMessages(line, "#ffffff")
                        added_count += 1
                
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

class ModernInitialScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.initUI()
        
    def initUI(self):
        desktop = QApplication.desktop()
        screen_width = desktop.screenGeometry().width()
        screen_height = desktop.screenGeometry().height()
        
        # Main layout with gradient background
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create pitch black background
        self.setStyleSheet("""
            QWidget {
                background: #000000;
            }
        """)
        
        # AI Assistant Logo/Animation with GIF
        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        
        # Load and display the 7ZN3.gif animation
        try:
            gif_path = GraphicsDirectoryPath("7ZN3.gif")
            if os.path.exists(gif_path):
                movie = QMovie(gif_path)
                movie.setScaledSize(QSize(400, 400))  # Enlarged GIF
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
        
        # Status label with modern styling
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
        
        # Modern microphone button
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
        self.update_mic_button()
        
        # Layout setup
        main_layout.addStretch(1)
        main_layout.addWidget(logo_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.status_label, alignment=Qt.AlignCenter)
        main_layout.addWidget(self.mic_button, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)
        
        self.setLayout(main_layout)
        self.setFixedHeight(screen_height)
        self.setFixedWidth(screen_width)
        
        # Timer for status updates - ultra fast updates
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_status)
        self.timer.start(25)  # Ultra fast updates
        
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
            
    def update_status(self):
        try:
            with open(TempDirectoryPath('Status.data'), "r", encoding='utf-8') as file:
                status = file.read()
                if status.strip():
                    self.status_label.setText(status)
        except:
            pass

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
        self.setFixedHeight(60)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2c3e50, stop:1 #34495e);
                border-bottom: 2px solid #4a90e2;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)
        layout.setSpacing(15)
        
        # Title with modern styling
        title_label = QLabel(f"🤖  AI Assistant")
        title_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        # Modern navigation buttons
        home_button = self.create_nav_button("🏠 Home", 0)
        chat_button = self.create_nav_button("💬 Chat", 1)
        
        # Window control buttons
        minimize_btn = self.create_control_button("─", self.minimize_window)
        maximize_btn = self.create_control_button("□", self.maximize_window)
        close_btn = self.create_control_button("✕", self.close_window, "#e74c3c")
        
        layout.addWidget(title_label)
        layout.addStretch(1)
        layout.addWidget(home_button)
        layout.addWidget(chat_button)
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
        
    def create_control_button(self, text, callback, color="#4a90e2"):
        button = QPushButton(text)
        button.setStyleSheet(f"""
            QPushButton {{
                background: {color};
                border: none;
                border-radius: 4px;
                color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 12px;
                font-weight: bold;
                padding: 6px 12px;
                min-width: 30px;
            }}
            QPushButton:hover {{
                background: {color.replace('e2', 'f2') if 'e2' in color else color.replace('3c', '4c')};
            }}
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
        
        # Create stacked widget for screens
        self.stacked_widget = QStackedWidget(self)
        
        # Create modern screens
        self.initial_screen = ModernInitialScreen()
        self.message_screen = ModernMessagesScreen()
        
        self.stacked_widget.addWidget(self.initial_screen)
        self.stacked_widget.addWidget(self.message_screen)
        
        # Set window properties
        self.setGeometry(0, 0, screen_width, screen_height)
        self.setStyleSheet("""
            QMainWindow {
                background: #000000;
            }
        """)
        
        # Create modern top bar
        self.top_bar = ModernTopBar(self, self.stacked_widget)
        self.setMenuWidget(self.top_bar)
        self.setCentralWidget(self.stacked_widget)

def ModernGraphicalUserInterface():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 9)
    app.setFont(font)
    
    window = ModernMainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    ModernGraphicalUserInterface() 