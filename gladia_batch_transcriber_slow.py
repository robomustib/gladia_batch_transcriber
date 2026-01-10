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
    print("ERROR: Please check .env file for API Key.")
    exit()

# ===========================
# PREPARATION
# ===========================
base_path = os.getcwd()
input_path = os.path.join(base_path, INPUT_FOLDER)
output_path = os.path.join(base_path, OUTPUT_FOLDER)

# Fallback: Look in current folder if input folder missing
if not os.path.exists(input_path):
    input_path = base_path 

if not os.path.exists(output_path):
    os.makedirs(output_path)

files = [f for f in os.listdir(input_path) if f.lower().endswith(".mp3")]
files.sort()

# ===========================
# START PROCESSING
# ===========================
headers = {"x-gladia-key": API_KEY}

print(f"--> Found {len(files)} files.")
print(f"--> Saving to: {OUTPUT_FOLDER}\n")

skipped_count = 0

for filename in files:
    mp3_path = os.path.join(input_path, filename)
    txt_path = os.path.join(output_path, filename.replace(".mp3", ".txt"))

    # RESUME FUNCTION: Skip if already done
    if os.path.exists(txt_path):
        skipped_count += 1
        # Print only every 10 files to keep log clean, or just silent
        continue

    if skipped_count > 0:
        print(f"--> Skipped {skipped_count} files (already done). Resuming...\n")
        skipped_count = 0 # Reset counter

    print(f"--- Processing: {filename} ---")

    # 1. UPLOAD
    print("   Uploading...", end=" ", flush=True)
    try:
        with open(mp3_path, 'rb') as f:
            payload = {'audio': (filename, f, 'audio/mpeg')}
            # Added timeout to prevent freezing
            response = requests.post(
                'https://api.gladia.io/v2/upload/',
                headers=headers,
                files=payload,
                timeout=60 
            )
        
        if response.status_code == 429:
            print("\n\n STOP: Hourly Limit Reached (429)!")
            print("   The script will stop now. Please wait 1 hour.")
            print("   Restart the script later to continue exactly here.")
            break 

        if response.status_code != 200:
            print(f"\n   UPLOAD ERROR: {response.text}")
            continue
            
        audio_url = response.json().get("audio_url")
        print("OK.")

    except Exception as e:
        print(f"\n   Network error during upload: {e}")
        time.sleep(5)
        continue

    # 2. START TRANSCRIPTION
    print("   Starting...", end=" ", flush=True)
    try:
        response = requests.post(
            'https://api.gladia.io/v2/pre-recorded/',
            headers=headers,
            json={"audio_url": audio_url},
            timeout=30
        )

        if response.status_code == 429:
            print("\n\n STOP: Hourly Limit Reached!")
            break

        if response.status_code != 201:
            print(f"\n   START ERROR: {response.text}")
            continue

        result_url = response.json().get("result_url")
        print("Running.", end=" ", flush=True)

    except Exception as e:
        print(f"\n   Network error during start: {e}")
        continue

    # 3. POLLING (Waiting)
    while True:
        try:
            poll = requests.get(result_url, headers=headers, timeout=30).json()
            status = poll.get("status")

            if status == "done":
                text = poll["result"]["transcription"]["full_transcript"]
                with open(txt_path, "w", encoding="utf-8") as tf:
                    tf.write(text)
                print(f"\n DONE! Saved.")
                break
            
            elif status == "error":
                print(f"\n LADIA ERROR: {poll}")
                break
            
            else:
                print(".", end="", flush=True)
                time.sleep(3)
        except KeyboardInterrupt:
            print("\n\n   Script interrupted by user. Exiting safely.")
            exit()
        except Exception:
            # On network hiccup, just wait a bit and try again
            time.sleep(3)
    
    # Polite pause
    time.sleep(1)

print("\n--- Script finished or stopped ---")
