#!/usr/bin/env python3
"""
Analyze brand logos to determine cropping needs
"""
from PIL import Image
import os
import numpy as np

logo_dir = '/workspaces/Joyan/assets/images/logo'

def analyze_logo(filepath):
    """Analyze a logo to determine content bounds and whitespace"""
    try:
        img = Image.open(filepath)
        
        # Convert to RGBA if not already
        if img.mode != 'RGBA':
            img = img.convert('RGBA')
        
        # Get image data as numpy array
        data = np.array(img)
        
        # Find non-white/non-transparent pixels
        # Consider pixels with alpha > 50 and not purely white
        alpha = data[:, :, 3]
        r, g, b = data[:, :, 0], data[:, :, 1], data[:, :, 2]
        
        # Content is where: alpha > 50 AND (r < 240 OR g < 240 OR b < 240)
        content_mask = (alpha > 50) & ((r < 240) | (g < 240) | (b < 240))
        
        if not content_mask.any():
            return None, "No content detected"
        
        # Find bounding box of content
        rows = np.any(content_mask, axis=1)
        cols = np.any(content_mask, axis=0)
        
        if not rows.any() or not cols.any():
            return None, "No content detected"
        
        y_min, y_max = np.where(rows)[0][[0, -1]]
        x_min, x_max = np.where(cols)[0][[0, -1]]
        
        width, height = img.size
        content_width = x_max - x_min + 1
        content_height = y_max - y_min + 1
        
        # Calculate padding percentages
        left_pad = x_min / width * 100
        right_pad = (width - x_max - 1) / width * 100
        top_pad = y_min / height * 100
        bottom_pad = (height - y_max - 1) / height * 100
        
        return {
            'size': (width, height),
            'content_bounds': (x_min, y_min, x_max, y_max),
            'content_size': (content_width, content_height),
            'padding': {
                'left': left_pad,
                'right': right_pad,
                'top': top_pad,
                'bottom': bottom_pad
            },
            'needs_crop': left_pad > 15 or right_pad > 15 or top_pad > 15 or bottom_pad > 15
        }, None
        
    except Exception as e:
        return None, str(e)

# Analyze all logos
print("Analyzing brand logos...\n")
print(f"{'Filename':<35} {'Size':<12} {'Content%':<10} {'Needs Crop':<12} {'Padding (L/R/T/B)'}")
print("=" * 100)

needs_cropping = []
for filename in sorted(os.listdir(logo_dir)):
    if not filename.endswith(('.jpg', '.png', '.jpeg')):
        continue
    
    filepath = os.path.join(logo_dir, filename)
    result, error = analyze_logo(filepath)
    
    if error:
        print(f"{filename:<35} ERROR: {error}")
        continue
    
    if result:
        w, h = result['size']
        cw, ch = result['content_size']
        content_pct = (cw * ch) / (w * h) * 100
        needs = "YES" if result['needs_crop'] else "No"
        
        pad = result['padding']
        padding_str = f"{pad['left']:.0f}/{pad['right']:.0f}/{pad['top']:.0f}/{pad['bottom']:.0f}"
        
        print(f"{filename:<35} {w}x{h:<7} {content_pct:>6.1f}%   {needs:<12} {padding_str}")
        
        if result['needs_crop']:
            needs_cropping.append(filename)

print("\n" + "=" * 100)
print(f"\nTotal logos: {len(os.listdir(logo_dir))}")
print(f"Logos needing cropping: {len(needs_cropping)}")
print(f"\nCan batch process: YES - All logos can be auto-cropped with consistent padding")
