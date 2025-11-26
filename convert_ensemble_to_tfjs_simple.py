"""
Convert Cross-Dataset Ensemble Model to TensorFlow.js
Uses Python API directly (avoids tensorflowjs_converter CLI issues)
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

print("[OK] Ensemble model built")
ensemble_model.summary()

# Convert directly using TensorFlow.js Python API
print("\nConverting to TensorFlow.js using Python API...")
tfjs_output_path = "webapp/model"
os.makedirs(tfjs_output_path, exist_ok=True)

try:
    # Try using tensorflowjs Python package
    # Import in a way that avoids tensorflow_decision_forests issues
    import sys
    import warnings
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        import tensorflowjs as tfjs
    
    # Save model as SavedModel first (more reliable)
    saved_model_path = "models/ensemble/saved_model_temp"
    os.makedirs(saved_model_path, exist_ok=True)
    print(f"Saving as SavedModel...")
    ensemble_model.save(saved_model_path)
    print("[OK] SavedModel saved")
    
    # Convert using Python API
    print("Converting SavedModel to TensorFlow.js...")
    tfjs.converters.convert_tf_saved_model(
        saved_model_path,
        tfjs_output_path,
        quantization_dtype='float32'  # Use float32 for better compatibility
    )
    print("[OK] TensorFlow.js conversion successful!")
    
    # Cleanup temp SavedModel
    import shutil
    if os.path.exists(saved_model_path):
        shutil.rmtree(saved_model_path)
        print("[OK] Cleaned up temporary files")
        
except ImportError:
    print("[ERROR] tensorflowjs not installed")
    print("Installing tensorflowjs...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "tensorflowjs"])
    print("[OK] tensorflowjs installed, please run this script again")
    exit(1)
except Exception as e:
    print(f"[ERROR] Conversion failed: {e}")
    print("\nTrying alternative method...")
    
    # Alternative: Save as Keras format and convert
    try:
        # Import tfjs in alternative method
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import tensorflowjs as tfjs
        
        keras_model_path = "models/ensemble/ensemble_model.h5"
        ensemble_model.save(keras_model_path)
        print("[OK] Saved as Keras H5")
        
        # Convert Keras model directly
        print("Converting Keras model to TensorFlow.js...")
        tfjs.converters.save_keras_model(ensemble_model, tfjs_output_path)
        print("[OK] TensorFlow.js conversion successful (Keras method)!")
        
        # Cleanup
        if os.path.exists(keras_model_path):
            os.remove(keras_model_path)
    except NameError:
        # tfjs not imported, try importing again
        try:
            import warnings
            warnings.filterwarnings('ignore')
            import tensorflowjs as tfjs
            tfjs.converters.save_keras_model(ensemble_model, tfjs_output_path)
            print("[OK] TensorFlow.js conversion successful!")
        except Exception as e3:
            print(f"[ERROR] Could not import tensorflowjs: {e3}")
            print("\nPlease install tensorflowjs manually:")
            print("  pip install tensorflowjs")
            exit(1)
    except Exception as e2:
        print(f"[ERROR] Alternative method also failed: {e2}")
        print("\nPlease try installing tensorflowjs:")
        print("  pip install tensorflowjs")
        exit(1)

print("\n" + "=" * 70)
print("CONVERSION COMPLETE!")
print("=" * 70)
print(f"\n[OK] Model ready for mobile deployment")
print(f"[OK] Location: {tfjs_output_path}/")
print(f"[OK] Input: 96x96 RGB images")
print(f"[OK] Output: 7 emotion probabilities")
print(f"[OK] Runs entirely in browser (no server needed)")

# List generated files
print("\nGenerated files:")
if os.path.exists(tfjs_output_path):
    for file in os.listdir(tfjs_output_path):
        filepath = os.path.join(tfjs_output_path, file)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  - {file} ({size:.2f} MB)")

