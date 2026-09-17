import os


# ============================================================
# FORMAT TIME
# ============================================================

def format_time(
    seconds,
):

    total_ms = int(
        round(seconds * 1000)
    )

    hours = (
        total_ms // 3_600_000
    )

    total_ms %= 3_600_000

    minutes = (
        total_ms // 60_000
    )

    total_ms %= 60_000

    secs = (
        total_ms // 1000
    )

    milliseconds = (
        total_ms % 1000
    )

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d},"
        f"{milliseconds:03d}"
    )


# ============================================================
# PARSE TIME
# ============================================================

def parse_srt_time(
    value,
):

    hours, minutes, rest = value.split(
        ":"
    )

    seconds, milliseconds = rest.split(
        ","
    )

    return (
        int(hours) * 3600
        + int(minutes) * 60
        + int(seconds)
        + int(milliseconds) / 1000
    )


# ============================================================
# SPLIT TEXT
# ============================================================

def split_text(
    text,
    max_chars=42,
):

    words = text.split()

    if not words:

        return []

    lines = []

    current = ""

    for word in words:

        candidate = (
            word
            if not current
            else current + " " + word
        )

        if len(candidate) <= max_chars:

            current = candidate

        else:

            if current:

                lines.append(
                    current
                )

            current = word

    if current:

        lines.append(
            current
        )

    return lines


# ============================================================
# CREATE SCENE SRT
# ============================================================

def create_scene_srt(
    narration,
    duration,
    output_path,
    max_chars=42,
):

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    lines = split_text(
        narration,
        max_chars,
    )

    if not lines:

        lines = [
            narration.strip()
        ]

    # Weight timing according to character count.
    weights = [
        max(1, len(line))
        for line in lines
    ]

    total_weight = sum(
        weights
    )

    current_time = 0.0

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as file:

        for index, line in enumerate(
            lines,
            start=1,
        ):

            segment_duration = (
                duration
                * weights[index - 1]
                / total_weight
            )

            start = current_time

            end = (
                current_time
                + segment_duration
            )

            file.write(
                f"{index}\n"
            )

            file.write(
                f"{format_time(start)} --> "
                f"{format_time(end)}\n"
            )

            file.write(
                line
                + "\n\n"
            )

            current_time = end

    return output_path


# ============================================================
# COMBINE SRT FILES
# ============================================================

def combine_srt_files(
    subtitle_files,
    scene_durations,
    output_path,
):

    if not subtitle_files:

        raise ValueError(
            "No subtitle files supplied."
        )

    if len(subtitle_files) != len(
        scene_durations
    ):

        raise ValueError(
            "Subtitle count and scene duration "
            "count do not match."
        )

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    subtitle_number = 1

    current_offset = 0.0

    with open(
        output_path,
        "w",
        encoding="utf-8",
    ) as output:

        for scene_index, subtitle_file in enumerate(
            subtitle_files
        ):

            with open(
                subtitle_file,
                "r",
                encoding="utf-8",
            ) as input_file:

                content = input_file.read().strip()

            if not content:

                current_offset += (
                    scene_durations[
                        scene_index
                    ]
                )

                continue

            blocks = content.split(
                "\n\n"
            )

            for block in blocks:

                lines = block.strip().splitlines()

                if len(lines) < 3:

                    continue

                timing = lines[1]

                if " --> " not in timing:

                    continue

                start_text, end_text = (
                    timing.split(
                        " --> ",
                        1
                    )
                )

                start = (
                    parse_srt_time(
                        start_text
                    )
                    + current_offset
                )

                end = (
                    parse_srt_time(
                        end_text
                    )
                    + current_offset
                )

                subtitle_text = "\n".join(
                    lines[2:]
                )

                output.write(
                    f"{subtitle_number}\n"
                )

                output.write(
                    f"{format_time(start)} --> "
                    f"{format_time(end)}\n"
                )

                output.write(
                    subtitle_text
                    + "\n\n"
                )

                subtitle_number += 1

            current_offset += (
                scene_durations[
                    scene_index
                ]
            )

    return output_path
