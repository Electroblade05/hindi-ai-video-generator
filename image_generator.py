import os
import base64
import urllib.parse

import requests

from PIL import Image


# ============================================================
# CLOUD IMAGE GENERATION
# ============================================================

def generate_cloud_image(
    prompt,
    output_path,
    width,
    height,
):

    if not prompt or not prompt.strip():

        raise ValueError(
            "Visual prompt is empty."
        )

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    enhanced_prompt = (
        prompt.strip()
        + ", cinematic composition, "
        "high detail, realistic lighting, "
        "professional film frame, "
        "sharp details, no text, no watermark"
    )

    encoded_prompt = urllib.parse.quote(
        enhanced_prompt,
        safe="",
    )

    url = (
        "https://image.pollinations.ai/prompt/"
        + encoded_prompt
        + f"?width={width}"
        + f"&height={height}"
        + "&nologo=true"
    )

    try:

        response = requests.get(
            url,
            timeout=180,
        )

    except Exception as error:

        raise RuntimeError(
            "Cloud image service connection failed:\n"
            + str(error)
        )

    if response.status_code != 200:

        raise RuntimeError(
            "Cloud image generation failed.\n"
            f"HTTP status: {response.status_code}"
        )

    content_type = response.headers.get(
        "content-type",
        "",
    )

    if "image" not in content_type.lower():

        raise RuntimeError(
            "Cloud service did not return an image."
        )

    with open(
        output_path,
        "wb",
    ) as file:

        file.write(
            response.content
        )

    return output_path


# ============================================================
# LOCAL STABLE DIFFUSION
# ============================================================

def generate_local_image(
    prompt,
    output_path,
    width,
    height,
    endpoint,
):

    if not prompt or not prompt.strip():

        raise ValueError(
            "Visual prompt is empty."
        )

    if not endpoint:

        raise ValueError(
            "Local AI endpoint is empty."
        )

    directory = os.path.dirname(
        output_path
    )

    if directory:

        os.makedirs(
            directory,
            exist_ok=True
        )

    endpoint = endpoint.rstrip("/")

    url = (
        endpoint
        + "/sdapi/v1/txt2img"
    )

    payload = {
        "prompt": prompt.strip(),

        "negative_prompt": (
            "text, watermark, logo, "
            "blurry, low quality, "
            "distorted, duplicate, "
            "deformed"
        ),

        "width": int(width),

        "height": int(height),

        "steps": 25,

        "cfg_scale": 7,

        "batch_size": 1,

        "n_iter": 1,
    }

    try:

        response = requests.post(
            url,
            json=payload,
            timeout=600,
        )

    except Exception as error:

        raise RuntimeError(
            "Could not connect to local AI server:\n"
            + str(error)
        )

    if response.status_code != 200:

        raise RuntimeError(
            "Local image generation failed.\n"
            f"HTTP status: {response.status_code}\n"
            + response.text[:1000]
        )

    try:

        data = response.json()

    except Exception as error:

        raise RuntimeError(
            "Local AI server returned invalid JSON:\n"
            + str(error)
        )

    images = data.get(
        "images"
    )

    if not images:

        raise RuntimeError(
            "Local AI server returned no image."
        )

    try:

        image_bytes = base64.b64decode(
            images[0]
        )

    except Exception as error:

        raise RuntimeError(
            "Could not decode local AI image:\n"
            + str(error)
        )

    with open(
        output_path,
        "wb",
    ) as file:

        file.write(
            image_bytes
        )

    return output_path


# ============================================================
# UPLOAD IMAGE
# ============================================================

def save_uploaded_image(
    uploaded_file,
    output_path,
):

    if uploaded_file is None:

        raise ValueError(
            "No image was uploaded."
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

        image = Image.open(
            uploaded_file
        )

        image = image.convert(
            "RGB"
        )

        image.save(
            output_path,
            "PNG",
        )

    except Exception as error:

        raise RuntimeError(
            "Could not process uploaded image:\n"
            + str(error)
        )

    return output_path


# ============================================================
# UNIVERSAL IMAGE FUNCTION
# ============================================================

def generate_scene_image(
    mode,
    prompt,
    output_path,
    width,
    height,
    uploaded_file=None,
    local_endpoint=None,
):

    if mode == "Free Cloud":

        return generate_cloud_image(
            prompt=prompt,
            output_path=output_path,
            width=width,
            height=height,
        )

    if mode == "Local AI":

        return generate_local_image(
            prompt=prompt,
            output_path=output_path,
            width=width,
            height=height,
            endpoint=local_endpoint,
        )

    if mode == "Upload Image":

        return save_uploaded_image(
            uploaded_file=uploaded_file,
            output_path=output_path,
        )

    raise ValueError(
        "Unknown image generation mode: "
        + str(mode)
  )
