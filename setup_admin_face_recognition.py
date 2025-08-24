#!/usr/bin/env python3
"""
Admin Face Recognition System Setup Script
This script sets up the complete YOLOv8-based face recognition system for admin authentication
"""

import os
import sys
import subprocess
import shutil
import json
import logging
from pathlib import Path
import urllib.request
import zipfile

class AdminFaceRecognitionSetup:
    def __init__(self):
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.project_root = Path(__file__).parent
        self.admin_faces_dir = self.project_root / "admin_faces"
        self.models_dir = self.project_root / "models"
        self.config_file = self.project_root / "admin_config.json"
        
        # Create necessary directories
        self.admin_faces_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('setup_admin_face_recognition.log'),
                logging.StreamHandler()
            ]
        )
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        if sys.version_info < (3, 8):
            self.logger.error("Python 3.8 or higher is required")
            print("❌ Python 3.8 or higher is required")
            return False
        
        print(f"✅ Python version: {sys.version}")
        return True
    
    def check_dependencies(self):
        """Check if required dependencies are available"""
        required_packages = [
            'ultralytics',
            'opencv-python',
            'face-recognition',
            'numpy',
            'Pillow',
            'torch',
            'torchvision',
            'scikit-learn'
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace('-', '_'))
                print(f"✅ {package} - Available")
            except ImportError:
                missing_packages.append(package)
                print(f"❌ {package} - Missing")
        
        if missing_packages:
            print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
            return self.install_dependencies(missing_packages)
        
        return True
    
    def install_dependencies(self, packages):
        """Install missing dependencies"""
        try:
            for package in packages:
                print(f"Installing {package}...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package
                ])
                print(f"✅ {package} installed successfully")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to install dependencies: {e}")
            print(f"❌ Failed to install dependencies: {e}")
            return False
    
    def download_yolo_models(self):
        """Download required YOLOv8 models"""
        try:
            print("📥 Downloading YOLOv8 face detection models...")
            
            # YOLOv8n face detection model
            face_model_url = "https://github.com/derronqi/yolov8-face/releases/download/v0.0.0/yolov8n-face.pt"
            face_model_path = self.models_dir / "yolov8n-face.pt"
            
            if not face_model_path.exists():
                print("Downloading YOLOv8n face detection model...")
                urllib.request.urlretrieve(face_model_url, face_model_path)
                print("✅ YOLOv8n face detection model downloaded")
            else:
                print("✅ YOLOv8n face detection model already exists")
            
            # YOLOv8s face detection model (higher accuracy)
            s_face_model_url = "https://github.com/derronqi/yolov8-face/releases/download/v0.0.0/yolov8s-face.pt"
            s_face_model_path = self.models_dir / "yolov8s-face.pt"
            
            if not s_face_model_path.exists():
                print("Downloading YOLOv8s face detection model...")
                urllib.request.urlretrieve(s_face_model_url, s_face_model_path)
                print("✅ YOLOv8s face detection model downloaded")
            else:
                print("✅ YOLOv8s face detection model already exists")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to download YOLO models: {e}")
            print(f"❌ Failed to download YOLO models: {e}")
            return False
    
    def create_admin_config(self):
        """Create configuration file for admin settings"""
        try:
            config = {
                "face_recognition": {
                    "confidence_threshold": 0.8,
                    "face_tolerance": 0.6,
                    "recognition_timeout": 30,
                    "re_auth_timeout": 300
                },
                "cmd_integration": {
                    "require_auth_for_all": True,
                    "batch_execution_enabled": True,
                    "process_monitoring_enabled": True
                },
                "service": {
                    "auto_start": True,
                    "log_level": "INFO",
                    "check_interval": 5
                },
                "admin_users": [],
                "models": {
                    "face_detection": "yolov8n-face.pt",
                    "face_recognition": "default"
                }
            }
            
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            
            print("✅ Admin configuration file created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create config file: {e}")
            print(f"❌ Failed to create config file: {e}")
            return False
    
    def setup_admin_user(self, admin_name):
        """Setup a new admin user with face capture"""
        try:
            print(f"👤 Setting up admin user: {admin_name}")
            
            # Create admin directory
            admin_dir = self.admin_faces_dir / admin_name
            admin_dir.mkdir(exist_ok=True)
            
            # Import and use face recognition system
            try:
                from admin_face_recognition import AdminFaceRecognition
                
                # Initialize face recognition
                face_recognition = AdminFaceRecognition(str(self.admin_faces_dir))
                
                # Capture admin face
                print(f"📸 Capturing face samples for {admin_name}...")
                print("Look at the camera and press 'c' to capture, 'q' to quit")
                
                success = face_recognition.capture_admin_face(admin_name, num_samples=5)
                
                if success:
                    print(f"✅ Admin user {admin_name} setup completed successfully")
                    
                    # Update config
                    self.update_admin_config(admin_name)
                    
                    return True
                else:
                    print(f"❌ Failed to setup admin user {admin_name}")
                    return False
                    
            except ImportError as e:
                self.logger.error(f"Failed to import face recognition: {e}")
                print(f"❌ Face recognition system not available: {e}")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to setup admin user: {e}")
            print(f"❌ Failed to setup admin user: {e}")
            return False
    
    def update_admin_config(self, admin_name):
        """Update configuration with new admin user"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                
                if admin_name not in config["admin_users"]:
                    config["admin_users"].append(admin_name)
                    
                    with open(self.config_file, 'w') as f:
                        json.dump(config, f, indent=4)
                    
                    print(f"✅ Configuration updated with admin user: {admin_name}")
            
        except Exception as e:
            self.logger.error(f"Failed to update config: {e}")
    
    def create_startup_scripts(self):
        """Create startup scripts for easy system integration"""
        try:
            print("📝 Creating startup scripts...")
            
            # Windows batch file
            batch_content = f"""@echo off
