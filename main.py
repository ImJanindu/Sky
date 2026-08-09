import os
import sys
import pygame
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QThread, Signal

import wake_word
import stt
import intent
import actions
import tts
from gui import AssistantOverlay

# Initialize pygame audio mixer once
pygame.mixer.init()

# Locate wakeup.mp3 in the current script folder
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WAKEUP_SOUND_PATH = os.path.join(SCRIPT_DIR, "wakeup.mp3")

wakeup_sound = None

# Pre-load the sound effect onto a dedicated Pygame audio channel
if os.path.exists(WAKEUP_SOUND_PATH):
    try:
        wakeup_sound = pygame.mixer.Sound(WAKEUP_SOUND_PATH)
        wakeup_sound.set_volume(0.8)
        print("[Audio System]: wakeup.mp3 loaded successfully.")
    except Exception as e:
        print(f"[Audio Error]: Failed to load wakeup.mp3: {e}")
else:
    print(f"[Audio Warning]: '{WAKEUP_SOUND_PATH}' was not found. Place wakeup.mp3 in your project folder.")

def play_wakeup_chime():
    """Plays sound effect on an independent channel."""
    if wakeup_sound:
        wakeup_sound.play()
    else:
        # Fallback beep if wakeup.mp3 is missing
        try:
            import winsound
            winsound.Beep(1000, 150)
        except Exception:
            pass

class AssistantWorker(QThread):
    wake_word_detected = Signal()
    status_changed = Signal(str, str)
    command_finished = Signal(int)

    def run(self):
        print("\n===========================================")
        print(" JARVIS Voice Assistant Running in Background ")
        print(" Say 'Hey JARVIS' or 'Wakeup' to activate... ")
        print("===========================================\n")

        while True:
            # 1. Background Wake Word Listener
            detected = wake_word.listen_for_wakeword()
            
            if detected:
                # First, stop any active speech from previous responses
                tts.stop_speaking()

                # Second, play the wake-up chime effect on its dedicated channel
                #play_wakeup_chime()

                # 2. Wake Word Triggered -> Show UI
                self.wake_word_detected.emit()
                self.status_changed.emit("JARVIS is listening...", "Speak your command now")

                #tts.speak("Hello sir, at your service.", block=True)
                
                

                # 3. Speech-to-Text Transcription
                user_speech = stt.record_and_transcribe()

                if user_speech:
                    self.status_changed.emit("Processing...", f'"{user_speech}"')

                    # 4. Groq Intent & Conversational Context
                    parsed_intent = intent.parse_intent(user_speech)
                    action = parsed_intent.get("action", "unknown")

                    # 5. Handle Actions
                    if action == "answer_question":
                        answer_text = parsed_intent.get("answer", "Here is what I found.")
                        self.status_changed.emit("JARVIS says:", answer_text)
                        
                        tts.speak(answer_text)
                        
                        word_count = len(answer_text.split())
                        display_time_ms = max(5000, int(word_count * 330) + 2000)
                        self.command_finished.emit(display_time_ms)

                    elif action == "dismiss":
                        tts.stop_speaking()
                        intent.clear_context()
                        self.status_changed.emit("Cancelled", "JARVIS closed")
                        self.command_finished.emit(600)

                    elif action != "unknown":
                        tts.stop_speaking()
                        self.status_changed.emit("Executing Command", f"Action: {action}")
                        actions.execute_action(parsed_intent)
                        self.command_finished.emit(2400)

                    else:
                        self.status_changed.emit("Unrecognized Command", f'"{user_speech}"')
                        self.command_finished.emit(2400)

                else:
                    self.status_changed.emit("No Speech Detected", "Returning to idle state")
                    self.command_finished.emit(1500)

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    overlay = AssistantOverlay()
    worker = AssistantWorker()

    worker.wake_word_detected.connect(lambda: overlay.update_status("JARVIS is listening...", "Speak your command now"))
    worker.status_changed.connect(overlay.update_status)
    worker.command_finished.connect(overlay.schedule_hide)

    worker.start()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()