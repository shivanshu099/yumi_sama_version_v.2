import os
import warnings
import logging
import asyncio
import time
import simpleaudio as sa
from dotenv import load_dotenv
from vosk import Model, KaldiRecognizer
import pyfiglet
from termcolor import colored
import colorama
import soundfile as sf
import sounddevice as sd
from gtts import gTTS
from pydub import AudioSegment
import PyTubeStudio.client as pts
from llm import run_yumi_agent   # your Grok-powered agent
from utils import record_audio, transcribe_whisper

# ─── Initialization ───────────────────────────────────────────────
debug = True
colorama.init(autoreset=True)
load_dotenv()

warnings.filterwarnings(
    "ignore",
    message=r".*overrides an existing Pydantic .* decorator"
)
warnings.filterwarnings("ignore", category=UserWarning)


# ─── Wait for Audio to Finish ───────────────────────────────────
def wait_for_speak(path):
    try:
        with sf.SoundFile(path) as f:
            return len(f) / f.samplerate
    except Exception as e:
        print(colored(f"wait_for_speak ERROR: {e}", "red"))
        return 0


# ─── Text-to-Speech ─────────────────────────────────────────────

"""
def speak_and_play(text: str, filename="yumi.wav"):
    data,samle_rate = sf.read(filename)
    sd.play(data, samplerate=samle_rate)
    sd.wait()
"""

def speak_and_play(text: str, filename="yumi.wav"):
    try:
        tts=gTTS(text, lang='en',slow=False)
        tts.save(filename)

        #convert mps to wav
        sound=AudioSegment.from_mp3(filename)
        sound.export(filename,format="wav")
        #play the wav
        data,sample_rate=sf.read(filename)
        sd.play(data,samplerate=sample_rate)
        sd.wait()
        os.remove(filename)
    except Exception as e:
        print(colored(f"speak_and_play ERROR: {e}", "red"))



# ─── VTuber Session ─────────────────────────────────────────────
async def vtuber_session():
    vts = pts.PyTubeStudio(token_path="yumi_token.txt")

    try:
        await vts.connect()
        await vts.authenticate()
        print(colored("✅ Connected & authenticated to VTube Studio!", "green"))
    except Exception as e:
        print(colored(f"❌ Connection error: {e}", "red"))
        return

    iteration_count = 0
    while True:
        try:
            iteration_count += 1
            print(colored(f"\n--- Iteration {iteration_count} ---", "white"))

            choice = await asyncio.to_thread(
                input, colored("\n1=text  2=voice  3=exit → ", "cyan")
            )
            print(colored(f"Selected choice: {choice}", "yellow"))

            if choice == '1':
                text = await asyncio.to_thread(
                    input, colored("Enter message: ", "magenta")
                )
                print(colored(f"Processing text: {text}", "yellow"))

                reply = run_yumi_agent(text)
                print(colored("Yumi:", "blue"), reply)

                await asyncio.to_thread(speak_and_play, reply)
                print("waiting to finsh audio plaback...........")
                #time.sleep(wait_for_speak("yumi.wav"))  # Async sleep
                print(colored("Audio playback completed", "green"))

            elif choice == '2':
                wav = await asyncio.to_thread(record_audio)
                if not wav:
                    print(colored("Recording failed, try again.", "red"))
                    continue

                user_text = await asyncio.to_thread(transcribe_whisper, wav)
                print(colored("You said:", "blue"), user_text or colored("[no speech]", "yellow"))

                reply = run_yumi_agent(user_text)
                print(colored("Yumi:", "blue"), reply)

                await asyncio.to_thread(speak_and_play, reply)
                duration = wait_for_speak("yumi.wav")
                await asyncio.sleep(duration)  # Async sleep

                #deleting the yumi.wav
                """
                if os.path.exists("yumi.wav"):
                    os.remove("yumi.wav")
                else:
                    print(colored("Warning: Audio file not found for deletion", "yellow"))
                """
                print(colored("Audio playback completed", "green"))

            elif choice == '3':
                print(colored("Goodbye!", "yellow"))
                break

            else:
                print(colored("Invalid entry.", "red"))

            print(colored(f"Completed iteration {iteration_count}", "green"))

        except KeyboardInterrupt:
            print(colored("\nInterrupted by user", "yellow"))
            break
        except Exception as e:
            print(colored(f"Loop error, but continuing: {e}", "red"))

    try:
        await vts.close()
        print(colored("Session closed.", "yellow"))
    except Exception as e:
        print(colored(f"Error closing session: {e}", "red"))


# ─── Main ────────────────────────────────────────────────────────
if __name__ == "__main__":
    banner = colored(pyfiglet.figlet_format("Welcome to Yumi"), "cyan")
    print(banner)
    print(colored("made with ❤️ by Shivanshu Prajapati", "green"))
    asyncio.run(vtuber_session())



