echo Starting Admin Face Recognition System...
cd /d "{self.project_root}"
python admin_face_recognition.py
pause
"""
            
            batch_file = self.project_root / "start_admin_face_recognition.bat"
            with open(batch_file, 'w') as f:
                f.write(batch_content)
            
            # PowerShell script
            ps_content = f"""# Admin Face Recognition System Startup Script
Write-Host "Starting Admin Face Recognition System..." -ForegroundColor Green
Set-Location "{self.project_root}"
python admin_face_recognition.py
Read-Host "Press Enter to continue"
"""
            
            ps_file = self.project_root / "start_admin_face_recognition.ps1"
            with open(ps_file, 'w') as f:
                f.write(ps_content)
            
            print("✅ Startup scripts created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create startup scripts: {e}")
            print(f"❌ Failed to create startup scripts: {e}")
            return False
    
    def create_desktop_shortcut(self):
        """Create desktop shortcut for easy access"""
        try:
            print("🔗 Creating desktop shortcut...")
            
            # Get desktop path
            desktop = Path.home() / "Desktop"
            
            if desktop.exists():
                # Create shortcut file
                shortcut_content = f"""[InternetShortcut]
URL=file:///{self.project_root}/start_admin_face_recognition.bat
IconFile={sys.executable}
IconIndex=0
"""
                
                shortcut_file = desktop / "Admin Face Recognition.lnk"
                with open(shortcut_file, 'w') as f:
                    f.write(shortcut_content)
                
                print("✅ Desktop shortcut created")
                return True
            else:
                print("⚠️  Desktop directory not found, skipping shortcut creation")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to create desktop shortcut: {e}")
            print(f"❌ Failed to create desktop shortcut: {e}")
            return False
    
    def run_system_test(self):
        """Run a system test to verify everything works"""
        try:
            print("🧪 Running system test...")
            
            # Test imports
            try:
                from admin_face_recognition import AdminFaceRecognition
                from cmd_admin_integration import CMDAdminIntegration
                print("✅ All modules imported successfully")
            except ImportError as e:
                print(f"❌ Module import failed: {e}")
                return False
            
            # Test face recognition initialization
            try:
                face_recognition = AdminFaceRecognition(str(self.admin_faces_dir))
                print("✅ Face recognition system initialized")
            except Exception as e:
                print(f"❌ Face recognition initialization failed: {e}")
                return False
            
            # Test CMD integration
            try:
                cmd_integration = CMDAdminIntegration(face_recognition)
                print("✅ CMD integration initialized")
            except Exception as e:
                print(f"❌ CMD integration initialization failed: {e}")
                return False
            
            print("✅ System test completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"System test failed: {e}")
            print(f"❌ System test failed: {e}")
            return False
    
    def create_usage_guide(self):
        """Create a comprehensive usage guide"""
        try:
            print("📚 Creating usage guide...")
            
            guide_content = """# Admin Face Recognition System - Usage Guide

