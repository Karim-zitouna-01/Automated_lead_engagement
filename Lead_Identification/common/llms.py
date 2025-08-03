# Lead_Identification/common/llm.py

import os
import requests

#use .env
import os
from dotenv import load_dotenv
from google import genai
from google.genai import Client, types

# Load .env at startup
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

# GEMINI FLASH 2.5
def call_gemini_flash(prompt: str, system_prompt: str = None, temperature: float = 0.7, max_tokens: int = 300) -> str:
    try:
        client = Client(api_key=GEMINI_API_KEY)

        # Combine system and user prompt
        full_prompt = f"{system_prompt}\n{prompt}" if system_prompt else prompt

        # Wrap content as Part and use in a list
        contents = [types.Part.from_text(text=full_prompt)]

        # Configuration for the generation
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            
        )

        # Generate response
        response = client.models.generate_content(
            model="gemini-2.0-flash",  # or gemini-2.0-flash-001 depending on your access
            contents=contents,
            config=config
        )

        return response.text

    except Exception as e:
        print(f"❌ Gemini Flash call failed: {e}")
        return "[LLM error]"


# MISTRAL
def call_mistral(prompt: str, system_prompt: str = "You are a helpful assistant.", temperature: float = 0.7, max_tokens: int = 300) -> str:
    url = "https://api.mistral.ai/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {MISTRAL_API_KEY}"
    }
    payload = {
        "model": "mistral-small",  # You can change to mistral-medium or large if needed
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"❌ Mistral API call failed: {e}")
        return "[LLM error]"


