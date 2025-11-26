import cv2

print("Testing camera access...")
print("Trying different camera IDs...\n")

for i in range(5):
    print(f"Trying camera ID: {i}")
    cap = cv2.VideoCapture(i)
    
    if cap.isOpened():
        ret, frame = cap.read()
        if ret:
            print(f"✓ Camera {i} works! Frame shape: {frame.shape}")
            
            # Show a test window
            cv2.imshow(f'Camera {i} Test - Press any key to close', frame)
            cv2.waitKey(2000)  # Show for 2 seconds
            cv2.destroyAllWindows()
        else:
            print(f"✗ Camera {i} opened but couldn't read frame")
        cap.release()
    else:
        print(f"✗ Camera {i} not available")
    print()

print("\nTest complete!")