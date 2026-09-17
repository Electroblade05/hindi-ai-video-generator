import os
import streamlit as st

from config import (
    FEMALE_HINDI_VOICE,
    MALE_HINDI_VOICE,
    DEFAULT_LOCAL_IMAGE_ENDPOINT,
    OUTPUT_DIR,
    IMAGES_DIR,
    AUDIO_DIR,
    SCENES_DIR,
    CAPTIONS_DIR,
    FINAL_DIR,
)

from tts import generate_hinglish_voice

from image_generator import generate_scene_image

from video_generator import (
    get_media_duration,
    create_motion_scene,
)

from captions import (
    create_scene_srt,
    combine_srt_files,
)

from renderer import (
    concatenate_videos,
    concatenate_audio,
    mux_audio,
    burn_captions,
)

from utils import (
    clean_output,
    create_directories,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Hinglish AI Video Generator",
    page_icon="🎬",
    layout="wide",
)


# ============================================================
# HEADER
# ============================================================

st.title("🎬 Hinglish AI Video Generator")

st.markdown(
    """
Create videos using:

**Hinglish narration + visual prompts**

The app creates:

🎙️ Hinglish voice  
🖼️ Scene images  
🎥 Cinematic motion  
💬 Captions  
🎬 Final MP4
"""
)

st.info(
    "Your narration is sent directly to the TTS engine. "
    "The app does not translate your Hinglish narration."
)


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Video Settings")


# ============================================================
# ASPECT RATIO
# ============================================================

aspect_ratio = st.sidebar.selectbox(
    "Aspect Ratio",
    [
        "9:16 Shorts",
        "16:9 YouTube",
    ],
)


if aspect_ratio == "9:16 Shorts":
    width = 1080
    height = 1920
else:
    width = 1280
    height = 720


# ============================================================
# VOICE
# ============================================================

voice_option = st.sidebar.selectbox(
    "Voice",
    [
        "Female Hindi",
        "Male Hindi",
    ],
)


if voice_option == "Female Hindi":
    selected_voice = FEMALE_HINDI_VOICE
else:
    selected_voice = MALE_HINDI_VOICE


# ============================================================
# SPEECH RATE
# ============================================================

speech_rate = st.sidebar.selectbox(
    "Speech Rate",
    [
        "-15%",
        "-10%",
        "-5%",
        "+0%",
        "+5%",
        "+10%",
        "+15%",
    ],
    index=3,
)


# ============================================================
# CAPTIONS
# ============================================================

caption_enabled = st.sidebar.checkbox(
    "Enable captions",
    value=True,
)


# ============================================================
# IMAGE MODE
# ============================================================

image_mode = st.sidebar.selectbox(
    "Image Generation Mode",
    [
        "Free Cloud",
        "Local AI",
        "Upload Image",
    ],
)


# ============================================================
# LOCAL IMAGE SERVER
# ============================================================

local_endpoint = DEFAULT_LOCAL_IMAGE_ENDPOINT


if image_mode == "Local AI":

    local_endpoint = st.sidebar.text_input(
        "Local AI Endpoint",
        value=DEFAULT_LOCAL_IMAGE_ENDPOINT,
    )

    st.sidebar.info(
        "The endpoint must provide a "
        "Stable-Diffusion WebUI-compatible "
        "/sdapi/v1/txt2img API."
    )


# ============================================================
# SCENE COUNT
# ============================================================

scene_count = st.number_input(
    "Number of scenes",
    min_value=1,
    max_value=30,
    value=5,
    step=1,
)


# ============================================================
# SCENE INPUT
# ============================================================

scenes = []


