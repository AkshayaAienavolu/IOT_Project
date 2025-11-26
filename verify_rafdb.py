"""
Verify RAF-DB dataset structure before training
"""

import os

print("=" * 70)
print("RAF-DB Dataset Verification")
print("=" * 70)

# Check raf-db-raw (source)
print("\n1. Checking source (raf-db-raw):")
print("-" * 70)

raw_path = 'data/raf-db-raw'
if os.path.exists(raw_path):
    print(f"✓ Found: {raw_path}")
    for split in ['train', 'test']:
        split_path = os.path.join(raw_path, split)
        if os.path.exists(split_path):
            folders = [f for f in os.listdir(split_path) if os.path.isdir(os.path.join(split_path, f))]
            print(f"  {split}: {folders}")
        else:
            print(f"  ❌ Missing: {split}")
else:
    print(f"❌ Not found: {raw_path}")

# Check raf-db (organized)
print("\n2. Checking organized dataset (raf-db):")
print("-" * 70)

rafdb_path = 'data/raf-db'
expected_emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

if not os.path.exists(rafdb_path):
    print(f"❌ Not found: {rafdb_path}")
    print("\nRun: python organize_rafdb.py")
else:
    print(f"✓ Found: {rafdb_path}")
    
    for split in ['train', 'test']:
        print(f"\n{split.upper()}:")
        split_path = os.path.join(rafdb_path, split)
        
        if not os.path.exists(split_path):
            print(f"  ❌ Missing {split} folder")
            continue
        
        total = 0
        missing = []
        
        for emotion in expected_emotions:
            emotion_path = os.path.join(split_path, emotion)
            if os.path.exists(emotion_path):
                count = len([f for f in os.listdir(emotion_path) 
                            if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                total += count
                status = "✓" if count > 0 else "⚠"
                print(f"  {status} {emotion:10s}: {count:5d} images")
                
                if count == 0:
                    missing.append(emotion)
            else:
                print(f"  ❌ {emotion:10s}: folder missing")
                missing.append(emotion)
        
        print(f"  {'='*20}")
        print(f"  {'TOTAL':10s}: {total:5d} images")
        
        if missing:
            print(f"  ⚠ Missing/empty: {', '.join(missing)}")
        
        if total == 0:
            print(f"\n  ❌ ERROR: No images found in {split}!")

# Check if ready for training
print("\n" + "=" * 70)
print("Training Readiness:")
print("=" * 70)

ready = True

# Check organized dataset exists
if not os.path.exists(rafdb_path):
    print("❌ Organized dataset missing")
    print("   Run: python organize_rafdb.py")
    ready = False
else:
    # Check train folder
    train_path = os.path.join(rafdb_path, 'train')
    if os.path.exists(train_path):
        train_count = sum([len([f for f in os.listdir(os.path.join(train_path, emotion))
                               if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                          for emotion in expected_emotions
                          if os.path.exists(os.path.join(train_path, emotion))])
        
        if train_count > 0:
            print(f"✓ Train set ready: {train_count} images")
        else:
            print("❌ Train set empty")
            ready = False
    else:
        print("❌ Train folder missing")
        ready = False
    
    # Check test folder
    test_path = os.path.join(rafdb_path, 'test')
    if os.path.exists(test_path):
        test_count = sum([len([f for f in os.listdir(os.path.join(test_path, emotion))
                              if f.lower().endswith(('.jpg', '.jpeg', '.png'))])
                         for emotion in expected_emotions
                         if os.path.exists(os.path.join(test_path, emotion))])
        
        if test_count > 0:
            print(f"✓ Test set ready: {test_count} images")
        else:
            print("❌ Test set empty")
            ready = False
    else:
        print("❌ Test folder missing")
        ready = False

# Check prerequisite model
print("\n" + "=" * 70)
print("Prerequisite Check:")
print("=" * 70)

mobilenet_model = 'models/pretrained/mobilenetv3_finetuned.h5'
if os.path.exists(mobilenet_model):
    print(f"✓ ImageNet+FER2013 model ready")
else:
    print(f"❌ ImageNet+FER2013 model missing")
    print(f"   Run: python finetune_mobilenetv3.py")
    ready = False

# Final verdict
print("\n" + "=" * 70)
if ready:
    print("✅ READY TO TRAIN!")
    print("=" * 70)
    print("\nNext step:")
    print("  python finetune_rafdb.py")
else:
    print("❌ NOT READY")
    print("=" * 70)
    print("\nFix the issues above, then run this script again.")