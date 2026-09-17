import os
import shutil
import uuid

import streamlit as st

from ai_script import (
    generate_script,
    generate_scene_plan
)

from scene_generator import (
    calculate_scene_count,
    prepare_scenes
)

from video_generator import (
    generate_video_clip
)

from tts_engine import (
    generate_hindi_voice
)

from caption_engine import (
    create_srt
)

from music_engine import (
    generate_background_music
)

from video_engine import (
    combine_clips,
    render_final_video,
    get_audio_duration
)


st.set_page_config(
    page_title="Hindi AI Video Generator",
    page_icon="🎬",
    layout="centered"
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.title(
    "🎬 Hindi AI Video Generator"
)

st.write(
    "Create narrated Hindi AI videos "
    "from a simple topic."
)


# --------------------------------------------------
# INPUTS
# --------------------------------------------------

topic = st.text_area(
    "🎯 Video Topic",
    value="What if Earth had two moons?",
    height=100
)


duration = st.select_slider(
    "⏱️ Video Duration",
    options=[
        0.5,
        1.0,
        1.5,
        2.0,
        2.5,
        3.0
    ],
    value=2.0,
    format_func=lambda x: f"{x} minutes"
)


style = st.selectbox(
    "🎨 Video Style",
    [
        "Documentary",
        "Cinematic",
        "Educational",
        "Science",
        "Mystery",
        "Space",
        "History",
        "Nature"
    ]
)


aspect_ratio = st.selectbox(
    "📱 Aspect Ratio",
    [
        "9:16",
        "16:9"
    ]
)


resolution = st.selectbox(
    "📺 Resolution",
    [
        "720p",
        "1080p"
    ]
)


voice = st.selectbox(
    "🎙️ Hindi Voice",
    [
        "alloy",
        "echo",
        "fable",
        "onyx",
        "nova",
        "shimmer"
    ]
)


generate = st.button(
    "🚀 GENERATE VIDEO",
    use_container_width=True
)


# --------------------------------------------------
# GENERATION
# --------------------------------------------------

if generate:

    if not topic.strip():

        st.error(
            "Please enter a video topic."
        )

        st.stop()

    job_id = uuid.uuid4().hex[:10]

    output_dir = os.path.join(
        "outputs",
        job_id
    )

    os.makedirs(
        output_dir,
        exist_ok=True
    )

    try:

        # ------------------------------------------
        # STEP 1 — SCRIPT
        # ------------------------------------------

        st.subheader(
            "🧠 Step 1 — Creating Hindi script"
        )

        with st.spinner(
            "Writing Hindi narration..."
        ):

            script = generate_script(
                topic,
                duration,
                style
            )

        st.success(
            "Hindi script created."
        )

        with st.expander(
            "View generated script"
        ):

            st.write(script)


        # ------------------------------------------
        # STEP 2 — SCENES
        # ------------------------------------------

        st.subheader(
            "🎬 Step 2 — Planning scenes"
        )

        scene_count = calculate_scene_count(
            duration
        )

        with st.spinner(
            f"Creating {scene_count} scenes..."
        ):

            scenes = generate_scene_plan(
                topic,
                script,
                style,
                scene_count
            )

            scenes = prepare_scenes(
                scenes
            )

        st.success(
            f"{len(scenes)} scenes created."
        )


        # ------------------------------------------
        # STEP 3 — TTS
        # ------------------------------------------

        st.subheader(
            "🎙️ Step 3 — Generating Hindi narration"
        )

        narration_path = os.path.join(
            output_dir,
            "narration.mp3"
        )

        with st.spinner(
            "Generating Hindi voice..."
        ):

            generate_hindi_voice(
                script,
                narration_path,
                voice
            )

        narration_duration = (
            get_audio_duration(
                narration_path
            )
        )

        st.success(
            f"Narration ready — "
            f"{narration_duration:.1f} seconds"
        )


        # ------------------------------------------
        # STEP 4 — VIDEO CLIPS
        # ------------------------------------------

        st.subheader(
            "🎥 Step 4 — Generating AI video scenes"
        )

        clip_paths = []

        progress = st.progress(0)

        status = st.empty()

        total = len(scenes)

        for index, scene in enumerate(
            scenes
        ):

            scene_number = (
                scene["scene_number"]
            )

            status.write(
                f"Generating scene "
                f"{scene_number}/{total}..."
            )

            clip_path = os.path.join(
                output_dir,
                f"scene_{scene_number:02d}.mp4"
            )

            prompt = (
                scene["visual_prompt"]
                + "\n\nCamera: "
                + scene["camera"]
            )

            generate_video_clip(
                prompt=prompt,
                output_path=clip_path,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                progress_callback=lambda message:
                    status.write(
                        f"Scene "
                        f"{scene_number}/{total}: "
                        f"{message}"
                    )
            )

            clip_paths.append(
                clip_path
            )

            progress.progress(
                (index + 1) / total
            )


        st.success(
            "All AI scenes generated."
        )


        # ------------------------------------------
        # STEP 5 — JOIN VIDEO
        # ------------------------------------------

        st.subheader(
            "✂️ Step 5 — Joining scenes"
        )

        raw_video = os.path.join(
            output_dir,
            "raw_video.mp4"
        )

        with st.spinner(
            "Combining video scenes..."
        ):

            combine_clips(
                clip_paths,
                raw_video,
                output_dir
            )


        # ------------------------------------------
        # STEP 6 — CAPTIONS
        # ------------------------------------------

        st.subheader(
            "📝 Step 6 — Creating captions"
        )

        subtitles_path = os.path.join(
            output_dir,
            "captions.srt"
        )

        create_srt(
            script,
            narration_duration,
            subtitles_path
        )


        # ------------------------------------------
        # STEP 7 — MUSIC
        # ------------------------------------------

        st.subheader(
            "🎵 Step 7 — Creating background music"
        )

        music_path = os.path.join(
            output_dir,
            "music.wav"
        )

        generate_background_music(
            music_path,
            narration_duration
        )


        # ------------------------------------------
        # STEP 8 — FINAL RENDER
        # ------------------------------------------

        st.subheader(
            "🎞️ Step 8 — Rendering final video"
        )

        final_video = os.path.join(
            output_dir,
            "final_video.mp4"
        )

        with st.spinner(
            "Rendering final MP4..."
        ):

            render_final_video(
                raw_video,
                narration_path,
                music_path,
                subtitles_path,
                final_video
            )


        # ------------------------------------------
        # COMPLETE
        # ------------------------------------------

        st.success(
            "🎉 Your video is ready!"
        )

        st.video(
            final_video
        )

        with open(
            final_video,
            "rb"
        ) as file:

            st.download_button(
                label="⬇️ Download MP4",
                data=file,
                file_name=(
                    "hindi_ai_video.mp4"
                ),
                mime="video/mp4",
                use_container_width=True
            )


        with st.expander(
            "📋 Generated scene information"
        ):

            for scene in scenes:

                st.markdown(
                    f"### Scene {scene['scene_number']}"
                )

                st.write(
                    scene["visual_prompt"]
                )


    except Exception as error:

        st.error(
            "❌ Video generation failed."
        )

        st.exception(
            error
        )

    finally:

        # Do not delete output immediately.
        # Streamlit needs the files for playback/download.
        pass
