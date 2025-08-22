#!/usr/bin/env python3
"""
GUI Launcher for Xeno AI Assistant
Choose between Classic and Modern interfaces
"""

import sys
import os

def print_banner():
    print("=" * 60)
    print("🎨 XENO AI ASSISTANT GUI LAUNCHER")
    print("=" * 60)
    print("Choose your preferred interface:")
    print("1. Classic GUI (Original design)")
    print("2. Modern GUI (New sleek design)")
    print("3. Exit")
    print("=" * 60)

def check_dependencies():
    """Check if required dependencies are installed."""
    missing_deps = []
    
    try:
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        missing_deps.append("PyQt5")
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\n💡 Install missing dependencies with:")
        print("   pip install " + " ".join(missing_deps))
        return False
    
    return True

def launch_classic_gui():
    """Launch the classic GUI."""
    print("🎨 Launching Classic GUI...")
    try:
        from Frontend.GUI import GraphicalUserInterface
        GraphicalUserInterface()
    except ImportError as e:
        print(f"❌ Error importing Classic GUI: {e}")
    except Exception as e:
        print(f"❌ Error launching Classic GUI: {e}")

def launch_modern_gui():
    """Launch the modern GUI."""
    print("🚀 Launching Modern GUI...")
    try:
        from Frontend.ModernGUI import ModernGraphicalUserInterface
        ModernGraphicalUserInterface()
    except ImportError as e:
        print(f"❌ Error importing Modern GUI: {e}")
    except Exception as e:
        print(f"❌ Error launching Modern GUI: {e}")

def main():
    """Main launcher function."""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    while True:
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                launch_classic_gui()
                break
            elif choice == "2":
                launch_modern_gui()
                break
            elif choice == "3":
                print("👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 