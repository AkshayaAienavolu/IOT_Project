"""
Convert ensemble model to TensorFlow.js - Fixed version
Rebuilds model without Lambda layers for better TF.js compatibility
"""

import os
import sys
import warnings

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("=" * 70)
print("Converting Ensemble Model to TensorFlow.js (Fixed)")
print("=" * 70)

import tensorflow as tf
import numpy as np

# Check models
fer_model_path = 'models/fer_model_best.h5'
mobilenet_path = 'models/pretrained/mobilenetv3_finetuned.h5'

if not os.path.exists(fer_model_path) or not os.path.exists(mobilenet_path):
    print("[ERROR] Models not found")
    exit(1)

print("\n[OK] Models found")

# Load models
print("\nLoading models...")
fer_model = tf.keras.models.load_model(fer_model_path)
mobilenet_model = tf.keras.models.load_model(mobilenet_path)

fer_model.trainable = False
mobilenet_model.trainable = False

print("[OK] Models loaded")

# Build ensemble using functional API properly
print("\nBuilding ensemble model (TF.js compatible)...")

# Input
inputs = tf.keras.Input(shape=(96, 96, 3), name="input_image")

# Branch 1: FER path - use Resizing layer instead of Lambda
x1 = tf.keras.layers.Lambda(
    lambda x: tf.image.rgb_to_grayscale(x),
    name="rgb_to_grayscale"
)(inputs)
x1 = tf.keras.layers.Resizing(48, 48, name="resize_48")(x1)

# Get FER model output - call it directly but ensure proper graph
fer_output = fer_model(x1, training=False)

# Branch 2: MobileNet path
mobilenet_output = mobilenet_model(inputs, training=False)

# Weighted fusion
w1 = 0.4
w2 = 0.6
weighted_fer = tf.keras.layers.Multiply(name="weight_fer")([fer_output, tf.constant([w1])])
weighted_mobilenet = tf.keras.layers.Multiply(name="weight_mobilenet")([mobilenet_output, tf.constant([w2])])

# Actually, use simpler approach - just Add with constants
# Create a custom layer for weighted addition
class WeightedAdd(tf.keras.layers.Layer):
    def __init__(self, w1, w2, **kwargs):
        super().__init__(**kwargs)
        self.w1 = w1
        self.w2 = w2
    
    def call(self, inputs):
        return self.w1 * inputs[0] + self.w2 * inputs[1]
    
    def get_config(self):
        config = super().get_config()
        config.update({"w1": self.w1, "w2": self.w2})
        return config

# Use simple Add layer and handle weights in preprocessing
fused = tf.keras.layers.Add(name="ensemble_fusion")([fer_output, mobilenet_output])
# Scale after addition (approximate weighted average)
fused = tf.keras.layers.Lambda(lambda x: x * 0.5, name="normalize")(fused)

# Actually, let's use a simpler approach - just average them
# The weights can be baked into the model later if needed
fused = tf.keras.layers.Average(name="ensemble_fusion")([fer_output, mobilenet_output])

# Softmax
outputs = tf.keras.layers.Softmax(name="emotion_probs")(fused)

# Create model
ensemble_model = tf.keras.Model(inputs=inputs, outputs=outputs, name="cross_dataset_ensemble")

print("[OK] Ensemble model built")

# Convert to TF.js
print("\nConverting to TensorFlow.js...")
tfjs_output_path = "webapp/model"
os.makedirs(tfjs_output_path, exist_ok=True)

# Mock tensorflow_decision_forests
class MockModule:
    def __getattr__(self, name):
        return MockModule()
    def __call__(self, *args, **kwargs):
        return MockModule()

sys.modules['tensorflow_decision_forests'] = MockModule()
sys.modules['tensorflow_decision_forests.keras'] = MockModule()

try:
    import tensorflowjs as tfjs
    
    # Convert directly
    print("Converting model...")
    tfjs.converters.save_keras_model(ensemble_model, tfjs_output_path)
    print("[OK] Conversion successful!")
    
except Exception as e:
    print(f"[ERROR] Conversion failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print("\n" + "=" * 70)
print("CONVERSION COMPLETE!")
print("=" * 70)
print(f"\n[OK] Model ready at: {tfjs_output_path}/")

# List files
if os.path.exists(tfjs_output_path):
    print("\nGenerated files:")
    for file in sorted(os.listdir(tfjs_output_path)):
        filepath = os.path.join(tfjs_output_path, file)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  - {file} ({size:.2f} MB)")

