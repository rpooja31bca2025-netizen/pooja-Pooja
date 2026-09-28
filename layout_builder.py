def build_comic_layout(
    outline,
    story,
    image_paths
):
    """
    Combine outline, story and image
    information into one layout.
    """

    layout = []

    for index in range(5):

        outline_panel = outline[index]
        story_panel = story[index]

        layout.append(
            {
                "panel_number": index + 1,

                "title": (
                    story_panel.get(
                        "title"
                    )
                    or outline_panel.get(
                        "title"
                    )
                ),

                "scene_description": (
                    story_panel.get(
                        "scene_description"
                    )
                    or outline_panel.get(
                        "scene_description"
                    )
                ),

                "image_prompt": outline_panel.get(
                    "image_prompt",
                    ""
                ),

                "image": image_paths[index],

                "caption": story_panel.get(
                    "caption",
                    ""
                ),

                "narration": story_panel.get(
                    "narration",
                    ""
                ),

                "dialogue": story_panel.get(
                    "dialogue",
                    ""
                ),
            }
        )

    return layout