import json
import numpy as np
import keras
from keras.models import load_model
from preprocessing import normalize_window, is_dynamic

# Load both models immediately at startup — never inside a function 
print("Loading models...")
static_model  = load_model("artifacts/static_model.keras")
dynamic_model = load_model("artifacts/dynamic_model.keras")

# Load label maps
with open("artifacts/static_label_map.json")  as f: static_labels  = json.load(f)
with open("artifacts/dynamic_label_map.json") as f: dynamic_labels = json.load(f)

# Load normalization params 
with open("artifacts/static_norm_params.json")  as f: static_norm  = json.load(f)
with open("artifacts/dynamic_norm_params.json") as f: dynamic_norm = json.load(f)

print("✅ Model loaded successfully!")

#  Constants 
CONFIDENCE_THRESHOLD = 0.70
STATIC_TIMESTEPS     = 10    # static model expects exactly 10 rows
DYNAMIC_TIMESTEPS    = 40    # dynamic model expects exactly 40 rows
GY_THRESHOLD         = 2000.0


# Main predict function 
def predict(raw_window: np.ndarray):
    try:
        # Step 1 , decide static or dynamic from raw gyroscope std
        dynamic   = is_dynamic(raw_window, threshold=GY_THRESHOLD)
        sign_type = "dynamic" if dynamic else "static"
        model     = dynamic_model  if dynamic else static_model
        labels    = dynamic_labels if dynamic else static_labels
        timesteps = DYNAMIC_TIMESTEPS if dynamic else STATIC_TIMESTEPS

        # Step 2 , validate enough rows were collected
        if len(raw_window) < timesteps:
            print(f"❌ Not enough samples: got {len(raw_window)}, need {timesteps}")
            return None

        # Step 3 ,slice to the correct window size
        window_raw = raw_window[:timesteps]

        # Step 4 , normalize using training params
        window_norm = normalize_window(window_raw, sign_type)
        X           = window_norm.reshape(1, timesteps, 11).astype(np.float32)

        # Step 5, predict
        probs      = model.predict(X, verbose=0)[0]
        pred_idx   = int(probs.argmax())
        confidence = float(probs[pred_idx])
        pred_label = labels[str(pred_idx)]

        print(f"🤖 Prediction: {pred_label} ({confidence:.2f})")

        # Step 6 ,confidence threshold
        if confidence < CONFIDENCE_THRESHOLD:
            return {
                "prediction": "unknown",
                "confidence": round(confidence, 3)
            }

        return {
            "prediction": pred_label,
            "confidence": round(confidence, 3)
        }

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return None