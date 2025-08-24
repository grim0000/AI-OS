#!/usr/bin/env python3
"""
Demo script for Admin Face Recognition System
This script demonstrates the key features of the system
"""

import time
import sys
import os
from pathlib import Path

def print_banner():
    """Print system banner"""
    print("=" * 70)
    print("🔐 YOLOv8 ADMIN FACE RECOGNITION SYSTEM - DEMO")
    print("=" * 70)
    print("This demo showcases the key features of the admin face recognition system")
    print("=" * 70)

def demo_face_recognition():
    """Demo the face recognition system"""
    print("\n📸 DEMO: Face Recognition System")
    print("-" * 40)
    
    try:
        from admin_face_recognition import AdminFaceRecognition
        
        print("✅ Face recognition system imported successfully")
        print("🔧 Initializing system...")
        
        # Initialize face recognition
        face_recognition = AdminFaceRecognition()
        print("✅ System initialized")
        
        print("\n🎯 Available features:")
        print("• Real-time face recognition")
        print("• Admin face capture and training")
        print("• Multi-admin support")
        print("• Configurable confidence thresholds")
        
        return face_recognition
        
    except ImportError as e:
        print(f"❌ Failed to import face recognition: {e}")
        print("💡 Run 'python setup_admin_face_recognition.py setup' first")
        return None
    except Exception as e:
        print(f"❌ Face recognition initialization failed: {e}")
        return None

def demo_cmd_integration(face_recognition):
    """Demo the CMD integration system"""
    print("\n💻 DEMO: CMD Integration System")
    print("-" * 40)
    
    try:
        from cmd_admin_integration import CMDAdminIntegration
        
        print("✅ CMD integration system imported successfully")
        print("🔧 Initializing CMD integration...")
        
        # Initialize CMD integration
        cmd_integration = CMDAdminIntegration(face_recognition)
        print("✅ CMD integration initialized")
        
        print("\n🎯 Available features:")
        print("• Secure CMD sessions with face authentication")
        print("• Single command execution with auth")
        print("• Batch command execution")
        print("• Process monitoring")
        print("• Admin privilege verification")
        
        return cmd_integration
        
    except ImportError as e:
        print(f"❌ Failed to import CMD integration: {e}")
        return None
    except Exception as e:
        print(f"❌ CMD integration initialization failed: {e}")
        return None

def demo_windows_service():
    """Demo the Windows service integration"""
    print("\n🖥️ DEMO: Windows Service Integration")
    print("-" * 40)
    
    try:
        from windows_service_integration import AdminFaceRecognitionManager
        
        print("✅ Windows service integration imported successfully")
        print("🔧 Initializing service manager...")
        
        # Initialize service manager
        service_manager = AdminFaceRecognitionManager()
        print("✅ Service manager initialized")
        
        print("\n🎯 Available features:")
        print("• Install as Windows service")
        print("• Automatic startup with Windows")
        print("• Background process monitoring")
        print("• Service management (start/stop/status)")
        print("• System-wide admin protection")
        
        return service_manager
        
    except ImportError as e:
        print(f"❌ Failed to import Windows service integration: {e}")
        return None
    except Exception as e:
        print(f"❌ Windows service initialization failed: {e}")
        return None

def demo_face_capture(face_recognition):
    """Demo face capture functionality"""
    print("\n📸 DEMO: Face Capture System")
    print("-" * 40)
    
    if not face_recognition:
        print("❌ Face recognition system not available")
        return False
    
    print("🎯 This demo will capture face samples for training")
    print("💡 You can use this to add new admin users")
    
    choice = input("\nWould you like to try face capture? (y/n): ").strip().lower()
    
    if choice == 'y':
        admin_name = input("Enter admin name for demo: ").strip()
        if admin_name:
            print(f"\n📸 Starting face capture for {admin_name}...")
            print("Look at the camera and press 'c' to capture, 'q' to quit")
            
            try:
                success = face_recognition.capture_admin_face(admin_name, num_samples=3)
                if success:
                    print(f"✅ Face capture completed for {admin_name}")
                    return True
                else:
                    print(f"❌ Face capture failed for {admin_name}")
                    return False
            except Exception as e:
                print(f"❌ Face capture error: {e}")
                return False
        else:
            print("❌ Invalid admin name")
            return False
    else:
        print("⏭️  Skipping face capture demo")
        return False

