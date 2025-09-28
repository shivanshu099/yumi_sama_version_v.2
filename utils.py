
import os
import keyboard
import pyaudio
import wave
import time
import colorama
from termcolor import colored
import soundfile as sf
import whisper





# ─── Audio Recording ──────────────────────────────────────────────
def record_audio(path="input.wav"):
    """Record while RIGHT_SHIFT is held down, save to path, and return filepath."""
    try:
        CHUNK    = 1024
        FORMAT   = pyaudio.paInt16
        CHANNELS = 1
        RATE     = 44100

        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

        print(colored("Hold RIGHT_SHIFT to talk...", "yellow"))
        frames = []
        while not keyboard.is_pressed('RIGHT_SHIFT'):
            time.sleep(0.1)
        while keyboard.is_pressed('RIGHT_SHIFT'):
            frames.append(stream.read(CHUNK))
        print(colored("Recording stopped.", "yellow"))

        stream.stop_stream()
        stream.close()
        p.terminate()

        with wave.open(path, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))

        return path

    except Exception as e:
        print(colored(f"record_audio ERROR: {e}", "red"))
        return None
    


#transcribe audio using whisper
def transcribe_whisper(wav_path: str) -> str:
    try:
        mdoel =whisper.load_model("base")
        result=mdoel.transcribe(wav_path ,fp16=False)
        return result["text"].strip()
    except Exception as e:
        print(colored(f"transcribe_whisper ERROR: {e}", "red"))
        return ""

if __name__ == "__main__":
    audio_path="input.wav"
    print(transcribe_whisper(audio_path))
























