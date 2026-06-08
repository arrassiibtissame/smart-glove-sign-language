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

# Shared state 
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
    STATIC_LOCKOUT = 600

    def __init__(self):
        self.ring              = deque(maxlen=10)
        self.quiet_count       = 0
        self.lockout_remaining = 0
        self.sign_buffer       = []
        self.in_dynamic        = False

    def push(self, sample: np.ndarray) -> dict | None:
       
        # Always add to ring first 
        self.ring.append(sample)

        # Need at least 10 rows before we can compute gy_std
        if len(self.ring) < 10:
            return None

        recent = np.array(self.ring)
        gy_std = float(recent[:, 9].std())  # col 9 = gy, always on raw data

        #  DYNAMIC PATH 
        # Dynamic takes priority — if the hand is clearly moving,
        # handle it first and skip the static check entirely.

        if gy_std > self.DYNAMIC_START:
            # Hand is moving — dynamic sign territory
            # If a static lockout was running, cancel it — user moved
            self.lockout_remaining = 0
            self.quiet_count       = 0

            if not self.in_dynamic:
                # Sign just started — seed the buffer with the ring context
                self.in_dynamic  = True
                self.sign_buffer = list(recent)
                print(f"▶️ Dynamic sign started (gy_std={gy_std:.0f})")
            else:
                self.sign_buffer.append(sample)

            return None  # still collecting, no prediction yet

        # Still inside a dynamic sign but hand slowing down ─
        if self.in_dynamic:
            self.sign_buffer.append(sample)

            sign_ended = (gy_std < self.DYNAMIC_END
                          and len(self.sign_buffer) >= self.DYNAMIC_MIN)
            timed_out  = len(self.sign_buffer) >= self.DYNAMIC_MAX

            if sign_ended or timed_out:
                raw    = np.array(self.sign_buffer, dtype=np.float32)
                result = predict(raw)
                print(f"⏹️ Dynamic sign complete — {len(self.sign_buffer)} rows")
                # Reset dynamic state completely
                self.in_dynamic  = False
                self.sign_buffer = []
                return result

            return None  # still slowing down, keep collecting

        # STATIC PATH 
        # Only reached when gy_std is low AND no dynamic sign is active.

        # During lockout — ignore everything
        if self.lockout_remaining > 0:
            self.lockout_remaining -= 1
            self.quiet_count        = 0
            
            return None

        # Count consecutive quiet rows
        if gy_std < self.STATIC_QUIET:
            self.quiet_count += 1
        else:
            # Hand is slightly moving (transition between signs)
            # Not quiet enough for static, not loud enough for dynamic
            # Just reset the quiet counter and wait
            self.quiet_count = 0
            return None

        # Once we have enough consecutive quiet rows — static sign ready
        if self.quiet_count >= self.STATIC_NEEDED:
            # Take the current ring contents (last 10 quiet rows)
            raw    = np.array(list(self.ring), dtype=np.float32)
            result = predict(raw)
            print(f"📸 Static sign captured")
            # Start lockout so we don't predict again immediately
            self.lockout_remaining = self.STATIC_LOCKOUT
            self.quiet_count       = 0
            return result

        return None  # still building up quiet rows

    def reset(self):
        """Clear everything — call at start of a new user session."""
        self.ring.clear()
        self.quiet_count       = 0
        self.lockout_remaining = 0
        self.sign_buffer       = []
        self.in_dynamic        = False


# One buffer for the glove session 
_session_buffer = SessionBuffer()


# WEBAPP WEBSOCKET  /ws/ui
# Webapp connects here and waits for results to be pushed.
# useGloveConnection.ts needs ZERO changes.
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


# START / STOP — identical to original backend

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

# GLOVE WEBSOCKET  /ws/glove
# ESP32 connects here and pushes one row at a time, nonstop.
@app.websocket("/ws/glove")
async def glove_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ Glove connected!")
    try:
        while True:
            data = await websocket.receive_json()

            if not is_processing:
                continue

            # Parse the JSON row into a numpy array
            # ESP32 must send keys: flex1-5, ax, ay, az, gx, gy, gz
            try:
                sample = np.array([
                    data["flex1"], data["flex2"],data["flex3"],
                    data["flex4"], data["flex5"],
                    data["ax"],data["ay"],data["az"],
                    data["gx"],data["gy"],data["gz"],
                ], dtype=np.float32)
            except KeyError as e:
                print(f"⚠️ Missing key in glove data: {e}")
                continue

            # Push into buffer — returns None most of the time,
            # only returns a result when a complete sign is captured
            result = _session_buffer.push(sample)

            # Push result to webapp — identical to original backend
            if result and frontend_connection:
                await frontend_connection.send_json({
                    "letter":     result["prediction"],
                    "confidence": result["confidence"]
                })
                print(f"📤 Sent to frontend: {result['prediction']}")

    except WebSocketDisconnect:
        print("❌ Glove disconnected")