def demo_real_time_recognition(face_recognition):
    """Demo real-time face recognition"""
    print("\n🔍 DEMO: Real-time Face Recognition")
    print("-" * 40)
    
    if not face_recognition:
        print("❌ Face recognition system not available")
        return False
    
    print("🎯 This demo will test real-time face recognition")
    print("💡 Make sure you have admin faces registered first")
    
    choice = input("\nWould you like to try real-time recognition? (y/n): ").strip().lower()
    
    if choice == 'y':
        duration = input("Enter test duration in seconds (default 15): ").strip()
        try:
            duration = int(duration) if duration else 15
        except ValueError:
            duration = 15
        
        print(f"\n🔍 Starting real-time recognition for {duration} seconds...")
        print("Look at the camera for face recognition...")
        
        try:
            success = face_recognition.real_time_recognition(duration=duration)
            if success:
                print("✅ Real-time recognition successful!")
                return True
            else:
                print("❌ Real-time recognition failed or timed out")
                return False
        except Exception as e:
            print(f"❌ Real-time recognition error: {e}")
            return False
    else:
        print("⏭️  Skipping real-time recognition demo")
        return False

def demo_secure_cmd_session(cmd_integration):
    """Demo secure CMD session"""
    print("\n🛡️ DEMO: Secure CMD Session")
    print("-" * 40)
    
    if not cmd_integration:
        print("❌ CMD integration system not available")
        return False
    
    print("🎯 This demo will show how to start a secure CMD session")
    print("💡 Commands will only execute after face authentication")
    
    choice = input("\nWould you like to start a secure CMD session? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n🛡️ Starting secure CMD session...")
        print("You'll need to authenticate with your face first...")
        
        try:
            # Start secure session (this will run the full session)
            cmd_integration.start_secure_cmd_session()
            return True
        except Exception as e:
            print(f"❌ Secure CMD session error: {e}")
            return False
    else:
        print("⏭️  Skipping secure CMD session demo")
        return False

def demo_batch_commands(cmd_integration):
    """Demo batch command execution"""
    print("\n⚡ DEMO: Batch Command Execution")
    print("-" * 40)
    
    if not cmd_integration:
        print("❌ CMD integration system not available")
        return False
    
    print("🎯 This demo will show batch command execution with authentication")
    print("💡 Multiple commands can be executed after single face verification")
    
    choice = input("\nWould you like to try batch command execution? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n⚡ Starting batch command execution demo...")
        
        # Sample commands for demo
        demo_commands = [
            "echo Hello from Admin Face Recognition System",
            "whoami",
            "hostname",
            "date /t",
            "time /t"
        ]
        
        print(f"Commands to execute: {len(demo_commands)}")
        for i, cmd in enumerate(demo_commands, 1):
            print(f"  {i}. {cmd}")
        
        try:
            results = cmd_integration.batch_execute_commands(demo_commands)
            
            print("\n📊 Batch execution results:")
            for success, command, output in results:
                status = "✅" if success else "❌"
                print(f"{status} {command}")
                if output and output.strip():
                    print(f"   Output: {output.strip()}")
            
            return True
        except Exception as e:
            print(f"❌ Batch command execution error: {e}")
            return False
    else:
        print("⏭️  Skipping batch command execution demo")
        return False

