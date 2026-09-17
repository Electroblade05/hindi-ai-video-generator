import math
import wave
import struct


def generate_background_music(
    output_path,
    duration,
    volume=0.06
):

    sample_rate = 44100

    total_samples = int(
        sample_rate * duration
    )

    frequencies = [
        220.0,
        277.18,
        329.63
    ]

    with wave.open(
        output_path,
        "w"
    ) as wav:

        wav.setnchannels(1)

        wav.setsampwidth(2)

        wav.setframerate(
            sample_rate
        )

        for i in range(total_samples):

            t = i / sample_rate

            value = 0

            for frequency in frequencies:

                value += math.sin(
                    2 * math.pi * frequency * t
                )

            value /= len(frequencies)

            # Gentle fade-in/fade-out.
            fade = min(
                1,
                t / 2,
                (duration - t) / 2
            )

            sample = int(
                value *
                volume *
                fade *
                32767
            )

            wav.writeframes(
                struct.pack(
                    "<h",
                    sample
                )
            )

    return output_path
