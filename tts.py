import os
import asyncio

import edge_tts


# ============================================================
# INTERNAL ASYNC TTS
# ============================================================

async def _generate_voice(
    text,
    output_path,
    voice,
    rate="+0%",
    volume="+0%",
):

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice,
        rate=rate,
        volume=volume,
    )

    await communicate.save(
        output_path
    )


# ============================================================
# PUBLIC FUNCTION
# ============================================================

def generate_hinglish_voice(
    text,
    output_path,
    voice,
    rate="+0%",
):

    if not text or not text.strip():

        raise ValueError(
            "Narration is empty."
        )

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    try:

        asyncio.run(
            _generate_voice(
                text=text,
                output_path=output_path,
                voice=voice,
                rate=rate,
            )
        )

    except Exception as error:

        raise RuntimeError(
            "Hinglish TTS generation failed:\n"
            + str(error)
        )

    if not os.path.exists(
        output_path
    ):

        raise RuntimeError(
            "TTS audio file was not created."
        )

    if os.path.getsize(
        output_path
    ) == 0:

        raise RuntimeError(
            "TTS produced an empty audio file."
        )

    return output_path