for i in range(int(scene_count)):

    st.subheader(f"🎥 Scene {i + 1}")

    col1, col2 = st.columns(2)

    with col1:

        prompt = st.text_area(
            "Visual Prompt",
            key=f"prompt_{i}",
            height=160,
            placeholder=(
                "Cinematic realistic Earth from space, "
                "two moons visible, dramatic sunlight, "
                "deep blue atmosphere, realistic "
                "astronomy documentary frame"
            ),
        )

    with col2:

        narration = st.text_area(
            "Hinglish Narration",
            key=f"narration_{i}",
            height=160,
            placeholder=(
                "Socho agar Earth ke paas ek nahi, "
                "balki two moons hote. "
                "Raat ka sky completely different dikhta."
            ),
        )

    effect = st.selectbox(
        "Motion Effect",
        [
            "zoom_in",
            "zoom_out",
            "pan_left",
            "pan_right",
        ],
        key=f"effect_{i}",
    )

    uploaded_file = None

    if image_mode == "Upload Image":

        uploaded_file = st.file_uploader(
            "Upload Scene Image",
            type=[
                "png",
                "jpg",
                "jpeg",
                "webp",
            ],
            key=f"upload_{i}",
        )

    scenes.append(
        {
            "prompt": prompt,
            "narration": narration,
            "effect": effect,
            "uploaded_file": uploaded_file,
        }
    )


# ============================================================
# GENERATE BUTTON
# ============================================================

generate = st.button(
    "🚀 Generate Video",
    type="primary",
    use_container_width=True,
)


# ============================================================
# GENERATION
# ============================================================

