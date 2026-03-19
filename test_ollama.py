import openai
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(
    api_key="ollama",
    base_url="http://localhost:11434/v1"
)

print("--- TESTING OLLAMA CONNECTION ---")
try:
    response = client.chat.completions.create(
        model="phi3:latest",
        messages=[
            {"role": "user", "content": "Just say 'hello' and nothing else."}
        ]
    )
    print("Response received!")
    print(response.choices[0].message.content)
except Exception as e:
    print(f"Error: {e}")
