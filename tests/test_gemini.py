import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

image_path = r"C:\Users\OM S PAI\OneDrive\Documents\Breakthrough_hackathon\ClaimPilot\data\images\pngtree-front-of-white-car-get-damaged-by-accident-on-the-road-png-image_11496147.png"

with open(image_path, "rb") as f:
    image_bytes = f.read()

image_part = types.Part.from_bytes(
    data=image_bytes,
    mime_type="image/png"
)

prompt = """
Look at this vehicle image.

Identify:
1. Visible damaged parts
2. Damage severity
3. Whether the visible damage appears repairable or may require replacement
4. Any possible hidden damage that should be physically inspected

This is only a preliminary AI assessment.
Do not make a final insurance settlement decision.

Respond in plain text.
"""

models = [
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash"
]

for model in models:

    print("\n========================================")
    print("Testing:", model)
    print("========================================")

    try:
        response = client.models.generate_content(
            model=model,
            contents=[
                prompt,
                image_part
            ]
        )

        print("✅ IMAGE ANALYSIS SUCCESS")
        print(response.text)

        break

    except Exception as e:

        print("❌ FAILED")
        print(e)