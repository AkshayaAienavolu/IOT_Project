"""
Organize RAF-DB dataset that's already been renamed
Copies from raf-db-raw to raf-db with proper structure
"""

import os
import shutil
from pathlib import Path

print("=" * 70)
print("Organizing RAF-DB Dataset")
print("=" * 70)

# Source and target directories
source_dir = 'data/raf-db-raw'
target_dir = 'data/raf-db'

# Expected emotion folders (standard names)
expected_emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

# Alternative names that might exist
emotion_aliases = {
    'anger': 'angry',
    'happiness': 'happy',
    'sadness': 'sad',
    'surprised': 'surprise',
    'contempt': 'disgust',  # If contempt exists, map to disgust
}

# Check source directory exists
if not os.path.exists(source_dir):
    print(f"ERROR: Source directory not found: {source_dir}")
    print("\nExpected structure:")
    print("data/")
    print("  └── raf-db-raw/")
    print("      ├── train/")
    print("      │   ├── angry/")
    print("      │   ├── disgust/")
    print("      │   ├── fear/")
    print("      │   ├── happy/")
    print("      │   ├── neutral/")
    print("      │   ├── sad/")
    print("      │   └── surprise/")
    print("      └── test/")
    print("          └── (same structure)")
    exit(1)

print(f"✓ Found source directory: {source_dir}")

# Check train/test folders exist
for split in ['train', 'test']:
    split_path = os.path.join(source_dir, split)
    if not os.path.exists(split_path):
        print(f"ERROR: {split} folder not found: {split_path}")
        exit(1)
    print(f"✓ Found {split} folder")

# Create target directory structure
print(f"\nCreating target directory: {target_dir}")
os.makedirs(target_dir, exist_ok=True)

# Copy and organize
total_copied = 0

for split in ['train', 'test']:
    print(f"\n{'='*70}")
    print(f"Processing {split.upper()} set:")
    print('='*70)
    
    split_source = os.path.join(source_dir, split)
    split_target = os.path.join(target_dir, split)
    
    # Get all folders in source
    source_folders = [f for f in os.listdir(split_source) 
                     if os.path.isdir(os.path.join(split_source, f))]
    
    split_total = 0
    
    for folder in source_folders:
        # Normalize folder name
        folder_lower = folder.lower()
        
        # Check if it's an expected emotion or alias
        if folder_lower in expected_emotions:
            target_emotion = folder_lower
        elif folder_lower in emotion_aliases:
            target_emotion = emotion_aliases[folder_lower]
            print(f"  Mapping '{folder}' -> '{target_emotion}'")
        else:
            print(f"  ⚠ Skipping unknown folder: {folder}")
            continue
        
        # Create target folder
        target_folder = os.path.join(split_target, target_emotion)
        os.makedirs(target_folder, exist_ok=True)
        
        # Copy images
        source_folder = os.path.join(split_source, folder)
        image_files = [f for f in os.listdir(source_folder) 
                      if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        copied = 0
        for img_file in image_files:
            src = os.path.join(source_folder, img_file)
            dst = os.path.join(target_folder, img_file)
            
            try:
                shutil.copy2(src, dst)
                copied += 1
            except Exception as e:
                print(f"    Error copying {img_file}: {str(e)}")
        
        split_total += copied
        print(f"  {target_emotion:10s}: {copied:5d} images")
    
    print(f"\n  Total {split}: {split_total} images")
    total_copied += split_total

print("\n" + "=" * 70)
print("Organization Complete!")
print("=" * 70)

# Verify the organized dataset
print("\n📊 Verification:")
print("-" * 70)

for split in ['train', 'test']:
    print(f"\n{split.upper()}:")
    split_path = os.path.join(target_dir, split)
    
    if not os.path.exists(split_path):
        print("  ❌ Folder not created")
        continue
    
    split_total = 0
    for emotion in expected_emotions:
        emotion_path = os.path.join(split_path, emotion)
        if os.path.exists(emotion_path):
            count = len([f for f in os.listdir(emotion_path) 
                        if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
            split_total += count
            status = "✓" if count > 0 else "⚠"
            print(f"  {status} {emotion:10s}: {count:5d} images")
        else:
            print(f"  ❌ {emotion:10s}: folder missing")
    
    print(f"  {'Total':10s}: {split_total:5d} images")

print("\n" + "=" * 70)
print(f"✓ Total images copied: {total_copied}")
print(f"✓ Dataset ready at: {target_dir}")
print("\nNext step: python finetune_rafdb.py")