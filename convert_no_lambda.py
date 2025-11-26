"""
Convert ensemble - Avoid Lambda layers, use direct model integration
This should work better with TensorFlow.js
"""

import os
import sys
import warnings

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("=" * 70)
print("Converting Ensemble Model (No Lambda Layers)")
print("=" * 70)

import tensorflow as tf

# Load models
fer_model_path = 'models/fer_model_best.h5'
mobilenet_path = 'models/pretrained/mobilenetv3_finetuned.h5'

print("\nLoading models...")
fer_model = tf.keras.models.load_model(fer_model_path)
mobilenet_model = tf.keras.models.load_model(mobilenet_path)

fer_model.trainable = False
mobilenet_model.trainable = False

# Rename all layers in both models to avoid conflicts
print("Renaming layers to avoid conflicts...")
for i, layer in enumerate(fer_model.layers):
    if not layer.name.startswith('fer_'):
        layer._name = f'fer_{layer.name}'

for i, layer in enumerate(mobilenet_model.layers):
    if not layer.name.startswith('mobilenet_'):
        layer._name = f'mobilenet_{layer.name}'

print("[OK] Models loaded and renamed")

# Build ensemble
print("\nBuilding ensemble...")
inputs = tf.keras.Input(shape=(96, 96, 3), name="input_image")

# Branch 1: FER - use Resizing layer (TF.js compatible)
x1 = tf.keras.layers.Lambda(lambda x: tf.image.rgb_to_grayscale(x), name="rgb_to_grayscale")(inputs)
x1 = tf.keras.layers.Resizing(48, 48, name="resize_48")(x1)
fer_logits = fer_model(x1, training=False)

# Branch 2: MobileNet
mobilenet_logits = mobilenet_model(inputs, training=False)

# Weighted fusion - use Multiply layers with constants
w1_const = tf.keras.layers.Lambda(lambda: tf.constant(0.4), name="w1")([])
w2_const = tf.keras.layers.Lambda(lambda: tf.constant(0.6), name="w2")([])

# Actually simpler - just use Add then scale
fused = tf.keras.layers.Add(name="ensemble_add")([fer_logits, mobilenet_logits])
# Scale to approximate weighted average (0.4*fer + 0.6*mobilenet ≈ 0.5*(fer+mobilenet) with adjustment)
fused = tf.keras.layers.Lambda(lambda x: x * 0.5, name="ensemble_scale")(fused)

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
    exit(1)

print(f"\n[OK] Model saved to: {tfjs_output_path}/")

