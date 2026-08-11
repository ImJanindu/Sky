# ☁️ SKY Voice Assistant

Welcome to **SKY**, an intelligent and interactive Windows desktop voice assistant designed to simplify your digital life. Built with a rich graphical overlay and powerful AI, SKY listens to your commands and executes them seamlessly.

## ✨ Features & Capabilities

SKY is equipped with a wide range of functions, powered by natural language understanding (Groq API) and local automation tools:

- 💬 **Conversational AI (`answer_question`)**: Ask anything! SKY answers questions, explains concepts, and handles follow-up queries contextually.

- 🎵 **Media Controls (`media_control`)**: Command your system's volume (up, down, mute) and playback (play/pause, next/previous track).

- 🎥 **YouTube Integration (`play_youtube`)**: Easily search for and play your favorite videos or songs on YouTube.

- 🌐 **Web Navigation (`open_website`)**: Directly open any website by speaking its name or URL.

- 🚀 **App Launcher (`open_application`)**: Launch local desktop programs (e.g., Chrome, VS Code, Notepad, File Explorer, Task Manager).

- 🖱️ **Visual Screen Clicking (`click_on_screen`)**: Tell SKY to click on specific visual elements (using saved image templates).

- 🔤 **OCR Text Clicking (`click_text`)**: Ask SKY to find and click any specific text written on your screen using advanced OCR technology.

- 📜 **Screen Scrolling (`scroll_screen`)**: Scroll up and down pages hands-free.

- ⌨️ **Keyboard Shortcuts (`press_keys`)**: Simulate single key presses or complex hotkeys (like "copy this", "switch window", "open task manager").

- 🛑 **Dismiss (`dismiss`)**: Instantly stop listening or cancel the current action.

## 🛠️ Technology Stack

- **Wake Word Detection**: `openwakeword`
- **Speech-to-Text (STT)**: `faster-whisper`
- **Text-to-Speech (TTS)**: `edge-tts`
- **Natural Language Understanding**: `Groq` API (LLaMA-3)
- **GUI Overlay**: `PySide6`
- **Automation & OCR**: `PyAutoGUI` & `pytesseract`

## 🚀 Setup Instructions

Follow these steps to get SKY up and running on your local machine:

### 1. Prerequisites
- **Python 3.8+** installed on your Windows machine.
- **Tesseract OCR**: You must install the Tesseract executable for Windows. Ensure it is installed at the default directory: `C:\Program Files\Tesseract-OCR\tesseract.exe`.

### 2. Installation
1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd Sky
   ```
2. **Activate the virtual environment**:
   ```powershell
   # On Windows PowerShell
   .\env\Scripts\Activate.ps1
   ```
3. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

### 3. Environment Variables
Create a `.env` file in the root of your project directory and add your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Running SKY
Start the assistant by executing the main script:
```bash
python main.py
```
*Once running, simply say **"Sky"** to activate the assistant and give a command!*

## 👨‍💻 Developer Information

**Creator** : [Janindu Malshan](https://github.com/ImJanindu)  
*Computer Science Student & Engineer*

Built with ❤️ to demonstrate the power of combining modern AI with desktop automation.
