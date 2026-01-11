# 🎤 Bangla Speech-to-Text (STT)

High-accuracy Bangla/Bengali speech recognition using NVIDIA NeMo FastConformer. Supports both GUI and CLI interfaces.

## ✨ Features

- **High Accuracy**: Uses `hishab/titu_stt_bn_conformer_large` model (7.9% WER)
- **Two Interfaces**: GUI app + CLI script
- **Flexible Input**: File upload (WAV/MP3/FLAC/OGG/M4A) or microphone recording
- **GPU Accelerated**: CUDA support for fast inference
- **Cross-Platform**: Windows, Ubuntu, macOS

## 📊 Model Information

| Property | Value |
|----------|-------|
| Model | [hishab/titu_stt_bn_conformer_large](https://huggingface.co/hishab/titu_stt_bn_conformer_large) |
| Architecture | Conformer-CTC Large |
| WER (Word Error Rate) | 7.9% |
| Training Data | ~4,400 hours |
| Model Size | ~500 MB (downloaded once, cached locally) |

## 🔧 Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | None (CPU works) | NVIDIA GTX 1050+ (2GB+ VRAM) |
| RAM | 8 GB | 16 GB |
| Storage | 2 GB | 2 GB |

**Tested on**: RTX 2050 (4GB VRAM), 8GB RAM ✅

---

## 🚀 Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/alifarman007/bangla_stt_fastconformer.git
cd bangla_stt_fastconformer
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Activate (choose your OS):
# Windows (PowerShell):
.venv\Scripts\Activate.ps1

# Windows (Git Bash):
source .venv/Scripts/activate

# Ubuntu/macOS:
source .venv/bin/activate
```

### 3. Install PyTorch

**With CUDA (GPU - Recommended):**
```bash
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**CPU Only:**
```bash
pip install torch torchaudio
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Install FFmpeg

<details>
<summary><b>Windows</b></summary>

```powershell
# Using winget (Windows 11)
winget install FFmpeg

# Or using Chocolatey
choco install ffmpeg
```
Restart terminal after installation.
</details>

<details>
<summary><b>Ubuntu/Debian</b></summary>

```bash
sudo apt update && sudo apt install ffmpeg
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
brew install ffmpeg
```
</details>

<details>
<summary><b>Portable (No system install)</b></summary>

```bash
pip install imageio-ffmpeg
```
Then FFmpeg works automatically via Python.
</details>

### 6. Run

```bash
# CLI (recommended for testing)
python simple_stt.py

# GUI Application
python bangla_stt_app.py
```

---

## 📖 Usage

### CLI - Interactive Mode

```bash
python simple_stt.py
```

```
==================================================
🎤 Bangla Speech-to-Text
==================================================

Options:
  1. Transcribe audio file
  2. Record from microphone
  3. Exit

Select option (1/2/3):
```

### CLI - Direct Commands

```bash
# Transcribe a file
python simple_stt.py --file audio.wav

# Record from microphone (default 5 seconds)
python simple_stt.py --record

# Record for specific duration
python simple_stt.py --record --duration 10
```

### GUI Application

```bash
python bangla_stt_app.py
```

Features:
- 📁 File upload with drag & drop
- 🎤 Microphone recording with timer
- 📋 Copy result to clipboard
- ⚡ GPU/CPU auto-detection

---

## 🐍 Python API

```python
import nemo.collections.asr as nemo_asr
import torch

# Load model (downloads once, ~500MB)
model = nemo_asr.models.ASRModel.from_pretrained("hishab/titu_stt_bn_conformer_large")
model.eval()

# Transcribe
with torch.no_grad():
    result = model.transcribe(["audio.wav"])

print(result[0].text)
# Output: আজ আবহাওয়া অনেক সুন্দর
```

---

## 📁 Project Structure

```
bangla_stt_fastconformer/
├── simple_stt.py       # CLI script
├── bangla_stt_app.py   # GUI application
├── requirements.txt    # Dependencies
├── README.md           # This file
├── .gitignore          # Git ignore rules
└── *.wav / *.mp3       # Test audio files
```

---

## ❓ Troubleshooting

### "FFmpeg not found"

- **Windows**: Restart terminal after installing FFmpeg, or add to PATH manually
- **Alternative**: `pip install imageio-ffmpeg`

### "CUDA not available"

```bash
# Check CUDA status
python -c "import torch; print(f'CUDA: {torch.cuda.is_available()}')"
```

Model works on CPU too (just slower). Make sure you installed PyTorch with CUDA support.

### First run is slow

Normal! The model (~500MB) downloads on first run from Hugging Face. Cached at:
- **Windows**: `C:\Users\<username>\.cache\huggingface\`
- **Linux/macOS**: `~/.cache/huggingface/`

### antlr4-python3-runtime build error (Windows)

```bash
pip install antlr4-python3-runtime==4.13.1
pip install -r requirements.txt
```

### Git Bash FFmpeg PATH issue

Add to `~/.bashrc`:
```bash
export PATH="$PATH:/c/Users/<username>/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-8.0.1-full_build/bin"
```
Then: `source ~/.bashrc`

---

## 🎯 Performance

| Audio Type | Expected WER |
|------------|--------------|
| Clean standard Bangla | 6-10% |
| Conversational speech | 10-15% |
| Noisy environment | 15-25% |
| Regional dialects | 20-40% |

---

## 📚 Resources

- **Model**: [hishab/titu_stt_bn_conformer_large](https://huggingface.co/hishab/titu_stt_bn_conformer_large)
- **Framework**: [NVIDIA NeMo](https://github.com/NVIDIA/NeMo)
- **Alternative Model**: [hishab/titu_stt_bn_fastconformer](https://huggingface.co/hishab/titu_stt_bn_fastconformer) (faster, less accurate)

---

## 📄 License

This project uses the [hishab/titu_stt_bn_conformer_large](https://huggingface.co/hishab/titu_stt_bn_conformer_large) model which is licensed under **CC-BY-NC-4.0** (non-commercial use).

---

## 🤝 Contributing

Pull requests welcome! For major changes, please open an issue first.

---

## ⭐ Star History

If this project helped you, please give it a star! ⭐
