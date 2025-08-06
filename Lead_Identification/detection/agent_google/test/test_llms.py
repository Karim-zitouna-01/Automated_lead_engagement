# Lead_Identification/detection/agent_google/test/test_llms.py

import sys
import os
sys.path.append(os.path.abspath(os.path.join(__file__, "../../../..")))

from Lead_Identification.common.llms import call_mistral, call_gemini_flash

def test_call_mistral():
    prompt = "Give me 3 creative startup names for a food delivery app."
    try:
        response = call_mistral(prompt)
        print("\n[Mistral response]")
        print(response)
    except Exception as e:
        print(f"Error calling Mistral: {e}")

def test_call_gemini_flash():
    prompt = "Suggest 3 unique taglines for a fitness application."
    try:
        response = call_gemini_flash(prompt)
        print("\n[Gemini response]")
        print(response)
    except Exception as e:
        print(f"Error calling Gemini: {e}")

if __name__ == "__main__":
    test_call_mistral()
    test_call_gemini_flash()
