#!/usr/bin/env python3
"""
🧪 LOCAL TESTER FOR MATT'S DATASET LOADING
Tests the Matt's dataset loading functions locally without RunPod

This tests:
- Image validation with PIL
- Matt's dataset loading from 10_Matt folder
- Base64 encoding/decoding
- File validation
"""

import sys
import os

# Add the current directory to Python path to import handler functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from handler import load_matt_dataset, validate_image, handle_upload_training_data
import base64
import tempfile
import shutil

def test_matt_dataset_loading():
    """Test loading Matt's dataset locally."""
    print("🧪 TESTING MATT'S DATASET LOADING LOCALLY")
    print("=" * 50)
    
    print("\n📁 Testing load_matt_dataset() function...")
    
    try:
        matt_files = load_matt_dataset()
        
        if not matt_files:
            print("❌ No files loaded from Matt's dataset")
            return False
        
        print(f"✅ Loaded {len(matt_files)} files from Matt's dataset")
        
        image_count = 0
        caption_count = 0
        validation_errors = []
        
        # Analyze loaded files
        for file_info in matt_files:
            filename = file_info.get('filename', 'unknown')
            content = file_info.get('content', '')
            content_type = file_info.get('content_type', 'unknown')
            
            print(f"\n📄 File: {filename}")
            print(f"   📊 Type: {content_type}")
            print(f"   📏 Base64 size: {len(content)} characters")
            
            # Decode and validate
            try:
                file_data = base64.b64decode(content)
                print(f"   📦 Decoded size: {len(file_data)} bytes")
                
                # Validate images
                if filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                    is_valid, width, height, error_msg = validate_image(file_data, filename)
                    
                    if is_valid:
                        print(f"   🖼️ Image: {width}x{height} - ✅ VALID")
                        image_count += 1
                    else:
                        print(f"   🖼️ Image: ❌ INVALID - {error_msg}")
                        validation_errors.append(f"{filename}: {error_msg}")
                
                elif filename.endswith('.txt'):
                    try:
                        text_content = file_data.decode('utf-8')
                        print(f"   📝 Caption: {len(text_content)} chars - '{text_content[:50]}{'...' if len(text_content) > 50 else ''}'")
                        caption_count += 1
                    except UnicodeDecodeError:
                        print(f"   📝 Caption: ❌ Cannot decode UTF-8")
                        validation_errors.append(f"{filename}: Cannot decode text file")
                
            except Exception as e:
                print(f"   ❌ Failed to process: {e}")
                validation_errors.append(f"{filename}: {e}")
        
        print(f"\n📊 SUMMARY:")
        print(f"   🖼️ Valid images: {image_count}")
        print(f"   📝 Valid captions: {caption_count}")
        print(f"   ⚠️ Validation errors: {len(validation_errors)}")
        
        if validation_errors:
            print(f"\n❌ VALIDATION ERRORS:")
            for error in validation_errors:
                print(f"   - {error}")
        
        return image_count > 0 and len(validation_errors) == 0
        
    except Exception as e:
        print(f"❌ Exception while loading Matt's dataset: {e}")
        return False

