#!/usr/bin/env python3
"""
📸 CHECK MATT'S IMAGES - Verify images from 10_Matt folder
This script checks the images locally to ensure they're valid before upload
"""

import os
import sys
from PIL import Image
import glob

def check_matt_images():
    """Check all images in the 10_Matt folder."""
    print("📸 CHECKING MATT'S IMAGES")
    print("=" * 40)
    
    # Look for 10_Matt folder
    matt_folder = None
    possible_paths = [
        "../10_Matt",
        "../../10_Matt", 
        "../../../10_Matt",
        "../../Serverless/10_Matt",
        "../Serverless/10_Matt"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            matt_folder = path
            break
    
    if not matt_folder:
        print("❌ Cannot find 10_Matt folder!")
        print("Searched in:", possible_paths)
        return False
    
    print(f"📁 Found Matt folder: {matt_folder}")
    
    # Find all image files
    image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(glob.glob(os.path.join(matt_folder, ext)))
        image_files.extend(glob.glob(os.path.join(matt_folder, ext.upper())))
    
    if not image_files:
        print("❌ No image files found!")
        return False
    
    print(f"📸 Found {len(image_files)} image files")
    
    # Check each image
    valid_images = 0
    total_size = 0
    
    for img_path in image_files:
        filename = os.path.basename(img_path)
        
        try:
            # Check file size
            file_size = os.path.getsize(img_path)
            total_size += file_size
            
            # Open with PIL
            with Image.open(img_path) as img:
                width, height = img.size
                format_type = img.format
                
                # Check if valid for training
                if width >= 512 and height >= 512 and file_size > 5000:
                    status = "✅"
                    valid_images += 1
                else:
                    status = "⚠️"
                
                print(f"   {status} {filename}")
                print(f"      Size: {width}x{height} | Format: {format_type} | {file_size//1024}KB")
                
                # Check for caption file
                caption_file = img_path.replace('.jpg', '.txt').replace('.jpeg', '.txt').replace('.png', '.txt')
                if os.path.exists(caption_file):
                    with open(caption_file, 'r', encoding='utf-8') as f:
                        caption = f.read().strip()
                    print(f"      Caption: {caption[:50]}{'...' if len(caption) > 50 else ''}")
                else:
                    print(f"      ❌ No caption file found")
                
        except Exception as e:
            print(f"   ❌ {filename} - Error: {e}")
    
    print(f"\n📊 SUMMARY:")
    print(f"   Total images: {len(image_files)}")
    print(f"   Valid for training: {valid_images}")
    print(f"   Total size: {total_size//1024//1024}MB")
    
    if valid_images >= 3:
        print(f"   ✅ Sufficient images for training!")
        return True
    else:
        print(f"   ❌ Need at least 3 valid images")
        return False

if __name__ == "__main__":
    success = check_matt_images()
    
    if success:
        print("\n🎉 IMAGES ARE READY FOR TRAINING!")
    else:
        print("\n❌ IMAGES NEED FIXING")
        
    sys.exit(0 if success else 1)