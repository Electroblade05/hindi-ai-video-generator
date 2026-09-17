import os
import re
import subprocess

import imageio_ffmpeg

from PIL import Image

from config import FPS


FFMPEG = imageio_ffmpeg.get_ffmpeg()


# ============================================================
# MEDIA DURATION
# ============================================================

def get_media_duration(
    file_path,
):

    if not os.path.exists(
        file_path
    ):

        raise FileNotFoundError(
            file_path
        )

    command = [
        FFMPEG,
        "-i",
        file_path,
    ]

    result = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    match = re.search(
        r"Duration:\s*(\d+):(\d+):([\d.]+)",
        result.stderr,
    )

    if not match:

        raise RuntimeError(
            "Could not determine media duration:\n"
            + result.stderr[-2000:]
        )

    hours = int(
        match.group(1)
    )

    minutes = int(
        match.group(2)
    )

    seconds = float(
        match.group(3)
    )

    return (
        hours * 3600
        + minutes * 60
        + seconds
    )


# ============================================================
# PREPARE IMAGE
# ============================================================

def prepare_image(
    image_path,
    width,
    height,
):

    if not os.path.exists(
        image_path
    ):

        raise FileNotFoundError(
            image_path
        )

    try:

        image = Image.open(
            image_path
        ).convert("RGB")

        target_ratio = (
            width / height
        )

        image_ratio = (
            image.width / image.height
        )

        if image_ratio > target_ratio:

            new_height = image.height

            new_width = int(
                new_height * target_ratio
            )

            left = (
                image.width - new_width
            ) // 2

            image = image.crop(
                (
                    left,
                    0,
                    left + new_width,
                    new_height,
                )
            )

        else:

            new_width = image.width

            new_height = int(
                new_width / target_ratio
            )

            top = (
                image.height - new_height
            ) // 2

            image = image.crop(
                (
                    0,
                    top,
                    new_width,
                    top + new_height,
                )
            )

        image = image.resize(
            (
                width * 2,
                height * 2,
            ),
            Image.Resampling.LANCZOS,
        )

        image.save(
            image_path,
            "PNG",
        )

    except Exception as error:

        raise RuntimeError(
            "Could not prepare scene image:\n"
            + str(error)
        )

    return image_path


# ============================================================
# MOTION SCENE
# ============================================================

def create_motion_scene(
    image_path,
    output_path,
    duration,
    width,
    height,
    effect,
):

    if not os.path.exists(
        image_path
    ):

        raise FileNotFoundError(
            image_path
        )

    os.makedirs(
        os.path.dirname(output_path)
        or ".",
        exist_ok=True,
    )

    prepare_image(
        image_path=image_path,
        width=width,
        height=height,
    )

    frames = max(
        1,
        int(round(duration * FPS)),
    )

    denominator = max(
        1,
        frames - 1,
    )

    # ========================================================
    # ZOOM IN
    # ========================================================

    if effect == "zoom_in":

        zoom_expression = (
            f"1+0.15*on/{denominator}"
        )

        x_expression = (
            "iw/2-(iw/zoom/2)"
        )

        y_expression = (
            "ih/2-(ih/zoom/2)"
        )

    # ========================================================
    # ZOOM OUT
    # ========================================================

    elif effect == "zoom_out":

        zoom_expression = (
            f"1.15-0.15*on/{denominator}"
        )

        x_expression = (
            "iw/2-(iw/zoom/2)"
        )

        y_expression = (
            "ih/2-(ih/zoom/2)"
        )

    # ========================================================
    # PAN LEFT
    # ========================================================

    elif effect == "pan_left":

        zoom_expression = "1.08"

        x_expression = (
            f"(iw-iw/zoom)*on/{denominator}"
        )

        y_expression = (
            "ih/2-(ih/zoom/2)"
        )

    # ========================================================
    # PAN RIGHT
    # ========================================================

    elif effect == "pan_right":

        zoom_expression = "1.08"

        x_expression = (
            f"(iw-iw/zoom)*(1-on/{denominator})"
        )

        y_expression = (
            "ih/2-(ih/zoom/2)"
        )

    else:

        zoom_expression = "1.05"

        x_expression = (
            "iw/2-(iw/zoom/2)"
        )

        y_expression = (
            "ih/2-(ih/zoom/2)"
        )

    # ========================================================
    # ZOOMPAN FILTER
    # ========================================================

    filter_string = (
        "zoompan="
        f"z='{zoom_expression}':"
        f"x='{x_expression}':"
        f"y='{y_expression}':"
        f"d={frames}:"
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

        "-vf",
        filter_string,

        "-t",
        str(duration),

        "-r",
        str(FPS),

        "-an",

        "-c:v",
        "libx264",

        "-preset",
        "veryfast",

        "-crf",
        "23",

        "-pix_fmt",
        "yuv420p",

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
            "Motion scene generation failed:\n"
            + result.stderr[-4000:]
        )

    if not os.path.exists(
        output_path
    ):

        raise RuntimeError(
            "Motion scene was not created."
        )

    return output_path
