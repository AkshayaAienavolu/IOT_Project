"""
Convert ensemble model directly to TensorFlow.js Layers format
This avoids SavedModel format issues
"""

import os
import sys
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("=" * 70)
print("Converting Ensemble Model to TensorFlow.js Layers Format")
print("=" * 70)

import tensorflow as tf
import numpy as np

# Check if models exist
fer_model_path = 'models/fer_model_best.h5'
mobilenet_path = 'models/pretrained/mobilenetv3_finetuned.h5'

if not os.path.exists(fer_model_path):
    print(f"[ERROR] FER2013 model not found: {fer_model_path}")
    exit(1)

if not os.path.exists(mobilenet_path):
    print(f"[ERROR] MobileNet model not found: {mobilenet_path}")
    exit(1)

print("\n[OK] Models found")

# Load models
print("\nLoading models...")
fer_model = tf.keras.models.load_model(fer_model_path)
fer_model.trainable = False

mobilenet_model = tf.keras.models.load_model(mobilenet_path)
mobilenet_model.trainable = False

print("[OK] Models loaded")

# Build unified ensemble model with proper layer naming
print("\nBuilding unified ensemble model...")

inputs = tf.keras.Input(shape=(96, 96, 3), name="input_image")

# Branch 1: FER2013 path (grayscale, 48x48)
# Use Lambda layers to avoid direct model calls that cause naming issues
x1 = tf.keras.layers.Lambda(
    lambda x: tf.image.rgb_to_grayscale(x),
    name="rgb_to_grayscale"
)(inputs)
x1 = tf.keras.layers.Lambda(
    lambda x: tf.image.resize(x, (48, 48)),
    name="resize_to_48"
)(x1)

# Wrap FER model in a Lambda to isolate its namespace
fer_logits = tf.keras.layers.Lambda(
    lambda x: fer_model(x, training=False),
    name="fer_model_wrapper"
)(x1)

# Branch 2: MobileNet path (RGB, 96x96)
# Wrap MobileNet model in a Lambda
mobilenet_logits = tf.keras.layers.Lambda(
    lambda x: mobilenet_model(x, training=False),
    name="mobilenet_model_wrapper"
)(inputs)

# Weighted ensemble fusion
w1 = 0.4
w2 = 0.6
fused_logits = tf.keras.layers.Add(name="ensemble_fusion")([
    w1 * fer_logits,
    w2 * mobilenet_logits
])

# Final softmax output
outputs = tf.keras.layers.Softmax(name="emotion_probs")(fused_logits)

# Create final model
ensemble_model = tf.keras.Model(inputs=inputs, outputs=outputs, name="cross_dataset_ensemble")

print("[OK] Ensemble model built")

# Convert directly to TensorFlow.js Layers format
print("\nConverting to TensorFlow.js Layers format...")
tfjs_output_path = "webapp/model"
os.makedirs(tfjs_output_path, exist_ok=True)

# Workaround for tensorflow_decision_forests
class MockModule:
    def __getattr__(self, name):
        return MockModule()
    def __call__(self, *args, **kwargs):
        return MockModule()

sys.modules['tensorflow_decision_forests'] = MockModule()
sys.modules['tensorflow_decision_forests.keras'] = MockModule()

try:
    import tensorflowjs as tfjs
    
    # Save as Keras H5 first, then convert
    temp_h5_path = "models/ensemble/ensemble_temp.h5"
    print("Saving as Keras H5...")
    ensemble_model.save(temp_h5_path)
    print("[OK] Saved as Keras H5")
    
    # Convert Keras model to TensorFlow.js Layers format
    print("Converting to TensorFlow.js Layers format...")
    tfjs.converters.save_keras_model(ensemble_model, tfjs_output_path)
    print("[OK] Conversion successful!")
    
    # Cleanup
    if os.path.exists(temp_h5_path):
        os.remove(temp_h5_path)
        print("[OK] Cleaned up temporary files")
        
except Exception as e:
    print(f"[ERROR] Conversion failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 70)
print("CONVERSION COMPLETE!")
print("=" * 70)
print(f"\n[OK] Model ready at: {tfjs_output_path}/")

# List generated files
if os.path.exists(tfjs_output_path):
    print("\nGenerated files:")
    for file in sorted(os.listdir(tfjs_output_path)):
        filepath = os.path.join(tfjs_output_path, file)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  - {file} ({size:.2f} MB)")

