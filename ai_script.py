import json
from openai import OpenAI

from config import OPENAI_API_KEY, TEXT_MODEL


def get_client():
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to Streamlit Secrets."
        )

    return OpenAI(api_key=OPENAI_API_KEY)


def generate_script(topic, duration_minutes, style):
    client = get_client()

    target_words = int(duration_minutes * 125)

    prompt = f"""
Create a Hindi YouTube narration about:

TOPIC:
{topic}

STYLE:
{style}

TARGET LENGTH:
Approximately {target_words} Hindi words.

Requirements:

1. Write natural spoken Hindi.
2. Make it interesting for a general audience.
3. Use simple vocabulary.
4. Do not use unnecessary English.
5. Create a strong opening hook.
6. Explain the subject logically.
7. End with a memorable conclusion.
8. Do not include scene directions inside the narration.
9. Do not use emojis.
10. Return only the narration.
"""

    response = client.responses.create(
        model=TEXT_MODEL,
        input=prompt
    )

    return response.output_text.strip()


def generate_scene_plan(topic, script, style, scene_count):
    client = get_client()

    prompt = f"""
You are a professional AI video director.

Create a scene plan for a Hindi narrated video.

TOPIC:
{topic}

STYLE:
{style}

NARRATION:
{script}

Create exactly {scene_count} scenes.

For every scene provide:

- scene_number
- narration
- visual_prompt
- camera
- duration

Rules:

- visual_prompt must be written in English because it will be sent
  to a video generation model.
- Make every scene visually interesting.
- Avoid showing written text inside generated video.
- Maintain visual continuity.
- Use cinematic camera language.
- Do not create dangerous or graphic imagery.
- narration must contain the exact portion of narration belonging
  to that scene.

Return ONLY valid JSON.

Format:

[
  {{
    "scene_number": 1,
    "narration": "...",
    "visual_prompt": "...",
    "camera": "...",
    "duration": 8
  }}
]
"""

    response = client.responses.create(
        model=TEXT_MODEL,
        input=prompt
    )

    text = response.output_text.strip()

    # Remove accidental markdown fences.
    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    scenes = json.loads(text)

    return scenes
