import os
import subprocess


def run_ffmpeg(command):

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:

        raise RuntimeError(
            "FFmpeg failed:\n\n"
            + result.stderr[-4000:]
        )


def create_concat_file(
    clip_paths,
    output_path
):

    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:

        for path in clip_paths:

            absolute = os.path.abspath(path)

            # Escape single quotes.
            absolute = absolute.replace(
                "'",
                "'\\''"
            )

            file.write(
                f"file '{absolute}'\n"
            )


def combine_clips(
    clip_paths,
    output_path,
    temp_dir
):

    concat_file = os.path.join(
        temp_dir,
        "clips.txt"
    )

    create_concat_file(
        clip_paths,
        concat_file
    )

    run_ffmpeg([
        "ffmpeg",
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        concat_file,
        "-c",
        "copy",
        output_path
    ])

    return output_path


def get_audio_duration(audio_path):

    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            audio_path
        ],
        capture_output=True,
        text=True
    )

    return float(
        result.stdout.strip()
    )


def render_final_video(
    video_path,
    narration_path,
    music_path,
    subtitles_path,
    output_path
):

    subtitle_filter = (
        "subtitles="
        + subtitles_path.replace(
            "\\",
            "/"
        ).replace(
            ":",
            "\\:"
        )
        + ":force_style="
        "'FontSize=18,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=2,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=70'"
    )

    command = [
        "ffmpeg",
        "-y",

        "-i",
        video_path,

        "-i",
        narration_path,

        "-i",
        music_path,

        "-filter_complex",

        "[2:a]volume=0.12[music];"
        "[1:a][music]"
        "amix=inputs=2:"
        "duration=first:"
        "dropout_transition=2[audio]",

        "-map",
        "0:v",

        "-map",
        "[audio]",

        "-vf",
        subtitle_filter,

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "23",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-shortest",

        output_path
    ]

    run_ffmpeg(command)

    return output_path
