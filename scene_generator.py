def calculate_scene_count(duration_minutes):
    """
    Veo generates short clips, so approximately one scene
    is created for every 8 seconds.
    """

    seconds = duration_minutes * 60

    return max(3, round(seconds / 8))


def prepare_scenes(scenes):
    prepared = []

    for index, scene in enumerate(scenes, start=1):

        prepared.append({
            "scene_number": index,
            "narration": scene.get("narration", ""),
            "visual_prompt": scene.get("visual_prompt", ""),
            "camera": scene.get("camera", ""),
            "duration": int(scene.get("duration", 8))
        })

    return prepared
