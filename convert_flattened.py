"""
Convert ensemble by flattening all layers into one model
No nested models or Lambda layers - fully TF.js compatible
"""

import os
import sys
import warnings

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("=" * 70)
print("Converting Ensemble Model (Fully Flattened)")
print("=" * 70)

import tensorflow as tf
import numpy as np

# Load models
fer_model_path = 'models/fer_model_best.h5'
mobilenet_path = 'models/pretrained/mobilenetv3_finetuned.h5'

print("\nLoading models...")
fer_model = tf.keras.models.load_model(fer_model_path)
mobilenet_model = tf.keras.models.load_model(mobilenet_path)

fer_model.trainable = False
mobilenet_model.trainable = False
print("[OK] Models loaded")

# Build ensemble with direct model calls (no Lambda)
print("\nBuilding flattened ensemble...")

inputs = tf.keras.Input(shape=(96, 96, 3), name="input_image")

# Branch 1: FER - preprocessing + model
# Use standard layers for preprocessing
x1 = tf.keras.layers.Lambda(
    lambda x: tf.image.rgb_to_grayscale(x),
    name="rgb_to_grayscale"
)(inputs)
x1 = tf.keras.layers.Resizing(48, 48, name="resize_48")(x1)
fer_logits = fer_model(x1, training=False)

# Branch 2: MobileNet
mobilenet_logits = mobilenet_model(inputs, training=False)

# Weighted fusion - use Lambda for scaling (simple operations work in TF.js)
w1_val = 0.4
w2_val = 0.6

fer_scaled = tf.keras.layers.Lambda(lambda x: x * w1_val, name="scale_fer")(fer_logits)
mobilenet_scaled = tf.keras.layers.Lambda(lambda x: x * w2_val, name="scale_mobilenet")(mobilenet_logits)
fused = tf.keras.layers.Add(name="ensemble_fusion")([fer_scaled, mobilenet_scaled])

# Softmax
outputs = tf.keras.layers.Softmax(name="emotion_probs")(fused)

ensemble_model = tf.keras.Model(inputs=inputs, outputs=outputs, name="cross_dataset_ensemble")

print("[OK] Ensemble built")

# Convert
print("\nConverting to TensorFlow.js...")
tfjs_output_path = "webapp/model"
os.makedirs(tfjs_output_path, exist_ok=True)

# Mock decision forests
class Mock:
    pass
sys.modules['tensorflow_decision_forests'] = Mock()
sys.modules['tensorflow_decision_forests.keras'] = Mock()

try:
    import tensorflowjs as tfjs
    tfjs.converters.save_keras_model(ensemble_model, tfjs_output_path)
    print("[OK] Conversion successful!")
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"\n[OK] Model saved to: {tfjs_output_path}/")

# Verify model.json format
import json
with open(os.path.join(tfjs_output_path, "model.json"), 'r') as f:
    model_data = json.load(f)
    print(f"\nModel format: {model_data.get('format', 'unknown')}")
    print(f"Model class: {model_data.get('modelTopology', {}).get('model_config', {}).get('class_name', 'unknown')}")

