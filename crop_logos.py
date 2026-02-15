#!/usr/bin/env python3
"""
Batch crop brand logos with consistent padding
"""
from PIL import Image, ImageChops
import os

logo_dir = '/workspaces/Joyan/assets/images/logo'
output_dir = '/workspaces/Joyan/assets/images/logo_cropped'

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

def get_content_bounds(img):
    """Find the bounding box of non-white content in the image"""
    # Convert to RGB if necessary
    if img.mode == 'RGBA':
        # Create a white background
        bg = Image.new('RGB', img.size, (255, 255, 255))
        bg.paste(img, mask=img.split()[3])  # Use alpha as mask
        img = bg
    elif img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Create a white background of the same size
    bg = Image.new('RGB', img.size, (255, 255, 255))
    
    # Get the difference between image and white background
    diff = ImageChops.difference(img, bg)
    
    # Get bounding box of different pixels (non-white content)
    bbox = diff.getbbox()
    
    return bbox

def crop_with_padding(img, padding_percent=8):
    """
    Crop image to content and add consistent padding
    padding_percent: percentage of the content size to add as padding
    """
    # Get content bounding box
    bbox = get_content_bounds(img)
    
    if bbox is None:
        # Image is all white, return as is
        return img
    
    x1, y1, x2, y2 = bbox
    content_width = x2 - x1
    content_height = y2 - y1
    
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
    
    # Make it square by adding padding to the shorter dimension
    width, height = cropped.size
    max_dim = max(width, height)
    
    # Create a new square white image
    square_img = Image.new('RGB' if cropped.mode == 'RGB' else 'RGBA', 
                           (max_dim, max_dim), 
                           (255, 255, 255) if cropped.mode == 'RGB' else (255, 255, 255, 255))
    
    # Paste the cropped image in the center
    offset = ((max_dim - width) // 2, (max_dim - height) // 2)
    if cropped.mode == 'RGBA':
        square_img.paste(cropped, offset, cropped)
    else:
        square_img.paste(cropped, offset)
    
    return square_img

# Process all logos
print("Processing brand logos...\n")
print(f"{'Filename':<35} {'Original':<12} {'Cropped':<12} {'Status'}")
print("=" * 80)

processed = 0
skipped = 0

for filename in sorted(os.listdir(logo_dir)):
    if not filename.endswith(('.jpg', '.png', '.jpeg')):
        continue
    
    try:
        input_path = os.path.join(logo_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        # Open and process image
        img = Image.open(input_path)
        original_size = f"{img.size[0]}x{img.size[1]}"
        
        # Crop with 8% padding
        cropped_img = crop_with_padding(img, padding_percent=8)
        cropped_size = f"{cropped_img.size[0]}x{cropped_img.size[1]}"
        
        # Save as JPG for consistency (convert RGBA to RGB if needed)
        if cropped_img.mode == 'RGBA':
            rgb_img = Image.new('RGB', cropped_img.size, (255, 255, 255))
            rgb_img.paste(cropped_img, mask=cropped_img.split()[3])
            cropped_img = rgb_img
        
        # Save with high quality
        output_filename = filename.replace('.png', '.jpg')
        final_output = os.path.join(output_dir, output_filename)
        cropped_img.save(final_output, 'JPEG', quality=95)
        
        status = "✓ Processed"
        print(f"{filename:<35} {original_size:<12} {cropped_size:<12} {status}")
        processed += 1
        
    except Exception as e:
        print(f"{filename:<35} ERROR: {str(e)}")
        skipped += 1

print("\n" + "=" * 80)
print(f"\nProcessed: {processed} logos")
print(f"Skipped: {skipped} logos")
print(f"\nCropped logos saved to: {output_dir}")
print("\nNext steps:")
print("1. Review the cropped logos in the output directory")
print("2. If satisfied, replace the original logos with: mv assets/images/logo_cropped/* assets/images/logo/")
