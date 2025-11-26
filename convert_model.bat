@echo off
REM Convert SavedModel to TensorFlow.js
REM Workaround for tensorflow_decision_forests compatibility issue

echo ======================================================================
echo Converting SavedModel to TensorFlow.js
echo ======================================================================

REM Set environment variable to suppress warnings
set TF_CPP_MIN_LOG_LEVEL=2

REM Activate environment and run converter
call fer_env\Scripts\activate.bat
fer_env\Scripts\tensorflowjs_converter.exe --input_format tf_saved_model --output_format tfjs_layers_model models/ensemble/saved_model webapp/model

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Conversion successful!
    echo [OK] Model saved to: webapp/model/
) else (
    echo.
    echo [ERROR] Conversion failed
    echo.
    echo Alternative: Try using Python API method
    echo   python convert_ensemble_to_tfjs_simple.py
)

pause

