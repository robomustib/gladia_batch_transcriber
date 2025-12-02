# Gladia Batch Transcriber
**Author:** Mustafa Bilgin  

---

## Features

* **Batch Processing:** Automatically processes all files in a folder.
* **Smart Resume:** If the internet drops or the computer crashes, simply restart.  The script detects finished files and only processes the missing ones.
* **Progress Tracking:** Shows a loading bar indicating remaining time.
* **Dual Output:** Saves transcripts as both Text (`.txt`) and JSON (`.json`) files.

## Prerequisites (One-time Setup)

### 1. Install Python
 Your computer needs Python to run this script.

1. Go to [python.org/downloads](https://python.org/downloads).
2. Click the yellow button **"Download Python 3.x"**.
3. **Run the installer.**
> ⚠️ **IMPORTANT:** In the first window, make sure to check the box at the very bottom:  
>  `[x] Add python.exe to PATH`
4.   Click **"Install Now"**.

### 2. Setup the Project
1.   Download this repository (Code -> Download ZIP) and unzip it to your Desktop.
2.  Open the folder `gladia_batch_transcriber-main`.
3.   Create a new folder inside named `audio_files`.
4.   Copy all your audio files (MP3, WAV, M4A) into this new `audio_files` folder.

### 3. Install Dependencies
1.  Open the folder `gladia_batch_transcriber-main`.
2.   Click into the address bar of your file explorer, type `cmd`, and press **Enter** to open the terminal.
3.  Run the following command:

    ```bash
    pip install -r requirements.txt
    ```
    
*(Alternatively: `py -m pip install -r requirements.txt`)*


## Configuration

You need to provide your Gladia API Key.

1. Find the file `.env` in the project folder.
2. Open it with a text editor (Notepad, Editor, etc.).
3. Find the line:

    ```ini
    GLADIA_API_KEY=...
    ```
    
4. Replace `...` with your actual API key (e.g., `847593-hf74-...`).
5. Save and close the file.

> **Note on Limits:**
> * **Free Plan:** Processes 3 files concurrently.
> * **Paid Plan:** You can increase the speed by changing `CONCURRENCY_LIMIT` in the `.env` file to `25`.


## Usage

Whenever you want to transcribe files:

1. Ensure your audio files are in the `audio_files` folder.
2. Open the terminal in the project folder (type `cmd` in the address bar).
3. Run the script:

    ```bash
    python gladia_batch_transcriber.py
    ```

The transcripts will automatically appear in the `transcripts` folder once finished.

---

## Reference

If you use this software, please cite it as:
> Bilgin, M. (2025). Gladia Batch Transcriber (Version 1.3.1) [Computer software].  Zenodo. https://doi.org/10.5281/zenodo.17747599
