# Gladia Batch Transcriber

A robust Python tool for batch audio transcription using the Gladia API. Designed for researchers and developers who need to process multiple audio files efficiently.

## Key Features

**Asynchronous Processing** Uploads and processes multiple files in parallel (asyncio), significantly reducing total wait time compared to sequential processing.
**Robust Error Handling** Automatically handles network timeouts, API server errors, and Rate Limits (429) by implementing smart retry logic and backoff strategies.
**Smart Resume** Skips files that have already been successfully transcribed. If the script is interrupted, simply restart it, and it will pick up exactly where it left off.
**User Feedback** Features a professional progress bar (tqdm) showing real-time status, speed, and estimated time remaining.
**Dual Output** Saves results as both:

- JSON: Full data including timestamps, confidence scores, and speaker diarization.
- TXT: Clean, readable text format (Speaker: Text).

**Multi-Language Ready** Pre-configured for guided language detection (e.g., DE/TR/EN) to improve accuracy in multi-lingual audio.


## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt
```
# 2. Configure API key in .env
```bash
echo "GLADIA_API_KEY=your_key_here" > .env
```

# 3. Add audio files to audio_files/

# 4. Run transcription
python gladia_batch_transcriber.py

## Supported Formats

WAV, MP3, M4A, MP4

# Suitable for
- Research data processing
- Bulk audio transcription
- Multilingual datasets
- Qualitative research projects
