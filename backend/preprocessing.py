import numpy as np
import json

with open('artifacts/static_norm_params.json') as f:
    STATIC_NORM = json.load(f)

with open('artifacts/dynamic_norm_params.json') as f:
    DYNAMIC_NORM = json.load(f)

FLEX_COLS    = ['flex1', 'flex2', 'flex3', 'flex4', 'flex5']
IMU_COLS     = ['ax', 'ay', 'az', 'gx', 'gy', 'gz']
FEATURE_COLS = FLEX_COLS + IMU_COLS  # 11 features total


def normalize_window(raw_window: np.ndarray, sign_type: str) -> np.ndarray:
    norm   = STATIC_NORM if sign_type == 'static' else DYNAMIC_NORM
    data   = raw_window.astype(np.float32).copy()
    ranges = norm['global_ranges']

    # Flex sensors ,global min-max normalization
    for i, col in enumerate(FLEX_COLS):
        mn  = ranges[col]['min']
        mx  = ranges[col]['max']
        rng = mx - mn
        # If sensor range is too small (<5) it is unreliable set neutral 0.5
        data[:, i] = (data[:, i] - mn) / rng if rng > 5 else 0.5

    # IMU  global StandardScaler
    imu_mean  = np.array(norm['imu_mean'])
    imu_scale = np.array(norm['imu_scale'])
    data[:, 5:] = (data[:, 5:] - imu_mean) / imu_scale

    return data


def is_dynamic(raw_window: np.ndarray, threshold: float = 2000.0) -> bool:
    
    gy_std = float(raw_window[:, 9].std())   # col 9 = gy
    gz_std = float(raw_window[:, 10].std())  # col 10 = gz
    return gy_std > threshold or gz_std > threshold