#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import math
from pathlib import Path
import yaml

import cv2

IMAGE_EXT = [".jpg", ".jpeg", ".png", ".PNG"]

def _write_info(info_dict, output_dir:Path, yaml_name="video-info.yaml"):
    """Write video information to yaml file.
    
    input:
        info_dict: Information database of video, fps and size, frame count, etc.
        output_dir: Path of the directory where the result would be stored.
        yaml_name: Yaml file name, default='video-info.yaml'.
    """
    yaml_path = str(output_dir / yaml_name)
    with open(yaml_path, "w") as yf:
        yaml.dump(info_dict, yf, default_flow_style=False)


def main(video_path:Path, output_dir:Path, ext:str):
    """Create images from video.
    
    input:
        video_path: Path of target video.
        output_dir: Path of the directory where the result would be stored.
    """
    cap = cv2.VideoCapture(str(video_path))
    frame_count = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if ret:
            img_name = output_dir / f'images/{frame_count:06}{ext}'
            cv2.imwrite(str(img_name), frame)
            print('\rsuccess! ==> {}'.format(str(img_name)), end='')
            frame_count += 1
        else:
            break
    info_dict = {"fps": math.ceil(cap.get(cv2.CAP_PROP_FPS)),
                 "max_frame": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                 "video_width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                 "video_height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                 "fourcc": int(cap.get(cv2.CAP_PROP_FOURCC)).to_bytes(4, "little").decode("utf-8")}
    _write_info(info_dict, output_dir)


def _parser():
    """Set argments for video2image.py.
    
    --video_path: Path where video is stored.
    --output_dir: Path of the directory where the result would be stored.
    """
    args = argparse.ArgumentParser(description="show annotation bbox on image.")
    args.add_argument("--video_path", help="set video path", type=str)
    args.add_argument("--output_dir", help="set output dir path.", default="result/", type=str)
    args.add_argument("--ext", "-e", help=f"set any extinction, {IMAGE_EXT}", default=".PNG")
    return args.parse_args()


if __name__ == '__main__':
    # Configuration arguments
    args = _parser()
    video_path = Path(args.video_path)
    output_dir = Path(args.output_dir)
    ext = args.ext
    image_dir = output_dir / "images"
    image_dir.mkdir(exist_ok=True, parents=True)

    # Run main function
    main(video_path, output_dir, ext)
    print("\nsuccess all.")