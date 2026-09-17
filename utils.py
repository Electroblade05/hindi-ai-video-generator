import os
import shutil

from config import (
    OUTPUT_DIR,
    IMAGES_DIR,
    AUDIO_DIR,
    SCENES_DIR,
    CAPTIONS_DIR,
    FINAL_DIR,
)


# ============================================================
# CREATE DIRECTORIES
# ============================================================

def create_directories():

    directories = [
        OUTPUT_DIR,
        IMAGES_DIR,
        AUDIO_DIR,
        SCENES_DIR,
        CAPTIONS_DIR,
        FINAL_DIR,
    ]

    for directory in directories:

        os.makedirs(
            directory,
            exist_ok=True
        )


# ============================================================
# CLEAN OUTPUT
# ============================================================

def clean_output():

    if os.path.exists(
        OUTPUT_DIR
    ):

        for item in os.listdir(
            OUTPUT_DIR
        ):

            path = os.path.join(
                OUTPUT_DIR,
                item,
            )

            try:

                if os.path.isdir(
                    path
                ):

                    shutil.rmtree(
                        path
                    )

                else:

                    os.remove(
                        path
                    )

            except Exception as error:

                raise RuntimeError(
                    "Could not clean output:\n"
                    + str(error)
                )

    create_directories()
