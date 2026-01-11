import cv2
import time
from edge_impulse_linux.image import ImageImpulseRunner
import numpy as np
import threading
import subprocess
import signal
import requests
from pushbullet import Pushbullet
import logging

# === CONFIG ===
EIM_MODEL_PATH = '/home/aprem/Detect_fire_project/fire-detection-model-linux-armv7-v8.eim'
IP_STREAM = 'http://192.168.50.17:8080/video'
SAVE_IMAGES = False
RESIZE_DIM = (96, 96)
frame_skip = 5
frame_count = 0
previous_frame = None
frame = None
lock = threading.Lock()

# === GPS Tracking URL ===
URL = 'http://192.168.50.17:5050/get_gps'

# === Logging ===
logging.basicConfig(
    filename='fire_detection.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# === Pushbullet Initialization ===
PB_API_KEY = # Enter your pushbullet API Key in quotes
pb = Pushbullet(PB_API_KEY)

# === Initialize Model ===
try:
    runner = ImageImpulseRunner(EIM_MODEL_PATH)
    model_info = runner.init()
    labels = model_info['model_parameters']['labels']
    print("Model labels:", labels)
except Exception as e:
    print("Failed to initialize model:", e)
    exit(1)

# === Connect to IP Camera ===
cap = cv2.VideoCapture(IP_STREAM)
if not cap.isOpened():
    print("Failed to connect to smartphone stream.")
    if runner:
        runner.stop()
    exit(1)

# === Capture Thread ===
def capture_loop():
    global frame
    while True:
        ret, f = cap.read()
        if ret:
            with lock:
                frame = f

threading.Thread(target=capture_loop, daemon=True).start()

# === Float checker ===
def check_all_floats(obj):
    if isinstance(obj, list):
        return all(check_all_floats(x) for x in obj)
    return isinstance(obj, float)

# === Start Gas Reader as Subprocess ===
def start_gas_reader():
    return subprocess.Popen(
        ['sudo', 'python3', '-u', 'read_gas_value.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )

def read_latest_gas_value(proc):
    try:
        if proc.stdout.readable():
            line = proc.stdout.readline()
            if line and line.strip().isdigit():
                return int(line.strip())
    except Exception as e:
        print("Error reading gas value:", e)
    return None

# === GPS Tracking Function ===
def get_gps_location(retries=5, delay=2):
    url = URL
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                try:
                    gps_json = response.json()
                    lat = gps_json.get("latitude")
                    lon = gps_json.get("longitude")
                    if lat and lon:
                        gps_link = f"https://maps.google.com/?q={lat},{lon}"
                        print(f"📍 GPS Data: {gps_link}")
                        return {
                            "latitude": lat,
                            "longitude": lon,
                            "link": gps_link
                        }
                    else:
                        print("⚠️ GPS fix not yet available.")
                except ValueError:
                    print("❌ Invalid JSON in GPS response.")
            elif response.status_code == 503:
                print("⏳ GPS not ready (503). Retrying...")
            else:
                print(f"❌ Unexpected status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"❌ Error connecting to GPS server: {e}")
        time.sleep(delay)
    print("❌ GPS failed after multiple attempts.")
    return None

# === Send Pushbullet Notification ===
def send_pushbullet_alert(message):
    pb.push_note("Fire Alert!", message)

# === Main Inference Loop ===
try:
    while True:
        with lock:
            if frame is None:
                continue
            current_frame = frame.copy()

        if np.mean(current_frame) < 3:
            print("⚠️ Frame is too dark or blank — skipping.")
            time.sleep(1)
            continue

        if previous_frame is not None:
            diff = cv2.absdiff(current_frame, previous_frame)
            non_zero_count = np.count_nonzero(diff)
            if non_zero_count < 100:
                time.sleep(1)
                continue
        previous_frame = current_frame.copy()

        frame_count += 1
        if frame_count % frame_skip != 0:
            continue

        resized_frame = cv2.resize(current_frame, RESIZE_DIM, interpolation=cv2.INTER_LINEAR)
        gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)
        features = gray_frame.astype(float).flatten().tolist()

        if SAVE_IMAGES:
            filename = f"frame_{frame_count}.jpg"
            cv2.imwrite(filename, resized_frame)
            print(f"Saved {filename}")

        try:
            res = runner.classify(features)
        except Exception as e:
            print("Error during classification:", e)
            continue

        classification = res.get('result', {}).get('classification', {})
        if not classification:
            print("⚠️ No classification result returned.")
            continue

        print("\n--- Fire Detection ---")
        for label in classification:
            print(f"{label}: {classification[label] * 100:.2f}%")

        fire_type = None
        if classification.get("Normal_Fire", 0) > 0.9:
            fire_type = "Normal"
        elif classification.get("Wild_Fire", 0) > 0.9:
            fire_type = "Wild"

        if fire_type:
            print(f"🔥 {fire_type} Fire detected! Initiating gas reading subprocess.")
            logging.info(f"{fire_type} Fire detected!")

            gas_proc = start_gas_reader()
            start_time = time.time()

            try:
                while time.time() - start_time < 40:
                    gas_value = read_latest_gas_value(gas_proc)
                    if gas_value is not None:
                        print(f"MQ-2 Sensor Value: {gas_value}")
                        logging.info(f"MQ-2 Sensor Value: {gas_value}")
                        if gas_value > 60:
                            print("⚠️ Gas level above 70 Triggering emergency response.")
                            gps_data = get_gps_location()
                            if gps_data:
                                msg = (
                                    f"🔥 Fire + gas levels detected!\n"
                                    f"Latitude: {gps_data['latitude']}\n"
                                    f"Longitude: {gps_data['longitude']}\n"
                                    f"Map: {gps_data['link']}"
                                )
                                send_pushbullet_alert(msg)
                            else:
                                send_pushbullet_alert("🔥 Fire + gas levels detected!\n⚠️ Location unavailable.")
                            break
                    time.sleep(1)
            finally:
                try:
                    gas_proc.terminate()
                    gas_proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    gas_proc.kill()
        else:
            print("✅ No fire detected.")
        time.sleep(1)

except KeyboardInterrupt:
    print("Stopped by user.")
except Exception as e:
    print("Unexpected error during video processing:", e)
finally:
    if runner:
        runner.stop()
    cap.release()
