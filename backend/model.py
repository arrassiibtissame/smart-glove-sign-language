import json
import numpy as np
import tensorflow as tf

#  Load models once when server starts 

print("Loading models...")
static_model  = tf.keras.models.load_model("artifacts/static_model.keras")
dynamic_model = tf.keras.models.load_model("artifacts/dynamic_model.keras")

with open("artifacts/static_norm_params.json")  as f: STATIC_NORM   = json.load(f)
with open("artifacts/dynamic_norm_params.json") as f: DYNAMIC_NORM  = json.load(f)
with open("artifacts/static_label_map.json")    as f: STATIC_LABELS = json.load(f)
with open("artifacts/dynamic_label_map.json")   as f: DYNAMIC_LABELS = json.load(f)

print("✅ Models loaded!")

#  Settings
STATIC_STEPS  = 10   # static model expects 10 rows
DYNAMIC_STEPS = 40   # dynamic model expects 40 rows
CONFIDENCE    = 0.7  # minimum confidence

FLEX_COLS = ["flex1","flex2","flex3","flex4","flex5"]

#  Normalize window 
def normalize(window: np.ndarray, mode: str) -> np.ndarray:
    norm   = STATIC_NORM if mode == "static" else DYNAMIC_NORM
    data   = window.astype(np.float32).copy()
    ranges = norm["global_ranges"]

    # flex → min max normalization
    for i, col in enumerate(FLEX_COLS):
        mn  = ranges[col]["min"]
        mx  = ranges[col]["max"]
        rng = mx - mn
        data[:, i] = (data[:, i] - mn) / rng if rng > 5 else 0.5

    # imu → standard scaler
    mean  = np.array(norm["imu_mean"])
    scale = np.array(norm["imu_scale"])
    data[:, 5:] = (data[:, 5:] - mean) / scale

    return data

#  Main predict function 
def predict(raw: np.ndarray) -> dict | None:
    try:
        n_rows = len(raw)

        if n_rows >= DYNAMIC_STEPS:
            # DYNAMIC 
            window     = raw[-DYNAMIC_STEPS:]
            normalized = normalize(window, "dynamic")
            input_data = normalized.reshape(1, DYNAMIC_STEPS, 11)

            preds      = dynamic_model.predict(input_data, verbose=0)
            pred_idx   = int(np.argmax(preds[0]))
            confidence = float(preds[0][pred_idx])

            if confidence >= CONFIDENCE:
                label = DYNAMIC_LABELS[str(pred_idx)]
                print(f" Dynamic: {label} ({confidence:.2f})")
                return {"prediction": label, "confidence": confidence}

        else:
            # STATIC 
            window     = raw[-STATIC_STEPS:]
            normalized = normalize(window, "static")
            input_data = normalized.reshape(1, STATIC_STEPS, 11)

            preds      = static_model.predict(input_data, verbose=0)
            pred_idx   = int(np.argmax(preds[0]))
            confidence = float(preds[0][pred_idx])

            if confidence >= CONFIDENCE:
                label = STATIC_LABELS[str(pred_idx)]
                print(f" Static: {label} ({confidence:.2f})")
                return {"prediction": label, "confidence": confidence}

        print(f"⚠️ Low confidence: {confidence:.2f}")
        return None

    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return None