if generate:

    # ========================================================
    # VALIDATION
    # ========================================================

    for index, scene in enumerate(scenes):

        number = index + 1

        narration = scene["narration"].strip()
        prompt = scene["prompt"].strip()

        if not narration:

            st.error(
                f"Scene {number}: Hinglish narration is empty."
            )

            st.stop()

        if image_mode != "Upload Image" and not prompt:

            st.error(
                f"Scene {number}: Visual prompt is empty."
            )

            st.stop()

        if image_mode == "Upload Image":

            if scene["uploaded_file"] is None:

                st.error(
                    f"Scene {number}: Please upload an image."
                )

                st.stop()

    # ========================================================
    # CLEAN OLD OUTPUT
    # ========================================================

    try:

        clean_output()
        create_directories()

    except Exception as error:

        st.error(
            "Could not prepare output directories:\n"
            + str(error)
        )

        st.stop()

    # ========================================================
    # ARRAYS
    # ========================================================

    scene_videos = []
    audio_files = []
    subtitle_files = []
    scene_durations = []

    progress = st.progress(0)

    status = st.empty()

    # ========================================================
    # PROCESS EACH SCENE
    # ========================================================

    for index, scene in enumerate(scenes):

        number = index + 1

        status.write(
            f"### Processing Scene {number}/{len(scenes)}"
        )

        # ====================================================
        # PATHS
        # ====================================================

        image_path = os.path.join(
            IMAGES_DIR,
            f"scene_{number:02d}.png",
        )

        audio_path = os.path.join(
            AUDIO_DIR,
            f"scene_{number:02d}.mp3",
        )

        scene_video = os.path.join(
            SCENES_DIR,
            f"scene_{number:02d}.mp4",
        )

        subtitle_path = os.path.join(
            CAPTIONS_DIR,
            f"scene_{number:02d}.srt",
        )

        # ====================================================
        # IMAGE
        # ====================================================

        status.write(
            f"### Scene {number}: Creating image..."
        )

        try:

            generate_scene_image(
                mode=image_mode,
                prompt=scene["prompt"],
                output_path=image_path,
                width=width,
                height=height,
                uploaded_file=scene["uploaded_file"],
                local_endpoint=local_endpoint,
            )

        except Exception as error:

            st.error(
                f"Scene {number} image generation failed:\n"
                + str(error)
            )

            st.stop()

        st.image(
            image_path,
            caption=f"Scene {number}",
            width="stretch",
        )

        # ====================================================
        # TTS
        # ====================================================

        status.write(
            f"### Scene {number}: Creating Hinglish voice..."
        )

        try:

            generate_hinglish_voice(
                text=scene["narration"],
                output_path=audio_path,
                voice=selected_voice,
                rate=speech_rate,
            )

        except Exception as error:

            st.error(
                f"Scene {number} Hinglish TTS failed:\n"
                + str(error)
            )

            st.stop()

        audio_files.append(audio_path)

        # ====================================================
        # AUDIO DURATION
        # ====================================================

        try:

            duration = get_media_duration(
                audio_path
            )

        except Exception as error:

            st.error(
                f"Scene {number} audio duration detection failed:\n"
                + str(error)
            )

            st.stop()

        # Keep the video slightly longer than audio.
        duration = max(
            1.0,
            duration + 0.15,
        )

        scene_durations.append(duration)

        # ====================================================
        # MOTION VIDEO
        # ====================================================

        status.write(
            f"### Scene {number}: Creating motion..."
        )

        try:

            create_motion_scene(
                image_path=image_path,
                output_path=scene_video,
                duration=duration,
                width=width,
                height=height,
                effect=scene["effect"],
            )

        except Exception as error:

            st.error(
                f"Scene {number} motion generation failed:\n"
                + str(error)
            )

            st.stop()

        scene_videos.append(scene_video)

        # ====================================================
        # CAPTIONS
        # ====================================================

        if caption_enabled:

            status.write(
                f"### Scene {number}: Creating captions..."
            )

            try:

                create_scene_srt(
                    narration=scene["narration"],
                    duration=duration,
                    output_path=subtitle_path,
                )

            except Exception as error:

                st.error(
                    f"Scene {number} caption generation failed:\n"
                    + str(error)
                )

                st.stop()

            subtitle_files.append(
                subtitle_path
            )

        progress.progress(
            (index + 1) / len(scenes)
        )

    # ========================================================
    # COMBINE VIDEO
    # ========================================================

    status.write(
        "### 🎬 Combining video scenes..."
    )

    combined_video = os.path.join(
        FINAL_DIR,
        "combined_video.mp4",
    )

    try:

        concatenate_videos(
            video_files=scene_videos,
            output_path=combined_video,
        )

    except Exception as error:

        st.error(
            "Video combination failed:\n"
            + str(error)
        )

        st.stop()

    # ========================================================
    # COMBINE AUDIO
    # ========================================================

    status.write(
        "### 🎙️ Combining narration..."
    )

    combined_audio = os.path.join(
        FINAL_DIR,
        "combined_audio.mp3",
    )

    try:

        concatenate_audio(
            audio_files=audio_files,
            output_path=combined_audio,
        )

    except Exception as error:

        st.error(
            "Audio combination failed:\n"
            + str(error)
        )

        st.stop()

    # ========================================================
    # MUX AUDIO + VIDEO
    # ========================================================

    status.write(
        "### 🔊 Adding Hinglish narration..."
    )

    video_with_audio = os.path.join(
        FINAL_DIR,
        "video_with_audio.mp4",
    )

    try:

        mux_audio(
            video_path=combined_video,
            audio_path=combined_audio,
            output_path=video_with_audio,
        )

    except Exception as error:

        st.error(
            "Audio/video rendering failed:\n"
            + str(error)
        )

        st.stop()

    # ========================================================
    # CAPTIONS
    # ========================================================

    final_video = video_with_audio

    if caption_enabled:

        status.write(
            "### 💬 Combining captions..."
        )

        combined_srt = os.path.join(
            FINAL_DIR,
            "captions.srt",
        )

        try:

            combine_srt_files(
                subtitle_files=subtitle_files,
                scene_durations=scene_durations,
                output_path=combined_srt,
            )

        except Exception as error:

            st.error(
                "Caption combination failed:\n"
                + str(error)
            )

            st.stop()

        status.write(
            "### 🎨 Burning captions into video..."
        )

        captioned_video = os.path.join(
            FINAL_DIR,
            "final_video.mp4",
        )

        try:

            burn_captions(
                video_path=video_with_audio,
                subtitle_path=combined_srt,
                output_path=captioned_video,
            )

        except Exception as error:

            st.error(
                "Caption rendering failed:\n"
                + str(error)
            )

            st.stop()

        final_video = captioned_video

    # ========================================================
    # COMPLETE
    # ========================================================

    progress.progress(1.0)

    status.success(
        "🎉 Video generation complete!"
    )

    st.balloons()

    st.subheader(
        "🎬 Final Video"
    )

    try:

        with open(
            final_video,
            "rb",
        ) as file:

            video_bytes = file.read()

    except Exception as error:

        st.error(
            "Could not read final video:\n"
            + str(error)
        )

        st.stop()

    st.video(
        video_bytes
    )

    st.download_button(
        label="⬇️ Download Final MP4",
        data=video_bytes,
        file_name="hinglish_ai_video.mp4",
        mime="video/mp4",
        use_container_width=True,
    )

    st.success(
        "Your Hinglish video is ready."
)
