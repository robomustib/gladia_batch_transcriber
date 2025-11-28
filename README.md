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

## Supported Formats

WAV, MP3, M4A, MP4

# Suitable for
- Research data processing
- Bulk audio transcription
- Multilingual datasets
- Qualitative research projects

## Flowchart
<img src="https://github.com/robomustib/gladia_batch_transcriber/blob/main/img/flowchart.svg" alt="Flowchart of Gladia Batch Transcriber" width="50%"/>

# Color Legend

- Green - Successful operations (completion, success statistics, final report)
- Blue - Active processing steps (upload, transcription, file operations)
- Yellow - Waiting states (queue, delays, polling intervals)
- Orange - Error conditions (failures, missing requirements, API errors)
- Pink - Decision points (conditional logic, checks, validations)

## Installation

# 1. Clone the Repository

```bash
git clone https://github.com/robomustib/gladia-batch-transcriber.git
cd gladia-batch-transcriber
```

# 2. Install Dependencies
It is recommended to use a virtual environment.
```bash
pip install -r requirements.txt
```

# 3. Configuration (.env)
Create a file named .env in the root directory. You can use the example below. Crucial: Set the CONCURRENCY_LIMIT according to your Gladia plan to avoid errors.

```python

# Your Gladia API Key (Required)
GLADIA_API_KEY=your_api_key_goes_here

# Concurrency Limit (Simultaneous Uploads)
# Free Tier: max 3
# Paid/Pro Tier: max 25 (Recommended for speed)
CONCURRENCY_LIMIT=3

# Polling Interval in seconds (Default: 10)
POLLING_INTERVAL=10

```

## Usage
Place your audio files into the audio_files directory.

Run the script:
```bash

python gladia_batch_transcriber.py

```

The script will:

- Scan the folder for supported audio formats.
- Display a summary of file types found.
- Start processing and show a progress bar.
- Save all transcripts to the transcripts folder.

## Customization (Languages)

By default, the script is optimized for German, Turkish, and English with Code Switching enabled. To change this, open transcribe.py and modify the TRANSCRIPTION_CONFIG dictionary:
```python
    TRANSCRIPTION_CONFIG = {
        "language_config": {
            # Edit languages here (e.g., add "fr" for French, "es" for Spanish)
            "languages": ["de", "tr", "en"], 
            "code_switching": True,
        },
        "diarization": True, # Detects different speakers
    }

```

## Troubleshooting
- **401 Unauthorized** API Key is missing or invalid.* Check your .env file. Ensure there are no spaces around the key.
- **429 Too Many Requests** Concurrency limit exceeded.* Lower the CONCURRENCY_LIMIT in .env (e.g., set to 3).
- **File is empty (0 Bytes)**	*Corrupt audio file.* Check the source file in audio_files. It might have been copied incorrectly.
- **TimeoutError Processing took > 2 hours** *The file might be extremely large or the API is hanging.* Check your internet connection.

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this software for your research, please cite it as follows:

**APA Format:**
> Bilgin, M. (2025). *Gladia Batch Transcriber* (Version 1.3.1) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.17747599

**BibTeX:**
```bibtex

@software{gladia_batch_transcriber,
  author       = {Bilgin, Mustafa},
  title        = {Gladia Batch Transcriber - Efficient Large-Scale Audio Transcription},
  year         = {2025},
  publisher    = {Zenodo},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.17747599},
  url          = {https://doi.org/10.5281/zenodo.17747599}
}

```
