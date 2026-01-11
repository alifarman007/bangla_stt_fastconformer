"""
===============================================================================
🎤 Bangla Speech-to-Text - Simple Version
===============================================================================
Use this to test if everything works before running the full GUI.

Usage:
    python simple_stt.py                     # Interactive menu
    python simple_stt.py --file audio.wav    # Transcribe a file
    python simple_stt.py --record            # Record and transcribe
===============================================================================
"""

import os
import sys
import tempfile
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION
# ============================================================================
MODEL_NAME = "hishab/titu_stt_bn_fastconformer"
SAMPLE_RATE = 16000
RECORD_SECONDS = 5  # Default recording duration

# ============================================================================
# MAIN FUNCTIONS
# ============================================================================

def check_dependencies():
    """Check if all required packages are installed"""
    print("📦 Checking dependencies...")
    
    missing = []
    
    try:
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"   ✅ PyTorch {torch.__version__} ({device.upper()})")
        if device == "cuda":
            print(f"      GPU: {torch.cuda.get_device_name(0)}")
    except ImportError:
        missing.append("torch")
        print("   ❌ PyTorch")
    
    try:
        import nemo.collections.asr
        print("   ✅ NeMo ASR")
    except ImportError:
        missing.append("nemo_toolkit[asr]")
        print("   ❌ NeMo ASR")
    
    try:
        from pydub import AudioSegment
        print("   ✅ Pydub")
    except ImportError:
        missing.append("pydub")
        print("   ❌ Pydub")
    
    try:
        import sounddevice
        print("   ✅ Sounddevice")
    except ImportError:
        missing.append("sounddevice")
        print("   ❌ Sounddevice")
    
    try:
        import soundfile
        print("   ✅ Soundfile")
    except ImportError:
        missing.append("soundfile")
        print("   ❌ Soundfile")
    
    if missing:
        print(f"\n❌ Missing packages: {', '.join(missing)}")
        print("   Run: pip install " + " ".join(missing))
        return False
    
    print("   All dependencies OK!")
    return True


def load_model():
    """Load the ASR model"""
    import nemo.collections.asr as nemo_asr
    
    print(f"\n⏳ Loading model: {MODEL_NAME}")
    print("   (First run downloads ~463MB, please wait...)")
    
    model = nemo_asr.models.ASRModel.from_pretrained(MODEL_NAME)
    model.eval()
    
    print("✅ Model loaded successfully!")
    return model


def transcribe_file(model, audio_path):
    """Transcribe an audio file"""
    import torch
    from pydub import AudioSegment
    
    print(f"\n📁 Processing: {audio_path}")
    
    # Convert to 16kHz mono WAV
    temp_wav = tempfile.mktemp(suffix=".wav")
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1).set_frame_rate(SAMPLE_RATE)
    audio.export(temp_wav, format="wav")
    
    duration = len(audio) / 1000
    print(f"   Duration: {duration:.2f} seconds")
    
    # Transcribe
    print("⏳ Transcribing...")
    with torch.no_grad():
        result = model.transcribe([temp_wav])
    
    # Extract text
    if hasattr(result[0], 'text'):
        text = result[0].text
    else:
        text = str(result[0])
    
    # Cleanup
    os.remove(temp_wav)
    
    return text, duration


def record_audio(duration=RECORD_SECONDS):
    """Record audio from microphone"""
    import sounddevice as sd
    import soundfile as sf
    
    print(f"\n🎤 Recording for {duration} seconds...")
    print("   Speak now!")
    
    # Record
    recording = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype='int16'
    )
    
    # Show countdown
    for i in range(duration, 0, -1):
        print(f"   {i}...", end=" ", flush=True)
        sd.sleep(1000)
    
    sd.wait()  # Wait until recording is finished
    print("\n✅ Recording complete!")
    
    # Save to temp file
    temp_path = tempfile.mktemp(suffix=".wav")
    sf.write(temp_path, recording, SAMPLE_RATE)
    
    return temp_path


def interactive_mode(model):
    """Interactive menu mode"""
    while True:
        print("\n" + "=" * 50)
        print("🎤 Bangla Speech-to-Text")
        print("=" * 50)
        print("\nOptions:")
        print("  1. Transcribe audio file")
        print("  2. Record from microphone")
        print("  3. Exit")
        
        choice = input("\nSelect option (1/2/3): ").strip()
        
        if choice == "1":
            filepath = input("Enter audio file path: ").strip()
            # Remove quotes if present
            filepath = filepath.strip('"').strip("'")
            
            if os.path.exists(filepath):
                text, duration = transcribe_file(model, filepath)
                print("\n" + "=" * 50)
                print("📝 RESULT")
                print("=" * 50)
                print(f"\n🎯 {text}")
                print(f"\n⏱️ Duration: {duration:.2f}s")
            else:
                print(f"❌ File not found: {filepath}")
        
        elif choice == "2":
            try:
                dur = input(f"Recording duration in seconds [{RECORD_SECONDS}]: ").strip()
                dur = int(dur) if dur else RECORD_SECONDS
                
                audio_path = record_audio(dur)
                text, duration = transcribe_file(model, audio_path)
                
                print("\n" + "=" * 50)
                print("📝 RESULT")
                print("=" * 50)
                print(f"\n🎯 {text}")
                print(f"\n⏱️ Duration: {duration:.2f}s")
                
                # Cleanup
                os.remove(audio_path)
                
            except Exception as e:
                print(f"❌ Recording failed: {e}")
        
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid option!")


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 60)
    print("🎤 Bangla Speech-to-Text")
    print("   Model: hishab/titu_stt_bn_fastconformer")
    print("=" * 60)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Parse arguments
    import argparse
    parser = argparse.ArgumentParser(description="Bangla Speech-to-Text")
    parser.add_argument("--file", type=str, help="Audio file to transcribe")
    parser.add_argument("--record", action="store_true", help="Record from microphone")
    parser.add_argument("--duration", type=int, default=5, help="Recording duration (seconds)")
    args = parser.parse_args()
    
    # Load model
    model = load_model()
    
    if args.file:
        # File mode
        if os.path.exists(args.file):
            text, duration = transcribe_file(model, args.file)
            print("\n" + "=" * 50)
            print("📝 RESULT")
            print("=" * 50)
            print(f"\n🎯 {text}")
        else:
            print(f"❌ File not found: {args.file}")
    
    elif args.record:
        # Record mode
        audio_path = record_audio(args.duration)
        text, duration = transcribe_file(model, audio_path)
        print("\n" + "=" * 50)
        print("📝 RESULT")
        print("=" * 50)
        print(f"\n🎯 {text}")
        os.remove(audio_path)
    
    else:
        # Interactive mode
        interactive_mode(model)


if __name__ == "__main__":
    main()
