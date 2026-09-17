import os
import subprocess

import imageio_ffmpeg


FFMPEG = imageio_ffmpeg.get_ffmpeg()


# ============================================================
# CREATE CONCAT FILE
# ============================================================

def create_concat_file(
    media_files,
    concat_file,
):

    if not media_files:

        raise ValueError(
            "No media files supplied."
        )

    directory = os.path.dirname(
        concat_file
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    with open(
        concat_file,
        "w",
        encoding="utf-8",
    ) as file:

        for media in media_files:

            if not os.path.exists(
                media
            ):

                raise FileNotFoundError(
                    media
                )

            absolute_path = os.path.abspath(
                media
            )

            escaped = (
                absolute_path
                .replace(
                    "'",
                    "'\\''"
                )
            )

            file.write(
                f"file '{escaped}'\n"
            )


# ============================================================
# CONCATENATE VIDEOS
# ============================================================

def concatenate_videos(
    video_files,
    output_path,
):

    if not video_files:

        raise ValueError(
            "No scene videos supplied."
        )

    concat_file = os.path.join(
        os.path.dirname(output_path),
        "video_concat.txt",
    )

    create_concat_file(
        video_files,
        concat_file,
    )

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    command = [
        FFMPEG,

        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        concat_file,

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "23",

        "-pix_fmt",
        "yuv420p",

        "-r",
        "30",

        "-movflags",
        "+faststart",

        output_path,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Video concatenation failed:\n"
            + result.stderr[-5000:]
        )

    return output_path


# ============================================================
# CONCATENATE AUDIO
# ============================================================

def concatenate_audio(
    audio_files,
    output_path,
):

    if not audio_files:

        raise ValueError(
            "No audio files supplied."
        )

    concat_file = os.path.join(
        os.path.dirname(output_path),
        "audio_concat.txt",
    )

    create_concat_file(
        audio_files,
        concat_file,
    )

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    command = [
        FFMPEG,

        "-y",

        "-f",
        "concat",

        "-safe",
        "0",

        "-i",
        concat_file,

        "-c:a",
        "libmp3lame",

        "-b:a",
        "192k",

        output_path,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Audio concatenation failed:\n"
            + result.stderr[-5000:]
        )

    return output_path


# ============================================================
# MUX AUDIO + VIDEO
# ============================================================

def mux_audio(
    video_path,
    audio_path,
    output_path,
):

    if not os.path.exists(
        video_path
    ):

        raise FileNotFoundError(
            video_path
        )

    if not os.path.exists(
        audio_path
    ):

        raise FileNotFoundError(
            audio_path
        )

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    command = [
        FFMPEG,

        "-y",

        "-i",
        video_path,

        "-i",
        audio_path,

        "-map",
        "0:v:0",

        "-map",
        "1:a:0",

        "-c:v",
        "copy",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-shortest",

        "-movflags",
        "+faststart",

        output_path,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Audio/video muxing failed:\n"
            + result.stderr[-5000:]
        )

    return output_path


# ============================================================
# BURN CAPTIONS
# ============================================================

def burn_captions(
    video_path,
    subtitle_path,
    output_path,
):

    if not os.path.exists(
        video_path
    ):

        raise FileNotFoundError(
            video_path
        )

    if not os.path.exists(
        subtitle_path
    ):

        raise FileNotFoundError(
            subtitle_path
        )

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    subtitle_path = os.path.abspath(
        subtitle_path
    )

    # Convert Windows separators to FFmpeg-compatible
    # forward slashes.
    subtitle_path = subtitle_path.replace(
        "\\",
        "/"
    )

    # Escape characters required by the FFmpeg filter.
    escaped_subtitle = (
        subtitle_path
        .replace(
            ":",
            "\\:"
        )
        .replace(
            "'",
            "\\'"
        )
        .replace(
            "[",
            "\\["
        )
        .replace(
            "]",
            "\\]"
        )
    )

    fonts_directory = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "fonts",
        )
    ).replace(
        "\\",
        "/"
    )

    fonts_directory = (
        fonts_directory
        .replace(
            ":",
            "\\:"
        )
        .replace(
            "'",
            "\\'"
        )
    )

    subtitle_filter = (
        "subtitles="
        f"'{escaped_subtitle}'"
        f":fontsdir='{fonts_directory}'"
        ":force_style="
        "'FontName=Noto Sans Devanagari,"
        "FontSize=18,"
        "Alignment=2,"
        "MarginV=90,"
        "Outline=2,"
        "Shadow=1'"
    )

    command = [
        FFMPEG,

        "-y",

        "-i",
        video_path,

        "-vf",
        subtitle_filter,

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "23",

        "-pix_fmt",
        "yuv420p",

        "-c:a",
        "aac",

        "-b:a",
        "192k",

        "-movflags",
        "+faststart",

        output_path,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:

        raise RuntimeError(
            "Caption burning failed:\n"
            + result.stderr[-6000:]
        )

    return output_path
