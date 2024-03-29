import matplotlib.pyplot as plot
from datetime import datetime
from io import BytesIO
from PIL import Image
import math
import os

FONT_POINTS = 10


def export_as_gif(strings: list[str], updates_per_s: int = 1) -> bool:
    """Returns True if successful, False otherwise"""

    if not strings:
        return False

    # File name
    DIR_NAME = "gifs"
    _ensure_gif_dir_exists(DIR_NAME)
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"GAMEofLIFE-{now}.gif"

    # Generate frames
    img_bytes_list = []
    x, y = _get_inches_xy(strings[0])

    for s in strings:
        img_bytes_list.append(_convert_to_img_bytes(s, x, y))

    frames = [Image.open(img) for img in img_bytes_list]
    final_frames = frames[1:]

    # BOOMERANG EFFECT
    if len(frames) > 1:
        final_frames = frames[1:] + frames[-2::-1]

    # NOTE: Known issues with Pillow ignoring duration param for GIF...
    # For now use a constant
    # See:
    #   - https://github.com/python-pillow/Pillow/issues/3073
    #   - https://stackoverflow.com/a/64530622
    FRAME_DURATION = 33
    frames[0].save(
        f"{DIR_NAME}/{file_name}",
        save_all=True,
        append_images=final_frames,
        duration=FRAME_DURATION,
        loop=0,
    )

    return True


def _ensure_gif_dir_exists(name: str):
    """Ensures a directory exists in the directory the app is executed"""
    if not os.path.exists(name):
        os.makedirs(name)


def _get_inches_xy(string: str) -> tuple[float, float]:
    # COMPUTE SIZE DYNAMICALLY
    # Great summary for Matplotlib's size ratios (dots vs inches): https://stackoverflow.com/a/47639545
    lines = string.split("\n")
    string_width = math.floor((len(lines[0]) / 2))  # divide by 2 as cells are 2 chars wide '██'
    string_height = len(lines)

    font_points_x = FONT_POINTS * string_width
    font_points_y = FONT_POINTS * string_height

    # Divding values were determined from testing exporting gifs...
    inches_x = font_points_x / 46.4
    inches_y = font_points_y / 45

    # Avoid errors ensuring values are within bounds for Pillow and Matplotlib
    inches_x = 0.1 if inches_x == 0 else inches_x
    inches_y = 0.1 if inches_y == 0 else inches_y

    return (inches_x, inches_y)


def _convert_to_img_bytes(string: str, width: float, height: float):
    img_bytes = BytesIO()

    plot.figure(figsize=(width, height), facecolor="silver")
    plot.axis("off")  # toggle "on" (comment out) for debugging
    plot.text(0, 0, string, fontfamily="monospace", fontsize=FONT_POINTS)
    plot.savefig(
        img_bytes,
        dpi=100,
        format="png",
        # NOTE: Issue when removing padding, images are slightly different sizes which causes Pillow to throw when merging into GIF
        # pad_inches=0,
        # bbox_inches="tight",
    )
    plot.close()

    return img_bytes
