# 🔐 YOLOv8 Admin Face Recognition System

A comprehensive Windows-based admin authentication system that uses YOLOv8 for face detection and recognition, integrated with Windows CMD for secure admin operations.

## 🚀 Features

- **YOLOv8 Face Detection**: State-of-the-art face detection using YOLOv8 models
- **Face Recognition**: Secure admin authentication using facial biometrics
- **CMD Integration**: Monitors and secures Windows command prompt operations
- **Process Monitoring**: Continuously monitors for new admin processes
- **Windows Service**: Can run as a background service for system-wide protection
- **Real-time Authentication**: Live camera feed with instant face recognition
- **Multi-Admin Support**: Support for multiple admin users
- **Secure Command Execution**: Commands only execute after face verification

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Admin Face Recognition System            │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   YOLOv8 Face   │  │   Face          │  │   CMD       │ │
│  │   Detection     │  │   Recognition   │  │ Integration │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
│           │                     │                   │       │
│           └─────────────────────┼───────────────────┘       │
│                                 │                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐ │
│  │   Windows       │  │   Process       │  │   Admin     │ │
│  │   Service       │  │   Monitoring    │  │   Config    │ │
│  └─────────────────┘  └─────────────────┘  └─────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 📋 Requirements

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.8 or higher
- **Camera**: Webcam or USB camera
- **RAM**: Minimum 4GB, Recommended 8GB+
- **Storage**: 2GB free space for models and data

## 🛠️ Installation

### Quick Setup

1. **Clone or download the project**
2. **Run the setup script**:
   ```bash
   python setup_admin_face_recognition.py setup
   ```

### Manual Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r Requirements.txt
   ```

2. **Download YOLOv8 models**:
   ```bash
   python setup_admin_face_recognition.py config
   ```

3. **Add admin users**:
   ```bash
   python setup_admin_face_recognition.py add-admin <admin_name>
   ```

## 🚀 Usage

### Starting the System

1. **Run the startup script**:
   ```bash
   start_admin_face_recognition.bat
   ```

2. **Or run directly**:
   ```bash
   python admin_face_recognition.py
   ```

### Main Menu Options

1. **Start secure CMD session** - Interactive secure command prompt
2. **Execute single command** - Run one command with authentication
3. **Batch execute commands** - Run multiple commands with authentication
4. **Monitor CMD processes** - Monitor for new admin processes
5. **Add new admin face** - Register a new admin user
6. **Exit** - Close the system

### Adding Admin Users

1. Select option 5 from the main menu
2. Enter the admin name
3. Look at the camera and press 'c' to capture face samples
4. Capture 5 samples for better recognition accuracy
5. Press 'q' to finish

### Secure CMD Session

1. Select option 1 from the main menu
2. Complete initial face authentication
3. Execute commands normally - they'll run with admin privileges
4. System will re-authenticate every 5 minutes
5. Type 'exit' to end the session

## 🔧 Configuration

Edit `admin_config.json` to customize settings:

```json
{
    "face_recognition": {
        "confidence_threshold": 0.8,
        "face_tolerance": 0.6,
        "recognition_timeout": 30,
        "re_auth_timeout": 300
    },
    "cmd_integration": {
        "require_auth_for_all": true,
        "batch_execution_enabled": true,
        "process_monitoring_enabled": true
    },
    "service": {
        "auto_start": true,
        "log_level": "INFO",
        "check_interval": 5
    }
}
```

## 🏃‍♂️ Windows Service Integration

### Install as Service

```bash
# Run as Administrator
python windows_service_integration.py install
```

### Service Management

```bash
# Start service
python windows_service_integration.py start

# Stop service
python windows_service_integration.py stop

# Check status
python windows_service_integration.py status

