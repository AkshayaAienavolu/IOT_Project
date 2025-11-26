# Quick Start - Model Conversion

## The Issue
The automatic conversion is failing due to a TensorFlow Decision Forests compatibility issue. This doesn't affect your model - it's just a library conflict.

## Solution: Use the SavedModel That Was Already Created

Your SavedModel was successfully created at `models/ensemble/saved_model/`. We just need to convert it to TensorFlow.js format.

## Option 1: Use Batch Script (Easiest)

Run this in Command Prompt:

```cmd
convert_model.bat
```

## Option 2: Manual Command

Open Command Prompt and run:

```cmd
cd C:\Users\18003\Iot_proj
fer_env\Scripts\activate
set TF_CPP_MIN_LOG_LEVEL=2
fer_env\Scripts\tensorflowjs_converter.exe --input_format tf_saved_model --output_format tfjs_layers_model models/ensemble/saved_model webapp/model
```

## Option 3: Use Python (If Above Fails)

The SavedModel exists, so we can try a different Python approach:

```cmd
cd C:\Users\18003\Iot_proj
fer_env\Scripts\activate
python convert_savedmodel_to_tfjs.py
```

## Verify Conversion

After conversion, check that files exist:

```cmd
dir webapp\model
```

You should see:
- `model.json`
- `weights.bin` (or multiple `.bin` files)

## Then Start Server

Once conversion is successful:

```cmd
cd webapp
python -m http.server 8000
```

Open browser: `http://localhost:8000`

## If All Methods Fail

The SavedModel is ready. You can:
1. Use an online converter
2. Use a different machine/environment
3. The model structure is correct - it's just the conversion tool having issues

The important part (creating the ensemble model) is already done!

