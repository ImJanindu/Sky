import pyaudio
import numpy as np
from faster_whisper import WhisperModel

print("Loading Whisper Base Speech to Text model...")
# compute_type="int8" compresses the model to run lightning-fast on your Ryzen CPU
model = WhisperModel("base.en", device="cpu", compute_type="int8")
print("Model loaded successfully.")

def record_and_transcribe():
    # Audio stream configuration
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    # Silence detection parameters
    SILENCE_THRESHOLD = 300  # Increase if your room is noisy, decrease if mic is quiet
    SILENCE_DURATION = 1.5   # Seconds of silence before stopping

    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT, 
        channels=CHANNELS, 
        rate=RATE, 
        input=True, 
        frames_per_buffer=CHUNK
    )

    print("\n[SKY is listening... Speak your command]")
    
    frames = []
    silence_chunks = 0
    is_speaking = False
    max_silence_chunks = int((RATE / CHUNK) * SILENCE_DURATION)

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            frames.append(data)
            
            # Convert bytes to numpy array to calculate audio volume (RMS)
            audio_data = np.frombuffer(data, dtype=np.int16)
            rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32))))
            
            # Detect if user has started speaking
            if rms > SILENCE_THRESHOLD:
                is_speaking = True
                silence_chunks = 0
            elif is_speaking:
                silence_chunks += 1
            
            # Stop recording if user pauses for 1.5 seconds
            if is_speaking and silence_chunks > max_silence_chunks:
                break

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    print("[Processing audio...]")
    
    # Whisper expects a flat float32 array normalized between -1.0 and 1.0
    audio_np = np.frombuffer(b''.join(frames), dtype=np.int16).astype(np.float32) / 32768.0
    
    # Transcribe the audio from memory
    segments, _ = model.transcribe(audio_np, beam_size=5)
    
    # Join the transcribed segments into a single string
    transcribed_text = "".join([segment.text for segment in segments]).strip()
    
    print(f"[Captured Text]: \"{transcribed_text}\"")
    return transcribed_text

if __name__ == "__main__":
    result = record_and_transcribe()