## Overview
This system provides secure admin authentication using YOLOv8 face recognition technology.
It monitors CMD processes and requires face authentication for admin operations.

## Quick Start
1. Run `start_admin_face_recognition.bat` to start the system
2. Use option 5 to add your admin face
3. Use option 1 to start a secure CMD session

## Features
- **Face Recognition**: Uses YOLOv8 for accurate face detection and recognition
- **CMD Integration**: Monitors and secures Windows command prompt operations
- **Admin Authentication**: Requires face verification for admin commands
- **Process Monitoring**: Continuously monitors for new admin processes
- **Windows Service**: Can run as a background service

## Commands
- `python admin_face_recognition.py` - Main face recognition system
- `python cmd_admin_integration.py` - CMD integration system
- `python windows_service_integration.py install` - Install as Windows service

## Configuration
Edit `admin_config.json` to customize:
- Confidence thresholds
- Timeout values
- Service settings
- Model preferences

## Security Features
- Continuous face verification
- Process monitoring
- Admin privilege verification
- Secure command execution

## Troubleshooting
- Ensure camera is accessible
- Check admin face samples quality
- Verify Python dependencies
- Check service status if running as service

## Support
For issues, check the log files:
- `admin_face_recognition.log`
- `setup_admin_face_recognition.log`
"""
            
            guide_file = self.project_root / "USAGE_GUIDE.md"
            with open(guide_file, 'w') as f:
                f.write(guide_content)
            
            print("✅ Usage guide created")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create usage guide: {e}")
            print(f"❌ Failed to create usage guide: {e}")
            return False
    
    def run_complete_setup(self):
        """Run the complete setup process"""
        try:
            print("🚀 ADMIN FACE RECOGNITION SYSTEM SETUP")
            print("=" * 50)
            
            # Check Python version
            if not self.check_python_version():
                return False
            
            # Check and install dependencies
            if not self.check_dependencies():
                return False
            
            # Download YOLO models
            if not self.download_yolo_models():
                return False
            
            # Create configuration
            if not self.create_admin_config():
                return False
            
            # Create startup scripts
            if not self.create_startup_scripts():
                return False
            
            # Create desktop shortcut
            self.create_desktop_shortcut()
            
            # Create usage guide
            if not self.create_usage_guide():
                return False
            
            # Run system test
            if not self.run_system_test():
                return False
            
            print("\n🎉 SETUP COMPLETED SUCCESSFULLY!")
            print("=" * 50)
            print("Next steps:")
            print("1. Run 'start_admin_face_recognition.bat' to start the system")
            print("2. Use option 5 to add your admin face")
            print("3. Use option 1 to start a secure CMD session")
            print("\nFor more information, see USAGE_GUIDE.md")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Setup failed: {e}")
            print(f"❌ Setup failed: {e}")
            return False

def main():
    """Main function"""
    try:
        setup = AdminFaceRecognitionSetup()
        
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "setup":
                setup.run_complete_setup()
            elif command == "add-admin":
                if len(sys.argv) > 2:
                    admin_name = sys.argv[2]
                    setup.setup_admin_user(admin_name)
                else:
                    print("Usage: python setup_admin_face_recognition.py add-admin <admin_name>")
            elif command == "test":
                setup.run_system_test()
            elif command == "config":
                setup.create_admin_config()
            else:
                print("Unknown command. Use: setup, add-admin, test, or config")
        else:
            # Interactive setup
            print("🔐 Admin Face Recognition System Setup")
            print("=" * 50)
            print("1. Complete setup")
            print("2. Add admin user")
            print("3. Run system test")
            print("4. Exit")
            
            while True:
                try:
                    choice = input("\nSelect option (1-4): ").strip()
                    
                    if choice == "1":
                        setup.run_complete_setup()
                        break
                    elif choice == "2":
                        admin_name = input("Enter admin name: ").strip()
                        if admin_name:
                            setup.setup_admin_user(admin_name)
                        break
                    elif choice == "3":
                        setup.run_system_test()
                        break
                    elif choice == "4":
                        print("👋 Setup cancelled.")
                        break
                    else:
                        print("Invalid option. Please select 1-4.")
                        
                except KeyboardInterrupt:
                    print("\n⚠️  Setup interrupted.")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
                    break
                    
    except Exception as e:
        print(f"❌ Setup error: {e}")
        logging.error(f"Setup error: {e}")

if __name__ == "__main__":
    main()
