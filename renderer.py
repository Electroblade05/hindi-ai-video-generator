
import os
import subprocess

from config import FONT_DIR

FFMPEG = "ffmpeg"


def run_ffmpeg(command):
    """Execute FFmpeg and report useful errors."""
    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError(
            "FFmpeg is not installed or not available in PATH."
        ) from exc

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg error:\n" + result.stderr[-6000:]
        )

    return result


def prepare_output(output_path):
    if not output_path:
        raise ValueError("Output path is required.")

    os.makedirs(
        os.path.dirname(os.path.abspath(output_path)),
        exist_ok=True,
    )


def validate_files(paths, description):
    if not paths:
        raise ValueError(f"No {description} files provided.")

    valid = [
        os.fspath(path)
        for path in paths
        if path and os.path.isfile(path)
    ]

    if not valid:
        raise FileNotFoundError(
            f"No valid {description} files found."
        )

    return valid


def create_concat_list(paths, output_path, name):
    directory = os.path.dirname(
        os.path.abspath(output_path)
    )

    list_path = os.path.join(
        directory,
        f"{name}_concat_list.txt"
    )

    with open(list_path, "w", encoding="utf-8") as file:
        for path in paths:
            path = os.path.abspath(path).replace("\\", "/")
            path = path.replace("'", "'\\''")
            file.write(f"file '{path}'\n")

    return list_path


def concatenate_videos(
    video_paths=None,
    output_path=None,
    video_files=None
):
    # Support old and new app.py argument names.
    if video_paths is None:
        video_paths = video_files

    videos = validate_files(video_paths, "video")
    prepare_output(output_path)

    concat_list = create_concat_list(
        videos, output_path, "video"
    )

    try:
        run_ffmpeg([
            FFMPEG, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            "-movflags", "+faststart",
            output_path
        ])
    finally:
        if os.path.exists(concat_list):
            os.remove(concat_list)

    return output_path


def concatenate_audio(
    audio_paths=None,
    output_path=None,
    audio_files=None
):
    # Support old and new app.py argument names.
    if audio_paths is None:
        audio_paths = audio_files

    audios = validate_files(audio_paths, "audio")
    prepare_output(output_path)

    concat_list = create_concat_list(
        audios, output_path, "audio"
    )

    try:
        run_ffmpeg([
            FFMPEG, "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", concat_list,
            "-c", "copy",
            output_path
        ])
    finally:
        if os.path.exists(concat_list):
            os.remove(concat_list)

    return output_path


def mux_audio(video_path, audio_path, output_path):
    """Combine video and narration audio."""

    if not os.path.isfile(video_path):
        raise FileNotFoundError(video_path)

    if not os.path.isfile(audio_path):
        raise FileNotFoundError(audio_path)

    prepare_output(output_path)

    run_ffmpeg([
        FFMPEG, "-y",
        "-i", video_path,
        "-i", audio_path,
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        "-movflags", "+faststart",
        output_path
    ])

    return output_path


def burn_captions(
    video_path,
    subtitle_path,
    output_path
):
    """Burn Hindi/English SRT subtitles into the video."""

    if not os.path.isfile(video_path):
        raise FileNotFoundError(video_path)

    if not os.path.isfile(subtitle_path):
        raise FileNotFoundError(subtitle_path)

    prepare_output(output_path)

    def escape_path(path):
        path = os.path.abspath(path).replace("\\", "/")
        for char in ("\\", ":", "'", ",", "[", "]"):
            path = path.replace(char, "\\" + char)
        return path

    subtitle = escape_path(subtitle_path)
    fonts = escape_path(FONT_DIR)

    style = (
        "FontName=Noto Sans Devanagari,"
        "FontSize=24,"
        "PrimaryColour=&H00FFFFFF,"
        "OutlineColour=&H00000000,"
        "BorderStyle=1,"
        "Outline=2,"
        "Shadow=1,"
        "Alignment=2,"
        "MarginV=70"
    )

    subtitle_filter = (
        f"subtitles=filename='{subtitle}'"
        f":fontsdir='{fonts}'"
        f":force_style='{style}'"
    )

    run_ffmpeg([
        FFMPEG, "-y",
        "-i", video_path,
        "-vf", subtitle_filter,
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        output_path
    ])

    return output_path


def normalize_video(
    input_path,
    output_path,
    width=1080,
    height=1920,
    fps=30
):
    """Normalize video dimensions, frame rate and encoding."""

    if not os.path.isfile(input_path):
        raise FileNotFoundError(input_path)

    prepare_output(output_path)

    video_filter = (
        f"scale={width}:{height}:"
        "force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2"
    )

    run_ffmpeg([
        FFMPEG, "-y",
        "-i", input_path,
        "-vf", video_filter,
        "-r", str(fps),
        "-map", "0:v:0",
        "-map", "0:a?",
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "23",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ])

    return output_path
            
