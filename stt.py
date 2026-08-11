import pyaudio
import numpy as np
from faster_whisper import WhisperModel

print("Loading Whisper Base Speech to Text model...")
model = WhisperModel("base.en", device="cpu", compute_type="int8")
print("Model loaded successfully.")

def record_and_transcribe():
    # Audio stream configuration
    CHUNK = 2048
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    
    # Silence detection parameters
    SILENCE_THRESHOLD = 300 
    SILENCE_DURATION = 1.5 

    p = pyaudio.PyAudio()
    stream = p.open(
        format=FORMAT, 
        channels=CHANNELS, 
        rate=RATE, 
        input=True, 
        frames_per_buffer=CHUNK
    )

    print("\n[SKY is listening... Speak your command]")
    
    # Optimization 1: Use a contiguous bytearray instead of a list
    audio_buffer = bytearray()
    silence_chunks = 0
    is_speaking = False
    max_silence_chunks = int((RATE / CHUNK) * SILENCE_DURATION)

    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            audio_buffer.extend(data)
            
            # Optimization 2: Use integer Mean Absolute Value instead of Float RMS
            audio_data = np.frombuffer(data, dtype=np.int16)
            volume = np.mean(np.abs(audio_data))
            
            # Detect if user has started speaking
            if volume > SILENCE_THRESHOLD:
                is_speaking = True
                silence_chunks = 0
            elif is_speaking:
                silence_chunks += 1
            
            # Stop recording if user pauses
            if is_speaking and silence_chunks > max_silence_chunks:
                break

    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

    print("[Processing audio...]")
    
    # Convert the contiguous buffer to the required float32 format
    audio_np = np.frombuffer(audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0
    
    # Optimization 3: Greedy decoding, skip language detection, and apply VAD
    segments, _ = model.transcribe(
        audio_np, 
        beam_size=1, 
        language="en",
        vad_filter=True
    )
    
    # Join the transcribed segments into a single string
    transcribed_text = "".join([segment.text for segment in segments]).strip()
    
    print(f"[Captured Text]: \"{transcribed_text}\"")
    return transcribed_text

if __name__ == "__main__":
    result = record_and_transcribe()