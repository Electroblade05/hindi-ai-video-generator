import os
import time

from google import genai
from google.genai import types

from config import GEMINI_API_KEY, VEO_MODEL


def get_client():

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY is missing. "
            "Add it to Streamlit Secrets."
        )

    return genai.Client(api_key=GEMINI_API_KEY)


def generate_video_clip(
    prompt,
    output_path,
    aspect_ratio="9:16",
    resolution="720p",
    progress_callback=None
):

    client = get_client()

    full_prompt = f"""
Create a cinematic video clip.

{prompt}

Visual requirements:

- cinematic composition
- realistic natural movement
- smooth camera movement
- coherent lighting
- detailed environment
- no subtitles
- no captions
- no logos
- no watermarks
- no visible written text
"""

    operation = client.models.generate_videos(
        model=VEO_MODEL,
        prompt=full_prompt,
        config=types.GenerateVideosConfig(
            number_of_videos=1,
            aspect_ratio=aspect_ratio,
            resolution=resolution
        )
    )

    while not operation.done:

        if progress_callback:
            progress_callback(
                "Waiting for AI video generation..."
            )

        time.sleep(10)

        operation = client.operations.get(operation)

    if not operation.response:
        raise RuntimeError(
            "Video generation failed: empty response."
        )

    generated_video = (
        operation.response.generated_videos[0].video
    )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    client.files.download(
        file=generated_video,
        destination=output_path
    )

    return output_path
