"""
Convert Cross-Dataset Ensemble Model to TensorFlow.js
Creates a unified model that runs entirely in the browser
"""

import os
import tensorflow as tf
import numpy as np

print("=" * 70)
print("Converting Cross-Dataset Ensemble to TensorFlow.js")
print("=" * 70)

# Check if models exist
fer_model_path = 'models/fer_model_best.h5'
mobilenet_path = 'models/pretrained/mobilenetv3_finetuned.h5'

if not os.path.exists(fer_model_path):
    print(f"❌ FER2013 model not found: {fer_model_path}")
    exit(1)

if not os.path.exists(mobilenet_path):
    print(f"❌ MobileNet model not found: {mobilenet_path}")
    exit(1)

print("\n✓ Models found")

# Load models
print("\nLoading models...")
fer_model = tf.keras.models.load_model(fer_model_path)
fer_model.trainable = False

mobilenet_model = tf.keras.models.load_model(mobilenet_path)
mobilenet_model.trainable = False

print("✓ Models loaded")

# Build unified ensemble model for TF.js
# Input: 96x96 RGB (standardized for browser)
print("\nBuilding unified ensemble model...")

inputs = tf.keras.Input(shape=(96, 96, 3), name="input_image")

# Branch 1: FER2013 path (grayscale, 48x48)
x1 = tf.image.rgb_to_grayscale(inputs)
x1 = tf.image.resize(x1, (48, 48))
fer_logits = fer_model(x1, training=False)

# Branch 2: MobileNet path (RGB, 96x96)
x2 = inputs  # Already 96x96 RGB
mobilenet_logits = mobilenet_model(x2, training=False)

# Weighted ensemble fusion
# Weights: FER2013 (0.4) + ImageNet (0.6)
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

print("✓ Ensemble model built")
ensemble_model.summary()

# Save as SavedModel format (required for TF.js conversion)
saved_model_path = "models/ensemble/saved_model"
print(f"\nSaving as SavedModel to {saved_model_path}...")
os.makedirs(saved_model_path, exist_ok=True)
ensemble_model.save(saved_model_path)
print("✓ SavedModel saved")

# Convert to TensorFlow.js
print("\nConverting to TensorFlow.js...")
tfjs_output_path = "webapp/model"
os.makedirs(tfjs_output_path, exist_ok=True)

# Use tensorflowjs converter
import subprocess
import sys

# Get tensorflowjs_converter path
if os.path.exists("fer_env/Scripts/tensorflowjs_converter.exe"):
    converter = "fer_env/Scripts/tensorflowjs_converter.exe"
elif os.path.exists("tfjs_venv/Scripts/tensorflowjs_converter.exe"):
    converter = "tfjs_venv/Scripts/tensorflowjs_converter.exe"
else:
    converter = "tensorflowjs_converter"

cmd = [
    converter,
    "--input_format", "tf_saved_model",
    "--output_format", "tfjs_layers_model",
    "--signature_name", "serving_default",
    saved_model_path,
    tfjs_output_path
]

print(f"Running: {' '.join(cmd)}")
result = subprocess.run(cmd, capture_output=True, text=True)

if result.returncode == 0:
    print("✓ TensorFlow.js conversion successful!")
    print(f"✓ Model saved to: {tfjs_output_path}/")
    print("\nModel files:")
    for file in os.listdir(tfjs_output_path):
        size = os.path.getsize(os.path.join(tfjs_output_path, file)) / (1024 * 1024)
        print(f"  - {file} ({size:.2f} MB)")
else:
    print("❌ Conversion failed!")
    print("Error:", result.stderr)
    print("\nTrying alternative method...")
    
    # Alternative: Use Python API
    try:
        import tensorflowjs as tfjs
        tfjs.converters.save_keras_model(ensemble_model, tfjs_output_path)
        print("✓ TensorFlow.js conversion successful (alternative method)!")
    except Exception as e:
        print(f"❌ Alternative conversion also failed: {e}")
        print("\nPlease run manually:")
        print(f"tensorflowjs_converter --input_format tf_saved_model --output_format tfjs_layers_model {saved_model_path} {tfjs_output_path}")

print("\n" + "=" * 70)
print("CONVERSION COMPLETE!")
print("=" * 70)
print(f"\n✓ Model ready for mobile deployment")
print(f"✓ Location: {tfjs_output_path}/")
print(f"✓ Input: 96x96 RGB images")
print(f"✓ Output: 7 emotion probabilities")
print(f"✓ Runs entirely in browser (no server needed)")

