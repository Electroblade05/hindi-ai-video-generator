import os
import asyncio
import edge_tts


DEFAULT_VOICE = "hi-IN-SwaraNeural"


async def _generate_voice(
    text,
    output_path,
    voice
):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice
    )

    await communicate.save(output_path)


def generate_hindi_voice(
    text,
    output_path,
    voice=DEFAULT_VOICE
):

    if not text or not text.strip():
        raise ValueError(
            "Hindi text is empty."
        )

    output_dir = os.path.dirname(output_path)

    if output_dir:
        os.makedirs(
            output_dir,
            exist_ok=True
        )

    asyncio.run(
        _generate_voice(
            text,
            output_path,
            voice
        )
    )

    if not os.path.exists(output_path):
        raise RuntimeError(
            "Hindi voice generation failed."
        )

    return output_path
    
