#!/usr/bin/env python3
"""
Test script to verify GIF loading functionality
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QSize

def test_gif_loading():
    """Test if the 7ZN3.gif can be loaded and displayed"""
    app = QApplication(sys.argv)
    
    # Create a simple window
    window = QWidget()
    window.setWindowTitle("GIF Test")
    window.setGeometry(100, 100, 400, 300)
    
    layout = QVBoxLayout()
    
    # Test GIF loading
    gif_path = "Frontend/Graphics/7ZN3.gif"
    if os.path.exists(gif_path):
        print(f"✅ GIF file found at: {gif_path}")
        
        try:
            movie = QMovie(gif_path)
            movie.setScaledSize(QSize(200, 200))
            
            label = QLabel()
            label.setMovie(movie)
            movie.start()
            
            layout.addWidget(label)
            print("✅ GIF loaded and displayed successfully!")
            
        except Exception as e:
            print(f"❌ Error loading GIF: {e}")
            label = QLabel("❌ GIF loading failed")
            layout.addWidget(label)
    else:
        print(f"❌ GIF file not found at: {gif_path}")
        label = QLabel("❌ GIF file not found")
        layout.addWidget(label)
    
    window.setLayout(layout)
    window.show()
    
    print("🎬 Test window opened. Close it to continue...")
    sys.exit(app.exec_())

if __name__ == "__main__":
    test_gif_loading() 