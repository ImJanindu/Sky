import pyaudio
import numpy as np
from openwakeword.model import Model
import os

def listen_for_wakeword():
    # Audio stream parameters required by the model
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280

    # Initialize PyAudio microphone stream
    audio = pyaudio.PyAudio()
    mic_stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    print("Loading custom Sky OpenWakeWord model...")

    # Load your custom ONNX model directly
    # Ensure sky.onnx is placed in the same directory as this script
    model_path = r"src\sky.onnx"
    
    if not os.path.exists(model_path):
        print(f"Error: Could not find the model file at {os.path.abspath(model_path)}")
        return False

    oww_model = Model(
        wakeword_models=[model_path], 
        inference_framework="onnx"
    )
    
    print("Listening for wake word 'Sky'...")

    try:
        while True:
            # Read a chunk of audio from the hardware
            audio_data = np.frombuffer(mic_stream.read(CHUNK), dtype=np.int16)
            
            # Feed the audio frame to the classification model
            oww_model.predict(audio_data)
            
            # Check the confidence scores of the custom model
            for model_name, scores in oww_model.prediction_buffer.items():
                latest_score = scores[-1]
                
                # A score above 0.5 indicates a successful trigger
                if latest_score > 0.5:
                    print(f"\nWake word detected! Model: {model_name}, Score: {latest_score}")
                    return True

    except KeyboardInterrupt:
        print("\nStopping listener.")
    finally:
        # Safely release hardware resources
        mic_stream.stop_stream()
        mic_stream.close()
        audio.terminate()

if __name__ == "__main__":
    # Test the function directly
    while True:
        detected = listen_for_wakeword()
        if detected:
            print("Action triggered. Resetting listener...")