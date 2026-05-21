
from openai import OpenAI
from dotenv import load_dotenv
import os 
load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

def get_response(user, msg):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",  # ✅ updated model
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": msg}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        print("Groq Error:", e)
        print(client.models.list())
        return "⚠️ AI not available right now."