def demo_service_management(service_manager):
    """Demo Windows service management"""
    print("\n⚙️ DEMO: Windows Service Management")
    print("-" * 40)
    
    if not service_manager:
        print("❌ Windows service manager not available")
        return False
    
    print("🎯 This demo will show Windows service management capabilities")
    print("💡 You can install, start, stop, and manage the service")
    
    print("\n📋 Available service commands:")
    print("• install    - Install as Windows service")
    print("• start      - Start the service")
    print("• stop       - Stop the service")
    print("• status     - Check service status")
    print("• uninstall  - Remove the service")
    print("• debug      - Run in debug mode")
    
    choice = input("\nWould you like to check service status? (y/n): ").strip().lower()
    
    if choice == 'y':
        try:
            print("\n🔍 Checking service status...")
            service_manager.get_service_status()
            return True
        except Exception as e:
            print(f"❌ Service status check error: {e}")
            return False
    else:
        print("⏭️  Skipping service status check")
        return False

def run_complete_demo():
    """Run the complete demo"""
    print_banner()
    
    print("\n🚀 Starting comprehensive demo...")
    print("This will demonstrate all major features of the system")
    
    # Demo 1: Face Recognition
    face_recognition = demo_face_recognition()
    
    # Demo 2: CMD Integration
    cmd_integration = demo_cmd_integration(face_recognition)
    
    # Demo 3: Windows Service
    service_manager = demo_windows_service()
    
    # Demo 4: Face Capture (if face recognition is available)
    if face_recognition:
        demo_face_capture(face_recognition)
    
    # Demo 5: Real-time Recognition (if face recognition is available)
    if face_recognition:
        demo_real_time_recognition(face_recognition)
    
    # Demo 6: Secure CMD Session (if CMD integration is available)
    if cmd_integration:
        demo_secure_cmd_session(cmd_integration)
    
    # Demo 7: Batch Commands (if CMD integration is available)
    if cmd_integration:
        demo_batch_commands(cmd_integration)
    
    # Demo 8: Service Management (if service manager is available)
    if service_manager:
        demo_service_management(service_manager)
    
    print("\n🎉 DEMO COMPLETED!")
    print("=" * 70)
    print("You've seen all the major features of the Admin Face Recognition System")
    print("\n💡 Next steps:")
    print("1. Run 'python setup_admin_face_recognition.py setup' for full setup")
    print("2. Add your admin face using the system")
    print("3. Start using the secure CMD sessions")
    print("4. Consider installing as a Windows service for system-wide protection")
    print("\n📚 For more information, see:")
    print("• ADMIN_FACE_RECOGNITION_README.md")
    print("• USAGE_GUIDE.md")
    print("• setup_admin_face_recognition.py --help")

def main():
    """Main function"""
    try:
        if len(sys.argv) > 1:
            command = sys.argv[1].lower()
            
            if command == "face":
                face_recognition = demo_face_recognition()
                if face_recognition:
                    demo_face_capture(face_recognition)
                    demo_real_time_recognition(face_recognition)
            elif command == "cmd":
                face_recognition = demo_face_recognition()
                cmd_integration = demo_cmd_integration(face_recognition)
                if cmd_integration:
                    demo_secure_cmd_session(cmd_integration)
                    demo_batch_commands(cmd_integration)
            elif command == "service":
                service_manager = demo_windows_service()
                if service_manager:
                    demo_service_management(service_manager)
            elif command == "help":
                print("Available demo commands:")
                print("  python demo_admin_face_recognition.py          - Run complete demo")
                print("  python demo_admin_face_recognition.py face    - Face recognition demo")
                print("  python demo_admin_face_recognition.py cmd     - CMD integration demo")
                print("  python demo_admin_face_recognition.py service - Windows service demo")
                print("  python demo_admin_face_recognition.py help    - Show this help")
            else:
                print(f"Unknown command: {command}")
                print("Use 'help' to see available commands")
        else:
            # Run complete demo
            run_complete_demo()
            
    except KeyboardInterrupt:
        print("\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo error: {e}")
        print("💡 Make sure you've run the setup script first:")
        print("   python setup_admin_face_recognition.py setup")

if __name__ == "__main__":
    main()
