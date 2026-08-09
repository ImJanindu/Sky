import os
import uuid
import threading
import asyncio
import edge_tts
import pygame
import time

# Initialize Pygame audio mixer
if not pygame.mixer.get_init():
    pygame.mixer.init()

VOICE_MODEL = "en-US-GuyNeural"
_speech_lock = threading.Lock()

def stop_speaking():
    """Instantly halts audio playback and releases the file handle."""
    try:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    except Exception:
        pass

async def _generate_and_play(text: str):
    """Generates a unique audio file and plays it safely."""
    # Create a unique filename to avoid Windows file lock collisions
    unique_id = uuid.uuid4().hex[:8]
    temp_file = f"response_{unique_id}.mp3"

    try:
        # Generate audio file
        communicate = edge_tts.Communicate(text, VOICE_MODEL, rate="+10%")
        await communicate.save(temp_file)
        
        with _speech_lock:
            # Safely unload any previous audio handle before loading new file
            pygame.mixer.music.unload()
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            
            # Wait for playback to complete or be interrupted
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
                
            pygame.mixer.music.unload()

    except Exception as error:
        print(f"[TTS Error]: {error}")
    finally:
        # Clean up temporary audio file from disk
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except Exception:
                pass

def _worker(text: str):
    """Asyncio wrapper for background thread execution."""
    time.sleep(0.1)
    asyncio.run(_generate_and_play(text))

def speak(text: str, block: bool = False):
    """Speaks text using neural TTS without thread locking errors."""
    stop_speaking()
    if not text or not text.strip():
        return
        
    if block:
        _worker(text)
    else:
        threading.Thread(target=_worker, args=(text,), daemon=True).start()

if __name__ == "__main__":
    print("Testing thread-safe TTS engine...")
    speak("Testing speech interruption logic.", block=True)