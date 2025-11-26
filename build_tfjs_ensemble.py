import tensorflow as tf

# -------------------------------
# Load Your Two Models
# -------------------------------
print("Loading FER2013 model...")
fer_model = tf.keras.models.load_model("models/fer_model_best.h5")
fer_model.trainable = False

print("Loading MobileNetV3 (FER+RAF) model...")
multi_model = tf.keras.models.load_model("models/pretrained/mobilenetv3_finetuned.h5")
multi_model.trainable = False

# -------------------------------
# Build TF.js-Compatible Ensemble
# -------------------------------

# Single unified input: 96x96 RGB
inputs = tf.keras.Input(shape=(96, 96, 3), name="input_image")

# ----- Branch 1: FER2013 Path (expects 48×48 GRAY) -----
x1 = tf.image.rgb_to_grayscale(inputs)
x1 = tf.image.resize(x1, (48, 48))
fer_logits = fer_model(x1, training=False)

# ----- Branch 2: MobileNetV3 Path (expects 96×96 RGB) -----
x2 = tf.image.resize(inputs, (96, 96))
multi_logits = multi_model(x2, training=False)

# ----- Weighted Fusion -----
w1 = 0.3
w2 = 0.7
fused_logits = tf.keras.layers.Add(name="weighted_sum")([
    w1 * fer_logits,
    w2 * multi_logits
])

# ----- Final Probabilities -----
outputs = tf.keras.layers.Softmax(name="emotion_probs")(fused_logits)

# -------------------------------
# Create Final Ensemble Model
# -------------------------------
ensemble_model = tf.keras.Model(inputs=inputs, outputs=outputs)
ensemble_model.summary()

# -------------------------------
# Save Model for TF.js Conversion
# -------------------------------
ensemble_model.save("ensemble_tfjs_ready.h5")
print("\n✓ Saved unified TF.js-ready ensemble model:")
print("  ensemble_tfjs_ready.h5")
