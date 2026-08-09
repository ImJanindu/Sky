import pyaudio
import numpy as np
from openwakeword.model import Model

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

    print("Loading OpenWakeWord model...")

    # Explicitly force the ONNX inference framework for Windows compatibility
    import openwakeword
    openwakeword.utils.download_models() # Ensure ONNX models are downloaded
    oww_model = Model(inference_framework="onnx")
    print("Listening for wake word...")

    try:
        while True:
            # Read a chunk of audio from the hardware
            audio_data = np.frombuffer(mic_stream.read(CHUNK), dtype=np.int16)
            
            # Feed the audio frame to the classification model
            oww_model.predict(audio_data)
            
            # Check the confidence scores of all loaded models
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