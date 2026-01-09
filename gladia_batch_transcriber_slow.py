import os
import time
import requests
from dotenv import load_dotenv

# ===========================
# CONFIGURATION
# ===========================
load_dotenv() 

API_KEY = os.getenv("GLADIA_API_KEY")
INPUT_FOLDER = os.getenv("INPUT_FOLDER", "audio_files")
OUTPUT_FOLDER = os.getenv("OUTPUT_FOLDER", "transkripte_output")

if not API_KEY:
    print("ERROR: Please enter the API Key in the .env file!")
    exit()

# ===========================
# PREPARATION
# ===========================
base_path = os.getcwd()
input_path = os.path.join(base_path, INPUT_FOLDER)
output_path = os.path.join(base_path, OUTPUT_FOLDER)

if not os.path.exists(input_path):
    print(f"ERROR: The folder '{INPUT_FOLDER}' is missing.")
    exit()

if not os.path.exists(output_path):
    os.makedirs(output_path)

files = [f for f in os.listdir(input_path) if f.lower().endswith(".mp3")]
files.sort()

print(f"--> Found: {len(files)} files.")
print(f"--> Results will be saved in: '{OUTPUT_FOLDER}'\n")

# ===========================
# START PROCESSING
# ===========================
headers = {"x-gladia-key": API_KEY}

for filename in files:
    mp3_path = os.path.join(input_path, filename)
    txt_path = os.path.join(output_path, filename.replace(".mp3", ".txt"))

    # If text already exists -> Skip (Resume function)
    if os.path.exists(txt_path):
        # We don't print a message to keep the screen clean
        continue

    print(f"--- Processing: {filename} ---")

    # 1. UPLOAD
    print("   Uploading...", end=" ", flush=True)
    try:
        with open(mp3_path, 'rb') as f:
            payload = {'audio': (filename, f, 'audio/mpeg')}
            response = requests.post(
                'https://api.gladia.io/v2/upload/',
                headers=headers,
                files=payload
            )
        
        # CHECK FOR RATE LIMIT (429)
        if response.status_code == 429:
            print("\n\n STOP: Gladia hourly limit reached!")
            print("   You have uploaded too many files in the last hour.")
            print("   --> Wait approx. 60 minutes and restart this script.")
            print("   --> It will automatically resume where it left off.")
            break # Ends the loop immediately

        if response.status_code != 200:
            print(f"\n   UPLOAD ERROR: {response.text}")
            continue
            
        audio_url = response.json().get("audio_url")
        print("OK.")

    except Exception as e:
        print(f"\n   Crash during upload: {e}")
        continue

    # 2. START TRANSCRIPTION
    print("   Starting job...", end=" ", flush=True)
    response = requests.post(
        'https://api.gladia.io/v2/pre-recorded/',
        headers=headers,
        json={
            "audio_url": audio_url,
            "language_behaviour": "automatic",
            "output_format": "txt"
        }
    )

    if response.status_code == 429:
        print("\n\n STOP: Gladia hourly limit reached (during start)!")
        print("   --> Wait approx. 60 minutes and restart.")
        break

    if response.status_code != 201:
        print(f"\n ERROR starting job: {response.text}")
        continue

    result_url = response.json().get("result_url")
    print("running.", end=" ", flush=True)

    # 3. POLLING (Waiting)
    while True:
        try:
            poll = requests.get(result_url, headers=headers).json()
            status = poll.get("status")

            if status == "done":
                text = poll["result"]["transcription"]["full_transcript"]
                with open(txt_path, "w", encoding="utf-8") as tf:
                    tf.write(text)
                print(f"\n DONE! Saved.")
                break
            
            elif status == "error":
                print(f"\n GLADIA ERROR: {poll}")
                break
            
            else:
                print(".", end="", flush=True)
                time.sleep(3)
        except Exception:
            time.sleep(3)
    
    # Short pause between files to be polite to the server
    time.sleep(1)

print("\n--- Script finished (Current progress saved) ---")
