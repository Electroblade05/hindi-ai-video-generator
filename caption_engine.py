import re


def seconds_to_srt(seconds):

    hours = int(seconds // 3600)

    minutes = int(
        (seconds % 3600) // 60
    )

    secs = int(seconds % 60)

    milliseconds = int(
        (seconds - int(seconds)) * 1000
    )

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{milliseconds:03d}"
    )


def split_text(text, max_words=10):

    words = text.split()

    chunks = []

    current = []

    for word in words:

        current.append(word)

        if len(current) >= max_words:

            chunks.append(
                " ".join(current)
            )

            current = []

    if current:
        chunks.append(
            " ".join(current)
        )

    return chunks


def create_srt(
    script,
    audio_duration,
    output_path
):

    chunks = split_text(script)

    if not chunks:
        raise ValueError(
            "No text available for captions."
        )

    chunk_duration = (
        audio_duration / len(chunks)
    )

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        for i, chunk in enumerate(chunks):

            start = i * chunk_duration

            end = (
                (i + 1) * chunk_duration
            )

            file.write(
                f"{i + 1}\n"
            )

            file.write(
                f"{seconds_to_srt(start)} --> "
                f"{seconds_to_srt(end)}\n"
            )

            file.write(
                chunk + "\n\n"
            )

    return output_path
