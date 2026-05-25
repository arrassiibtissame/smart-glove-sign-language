import asyncio
import numpy as np
from collections import deque
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from model import predict


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

frontend_connection: WebSocket | None = None
is_processing: bool = False


# SESSION BUFFER

class SessionBuffer:

    DYNAMIC_START  = 2000
    DYNAMIC_END    = 500
    DYNAMIC_MIN    = 40
    DYNAMIC_MAX    = 100

    STATIC_QUIET   = 700
    STATIC_NEEDED  = 10
    STATIC_LOCKOUT = 20

    def __init__(self):
        self.ring              = deque(maxlen=10)
        self.quiet_count       = 0
        self.lockout_remaining = 0
        self.sign_buffer       = []
        self.in_dynamic        = False

    def push(self, sample: np.ndarray) -> dict | None:
        # always add to ring first
        self.ring.append(sample)

        # need at least 10 rows before computing gy_std
        if len(self.ring) < 10:
            return None

        recent = np.array(self.ring)
        gy_std = float(recent[:, 9].std())  # col 9 = gy

        # DYNAMIC PATH 
        if gy_std > self.DYNAMIC_START:
            self.lockout_remaining = 0
            self.quiet_count       = 0

            if not self.in_dynamic:
                self.in_dynamic  = True
                self.sign_buffer = list(recent)
                print(f"▶️ Dynamic sign started (gy_std={gy_std:.0f})")
            else:
                self.sign_buffer.append(sample)

            return None

        # Still inside dynamic but slowing down 
        if self.in_dynamic:
            self.sign_buffer.append(sample)

            sign_ended = (gy_std < self.DYNAMIC_END
                          and len(self.sign_buffer) >= self.DYNAMIC_MIN)
            timed_out  = len(self.sign_buffer) >= self.DYNAMIC_MAX

            if sign_ended or timed_out:
                raw    = np.array(self.sign_buffer, dtype=np.float32)
                result = predict(raw)
                print(f"⏹️ Dynamic sign complete — {len(self.sign_buffer)} rows")
                self.in_dynamic  = False
                self.sign_buffer = []
                return result

            return None

        # STATIC PATH 
        if self.lockout_remaining > 0:
            self.lockout_remaining -= 1
            self.quiet_count        = 0
            return None

        if gy_std < self.STATIC_QUIET:
            self.quiet_count += 1
        else:
            self.quiet_count = 0
            return None

        if self.quiet_count >= self.STATIC_NEEDED:
            raw    = np.array(list(self.ring), dtype=np.float32)
            result = predict(raw)
            print("📸 Static sign captured")
            self.lockout_remaining = self.STATIC_LOCKOUT
            self.quiet_count       = 0
            return result

        return None

    def reset(self):
        self.ring.clear()
        self.quiet_count       = 0
        self.lockout_remaining = 0
        self.sign_buffer       = []
        self.in_dynamic        = False


#  One buffer for the glove session 
_session_buffer = SessionBuffer()


@app.websocket("/ws/ui")
async def ui_endpoint(websocket: WebSocket):
    global frontend_connection
    await websocket.accept()
    frontend_connection = websocket
    print("✅ Frontend connected!")
    try:
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        frontend_connection = None
        print("❌ Frontend disconnected")


@app.post("/start")
async def start_processing():
    global is_processing
    is_processing = True
    print("▶️ Started processing glove data")
    return {"message": "Processing started"}


@app.post("/stop")
async def stop_processing():
    global is_processing
    is_processing = False
    print("⏹️ Stopped processing glove data")
    return {"message": "Processing stopped"}


@app.websocket("/ws/glove")
async def glove_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Glove connected!")
    try:
        while True:
            data = await websocket.receive_json()

            if not is_processing:
                continue

            try:
                sample = np.array([
                    data["flex1"], data["flex2"], data["flex3"],
                    data["flex4"], data["flex5"],
                    data.get("ax") or data.get("acc_x"),
                    data.get("ay") or data.get("acc_y"),
                    data.get("az") or data.get("acc_z"),
                    data.get("gx") or data.get("gyro_x"),
                    data.get("gy") or data.get("gyro_y"),
                    data.get("gz") or data.get("gyro_z"),
                ], dtype=np.float32)

            except KeyError as e:
                print(f"⚠️ Missing key in glove data: {e}")
                continue

            result = _session_buffer.push(sample)

            if result and frontend_connection:
                await frontend_connection.send_json({
                    "letter":     result["prediction"],
                    "confidence": result["confidence"]
                })
                print(f" 📤 Sent to frontend: {result['prediction']}")

    except WebSocketDisconnect:
        print("❌ Glove disconnected")

# thsi will be changed becasue it not good to click a button in frontend to reset buffer in backend i already found another way i will use it but after changing the way to reset buffer i will remove this endpoint
@app.post("/reset")
async def reset_buffer():
    _session_buffer.reset()
    print("🔄 Session buffer cleared")
    return {"message": "Buffer reset"}
