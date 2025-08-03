#!/usr/bin/env python3
"""
🖼️ MATT DATASET UPLOADER
Upload all Matt photos and captions from 10_Matt folder to LoRA training endpoint.
"""

import os
import base64
import requests
import time
from pathlib import Path
from PIL import Image

# Configuration
ENDPOINT_ID = "8s9y5exor2uidx"  # MODEL-DOWNLOAD endpoint
RUNPOD_TOKEN = "rpa_G4713KLVTYYBJYWPO157LX7VVPGV7NZ2K87SX6B17otl1t"
BASE_URL = f"https://api.runpod.ai/v2/{ENDPOINT_ID}"

headers = {
    'Authorization': f'Bearer {RUNPOD_TOKEN}',
    'Content-Type': 'application/json'
}

def validate_image(image_path: str) -> bool:
    """Validate image dimensions and format."""
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            print(f"   📏 {os.path.basename(image_path)}: {width}x{height} px")
            
            if width <= 0 or height <= 0:
                print(f"   ❌ Invalid dimensions: {width}x{height}")
                return False
                
            if width < 256 or height < 256:
                print(f"   ⚠️ Warning: Very small image {width}x{height}")
                return False
                
            return True
    except Exception as e:
        print(f"   ❌ Cannot validate {image_path}: {e}")
        return False

def encode_file_to_base64(file_path: str) -> str:
    """Encode file to base64."""
    with open(file_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

def load_matt_dataset(dataset_folder: str) -> list:
    """Load all Matt images and captions from folder."""
    dataset_path = Path(dataset_folder)
    
    if not dataset_path.exists():
        print(f"❌ Dataset folder not found: {dataset_folder}")
        return []
    
    print(f"📂 Loading Matt dataset from: {dataset_folder}")
    
    # Find all image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(list(dataset_path.glob(f"*{ext}")))
        image_files.extend(list(dataset_path.glob(f"*{ext.upper()}")))
    
    print(f"🔍 Found {len(image_files)} image files")
    
    files_to_upload = []
    valid_count = 0
    
    for image_file in image_files:
        # Check if corresponding caption exists
        caption_file = image_file.with_suffix('.txt')
        
        if not caption_file.exists():
            print(f"⚠️ Missing caption for {image_file.name}")
            continue
        
        # Validate image
        if not validate_image(str(image_file)):
            print(f"❌ Skipping invalid image: {image_file.name}")
            continue
            
        # Read caption
        with open(caption_file, 'r', encoding='utf-8') as f:
            caption_text = f.read().strip()
        
        if not caption_text:
            print(f"⚠️ Empty caption for {image_file.name}")
            continue
        
        print(f"   ✅ {image_file.name} + {caption_file.name}")
        print(f"      Caption: {caption_text[:60]}{'...' if len(caption_text) > 60 else ''}")
        
        # Encode files
        try:
            image_base64 = encode_file_to_base64(str(image_file))
            caption_base64 = base64.b64encode(caption_text.encode('utf-8')).decode('utf-8')
            
            # Add image
            files_to_upload.append({
                'filename': image_file.name,
                'content': image_base64,
                'content_type': 'image/jpeg' if image_file.suffix.lower() == '.jpg' else f'image/{image_file.suffix[1:].lower()}'
            })
            
            # Add caption
            files_to_upload.append({
                'filename': caption_file.name,
                'content': caption_base64,
                'content_type': 'text/plain'
            })
            
            valid_count += 1
            
        except Exception as e:
            print(f"❌ Error encoding {image_file.name}: {e}")
            continue
    
    print(f"📊 Dataset Summary:")
    print(f"   ✅ Valid image pairs: {valid_count}")
    print(f"   📁 Total files to upload: {len(files_to_upload)}")
    
    return files_to_upload

def upload_matt_dataset():
    """Upload Matt dataset for LoRA training."""
    print("🚀 MATT DATASET UPLOADER")
    print("=" * 50)
    
    # Load dataset
    dataset_folder = "../10_Matt"  # Relative to SimpleBackend folder
    files = load_matt_dataset(dataset_folder)
    
    if not files:
        print("❌ No files to upload!")
        return False
    
    # Prepare upload request
    upload_data = {
        "input": {
            "type": "upload_training_data",
            "training_name": "matt_lora_dataset",
            "trigger_word": "Matt",
            "cleanup_existing": True,
            "files": files
        }
    }
    
    print(f"\n📤 Uploading {len(files)} files to RunPod...")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print(f"📝 Training name: matt_lora_dataset")
    print(f"🏷️ Trigger word: Matt")
    
    try:
        response = requests.post(
            f"{BASE_URL}/runsync",
            headers=headers,
            json=upload_data,
            timeout=300  # 5 minutes timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            output = result.get('output', {})
            
            if output.get('status') == 'success':
                print(f"\n🎉 UPLOAD SUCCESS!")
                print(f"   📁 Training folder: {output.get('training_folder', 'unknown')}")
                print(f"   🖼️ Images uploaded: {output.get('total_images', 0)}")
                print(f"   📝 Captions uploaded: {output.get('total_captions', 0)}")
                print(f"   💾 Total files: {len(output.get('uploaded_files', []))}")
                return True
            else:
                print(f"❌ Upload failed: {output.get('error', 'unknown error')}")
                return False
                
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Upload timeout - files may be too large")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

if __name__ == "__main__":
    success = upload_matt_dataset()
    if success:
        print("\n✅ Ready for LoRA training with Matt's photos!")
    else:
        print("\n❌ Upload failed - check logs above")