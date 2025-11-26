import tensorflow as tf
import os

print("=" * 60)
print("Converting Model to TensorFlow Lite")
print("=" * 60)

# Load the trained model
print("\n[1/3] Loading trained model...")
model = tf.keras.models.load_model('models/fer_model_best.h5')
print("✓ Model loaded successfully")

# Convert to TensorFlow Lite
print("\n[2/3] Converting to TensorFlow Lite format...")
converter = tf.lite.TFLiteConverter.from_keras_model(model)

# Apply optimizations
converter.optimizations = [tf.lite.Optimize.DEFAULT]

# Convert
tflite_model = converter.convert()

# Save TFLite model
print("\n[3/3] Saving TensorFlow Lite model...")
tflite_path = 'models/fer_model.tflite'
with open(tflite_path, 'wb') as f:
    f.write(tflite_model)

# Get file sizes
h5_size = os.path.getsize('models/fer_model_best.h5') / (1024 * 1024)
tflite_size = os.path.getsize(tflite_path) / (1024 * 1024)

print("\n" + "=" * 60)
print("Conversion Complete!")
print("=" * 60)
print(f"Original model size: {h5_size:.2f} MB")
print(f"TFLite model size: {tflite_size:.2f} MB")
print(f"Size reduction: {((h5_size - tflite_size) / h5_size * 100):.1f}%")
print(f"\n✓ TensorFlow Lite model saved to: {tflite_path}")
print("\nThis model can be deployed on mobile devices (Android/iOS)")