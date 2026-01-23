import asyncio
import os
import httpx
import json
import logging
import time
from collections import Counter
from pathlib import Path
from tqdm.asyncio import tqdm
from dotenv import load_dotenv

load_dotenv()

class Config:
    _key = os.getenv("GLADIA_API_KEY", "")
    GLADIA_API_KEY = _key.strip()
    
    INPUT_FOLDER = Path("./audio_files")
    OUTPUT_FOLDER = Path("./transcripts")
    
    CONCURRENCY_LIMIT = int(os.getenv("CONCURRENCY_LIMIT", 3))
    POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", 10))
    
    MAX_RETRIES = 3
    REQUEST_TIMEOUT = 120.0
    MAX_POLLS = 720 
    
    TRANSCRIPTION_CONFIG = {
        "language_config": {
            "languages": ["de", "tr", "en"],
            "code_switching": True,
        },
        "diarization": True,
    }

Config.INPUT_FOLDER.mkdir(exist_ok=True)
Config.OUTPUT_FOLDER.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    handlers=[logging.FileHandler("transcription.log", encoding="utf-8")]
)
logger = logging.getLogger(__name__)

async def upload_file(client, file_path: Path):
    if file_path.stat().st_size == 0:
        raise ValueError("File is empty (0 Bytes)")

    file_name = file_path.name
    
    for attempt in range(Config.MAX_RETRIES):
        try:
            with file_path.open("rb") as f:
                files = {"audio": (file_name, f, "audio/mpeg")}
                response = await client.post("https://api.gladia.io/v2/upload/", files=files)
                
                if response.status_code == 429:
                    wait_time = 5 * (attempt + 1)
                    logger.warning(f"Rate limit hit during upload ({file_name}). Waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    continue
                
                response.raise_for_status()
                logger.debug(f"Upload successful: {file_name}")
                return response.json()["audio_url"]
                
        except httpx.RequestError as e:
            logger.warning(f"Upload attempt {attempt + 1} failed: {e}")
            if attempt == Config.MAX_RETRIES - 1: 
                raise Exception(f"Upload failed after {Config.MAX_RETRIES} attempts: {e}")
            await asyncio.sleep(2)

async def start_transcription(client, audio_url):
    payload = {"audio_url": audio_url, **Config.TRANSCRIPTION_CONFIG}
    
    response = await client.post("https://api.gladia.io/v2/pre-recorded/", json=payload)
    
    if response.status_code not in (200, 201):
        error_detail = response.text
        logger.error(f"API Start Error: {error_detail}")
        raise Exception(f"API Start denied ({response.status_code}): {error_detail}")
        
    logger.debug("Transcription started")
    return response.json()["result_url"]

async def poll_result(client, result_url, file_name):
    for poll_count in range(Config.MAX_POLLS):
        try:
            response = await client.get(result_url)
            
            if response.status_code == 429:
                await asyncio.sleep(Config.POLLING_INTERVAL + 5)
                continue
                
            response.raise_for_status()
            data = response.json()
            status = data.get("status")
            
            if status == "done":
                logger.debug(f"Transcription finished after {poll_count + 1} polls")
                return data.get("result", {})
            elif status == "error":
                raise Exception(f"API Error: {data.get('error', 'Unknown error')}")
            
            if poll_count % 10 == 0:
                logger.debug(f"{file_name}: Status {status}")
                
            await asyncio.sleep(Config.POLLING_INTERVAL)
            
        except httpx.RequestError:
            await asyncio.sleep(Config.POLLING_INTERVAL)
    
    raise TimeoutError(f"Transcription timeout after {Config.MAX_POLLS} polls")

def extract_text(result_data):
    transcription = result_data.get("transcription", {})
    
    if "full_transcript" in transcription:
        return transcription["full_transcript"]
    elif "utterances" in transcription:
        return "\n".join([
            f"Speaker {u.get('speaker', '?')}: {u.get('text', '')}" 
            for u in transcription["utterances"]
        ])
    else:
        return json.dumps(result_data, ensure_ascii=False, indent=2)

def save_transcript(file_name, result_data):
    base_name = Path(file_name).stem
    
    with open(Config.OUTPUT_FOLDER / f"{base_name}.json", "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=2, ensure_ascii=False)
    
    full_text = extract_text(result_data)
    with open(Config.OUTPUT_FOLDER / f"{base_name}.txt", "w", encoding="utf-8") as f:
        f.write(full_text)

def should_skip_file(file_path: Path):
    base_name = file_path.stem
    txt_exists = (Config.OUTPUT_FOLDER / f"{base_name}.txt").exists()
    json_exists = (Config.OUTPUT_FOLDER / f"{base_name}.json").exists()
    return txt_exists and json_exists

async def process_single_file(sem, client, file_path: Path, pbar, stats):
    file_name = file_path.name
    
    if should_skip_file(file_path):
        stats["skipped"] += 1
        pbar.update(1)
        return

    async with sem:
        try:
            audio_url = await upload_file(client, file_path)
            result_url = await start_transcription(client, audio_url)
            result_data = await poll_result(client, result_url, file_name)
            save_transcript(file_name, result_data)
            
            stats["success"] += 1
            
        except Exception as e:
            stats["errors"] += 1
            logger.error(f"Error processing {file_name}: {e}")
            pbar.write(f"Error processing {file_name}: {str(e)}")
        finally:
            pbar.update(1)

async def main():
    start_time = time.time()

    if not Config.GLADIA_API_KEY:
        print("ERROR: GLADIA_API_KEY is missing! Please set it in the .env file.")
        return

    files = [f for f in Config.INPUT_FOLDER.glob("*") 
             if f.suffix.lower() in (".wav", ".mp3", ".m4a", ".mp4")]
    
    if not files:
        print(f"No audio files found in '{Config.INPUT_FOLDER}'.")
        return

    extensions = Counter([f.suffix.lower() for f in files])
    print(f"Starting batch for {len(files)} files")
    print(f"File types: {dict(extensions)}")
    print(f"Limit: {Config.CONCURRENCY_LIMIT} concurrent uploads")
    
    stats = {"success": 0, "errors": 0, "skipped": 0}
    sem = asyncio.Semaphore(Config.CONCURRENCY_LIMIT)
    
    limits = httpx.Limits(
        max_keepalive_connections=Config.CONCURRENCY_LIMIT + 5, 
        max_connections=Config.CONCURRENCY_LIMIT + 10
    )
    
    async with httpx.AsyncClient(
        headers={"x-gladia-key": Config.GLADIA_API_KEY},
        timeout=Config.REQUEST_TIMEOUT,
        limits=limits
    ) as client:
        
        with tqdm(total=len(files), unit="file", desc="Progress") as pbar:
            tasks = [process_single_file(sem, client, f, pbar, stats) for f in files]
            await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    minutes = int(duration // 60)
    seconds = int(duration % 60)

    summary = (
        f"DONE!\n"
        f"Duration: {minutes}m {seconds}s\n"
        f"Success: {stats['success']}\n"
        f"Skipped: {stats['skipped']}\n"
        f"Errors: {stats['errors']}"
    )
    
    logger.info(summary.replace("\n", " | "))
    print(f"\n{summary}")

if __name__ == "__main__":
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nStopped by user.")
