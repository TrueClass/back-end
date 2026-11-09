from dotenv import load_dotenv
from google import genai
from google.genai import types
import numpy as np
import requests
import os

load_dotenv()
COLIBRI_API_KEY = os.getenv("COLIBRI_API_KEY")
COLIBRI_MODEL = "qwen3.6-colibri"
GEMINI_MODEL = "gemini-3.8-flash"
COLIBRI_TIMEOUT = 60

EMBEDDING_MODEL = "gemini-embedding-2"
EMBEDDING_DIMENSIONS = 768
EMBEDDING_MODEL_ID = f"{EMBEDDING_MODEL}@{EMBEDDING_DIMENSIONS}"
EMBEDDING_BATCH_SIZE = 100

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
        timeout=COLIBRI_TIMEOUT
    )

    resp.raise_for_status()

    return resp.json()['choices'][0]['message']['content']
    
def gemini_request(system_message, message: str):
    response = get_gemini_client().models.generate_content(
        model=GEMINI_MODEL,
        contents=message,
        config={"system_instruction": system_message}
    )

    return response.text

def gemini_structured_request(system_message: str, message: str, schema, temperature: float = 0.2):
    """Returns the response parsed into `schema` (a pydantic model), so the shape is always the same"""
    try:
        response = get_gemini_client().models.generate_content(
            model=GEMINI_MODEL,
            contents=message,
            config={
                "system_instruction": system_message,
                "temperature": temperature,
                "response_mime_type": "application/json",
                "response_schema": schema,
            }
        )
    except Exception as err:
        raise AIUnavailableError() from err
    if response.parsed is None:
        raise AIUnavailableError()
    return response.parsed

def embed_texts(texts: list[str], task: str = "clustering") -> list[np.ndarray]:
    """One L2-normalized float32 vector per text. Each text goes in its own Content, otherwise Gemini aggregates them into a single embedding"""
    vectors = []
    for i in range(0, len(texts), EMBEDDING_BATCH_SIZE):
        batch = texts[i:i + EMBEDDING_BATCH_SIZE]
        try:
            result = get_gemini_client().models.embed_content(
                model=EMBEDDING_MODEL,
                contents=[types.Content(parts=[types.Part.from_text(text=f"task: {task} | query: {t}")]) for t in batch],
                config=types.EmbedContentConfig(output_dimensionality=EMBEDDING_DIMENSIONS),
            )
        except Exception as err:
            raise AIUnavailableError() from err
        if len(result.embeddings) != len(batch):
            raise AIUnavailableError()

        for embedding in result.embeddings:
            v = np.asarray(embedding.values, dtype=np.float32)
            vectors.append(v / np.linalg.norm(v))
    return vectors

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
