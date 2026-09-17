import os

from openai import OpenAI

from config import OPENAI_API_KEY, TTS_MODEL


def generate_hindi_voice(
    text,
    output_path,
    voice="alloy"
):

    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is missing."
        )

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )

    os.makedirs(
        os.path.dirname(output_path),
        exist_ok=True
    )

    with client.audio.speech.with_streaming_response.create(
        model=TTS_MODEL,
        voice=voice,
        input=text,
        instructions=(
            "Speak naturally in Hindi. "
            "Use clear pronunciation, moderate speed, "
            "and an engaging documentary narration style."
        )
    ) as response:

        response.stream_to_file(output_path)

    return output_path
