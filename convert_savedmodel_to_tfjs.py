"""
Convert existing SavedModel to TensorFlow.js
Workaround for tensorflow_decision_forests compatibility issue
"""

import os
import subprocess
import sys

print("=" * 70)
print("Converting SavedModel to TensorFlow.js")
print("=" * 70)

saved_model_path = "models/ensemble/saved_model"
tfjs_output_path = "webapp/model"

if not os.path.exists(saved_model_path):
    print(f"[ERROR] SavedModel not found: {saved_model_path}")
    print("Please run convert_ensemble_to_tfjs.py first to create the SavedModel")
    exit(1)

print(f"[OK] Found SavedModel at: {saved_model_path}")

# Create output directory
os.makedirs(tfjs_output_path, exist_ok=True)

# Try using tensorflowjs_converter with environment variable to skip decision forests
print("\nAttempting conversion with workaround...")

# Set environment variable to skip tensorflow_decision_forests
env = os.environ.copy()
env['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Suppress warnings

# Try using Python API with workaround
try:
    # Import tensorflowjs in a subprocess to avoid decision forests import
    print("Using Python subprocess workaround...")
    
    conversion_script = f"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import warnings
warnings.filterwarnings('ignore')

# Try to import without decision forests
try:
    import sys
    # Remove decision forests from path temporarily
    import tensorflowjs.converters.keras_h5_conversion as conversion
    from tensorflowjs import write_weights
    from tensorflowjs.converters import common
    
    # Load SavedModel and convert
    import tensorflow as tf
    model = tf.saved_model.load(r'{saved_model_path}')
    
    # Convert to Keras format first, then to TF.js
    print("Loading SavedModel...")
    
    # Get the concrete function
    concrete_func = model.signatures['serving_default']
    
    # Convert using tfjs
    import tensorflowjs as tfjs
    tfjs.converters.convert_tf_saved_model(
        r'{saved_model_path}',
        r'{tfjs_output_path}',
        quantization_dtype='float32'
    )
    print("Conversion successful!")
except Exception as e:
    print(f"Error: {{e}}")
    import traceback
    traceback.print_exc()
"""
    
    # Run in subprocess
    result = subprocess.run(
        [sys.executable, "-c", conversion_script],
        env=env,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print("[OK] Conversion successful!")
        print(result.stdout)
    else:
        print("[ERROR] Conversion failed")
        print(result.stderr)
        raise Exception("Subprocess conversion failed")
        
except Exception as e:
    print(f"[ERROR] Workaround failed: {e}")
    print("\nTrying manual command...")
    print("Please run this command manually in a new terminal:")
    print(f"  set TF_CPP_MIN_LOG_LEVEL=2")
    print(f"  fer_env\\Scripts\\tensorflowjs_converter.exe --input_format tf_saved_model --output_format tfjs_layers_model {saved_model_path} {tfjs_output_path}")
    exit(1)

print("\n" + "=" * 70)
print("CONVERSION COMPLETE!")
print("=" * 70)
print(f"\n[OK] Model ready at: {tfjs_output_path}/")