def test_upload_training_data_with_matt():
    """Test the full upload_training_data function with Matt's data."""
    print("\n🔄 TESTING FULL UPLOAD PROCESS WITH MATT'S DATA")
    print("=" * 50)
    
    try:
        # Load Matt's files
        matt_files = load_matt_dataset()
        
        if not matt_files:
            print("❌ No Matt's files to test with")
            return False
        
        # Create test input
        job_input = {
            "training_name": "local_matt_test",
            "trigger_word": "Matt",
            "cleanup_existing": True,
            "files": matt_files
        }
        
        # Set up temporary workspace
        original_workspace = os.environ.get("WORKSPACE_PATH")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Set temporary workspace
            os.environ["WORKSPACE_PATH"] = temp_dir
            print(f"📁 Using temporary workspace: {temp_dir}")
            
            # Test the upload function
            result = handle_upload_training_data(job_input)
            
            print(f"\n📊 UPLOAD RESULT:")
            print(f"   Status: {result.get('status', 'unknown')}")
            print(f"   Images: {result.get('total_images', 0)}")
            print(f"   Captions: {result.get('total_captions', 0)}")
            print(f"   Worker ID: {result.get('worker_id', 'unknown')}")
            print(f"   Training folder: {result.get('training_folder', 'unknown')}")
            
            validation_errors = result.get('validation_errors', [])
            if validation_errors:
                print(f"   ⚠️ Validation errors: {len(validation_errors)}")
                for error in validation_errors[:3]:  # Show first 3
                    print(f"      - {error}")
            
            # Check if files were actually created
            training_folder = result.get('training_folder')
            if training_folder and os.path.exists(training_folder):
                files_created = os.listdir(training_folder)
                print(f"   📁 Files created: {len(files_created)}")
                
                # Check specific files
                for filename in files_created[:5]:  # Show first 5
                    file_path = os.path.join(training_folder, filename)
                    file_size = os.path.getsize(file_path)
                    print(f"      - {filename} ({file_size} bytes)")
            
            success = result.get('status') == 'success' and result.get('total_images', 0) > 0
            
        # Restore original workspace
        if original_workspace:
            os.environ["WORKSPACE_PATH"] = original_workspace
        elif "WORKSPACE_PATH" in os.environ:
            del os.environ["WORKSPACE_PATH"]
        
        return success
        
    except Exception as e:
        print(f"❌ Exception during upload test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bad_image_validation():
    """Test validation with intentionally bad images."""
    print("\n🚫 TESTING BAD IMAGE VALIDATION")
    print("=" * 50)
    
    try:
        # Test 1: 1x1 pixel image (like in the logs)
        bad_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAACXBIWXMAAAsTAAALEwEAmpwYAAAACklEQVR4nGNgYGAAAAAEAAFdzNuNAAAAAElFTkSuQmCC"
        bad_image_data = base64.b64decode(bad_image_b64)
        
        print("🧪 Testing 1x1 pixel image...")
        is_valid, width, height, error_msg = validate_image(bad_image_data, "test_1x1.png")
        
        if not is_valid:
            print(f"   ✅ Correctly rejected: {error_msg}")
            print(f"   📐 Detected dimensions: {width}x{height}")
        else:
            print(f"   ❌ Should have rejected 1x1 image but didn't")
            return False
        
        # Test 2: Corrupted data
        print("\n🧪 Testing corrupted image data...")
        corrupted_data = b"this is not an image"
        is_valid, width, height, error_msg = validate_image(corrupted_data, "corrupted.jpg")
        
        if not is_valid:
            print(f"   ✅ Correctly rejected: {error_msg}")
        else:
            print(f"   ❌ Should have rejected corrupted data but didn't")
            return False
        
        # Test 3: Too small file
        print("\n🧪 Testing too small file...")
        tiny_data = b"tiny"
        is_valid, width, height, error_msg = validate_image(tiny_data, "tiny.jpg")
        
        if not is_valid:
            print(f"   ✅ Correctly rejected: {error_msg}")
        else:
            print(f"   ❌ Should have rejected tiny file but didn't")
            return False
        
        print(f"\n✅ All validation tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Exception during validation test: {e}")
        return False

def main():
    """Run all local tests."""
    print("🧪 RUNNING LOCAL MATT'S DATASET TESTS")
    print("=" * 80)
    
    results = {}
    
    # Test 1: Basic dataset loading
    results['dataset_loading'] = test_matt_dataset_loading()
    
    # Test 2: Bad image validation
    results['validation'] = test_bad_image_validation()
    
    # Test 3: Full upload process
    if results['dataset_loading']:
        results['full_upload'] = test_upload_training_data_with_matt()
    else:
        print("\n❌ Skipping full upload test due to dataset loading failure")
        results['full_upload'] = False
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 LOCAL TEST SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {test_name.upper().replace('_', ' ')}: {status}")
    
    print(f"\n🎯 OVERALL: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL LOCAL TESTS PASSED!")
        print("📋 Ready to test on RunPod with test_fixed_system.py")
    else:
        print("❌ Some local tests failed - fix these before testing on RunPod")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)