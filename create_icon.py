#!/usr/bin/env python3
"""
Create professional icon for Instagram Bot
"""

from PIL import Image, ImageDraw

def create_icon():
    # Create 512x512 icon with Instagram-style gradient
    size = 512
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center = size // 2
    max_radius = size // 2
    
    # Create gradient from purple to orange
    for r in range(max_radius, 0, -2):
        t = 1 - (r / max_radius)
        if t < 0.5:
            # Purple to magenta
            red = int(131 + (237-131) * (t*2))
            green = int(58 + (117-58) * (t*2))
            blue = int(180)
        else:
            # Magenta to orange
            t2 = (t - 0.5) * 2
            red = int(237 + (252-237) * t2)
            green = int(117 + (175-117) * t2)
            blue = int(180 - 111 * t2)
        
        alpha = int(255 * (0.9 - t * 0.1))
        color = (red, green, blue, alpha)
        draw.ellipse([center-r, center-r, center+r, center+r], fill=color)
    
    # Add robot/automation symbol
    robot_size = size // 3
    
    # Robot head (circle)
    head_radius = robot_size // 4
    head_color = (255, 255, 255, 230)
    draw.ellipse([center - head_radius, center - head_radius - robot_size//8,
                  center + head_radius, center + head_radius - robot_size//8],
                 fill=head_color)
    
    # Robot body (rounded rectangle)
    body_width = robot_size // 3
    body_height = robot_size // 3
    body_top = center - robot_size//16
    draw.rounded_rectangle([center - body_width//2, body_top,
                           center + body_width//2, body_top + body_height],
                          radius=15, fill=head_color)
    
    # Robot eyes
    eye_size = 8
    eye_y = center - head_radius + 15
    eye_color = (80, 80, 80, 255)
    draw.ellipse([center - 20 - eye_size//2, eye_y - eye_size//2,
                  center - 20 + eye_size//2, eye_y + eye_size//2], fill=eye_color)
    draw.ellipse([center + 20 - eye_size//2, eye_y - eye_size//2,
                  center + 20 + eye_size//2, eye_y + eye_size//2], fill=eye_color)
    
    # Antenna
    antenna_top = center - head_radius - robot_size//8 - 20
    draw.line([center, center - head_radius - robot_size//8,
               center, antenna_top], fill=head_color, width=4)
    draw.ellipse([center-6, antenna_top-6, center+6, antenna_top+6], fill=head_color)
    
    # Save icon
    img.save('instagram_bot_icon.png')
    print("✅ Professional Instagram Bot icon created")

if __name__ == "__main__":
    create_icon() 