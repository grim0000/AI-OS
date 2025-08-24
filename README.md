# Jarvis AI Assistant

A comprehensive AI-powered personal assistant that can handle email management, system automation, web searches, and intelligent conversations.

## 🚀 Features

### Core Capabilities
- **🤖 AI-Powered Conversations**: Natural language processing with multiple AI models
- **📧 Email Management**: Gmail integration for drafting and sending emails
- **🔍 Web Search**: Real-time search capabilities with multiple engines
- **⚙️ System Automation**: Control your computer with voice/text commands
- **🎵 Media Control**: Play music, control applications, and manage files
- **📊 Excel Automation**: Advanced spreadsheet manipulation
- **🖥️ Screen Vision**: Computer vision for automation tasks
- **🧠 Intelligent Memory**: Learns from conversations and improves responses

### Advanced Features
- **Voice Recognition**: Speech-to-text capabilities
- **Text-to-Speech**: Natural voice responses
- **GUI Interface**: Modern graphical user interface
- **Command Line Automation**: Execute system commands
- **CNN Log Analysis**: Machine learning for response optimization

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11 (Primary support)
- **Python**: 3.8 or higher
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Internet**: Required for AI services and web searches

### Required Software
- Python 3.8+
- Git (for cloning)
- Chrome/Edge browser (for web automation)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd jarvis
```

### 2. Create Virtual Environment
```bash
python -m venv .venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
.venv\Scripts\activate
```

**Linux/Mac:**
```bash
source .venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Environment Setup
Create a `.env` file in the root directory:
```env
# AI API Keys
GroqAPIKey=your_groq_api_key_here
CohereAPIKey=your_cohere_api_key_here

# User Configuration
Username=YourName
AssistantName=Jarvis

# Optional: Gmail Integration
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
```

## 🚀 Getting Started

### 1. Start Jarvis
```bash
python Main.py
```

### 2. Initial Setup
- The system will initialize all components
- You'll see the GUI interface appear
- Grant necessary permissions when prompted

### 3. First Conversation
- Type or speak: "Hello Jarvis"
- The assistant will respond and guide you through available features

## 📖 Usage Guide

### Basic Commands

#### 🗣️ General Conversation
```
"Hello Jarvis"
"How are you?"
"What can you do?"
"Tell me a joke"
```

#### 🔍 Web Search
```
"Search for Python tutorials"
"Find information about AI"
"Look up weather in London"
"Google machine learning basics"
```

#### 📧 Email Management
```
"Send an email to john@example.com subject meeting body I'll be there at 2 PM"
"Draft an email to manager@company.com about project update"
"Write an email to support@service.com regarding technical issue"
"Send email to client@business.com subject proposal body Here's our proposal"
```

#### ⚙️ System Control
```
"Open notepad"
"Close chrome"
"Open calculator"
"Shutdown computer"
"Restart computer"
"Open file explorer"
```

#### 🎵 Media Control
```
"Play music"
"Open spotify"
"Play song Bohemian Rhapsody"
"Pause music"
"Next song"
```

#### 📊 Excel Operations
```
"Open Excel file data.xlsx"
"Add data to cell A1 in sheet1"
"Create chart in Excel"
"Save Excel file"
"Close Excel"
```

#### 🖥️ Screen Automation
```
"Click on the search button"
"Find text on screen"
"Take screenshot"
"Automate this task"
```

### Advanced Commands

#### 🔧 Command Line Automation
```
"Run command dir"
"Execute python script.py"
"Open terminal"
"Install package requests"
```

#### 📝 Content Generation
```
"Write a professional email"
"Draft a meeting agenda"
"Create a project proposal"
"Generate a report"
```

#### 🧠 Intelligent Features
```
"Remember this: I prefer dark mode"
"What did we discuss yesterday?"
"Learn from this conversation"
"Optimize your responses"
```

## 🔧 Configuration

### Gmail Integration Setup

1. **Enable Gmail API**:
   - Go to Google Cloud Console
   - Create a new project
   - Enable Gmail API
   - Create OAuth 2.0 credentials

2. **Download Credentials**:
   - Download the JSON credentials file
   - Place it in `Data/gmail_credentials.json`

3. **First Authentication**:
   - Run: "setup gmail" in Jarvis
   - Follow the browser authentication process

### AI Model Configuration

The system uses multiple AI models:
- **Groq**: Primary conversation model
- **Cohere**: Decision making and classification
- **Local Models**: Fallback and specialized tasks

### Voice Configuration

Configure voice settings in the GUI:
- Voice speed
- Voice type
- Language selection
- Audio output device

## 🛠️ Troubleshooting

### Common Issues

#### 1. Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### 2. API Key Issues
- Verify API keys in `.env` file
- Check API quotas and limits
- Ensure internet connection

#### 3. Gmail Authentication
```bash
# Reset Gmail credentials
rm Data/gmail_token.json
# Then run "setup gmail" in Jarvis
```

#### 4. Voice Issues
- Check microphone permissions
- Verify audio drivers
- Test with system voice settings

#### 5. GUI Not Loading
```bash
# Install PyQt5
pip install PyQt5
```

### Performance Optimization

#### For Better Performance:
1. **Close unnecessary applications**
2. **Use SSD storage**
3. **Increase RAM if possible**
4. **Use wired internet connection**

#### For Faster Responses:
1. **Use text input instead of voice**
2. **Keep conversations focused**
3. **Use specific commands**

## 📁 Project Structure

```
jarvis/
├── Backend/                 # Core functionality
│   ├── Automation.py       # System automation
│   ├── Chatbot.py          # AI conversation
│   ├── GmailIntegration.py # Email management
│   ├── CNNLogAnalyzer.py   # Machine learning
│   └── ...
├── Frontend/               # User interface
│   ├── ModernGUI.py        # Main GUI
│   └── ...
├── Data/                   # Data storage
│   ├── ChatLog.json        # Conversation history
│   └── ...
├── Main.py                 # Application entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## 🔒 Privacy & Security

### Data Handling
- **Local Storage**: Conversations stored locally
- **API Calls**: Minimal data sent to AI services
- **No Personal Data**: Email content not stored permanently
- **Secure Authentication**: OAuth 2.0 for Gmail

### Best Practices
- Keep API keys secure
- Regularly update dependencies
- Monitor system permissions
- Use strong passwords for accounts

## 🤝 Contributing

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Code Style
- Follow PEP 8 guidelines
- Add proper documentation
- Include error handling
- Write unit tests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **AI Models**: Groq, Cohere, OpenAI
- **GUI Framework**: PyQt5
- **Voice Processing**: Edge TTS, Speech Recognition
- **Web Automation**: Selenium, WebDriver Manager

## 📞 Support

### Getting Help
1. Check this README first
2. Review the troubleshooting section
3. Search existing issues
4. Create a new issue with details

### Issue Reporting
When reporting issues, include:
- Operating system and version
- Python version
- Error messages
- Steps to reproduce
- Expected vs actual behavior

---

**Happy Assisting! 🤖✨**

*Jarvis AI Assistant - Your intelligent companion for productivity and automation.*
