"""
Final conversion script - Workaround for tensorflow_decision_forests issue
Uses direct API calls to avoid the problematic import
"""

import os
import sys
import warnings

# Suppress all warnings
warnings.filterwarnings('ignore')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

print("=" * 70)
print("Converting SavedModel to TensorFlow.js (Final Attempt)")
print("=" * 70)

saved_model_path = "models/ensemble/saved_model"
tfjs_output_path = "webapp/model"

if not os.path.exists(saved_model_path):
    print(f"[ERROR] SavedModel not found: {saved_model_path}")
    exit(1)

print(f"[OK] Found SavedModel at: {saved_model_path}")

# Workaround: Patch tensorflow_decision_forests before importing tensorflowjs
print("Applying import workaround...")

# Create a mock module for tensorflow_decision_forests
class MockModule:
    def __getattr__(self, name):
        return MockModule()
    
    def __call__(self, *args, **kwargs):
        return MockModule()

# Insert mock before tensorflowjs tries to import
sys.modules['tensorflow_decision_forests'] = MockModule()
sys.modules['tensorflow_decision_forests.keras'] = MockModule()

try:
    # Now try to import tensorflowjs
    print("Importing tensorflowjs...")
    import tensorflowjs as tfjs
    print("[OK] TensorFlow.js imported")
    
    # Try to use the converter
    print("Converting SavedModel to TensorFlow.js...")
    os.makedirs(tfjs_output_path, exist_ok=True)
    
    # Use the converter function (correct API)
    tfjs.converters.convert_tf_saved_model(
        saved_model_path,
        tfjs_output_path
    )
    
    print("[OK] Conversion successful!")
    
except Exception as e:
    print(f"[ERROR] Conversion failed: {e}")
    print("\nTrying alternative: Direct Keras model conversion...")
    
    try:
        # Alternative: Load SavedModel, convert to Keras, then to TF.js
        import tensorflow as tf
        
        print("Loading SavedModel...")
        model = tf.saved_model.load(saved_model_path)
        print("[OK] SavedModel loaded")
        
        # Get the concrete function
        if hasattr(model, 'signatures') and 'serving_default' in model.signatures:
            concrete_func = model.signatures['serving_default']
            print("[OK] Found serving_default signature")
        else:
            # Try to get the model directly
            print("Attempting to extract Keras model...")
            # This might not work for all SavedModels
            raise Exception("Cannot extract Keras model from SavedModel")
        
        # Try to convert using tfjs directly on the SavedModel
        # But we need to bypass the import issue
        print("Attempting direct conversion...")
        
        # Use subprocess to run conversion in isolated environment
        import subprocess
        
        # Create a temporary conversion script
        conv_script = f"""
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import warnings
warnings.filterwarnings('ignore')

# Mock tensorflow_decision_forests
import sys
class Mock:
    pass
sys.modules['tensorflow_decision_forests'] = Mock()
sys.modules['tensorflow_decision_forests.keras'] = Mock()

import tensorflowjs as tfjs
tfjs.converters.convert_tf_saved_model(
    r'{os.path.abspath(saved_model_path)}',
    r'{os.path.abspath(tfjs_output_path)}'
)
print("SUCCESS")
"""
        
        # Write temp script
        temp_script = "temp_convert.py"
        with open(temp_script, 'w') as f:
            f.write(conv_script)
        
        # Run in subprocess
        print("Running conversion in subprocess...")
        result = subprocess.run(
            [sys.executable, temp_script],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        # Cleanup
        if os.path.exists(temp_script):
            os.remove(temp_script)
        
        if result.returncode == 0 and "SUCCESS" in result.stdout:
            print("[OK] Conversion successful via subprocess!")
        else:
            print(f"[ERROR] Subprocess conversion failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            raise Exception("All conversion methods failed")
            
    except Exception as e2:
        print(f"[ERROR] Alternative method failed: {e2}")
        print("\n" + "=" * 70)
        print("CONVERSION FAILED - Please use Google Colab")
        print("=" * 70)
        print("\nYour SavedModel is ready at:")
        print(f"  {os.path.abspath(saved_model_path)}")
        print("\nTo convert:")
        print("1. Upload saved_model folder to Google Drive")
        print("2. Open Google Colab")
        print("3. Run:")
        print("   !pip install tensorflowjs")
        print("   import tensorflowjs as tfjs")
        print(f"   tfjs.converters.convert_tf_saved_model('/content/drive/MyDrive/saved_model', '/content/drive/MyDrive/tfjs_model')")
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

