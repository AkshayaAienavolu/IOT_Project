"""
Convert SavedModel to TensorFlow.js Graph format
Graph format handles Lambda layers better than Layers format
"""

import os
import sys
import warnings

warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("=" * 70)
print("Converting SavedModel to TensorFlow.js Graph Format")
print("=" * 70)

saved_model_path = "models/ensemble/saved_model"
tfjs_output_path = "webapp/model"

if not os.path.exists(saved_model_path):
    print(f"[ERROR] SavedModel not found: {saved_model_path}")
    exit(1)

print(f"[OK] Found SavedModel")

# Mock tensorflow_decision_forests
class Mock:
    pass
sys.modules['tensorflow_decision_forests'] = Mock()
sys.modules['tensorflow_decision_forests.keras'] = Mock()

try:
    import tensorflowjs as tfjs
    
    print("Converting to TensorFlow.js Graph format...")
    os.makedirs(tfjs_output_path, exist_ok=True)
    
    # Convert SavedModel - this produces Graph format by default
    tfjs.converters.convert_tf_saved_model(
        saved_model_path,
        tfjs_output_path
    )
    
    print("[OK] Conversion successful (Graph format)!")
    
except Exception as e:
    print(f"[ERROR] Conversion failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"\n[OK] Model saved to: {tfjs_output_path}/")

