import os
import subprocess

from config import FPS


FFMPEG = "ffmpeg"


def get_media_duration(media_path):
    """
    Get the duration of an audio/video file in seconds.
    """

    if not media_path or not os.path.exists(media_path):
        return 0.0

    command = [
        FFMPEG,
        "-i",
        media_path,
    ]

    try:
        result = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        output = result.stderr

        for line in output.splitlines():

            if "Duration:" in line:

                duration_text = (
                    line.split("Duration:")[1]
                    .split(",")[0]
                    .strip()
                )

                hours, minutes, seconds = (
                    duration_text.split(":")
                )

                return (
                    float(hours) * 3600
                    + float(minutes) * 60
                    + float(seconds)
                )

    except Exception:
        pass

    return 0.0


def create_motion_scene(
    image_path,
    output_path,
    duration,
    width=1080,
    height=1920,
    zoom_start=1.0,
    zoom_end=1.08,
):
    """
    Create a vertical 9:16 animated video
    from a still image using a slow zoom effect.
    """

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    duration = max(float(duration), 0.1)

    total_frames = max(
        int(duration * FPS),
        1,
    )

    if total_frames > 1:

        zoom_step = (
            zoom_end - zoom_start
        ) / (total_frames - 1)

    else:

        zoom_step = 0

    zoom_expression = (
        f"min("
        f"{zoom_start}+"
        f"{zoom_step:.8f}*on,"
        f"{zoom_end}"
        f")"
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
        f"force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"zoompan="
        f"z='{zoom_expression}':"
        f"x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':"
        f"d={total_frames}:"
        f"s={width}x{height}:"
        f"fps={FPS}"
    )

    command = [
        FFMPEG,
        "-y",
        "-loop",
        "1",
        "-i",
        image_path,
        "-t",
        str(duration),
        "-vf",
        video_filter,
        "-r",
        str(FPS),
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
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
            "FFmpeg failed while creating the motion scene.\n\n"
            + result.stderr[-4000:]
        )

    if not os.path.exists(output_path):

        raise RuntimeError(
            "FFmpeg completed, but the output video "
            "was not created."
        )

    return output_path


def create_motion_scene_landscape(
    image_path,
    output_path,
    duration,
    width=1920,
    height=1080,
    zoom_start=1.0,
    zoom_end=1.08,
):
    """
    Create a 16:9 animated video
    from a still image using a slow zoom effect.
    """

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    duration = max(float(duration), 0.1)

    total_frames = max(
        int(duration * FPS),
        1,
    )

    if total_frames > 1:

        zoom_step = (
            zoom_end - zoom_start
        ) / (total_frames - 1)

    else:

        zoom_step = 0

    zoom_expression = (
        f"min("
        f"{zoom_start}+"
        f"{zoom_step:.8f}*on,"
        f"{zoom_end}"
        f")"
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
        f"force_original_aspect_ratio=increase,"
        f"crop={width}:{height},"
        f"zoompan="
        f"z='{zoom_expression}':"
        f"x='iw/2-(iw/zoom/2)':"
        f"y='ih/2-(ih/zoom/2)':"
        f"d={total_frames}:"
        f"s={width}x{height}:"
        f"fps={FPS}"
    )

    command = [
        FFMPEG,
        "-y",
        "-loop",
        "1",
        "-i",
        image_path,
        "-t",
        str(duration),
        "-vf",
        video_filter,
        "-r",
        str(FPS),
        "-an",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
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
            "FFmpeg failed while creating the landscape motion scene.\n\n"
            + result.stderr[-4000:]
        )

    if not os.path.exists(output_path):

        raise RuntimeError(
            "FFmpeg completed, but the output video "
            "was not created."
        )

    return output_path
