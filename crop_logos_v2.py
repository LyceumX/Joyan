#!/usr/bin/env python3
"""
Batch crop brand logos ignoring black borders, focusing on center content
"""
from PIL import Image, ImageChops
import os
import numpy as np

logo_dir = '/workspaces/Joyan/assets/images/logo'
output_dir = '/workspaces/Joyan/assets/images/logo_cropped'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def remove_border_and_find_content(img, border_threshold=0.05):
    """
    Remove black/white borders and find the actual logo content
    border_threshold: proportion of image to ignore as potential border
    """
    # Convert to RGB
    if img.mode == 'RGBA':
        bg = Image.new('RGB', img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Convert to numpy array
    data = np.array(img)
    width, height = img.size
    
    # Calculate border size to ignore (5% on each side)
    border_x = int(width * border_threshold)
    border_y = int(height * border_threshold)
    
    # Crop out the border area
    interior_data = data[border_y:height-border_y, border_x:width-border_x]
    
    if interior_data.size == 0:
        return None
    
    # Find content in the interior (not pure white and not pure black borders)
    r, g, b = interior_data[:, :, 0], interior_data[:, :, 1], interior_data[:, :, 2]
    
    # Content is pixels that are:
    # - Not pure white (< 250 in all channels)
    # - Not black borders (if a pixel is very dark, it should be part of logo, not border)
    # We'll use a more sophisticated approach: find pixels that differ from both white and black
    
    is_white = (r > 240) & (g > 240) & (b > 240)
    is_black = (r < 15) & (g < 15) & (b < 15)
    
    # Content is anything that's not pure white or pure black
    content_mask = ~(is_white | is_black)
    
    if not content_mask.any():
        # If no content found, just look for non-white
        content_mask = ~is_white
    
    if not content_mask.any():
        return None
    
    # Find bounding box of content in the interior region
    rows = np.any(content_mask, axis=1)
    cols = np.any(content_mask, axis=0)
    
    if not rows.any() or not cols.any():
        return None
    
    y_indices = np.where(rows)[0]
    x_indices = np.where(cols)[0]
    
    if len(y_indices) == 0 or len(x_indices) == 0:
        return None
    
    # Get bounds relative to interior
    interior_y_min, interior_y_max = y_indices[0], y_indices[-1]
    interior_x_min, interior_x_max = x_indices[0], x_indices[-1]
    
    # Convert back to full image coordinates
    x_min = interior_x_min + border_x
    x_max = interior_x_max + border_x
    y_min = interior_y_min + border_y
    y_max = interior_y_max + border_y
    
    return (x_min, y_min, x_max + 1, y_max + 1)

def crop_with_padding(img, padding_percent=10):
    """
    Crop image to content (ignoring borders) and add consistent padding
    """
    # Get content bounding box (ignoring borders)
    bbox = remove_border_and_find_content(img)
    
    if bbox is None:
        # Couldn't find content, return original
        print("    Warning: Could not detect content, keeping original")
        return img
    
    x1, y1, x2, y2 = bbox
    content_width = x2 - x1
    content_height = y2 - y1
    
    print(f"    Content detected: {content_width}x{content_height} at ({x1},{y1})")
    
    # Calculate padding in pixels
    pad_x = int(content_width * padding_percent / 100)
    pad_y = int(content_height * padding_percent / 100)
    
    # Calculate new bounds with padding
    new_x1 = max(0, x1 - pad_x)
    new_y1 = max(0, y1 - pad_y)
    new_x2 = min(img.size[0], x2 + pad_x)
    new_y2 = min(img.size[1], y2 + pad_y)
    
    # Crop to new bounds
    cropped = img.crop((new_x1, new_y1, new_x2, new_y2))
    
    # Make it square by adding white padding to the shorter dimension
    width, height = cropped.size
    max_dim = max(width, height)
    
    # Create a new square white image
    square_img = Image.new('RGB', (max_dim, max_dim), (255, 255, 255))
    
    # Paste the cropped image in the center
    offset = ((max_dim - width) // 2, (max_dim - height) // 2)
    square_img.paste(cropped, offset)
    
    return square_img

# Process all logos
print("Processing brand logos (ignoring black borders)...\n")
print(f"{'Filename':<35} {'Original':<12} {'Cropped':<12} {'Reduction'}")
print("=" * 85)

processed = 0
skipped = 0

for filename in sorted(os.listdir(logo_dir)):
    if not filename.endswith(('.jpg', '.png', '.jpeg')):
        continue
    
    try:
        input_path = os.path.join(logo_dir, filename)
        
        # Open and process image
        img = Image.open(input_path)
        original_size = f"{img.size[0]}x{img.size[1]}"
        original_pixels = img.size[0] * img.size[1]
        
        print(f"{filename:<35} {original_size:<12}", end=" ")
        
        # Crop with 10% padding
        cropped_img = crop_with_padding(img, padding_percent=10)
        cropped_size = f"{cropped_img.size[0]}x{cropped_img.size[1]}"
        cropped_pixels = cropped_img.size[0] * cropped_img.size[1]
        
        reduction = ((original_pixels - cropped_pixels) / original_pixels * 100) if original_pixels > 0 else 0
        
        print(f"{cropped_size:<12} {reduction:>5.1f}%")
        
        # Convert RGBA to RGB if needed
        if cropped_img.mode == 'RGBA':
            rgb_img = Image.new('RGB', cropped_img.size, (255, 255, 255))
            rgb_img.paste(cropped_img, mask=cropped_img.split()[3])
            cropped_img = rgb_img
        
        # Save with high quality
        output_filename = filename.replace('.png', '.jpg')
        final_output = os.path.join(output_dir, output_filename)
        cropped_img.save(final_output, 'JPEG', quality=95)
        
        processed += 1
        
    except Exception as e:
        print(f"{filename:<35} ERROR: {str(e)}")
        skipped += 1

print("\n" + "=" * 85)
print(f"\nProcessed: {processed} logos")
print(f"Skipped: {skipped} logos")
print(f"\nCropped logos saved to: {output_dir}")
print("\nTo replace originals: mv assets/images/logo_cropped/* assets/images/logo/")