# Uninstall service
python windows_service_integration.py uninstall
```

### Service Features

- **Automatic Startup**: Service starts with Windows
- **Background Monitoring**: Continuously monitors CMD processes
- **Face Authentication**: Requires authentication for new admin processes
- **Logging**: Comprehensive logging to `C:\admin_face_recognition_service.log`

## 🔒 Security Features

### Face Recognition Security

- **Multi-sample Training**: Uses 5 face samples per admin for accuracy
- **Confidence Thresholds**: Configurable confidence levels for recognition
- **Face Tolerance**: Adjustable tolerance for face matching
- **Real-time Verification**: Continuous authentication during sessions

### Process Security

- **Admin Process Detection**: Identifies processes running with admin privileges
- **Authentication Required**: Face verification needed for admin operations
- **Process Monitoring**: Continuous monitoring of new CMD processes
- **Secure Execution**: Commands only execute after authentication

### System Security

- **Windows Service**: Runs with system privileges for comprehensive monitoring
- **Logging**: Detailed logging of all authentication attempts and operations
- **Configuration**: Secure configuration management
- **Error Handling**: Graceful error handling and recovery

## 📁 File Structure

```
AI-OS-500pm/
├── admin_face_recognition.py          # Main face recognition system
├── cmd_admin_integration.py           # CMD integration module
├── windows_service_integration.py     # Windows service integration
├── setup_admin_face_recognition.py    # Setup and configuration script
├── Requirements.txt                   # Python dependencies
├── admin_faces/                      # Admin face images and encodings
├── models/                           # YOLOv8 model files
├── admin_config.json                 # Configuration file
├── start_admin_face_recognition.bat  # Windows startup script
├── start_admin_face_recognition.ps1  # PowerShell startup script
├── USAGE_GUIDE.md                    # Detailed usage guide
└── README.md                         # This file
```

## 🧪 Testing

### System Test

```bash
python setup_admin_face_recognition.py test
```

### Individual Component Testing

```bash
# Test face recognition
python admin_face_recognition.py

# Test CMD integration
python cmd_admin_integration.py

# Test service (debug mode)
python windows_service_integration.py debug
```

## 🐛 Troubleshooting

### Common Issues

1. **Camera not accessible**
   - Check camera permissions
   - Ensure no other applications are using the camera
   - Try restarting the system

2. **Face recognition not working**
   - Ensure good lighting conditions
   - Check face sample quality
   - Verify admin face samples are properly captured

3. **Service not starting**
   - Run as Administrator
   - Check Windows Event Viewer for errors
   - Verify service dependencies

4. **Dependencies missing**
   - Run setup script: `python setup_admin_face_recognition.py setup`
   - Check Python version compatibility
   - Verify pip installation

### Log Files

- **Main System**: `admin_face_recognition.log`
- **Setup**: `setup_admin_face_recognition.log`
- **Service**: `C:\admin_face_recognition_service.log`

## 🔄 Updates and Maintenance

### Updating Models

```bash
# Download latest YOLOv8 models
python setup_admin_face_recognition.py config
```

### Adding New Admins

```bash
# Add new admin user
python setup_admin_face_recognition.py add-admin <admin_name>
```

### Configuration Updates

Edit `admin_config.json` and restart the service for changes to take effect.

## 📚 API Reference

### AdminFaceRecognition Class

```python
class AdminFaceRecognition:
    def __init__(self, admin_faces_dir="admin_faces", confidence_threshold=0.8)
    def load_admin_faces(self)
    def add_admin_face(self, image_path, admin_name)
    def recognize_admin_face(self, frame)
    def capture_admin_face(self, admin_name, num_samples=5)
    def real_time_recognition(self, duration=30)
```

### CMDAdminIntegration Class

```python
class CMDAdminIntegration:
    def __init__(self, face_recognition)
    def authenticate_admin_face(self, timeout=30)
    def execute_cmd_with_auth(self, command, require_auth=True)
    def start_secure_cmd_session(self)
    def batch_execute_commands(self, commands, require_auth=True)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This system is designed for educational and development purposes. Use in production environments at your own risk. Ensure compliance with local privacy and security regulations.

## 🆘 Support

For support and questions:

1. Check the troubleshooting section
2. Review log files for error details
3. Check the USAGE_GUIDE.md for detailed instructions
4. Create an issue in the repository

## 🔮 Future Enhancements

- **Multi-factor Authentication**: Combine face recognition with other methods
- **Cloud Integration**: Remote admin authentication
- **Mobile App**: Mobile admin authentication
- **Advanced Analytics**: Authentication analytics and reporting
- **Integration APIs**: REST API for external system integration

---

**Built with ❤️ using YOLOv8, OpenCV, and Python**
