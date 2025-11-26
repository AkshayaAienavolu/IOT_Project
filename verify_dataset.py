import os

# Check dataset structure
base_path = 'data/fer2013'
emotions = ['angry', 'disgust', 'fear', 'happy', 'neutral', 'sad', 'surprise']

print("=" * 50)
print("FER2013 Dataset Verification")
print("=" * 50)

for split in ['train', 'test']:
    print(f"\n{split.upper()} SET:")
    split_path = os.path.join(base_path, split)
    
    if not os.path.exists(split_path):
        print(f"  ❌ {split} folder not found!")
        continue
    
    total_images = 0
    for emotion in emotions:
        emotion_path = os.path.join(split_path, emotion)
        if os.path.exists(emotion_path):
            count = len([f for f in os.listdir(emotion_path) if f.endswith(('.jpg', '.png'))])
            total_images += count
            print(f"  ✓ {emotion:10s}: {count:5d} images")
        else:
            print(f"  ❌ {emotion:10s}: folder not found")
    
    print(f"  Total: {total_images} images")

print("\n" + "=" * 50)