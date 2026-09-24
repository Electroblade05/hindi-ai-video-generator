import os
import subprocess


# ============================================================
# FFMPEG
# ============================================================

FFMPEG = "ffmpeg"


# ============================================================
# RUN FFMPEG
# ============================================================

def run_ffmpeg(command):
    """
    Run an FFmpeg command and raise an error if it fails.
    """

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "FFmpeg failed:\n\n"
            + result.stderr[-5000:]
        )

    return result


# ============================================================
# CONCATENATE VIDEOS
# ============================================================

def concatenate_videos(video_paths, output_path):
    """
    Concatenate multiple video files into one video.
    """

    if not video_paths:
        raise ValueError("No video files were provided.")

    valid_paths = [
        path for path in video_paths
        if path and os.path.exists(path)
    ]

    if not valid_paths:
        raise FileNotFoundError(
            "None of the video files exist."
        )

    output_directory = os.path.dirname(
        os.path.abspath(output_path)
    )

    os.makedirs(
        output_directory,
        exist_ok=True,
    )

    list_file = os.path.join(
        output_directory,
        "video_concat_list.txt",
    )

    with open(
        list_file,
        "w",
        encoding="utf-8",
    ) as f:

        for path in valid_paths:

            absolute_path = os.path.abspath(path)

            safe_path = (
                absolute_path
                .replace("\\", "/")
                .replace("'", "'\\''")
            )

            f.write(
                f"file '{safe_path}'\n"
            )

    command = [
        FFMPEG,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_file,
        "-c",
        "copy",
        output_path,
    ]

    try:

        run_ffmpeg(command)

    finally:

        if os.path.exists(list_file):
            os.remove(list_file)

    if not os.path.exists(output_path):
        raise RuntimeError(
            "FFmpeg completed, but the "
            "concatenated video was not created."
        )

    return output_path


# ============================================================
# CONCATENATE AUDIO
# ============================================================

def concatenate_audio(audio_paths, output_path):
    """
    Concatenate multiple audio files into one audio file.
    """

    if not audio_paths:
        raise ValueError("No audio files were provided.")

    valid_paths = [
        path for path in audio_paths
        if path and os.path.exists(path)
    ]

    if not valid_paths:
        raise FileNotFoundError(
            "None of the audio files exist."
        )

    output_directory = os.path.dirname(
        os.path.abspath(output_path)
    )

    os.makedirs(
        output_directory,
        exist_ok=True,
    )

    list_file = os.path.join(
        output_directory,
        "audio_concat_list.txt",
    )

    with open(
        list_file,
        "w",
        encoding="utf-8",
    ) as f:

        for path in valid_paths:

            absolute_path = os.path.abspath(path)

            safe_path = (
                absolute_path
                .replace("\\", "/")
                .replace("'", "'\\''")
            )

            f.write(
                f"file '{safe_path}'\n"
            )

    command = [
        FFMPEG,
        "-y",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_file,
        "-c",
        "copy",
        output_path,
    ]

    try:

        run_ffmpeg(command)

    finally:

        if os.path.exists(list_file):
            os.remove(list_file)

    if not os.path.exists(output_path):
        raise RuntimeError(
            "FFmpeg completed, but the "
            "concatenated audio was not created."
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
    """
    Combine a video file and an audio file.
    """

    if not os.path.exists(video_path):
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    if not os.path.exists(audio_path):
        raise FileNotFoundError(
            f"Audio not found: {audio_path}"
        )

    output_directory = os.path.dirname(
        os.path.abspath(output_path)
    )

    os.makedirs(
        output_directory,
        exist_ok=True,
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

    run_ffmpeg(command)

    if not os.path.exists(output_path):
        raise RuntimeError(
            "FFmpeg completed, but the final "
            "video was not created."
        )

    return output_path


# ============================================================
# ADD AUDIO TO VIDEO
# ============================================================

def add_audio_to_video(
    video_path,
    audio_path,
    output_path,
):
    """
    Alias for mux_audio().
    """

    return mux_audio(
        video_path,
        audio_path,
        output_path,
    )


# ============================================================
# NORMALIZE VIDEO
# ============================================================

def normalize_video(
    input_path,
    output_path,
    width=1080,
    height=1920,
    fps=30,
):
    """
    Re-encode a video to a standard MP4 format.
    """

    if not os.path.exists(input_path):
        raise FileNotFoundError(
            f"Video not found: {input_path}"
        )

    output_directory = os.path.dirname(
        os.path.abspath(output_path)
    )

    os.makedirs(
        output_directory,
        exist_ok=True,
    )

    video_filter = (
        f"scale={width}:{height}:"
        "force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:"
        f"(ow-iw)/2:"
        f"(oh-ih)/2"
    )

    command = [
        FFMPEG,
        "-y",

        "-i",
        input_path,

        "-vf",
        video_filter,

        "-r",
        str(fps),

        "-c:v",
        "libx264",

        "-preset",
        "medium",

        "-crf",
        "23",

        "-pix_fmt",
        "yuv420p",

        "-movflags",
        "+faststart",

        output_path,
    ]

    run_ffmpeg(command)

    if not os.path.exists(output_path):
        raise RuntimeError(
            "FFmpeg completed, but the normalized "
            "video was not created."
        )

    return output_path
