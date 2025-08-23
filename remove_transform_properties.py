#!/usr/bin/env python3
"""
Script to remove all transform properties from ModernGUI.py
This will fix the "Unknown property transform" warnings
"""

import re

def remove_transform_properties():
    """Remove all transform properties from the CSS in ModernGUI.py"""
    
    # Read the file
    with open('Frontend/ModernGUI.py', 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove all transform properties
    # Pattern to match transform: scale(...); with optional whitespace
    pattern = r'\s*transform:\s*scale\([^)]+\);\s*\n?'
    
    # Remove the transform properties
    cleaned_content = re.sub(pattern, '', content)
    
    # Write back to file
    with open('Frontend/ModernGUI.py', 'w', encoding='utf-8') as file:
        file.write(cleaned_content)
    
    print("✅ Removed all transform properties from ModernGUI.py")
    print("🔧 This should fix the 'Unknown property transform' warnings")

if __name__ == "__main__":
    remove_transform_properties()
