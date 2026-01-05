#!/usr/bin/env python3
"""Generate static image assets for HoneyConvert"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_gradient(width, height):
    """Create a purple gradient image"""
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)

    # Purple gradient from #667eea to #764ba2
    start_color = (102, 126, 234)  # #667eea
    end_color = (118, 75, 162)     # #764ba2

    for y in range(height):
        for x in range(width):
            # Calculate gradient position (diagonal)
            t = (x + y) / (width + height)
            r = int(start_color[0] + (end_color[0] - start_color[0]) * t)
            g = int(start_color[1] + (end_color[1] - start_color[1]) * t)
            b = int(start_color[2] + (end_color[2] - start_color[2]) * t)
            draw.point((x, y), (r, g, b))

    return img

def create_favicon():
    """Create 64x64 favicon"""
    size = 64
    img = create_gradient(size, size)
    draw = ImageDraw.Draw(img)

    # Add rounded corners effect (approximate with white "H")
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
    except:
        font = ImageFont.load_default()

    # Draw "H" in center
    text = "H"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 5
    draw.text((x, y), text, fill='white', font=font)

    return img

def create_apple_touch_icon():
    """Create 180x180 apple touch icon"""
    size = 180
    img = create_gradient(size, size)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 120)
    except:
        font = ImageFont.load_default()

    text = "H"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (size - text_width) // 2
    y = (size - text_height) // 2 - 10
    draw.text((x, y), text, fill='white', font=font)

    return img

def create_og_image():
    """Create 1200x630 Open Graph image"""
    width, height = 1200, 630
    img = create_gradient(width, height)
    draw = ImageDraw.Draw(img)

    # Draw white card
    card_margin = 80
    card_rect = [card_margin, card_margin, width - card_margin, height - card_margin]
    draw.rounded_rectangle(card_rect, radius=20, fill='white')

    # Draw logo circle
    logo_center = (220, 315)
    logo_radius = 70
    draw.ellipse(
        [logo_center[0] - logo_radius, logo_center[1] - logo_radius,
         logo_center[0] + logo_radius, logo_center[1] + logo_radius],
        fill=(102, 126, 234)
    )

    try:
        logo_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        feature_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22)
    except:
        logo_font = title_font = subtitle_font = feature_font = ImageFont.load_default()

    # Draw "H" in logo
    draw.text((190, 265), "H", fill='white', font=logo_font)

    # Draw title
    draw.text((340, 200), "HoneyConvert", fill='#333333', font=title_font)

    # Draw subtitle
    draw.text((340, 290), "Free HEIC to PNG, JPEG, WebP Converter", fill='#666666', font=subtitle_font)

    # Draw features
    draw.text((340, 370), "No Registration  |  Instant Download  |  100% Free", fill=(102, 126, 234), font=feature_font)

    # Draw conversion info
    draw.text((340, 430), "Convert iPhone Photos: HEIC/HEIF > PNG | JPEG | WebP", fill='#888888', font=feature_font)

    return img

if __name__ == '__main__':
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    os.makedirs(static_dir, exist_ok=True)

    print("Generating favicon.png...")
    favicon = create_favicon()
    favicon.save(os.path.join(static_dir, 'favicon.png'), 'PNG')

    print("Generating apple-touch-icon.png...")
    apple_icon = create_apple_touch_icon()
    apple_icon.save(os.path.join(static_dir, 'apple-touch-icon.png'), 'PNG')

    print("Generating og-image.png...")
    og_image = create_og_image()
    og_image.save(os.path.join(static_dir, 'og-image.png'), 'PNG')

    print("Done! All assets generated in static/")
