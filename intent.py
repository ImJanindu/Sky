import os
import json
from groq import Groq

# Replace with your actual key if not using environment variables
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "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")
client = Groq(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """
You are the natural language understanding brain of a Windows desktop voice assistant named JARVIS.
Your job is to parse the user's spoken command into a structured JSON action.
You will receive recent conversation history so you understand context and follow-up questions.

Available actions:

1. answer_question: When user asks an informational question, explanation, fact, or a FOLLOW-UP question (e.g., "What is RAM?", "How does it work?", "Who invented it?").
   Provide a concise, direct, and conversational 3 to 4 sentence explanation.
   Structure: {"action": "answer_question", "answer": "<concise summary>"}

2. media_control: When user wants to adjust volume or media playback.
   Sub-commands: "volume_up", "volume_down", "mute", "play_pause", "next_track", "prev_track".
   Structure: {"action": "media_control", "command": "<sub-command>"}

3. play_youtube: When user wants to search and play a specific song or video on YouTube.
   Structure: {"action": "play_youtube", "query": "<search keywords>"}

4. open_website: When user wants to navigate to a website or URL.
   Structure: {"action": "open_website", "url": "<target url>"}

5. open_application: When user wants to launch a local program.
   Structure: {"action": "open_application", "app_name": "<program name>"}

6. dismiss: When user wants to cancel, stop listening, or close JARVIS.
   Structure: {"action": "dismiss"}

7. unknown: When the request does not fit any category.
   Structure: {"action": "unknown", "message": "<original query>"}

8. click_on_screen: When the user wants to click a visual element on the screen.
   Sub-commands should match the names of your saved image templates.
   Structure: {"action": "click_on_screen", "target": "<first_video | play_button | subscribe | close>"}

Rules:
- Output valid JSON only. Never output markdown fences or conversational filler.
"""

# Rolling conversation history buffer
conversation_history = []

def parse_intent(spoken_text: str) -> dict:
    global conversation_history
    if not spoken_text.strip():
        return {"action": "unknown", "message": "Empty speech"}

    # Prepare messages payload including system prompt and history
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(conversation_history)
    messages.append({"role": "user", "content": spoken_text})

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        response_text = completion.choices[0].message.content
        parsed = json.loads(response_text)

        # Append to history and keep last 6 turns (3 exchanges)
        conversation_history.append({"role": "user", "content": spoken_text})
        
        if parsed.get("action") == "answer_question":
            conversation_history.append({"role": "assistant", "content": parsed.get("answer", "")})
        else:
            conversation_history.append({"role": "assistant", "content": f"Executed action: {parsed.get('action')}"})

        if len(conversation_history) > 6:
            conversation_history = conversation_history[-6:]

        return parsed

    except Exception as error:
        print(f"[Groq Error]: {error}")
        return {"action": "unknown", "error": str(error)}

def clear_context():
    """Resets memory when assistant is dismissed."""
    global conversation_history
    conversation_history.clear()