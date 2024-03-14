import os

import cv2
import numpy as np
from pathlib import Path
from typing import Optional


def imread(path_file, flag=cv2.IMREAD_COLOR, dtype=np.uint8):
    """
    Read Korean file path
    Args:
        path_file: Image file path
        flag: Color mode
        dtype: Data type

    Returns:
        Image data of numpy array format
    """
    stream = open(path_file, "rb")
    stream_bytes = bytearray(stream.read())
    numpyarray = np.asanyarray(stream_bytes, dtype=dtype)
    bgr_image = cv2.imdecode(numpyarray, flag)
    return bgr_image


def imwrite(path_file, img, flag=None):
    """
    Write Korean file path
    Args:
        path_file: Saving image file path
        img: Saving image data
        flag: Encoding mode

    Returns:
        Bool
    """
    ext = os.path.splitext(path_file)[1]
    result, n = cv2.imencode(ext, img, flag)

    if result:
        with open(path_file, mode="w+b") as f:
            n.tofile(f)
            return True
    else:
        return False


def read_file_list(path: Path or str, file_formats: list) -> list:  # type: ignore
    """
    Args:
        path: Folder path
        file_formats: File format list for list-up

    Returns: Special format file list
    """
    if not path:
        return []
    for file_format in file_formats:
        file_list = glob.glob(str(path) + f"/*.{file_format}")
        if file_list:
            break
        else:
            file_list = glob.glob(str(path) + f"/*/*.{file_format}")
        if file_list:
            break
    return file_list


def split_image(image_path=Path, size: int = 1024, saving_dir=Path, image_color="gray"):
    """Image extension is limited by 'jpg' and 'png'
    Args:
        image_path: Input image directory
        size: Image size for split, (size, size)
        saving_dir: Saving path
        image_color: "gray" or "color", default: gray
    Returns:
        Split image list
    """
    if not image_path.is_file():
        print(f"Error!!: {image_path} -> There is no file.")
        return

    if image_color == "gray":
        flag = 0
    elif image_color == "color":
        flag = 1
    else:
        flag = 0

    image_object = imread(image_path, flag)
    image_size = image_object.shape[:2]

    image_max_x, image_max_y = image_size[1] // size, image_size[0] // size
    if image_max_x == 0 or image_max_y == 0:
        print(f"Error!!: {image_size} is smaller than input image size.")
        return

    if not image_size[1] % size:
        image_max_x -= 1
    if not image_size[0] % size:
        image_max_y -= 1

    print(f"Spliting {image_path.name}...")
    saving_path = saving_dir.joinpath(image_path.name)
    for y in range(0, image_max_y + 1):
        for x in range(0, image_max_x + 1):
            if x == image_max_x and y < image_max_y:
                split_img = image_object[y * size : (y + 1) * size, image_size[1] - size : image_size[1]]
            elif x < image_max_x and y == image_max_y:
                split_img = image_object[image_size[0] - size : image_size[0], x * size : (x + 1) * size]
            elif x == image_max_x and y == image_max_y:
                split_img = image_object[image_size[0] - size : image_size[0], image_size[1] - size : image_size[1]]
            else:
                split_img = image_object[y * size : (y + 1) * size, x * size : (x + 1) * size]
            if not split_img.size:
                continue

            imwrite(str(saving_path).replace(".jpg", f"_{y}_{x}.jpg"), split_img)
