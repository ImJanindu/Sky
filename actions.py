import os
import ctypes
import subprocess
import webbrowser
import urllib.parse
import pyautogui

import pytesseract

# Point pytesseract to the installed Windows binary
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Enable PyAutoGUI safety features
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# --- Windows Virtual Key Codes ---
VK_VOLUME_MUTE = 0xAD
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_UP = 0xAF
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_PLAY_PAUSE = 0xB3

def click_text_on_screen(target_text: str) -> bool:
    """Uses OCR to find a word on the screen and clicks its geometric center."""
    if not target_text:
        return False

    print(f"[Action Executing]: Running OCR scan for text '{target_text}'...")
    
    try:
        # Capture the entire screen
        screenshot = pyautogui.screenshot()
        
        # Extract text and bounding box data as a dictionary
        ocr_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
        
        target_lower = target_text.lower().strip()

        # Iterate through the recognized words
        for i in range(len(ocr_data['text'])):
            word = ocr_data['text'][i].lower().strip()
            
            # Check if the target text matches the scanned word
            if target_lower in word and len(word) > 0:
                # Extract geometric boundaries
                x = ocr_data['left'][i]
                y = ocr_data['top'][i]
                width = ocr_data['width'][i]
                height = ocr_data['height'][i]
                
                # Calculate the exact center pixel
                center_x = x + (width // 2)
                center_y = y + (height // 2)
                
                # Move and click
                pyautogui.moveTo(center_x, center_y, duration=0.4)
                pyautogui.click()
                print(f"[Action Success]: Clicked text '{word}' at coordinates ({center_x}, {center_y}).")
                return True
                
        print(f"[Action Failed]: The text '{target_text}' was not found on the screen.")
        return False

    except Exception as error:
        print(f"[Action Error]: OCR processing failed: {error}")
        return False


def send_virtual_key(vk_code: int):
    """Simulates a hardware key press and release event on Windows."""
    KEYEVENTF_KEYUP = 0x0002
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)


def handle_media_command(command: str):
    """Executes media playback and system volume adjustments."""
    cmd = command.lower().strip()

    if cmd == "volume_up":
        for _ in range(5):
            send_virtual_key(VK_VOLUME_UP)
        print("[Action Executing]: Increased master volume.")

    elif cmd == "volume_down":
        for _ in range(5):
            send_virtual_key(VK_VOLUME_DOWN)
        print("[Action Executing]: Decreased master volume.")

    elif cmd == "mute":
        send_virtual_key(VK_VOLUME_MUTE)
        print("[Action Executing]: Toggled audio mute.")

    elif cmd == "play_pause":
        send_virtual_key(VK_MEDIA_PLAY_PAUSE)
        print("[Action Executing]: Toggled media play/pause.")

    elif cmd == "next_track":
        send_virtual_key(VK_MEDIA_NEXT_TRACK)
        print("[Action Executing]: Skipped to next track.")

    elif cmd == "prev_track":
        send_virtual_key(VK_MEDIA_PREV_TRACK)
        print("[Action Executing]: Jumped to previous track.")

    else:
        print(f"[Action Warning]: Unrecognized media command '{command}'.")


def click_visual_target(target_name: str) -> bool:
    """Scans the screen for an image template and clicks its center location."""
    if not target_name:
        print("[Action Error]: Target template name was empty.")
        return False

    script_dir = os.path.dirname(os.path.abspath(__file__))
    clean_target = target_name.replace(".png", "") + ".png"
    image_path = os.path.join(script_dir, clean_target)

    if not os.path.exists(image_path):
        print(f"[Action Error]: Template image missing at '{image_path}'.")
        return False

    print(f"[Action Executing]: Searching screen for visual pattern '{clean_target}'...")

    try:
        target_location = pyautogui.locateCenterOnScreen(image_path, confidence=0.8)
        if target_location:
            pyautogui.moveTo(target_location.x, target_location.y, duration=0.4)
            pyautogui.click()
            print(f"[Action Success]: Clicked target '{clean_target}' at {target_location}.")
            return True
        else:
            print(f"[Action Failed]: Could not locate '{clean_target}' on screen.")
            return False

    except Exception as error:
        print(f"[Action Error]: Screen recognition failed: {error}")
        return False


def open_local_application(app_name: str):
    """Launches local desktop applications and Windows utilities."""
    clean_name = app_name.lower().strip()

    # Application lookup table mapping intent strings to Windows executables
    app_lookup = {
        "calculator": "calc.exe",
        "calc": "calc.exe",
        "notepad": "notepad.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "edge": "msedge.exe",
        "microsoft edge": "msedge.exe",
        "vs code": "code",
        "vscode": "code",
        "code": "code",
        "terminal": "wt.exe",
        "cmd": "cmd.exe",
        "command prompt": "cmd.exe",
        "file explorer": "explorer.exe",
        "explorer": "explorer.exe",
        "settings": "start ms-settings:",
        "task manager": "taskmgr.exe"
    }

    executable = app_lookup.get(clean_name, clean_name)

    try:
        if executable.startswith("start "):
            subprocess.Popen(executable, shell=True)
        else:
            subprocess.Popen(executable, shell=True)
        print(f"[Action Executing]: Launched '{clean_name}' via '{executable}'.")
    except Exception as error:
        print(f"[Action Error]: Failed to launch application '{app_name}': {error}")


def execute_action(intent_data: dict):
    """Primary router that receives parsed JSON actions from main.py."""
    if not isinstance(intent_data, dict):
        print("[Action Error]: Received invalid intent structure.")
        return

    action = intent_data.get("action")

    if action == "media_control":
        cmd = intent_data.get("command", "")
        handle_media_command(cmd)

    elif action == "play_youtube":
        query = intent_data.get("query", "").strip()
        if query:
            encoded_query = urllib.parse.quote_plus(query)
            target_url = f"https://www.youtube.com/results?search_query={encoded_query}"
            print(f"[Action Executing]: Opening YouTube search for '{query}'...")
            webbrowser.open(target_url)
        else:
            webbrowser.open("https://www.youtube.com")

    elif action == "open_website":
        raw_url = intent_data.get("url", "").strip()
        if raw_url:
            if not raw_url.startswith("http://") and not raw_url.startswith("https://"):
                raw_url = "https://" + raw_url
            print(f"[Action Executing]: Opening browser URL '{raw_url}'...")
            webbrowser.open(raw_url)

    elif action == "open_application":
        app_name = intent_data.get("app_name", "")
        if app_name:
            open_local_application(app_name)

    elif action == "click_on_screen":
        target = intent_data.get("target", "")
        click_visual_target(target)

    elif action == "click_text":
        target = intent_data.get("text", "")
        click_text_on_screen(target)

    elif action in ["answer_question", "dismiss"]:
        # Handled in main.py directly
        pass

    else:
        print(f"[Action Notice]: No handler defined for action type '{action}'.")