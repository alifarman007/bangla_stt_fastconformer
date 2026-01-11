# 🎤 Bangla Speech-to-Text (Local Setup)

## Prerequisites

1. **Python 3.10+** - Check: `python --version`
2. **FFmpeg** - Required for audio processing
3. **CUDA** (optional) - For GPU acceleration

### Install FFmpeg (Windows)

```powershell
# Option 1: Using winget (Windows 11)
winget install FFmpeg

# Option 2: Using Chocolatey
choco install ffmpeg
```

## Setup Instructions

### Step 1: Create Virtual Environment

```bash
# In your project folder
python -m venv venv

# Activate it
venv\Scripts\activate
```

### Step 2: Install PyTorch with CUDA

```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 3: Install Dependencies

```bash
pip install nemo_toolkit[asr] pydub sounddevice soundfile "numpy<2.1.0"
```

## Usage

### Simple Script (Recommended for Testing)

```bash
python simple_stt.py                    # Interactive menu
python simple_stt.py --file audio.wav   # Transcribe file
python simple_stt.py --record           # Record 5 seconds
python simple_stt.py --record --duration 10  # Record 10 seconds
```

### GUI Application

```bash
python bangla_stt_app.py
```

## Troubleshooting

### "FFmpeg not found"
Make sure FFmpeg is installed and in your PATH. Restart terminal after installing.

### "CUDA not available"
- Check: `python -c "import torch; print(torch.cuda.is_available())"`
- Model will still work on CPU (just slower)

### First run is slow
Normal! The model (~463MB) downloads on first run. Subsequent runs are instant.
