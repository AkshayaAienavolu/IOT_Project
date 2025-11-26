"""
Convert SavedModel to TensorFlow.js with workaround for tensorflow_decision_forests
"""

import os
import sys

# Workaround: Patch tensorflow_decision_forests import before tensorflowjs imports it
def patch_decision_forests():
    """Temporarily patch the problematic import"""
    import importlib.util
    
    # Create a dummy module for tensorflow_decision_forests
    spec = importlib.util.spec_from_loader('tensorflow_decision_forests', loader=None)
    dummy_module = importlib.util.module_from_spec(spec)
    
    # Add dummy keras submodule
    dummy_keras = type(sys.modules[__name__])('tensorflow_decision_forests.keras')
    dummy_module.keras = dummy_keras
    
    # Insert into sys.modules before tensorflowjs tries to import it
    sys.modules['tensorflow_decision_forests'] = dummy_module
    sys.modules['tensorflow_decision_forests.keras'] = dummy_keras

print("=" * 70)
print("Converting SavedModel to TensorFlow.js (with workaround)")
print("=" * 70)

saved_model_path = "models/ensemble/saved_model"
tfjs_output_path = "webapp/model"

if not os.path.exists(saved_model_path):
    print(f"[ERROR] SavedModel not found: {saved_model_path}")
    exit(1)

print(f"[OK] Found SavedModel")

# Apply workaround
print("Applying workaround for tensorflow_decision_forests...")
try:
    patch_decision_forests()
except Exception as e:
    print(f"Warning: Could not patch: {e}")

# Now try to import tensorflowjs
print("Importing tensorflowjs...")
try:
    import warnings
    warnings.filterwarnings('ignore')
    
    # Try to import tensorflowjs converters directly
    # Bypass the __init__ that imports decision forests
    from tensorflowjs.converters import keras_h5_conversion
    from tensorflowjs import write_weights
    
    print("[OK] TensorFlow.js imported successfully")
    
    # Load the SavedModel using TensorFlow
    print("Loading SavedModel...")
    import tensorflow as tf
    model = tf.saved_model.load(saved_model_path)
    print("[OK] SavedModel loaded")
    
    # Convert using the low-level API
    print("Converting to TensorFlow.js...")
    os.makedirs(tfjs_output_path, exist_ok=True)
    
    # Use the converter function directly
    from tensorflowjs.converters import tf_saved_model_conversion_v2
    tf_saved_model_conversion_v2.convert_tf_saved_model(
        saved_model_path,
        tfjs_output_path,
        quantization_dtype='float32'
    )
    
    print("[OK] Conversion successful!")
    
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    print("\nTrying alternative: Uninstall tensorflow_decision_forests temporarily")
    print("Run: pip uninstall tensorflow_decision_forests -y")
    print("Then: pip install tensorflowjs")
    exit(1)
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
    for file in os.listdir(tfjs_output_path):
        filepath = os.path.join(tfjs_output_path, file)
        if os.path.isfile(filepath):
            size = os.path.getsize(filepath) / (1024 * 1024)
            print(f"  - {file} ({size:.2f} MB)")

