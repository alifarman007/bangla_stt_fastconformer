"""
===============================================================================
🎤 Bangla Speech-to-Text - GUI Application
===============================================================================
Model: hishab/titu_stt_bn_fastconformer

Features:
- File Upload (WAV, MP3, FLAC, OGG, M4A)
- Microphone Recording (Click Start/Stop)
- GPU Accelerated (auto-detects CUDA)

Usage:
    python bangla_stt_app.py
===============================================================================
"""

import os
import sys
import tempfile
import threading
import time
import warnings
warnings.filterwarnings('ignore')

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# ============================================================================
# CONFIGURATION
# ============================================================================
MODEL_NAME = "hishab/titu_stt_bn_fastconformer"
SAMPLE_RATE = 16000

# ============================================================================
# GUI APPLICATION
# ============================================================================

class BanglaSTTApp:
    def __init__(self):
        self.model = None
        self.is_recording = False
        self.recorded_audio = None
        self.record_thread = None
        
        # Setup GUI
        self.setup_gui()
        
        # Load model in background
        self.load_model_async()
    
    def setup_gui(self):
        """Setup the graphical user interface"""
        self.root = tk.Tk()
        self.root.title("🎤 Bangla Speech-to-Text")
        self.root.geometry("650x580")
        self.root.resizable(True, True)
        
        # Configure styles
        style = ttk.Style()
        style.configure('Title.TLabel', font=('Segoe UI', 14, 'bold'))
        style.configure('Status.TLabel', font=('Segoe UI', 10))
        style.configure('Big.TButton', font=('Segoe UI', 11), padding=8)
        
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # ===== TITLE =====
        title = ttk.Label(main_frame, text="🎤 Bangla Speech-to-Text", style='Title.TLabel')
        title.grid(row=0, column=0, pady=(0, 5))
        
        model_label = ttk.Label(main_frame, text="Model: hishab/titu_stt_bn_fastconformer", 
                               font=('Segoe UI', 8), foreground='gray')
        model_label.grid(row=1, column=0, pady=(0, 15))
        
        # ===== STATUS SECTION =====
        status_frame = ttk.LabelFrame(main_frame, text="System Status", padding="10")
        status_frame.grid(row=2, column=0, sticky="ew", pady=(0, 15))
        status_frame.columnconfigure(0, weight=1)
        
        self.device_label = ttk.Label(status_frame, text="⏳ Checking device...", style='Status.TLabel')
        self.device_label.grid(row=0, column=0, sticky="w")
        
        self.model_status = ttk.Label(status_frame, text="⏳ Loading model...", style='Status.TLabel')
        self.model_status.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=400)
        self.progress.grid(row=2, column=0, sticky="ew", pady=(10, 0))
        self.progress.start()
        
        # ===== FILE UPLOAD SECTION =====
        file_frame = ttk.LabelFrame(main_frame, text="📁 Option 1: Upload Audio File", padding="12")
        file_frame.grid(row=3, column=0, sticky="ew", pady=(0, 15))
        file_frame.columnconfigure(0, weight=1)
        
        self.file_var = tk.StringVar(value="No file selected")
        file_label = ttk.Label(file_frame, textvariable=self.file_var, 
                              font=('Segoe UI', 9), foreground='gray')
        file_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))
        
        btn_frame1 = ttk.Frame(file_frame)
        btn_frame1.grid(row=1, column=0, sticky="w")
        
        self.select_btn = ttk.Button(btn_frame1, text="📂 Select File", 
                                    command=self.select_file, style='Big.TButton')
        self.select_btn.grid(row=0, column=0, padx=(0, 10))
        self.select_btn.state(['disabled'])
        
        self.transcribe_btn = ttk.Button(btn_frame1, text="▶️ Transcribe", 
                                        command=self.transcribe_file, style='Big.TButton')
        self.transcribe_btn.grid(row=0, column=1)
        self.transcribe_btn.state(['disabled'])
        
        # ===== MICROPHONE SECTION =====
        mic_frame = ttk.LabelFrame(main_frame, text="🎤 Option 2: Record from Microphone", padding="12")
        mic_frame.grid(row=4, column=0, sticky="ew", pady=(0, 15))
        mic_frame.columnconfigure(0, weight=1)
        
        self.rec_status = ttk.Label(mic_frame, text="Ready to record", 
                                   style='Status.TLabel', foreground='gray')
        self.rec_status.grid(row=0, column=0, pady=(0, 5))
        
        self.timer_label = ttk.Label(mic_frame, text="⏱️ 0.0s", font=('Segoe UI', 16, 'bold'))
        self.timer_label.grid(row=1, column=0, pady=(0, 10))
        
        btn_frame2 = ttk.Frame(mic_frame)
        btn_frame2.grid(row=2, column=0)
        
        self.start_btn = ttk.Button(btn_frame2, text="🎤 Start Recording", 
                                   command=self.start_recording, style='Big.TButton')
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        self.start_btn.state(['disabled'])
        
        self.stop_btn = ttk.Button(btn_frame2, text="⏹️ Stop Recording", 
                                  command=self.stop_recording, style='Big.TButton')
        self.stop_btn.grid(row=0, column=1)
        self.stop_btn.state(['disabled'])
        
        # ===== RESULT SECTION =====
        result_frame = ttk.LabelFrame(main_frame, text="📝 Transcription Result", padding="10")
        result_frame.grid(row=5, column=0, sticky="nsew", pady=(0, 10))
        result_frame.columnconfigure(0, weight=1)
        result_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)
        
        # Text widget with scrollbar
        text_frame = ttk.Frame(result_frame)
        text_frame.grid(row=0, column=0, sticky="nsew")
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)
        
        self.result_text = tk.Text(text_frame, height=5, width=60, font=('Segoe UI', 11),
                                  wrap=tk.WORD, state='disabled', bg='#f8f8f8')
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=self.result_text.yview)
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.result_text.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Duration and copy button
        bottom_frame = ttk.Frame(result_frame)
        bottom_frame.grid(row=1, column=0, sticky="ew", pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
        
        self.duration_label = ttk.Label(bottom_frame, text="", font=('Segoe UI', 9))
        self.duration_label.grid(row=0, column=0, sticky="w")
        
        self.copy_btn = ttk.Button(bottom_frame, text="📋 Copy", command=self.copy_result)
        self.copy_btn.grid(row=0, column=1, sticky="e")
    
    def load_model_async(self):
        """Load model in background thread"""
        thread = threading.Thread(target=self._load_model, daemon=True)
        thread.start()
    
    def _load_model(self):
        """Load the ASR model"""
        try:
            import torch
            
            # Check device
            device = "cuda" if torch.cuda.is_available() else "cpu"
            device_text = f"✅ Device: {device.upper()}"
            if device == "cuda":
                gpu = torch.cuda.get_device_name(0)
                vram = torch.cuda.get_device_properties(0).total_memory / 1e9
                device_text += f" | {gpu} ({vram:.1f}GB)"
            else:
                device_text += " (GPU not available, using CPU)"
            
            self.root.after(0, lambda: self.device_label.configure(text=device_text))
            
            # Load model
            import nemo.collections.asr as nemo_asr
            self.model = nemo_asr.models.ASRModel.from_pretrained(MODEL_NAME)
            self.model.eval()
            
            # Update UI
            self.root.after(0, self._on_model_loaded)
            
        except Exception as e:
            self.root.after(0, lambda: self._on_model_error(str(e)))
    
    def _on_model_loaded(self):
        """Called when model is loaded"""
        self.progress.stop()
        self.progress.grid_remove()
        self.model_status.configure(text="✅ Model loaded! Ready to transcribe.")
        
        # Enable buttons
        self.select_btn.state(['!disabled'])
        self.start_btn.state(['!disabled'])
    
    def _on_model_error(self, error):
        """Called on model load error"""
        self.progress.stop()
        self.model_status.configure(text=f"❌ Error: {error}", foreground='red')
        messagebox.showerror("Error", f"Failed to load model:\n{error}")
    
    def select_file(self):
        """Open file selection dialog"""
        filetypes = [
            ("Audio Files", "*.wav *.mp3 *.flac *.ogg *.m4a *.wma"),
            ("WAV", "*.wav"),
            ("MP3", "*.mp3"),
            ("All Files", "*.*")
        ]
        
        path = filedialog.askopenfilename(title="Select Audio File", filetypes=filetypes)
        
        if path:
            self.selected_file = path
            self.file_var.set(f"Selected: {os.path.basename(path)}")
            self.transcribe_btn.state(['!disabled'])
    
    def transcribe_file(self):
        """Transcribe the selected file"""
        if not hasattr(self, 'selected_file'):
            return
        
        self._set_result("⏳ Transcribing...")
        self._disable_buttons()
        
        def _do_transcribe():
            try:
                text, duration = self._transcribe(self.selected_file)
                self.root.after(0, lambda: self._show_result(text, duration))
            except Exception as e:
                self.root.after(0, lambda: self._show_error(str(e)))
            finally:
                self.root.after(0, self._enable_buttons)
        
        threading.Thread(target=_do_transcribe, daemon=True).start()
    
    def _transcribe(self, audio_path):
        """Transcribe audio file"""
        import torch
        from pydub import AudioSegment
        
        # Convert to 16kHz mono WAV
        temp_wav = tempfile.mktemp(suffix=".wav")
        audio = AudioSegment.from_file(audio_path)
        audio = audio.set_channels(1).set_frame_rate(SAMPLE_RATE)
        audio.export(temp_wav, format="wav")
        
        duration = len(audio) / 1000
        
        # Transcribe
        with torch.no_grad():
            result = self.model.transcribe([temp_wav])
        
        # Get text
        text = result[0].text if hasattr(result[0], 'text') else str(result[0])
        
        # Cleanup
        os.remove(temp_wav)
        
        return text, duration
    
    def start_recording(self):
        """Start microphone recording"""
        import sounddevice as sd
        
        self.is_recording = True
        self.recorded_audio = []
        self.record_start = time.time()
        
        # Update UI
        self.start_btn.state(['disabled'])
        self.stop_btn.state(['!disabled'])
        self._disable_file_buttons()
        self.rec_status.configure(text="🔴 Recording...", foreground='red')
        
        # Start recording thread
        def _record():
            try:
                with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='int16',
                                   callback=self._audio_callback):
                    while self.is_recording:
                        sd.sleep(100)
            except Exception as e:
                self.root.after(0, lambda: self._show_error(f"Recording error: {e}"))
        
        self.record_thread = threading.Thread(target=_record, daemon=True)
        self.record_thread.start()
        
        # Start timer
        self._update_timer()
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for audio recording"""
        if self.is_recording:
            self.recorded_audio.append(indata.copy())
    
    def _update_timer(self):
        """Update recording timer"""
        if self.is_recording:
            elapsed = time.time() - self.record_start
            self.timer_label.configure(text=f"⏱️ {elapsed:.1f}s")
            self.root.after(100, self._update_timer)
    
    def stop_recording(self):
        """Stop recording and transcribe"""
        import numpy as np
        import soundfile as sf
        
        self.is_recording = False
        
        # Update UI
        self.stop_btn.state(['disabled'])
        self.rec_status.configure(text="⏳ Processing...", foreground='orange')
        
        # Wait for recording thread
        if self.record_thread:
            self.record_thread.join(timeout=1)
        
        # Save recording
        if self.recorded_audio:
            audio_data = np.concatenate(self.recorded_audio, axis=0)
            temp_path = tempfile.mktemp(suffix=".wav")
            sf.write(temp_path, audio_data, SAMPLE_RATE)
            
            # Transcribe
            def _do_transcribe():
                try:
                    text, duration = self._transcribe(temp_path)
                    self.root.after(0, lambda: self._show_result(text, duration))
                except Exception as e:
                    self.root.after(0, lambda: self._show_error(str(e)))
                finally:
                    os.remove(temp_path)
                    self.root.after(0, self._reset_recording_ui)
            
            threading.Thread(target=_do_transcribe, daemon=True).start()
        else:
            self._show_error("No audio recorded!")
            self._reset_recording_ui()
    
    def _reset_recording_ui(self):
        """Reset recording UI"""
        self.start_btn.state(['!disabled'])
        self._enable_file_buttons()
        self.rec_status.configure(text="Ready to record", foreground='gray')
        self.timer_label.configure(text="⏱️ 0.0s")
    
    def _set_result(self, text):
        """Set result text"""
        self.result_text.configure(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, text)
        self.result_text.configure(state='disabled')
    
    def _show_result(self, text, duration):
        """Show transcription result"""
        self._set_result(text)
        self.duration_label.configure(text=f"⏱️ Duration: {duration:.2f}s")
        self.rec_status.configure(text="✅ Done!", foreground='green')
    
    def _show_error(self, error):
        """Show error"""
        self._set_result(f"❌ Error: {error}")
        messagebox.showerror("Error", error)
    
    def _disable_buttons(self):
        self.select_btn.state(['disabled'])
        self.transcribe_btn.state(['disabled'])
        self.start_btn.state(['disabled'])
    
    def _enable_buttons(self):
        self.select_btn.state(['!disabled'])
        if hasattr(self, 'selected_file'):
            self.transcribe_btn.state(['!disabled'])
        self.start_btn.state(['!disabled'])
    
    def _disable_file_buttons(self):
        self.select_btn.state(['disabled'])
        self.transcribe_btn.state(['disabled'])
    
    def _enable_file_buttons(self):
        self.select_btn.state(['!disabled'])
        if hasattr(self, 'selected_file'):
            self.transcribe_btn.state(['!disabled'])
    
    def copy_result(self):
        """Copy result to clipboard"""
        self.result_text.configure(state='normal')
        text = self.result_text.get(1.0, tk.END).strip()
        self.result_text.configure(state='disabled')
        
        if text and not text.startswith("❌") and not text.startswith("⏳"):
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            messagebox.showinfo("Copied", "Text copied to clipboard!")
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    app = BanglaSTTApp()
    app.run()
