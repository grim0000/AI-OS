#!/usr/bin/env python3
"""
Create modern graphics for Xeno AI Assistant
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_modern_icon(filename, size, color, text, bg_color="#2c3e50"):
    """Create a modern icon with text"""
    img = Image.new('RGBA', (size, size), bg_color)
    draw = ImageDraw.Draw(img)
    
    # Create rounded rectangle effect
    draw.ellipse([0, 0, size//4, size//4], fill=color)
    draw.ellipse([size*3//4, 0, size, size//4], fill=color)
    draw.ellipse([0, size*3//4, size//4, size], fill=color)
    draw.ellipse([size*3//4, size*3//4, size, size], fill=color)
    draw.rectangle([size//8, 0, size*7//8, size//4], fill=color)
    draw.rectangle([0, size//8, size//4, size*7//8], fill=color)
    draw.rectangle([size*3//4, size//8, size, size*7//8], fill=color)
    draw.rectangle([size//8, size*3//4, size*7//8, size], fill=color)
    draw.rectangle([size//4, size//4, size*3//4, size*3//4], fill=color)
    
    # Add text
    try:
        font = ImageFont.truetype("arial.ttf", size//3)
    except:
        font = ImageFont.load_default()
    
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (size - text_width) // 2
    y = (size - text_height) // 2
    
    draw.text((x, y), text, fill="white", font=font)
    
    return img

def create_gradient_background(filename, width, height, colors):
    """Create a gradient background"""
    img = Image.new('RGBA', (width, height), colors[0])
    draw = ImageDraw.Draw(img)
    
    for y in range(height):
        ratio = y / height
        r = int(colors[0][0] * (1 - ratio) + colors[1][0] * ratio)
        g = int(colors[0][1] * (1 - ratio) + colors[1][1] * ratio)
        b = int(colors[0][2] * (1 - ratio) + colors[1][2] * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
    
    return img

def main():
    # Create Graphics directory if it doesn't exist
    graphics_dir = "Frontend/Graphics"
    os.makedirs(graphics_dir, exist_ok=True)
    
    # Create modern icons
    icons = [
        ("modern_home.png", 64, "#4a90e2", "🏠"),
        ("modern_chat.png", 64, "#50c878", "💬"),
        ("modern_mic_on.png", 64, "#4a90e2", "🎤"),
        ("modern_mic_off.png", 64, "#e74c3c", "⏹️"),
        ("modern_minimize.png", 32, "#95a5a6", "─"),
        ("modern_maximize.png", 32, "#3498db", "□"),
        ("modern_close.png", 32, "#e74c3c", "✕"),
        ("modern_settings.png", 64, "#9b59b6", "⚙️"),
    ]
    
    for filename, size, color, text in icons:
        img = create_modern_icon(filename, size, color, text)
        img.save(os.path.join(graphics_dir, filename))
        print(f"Created {filename}")
    
    # Create gradient backgrounds
    gradients = [
        ("modern_bg_dark.png", 1920, 1080, [(15, 15, 35), (22, 30, 62)]),
        ("modern_bg_light.png", 1920, 1080, [(74, 144, 226), (53, 122, 189)]),
    ]
    
    for filename, width, height, colors in gradients:
        img = create_gradient_background(filename, width, height, colors)
        img.save(os.path.join(graphics_dir, filename))
        print(f"Created {filename}")
    
    print("Modern graphics created successfully!")

if __name__ == "__main__":
    main() 