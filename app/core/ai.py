from dotenv import load_dotenv
from google import genai
import requests
import os

load_dotenv()
COLIBRI_API_KEY = os.getenv("COLIBRI_API_KEY")
COLIBRI_MODEL = "qwen3.6-colibri"
GEMINI_MODEL = "gemini-3.8-flash"

gemini_client = None

def get_gemini_client() -> genai.Client:
    # created on first use so a missing GEMINI_API_KEY doesn't break the app on import
    global gemini_client
    if gemini_client is None:
        gemini_client = genai.Client()
    return gemini_client

def colibri_request(system_message: str, user_message: str, max_tokens: int, temperature: float = 0.7) -> str:
    resp = requests.post(
        "https://colibri.tz.net.br/v1/chat/completions",
        json={
                "model": COLIBRI_MODEL,
        "messages": [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": user_message
        }
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
        },
        headers={"Authorization": f"Bearer {COLIBRI_API_KEY}"},
        timeout=20
    )

    resp.raise_for_status()

    return resp.json()['choices'][0]['message']['content']
    
def gemini_request(system_message, message: str):
    interaction = get_gemini_client().interactions.create(
        model=GEMINI_MODEL,
        input=message,
        system_instruction=system_message
    )

    return interaction.output_text

def request_completion(system_message: str, user_message: str, temperature: float, max_tokens: int) -> tuple[str, str]:
    try:
        resp = colibri_request(system_message, user_message, max_tokens, temperature)
        if resp:
            return resp, COLIBRI_MODEL
    except (requests.RequestException, KeyError, IndexError, ValueError):
        pass

    try:
        resp = gemini_request(system_message, user_message)
    except Exception as err:
        raise AIUnavailableError() from err
    if not resp:
        raise AIUnavailableError()
    return resp, GEMINI_MODEL

class AIUnavailableError(Exception):
    """Raised when neither Colibri nor Gemini could generate a completion"""
    pass
