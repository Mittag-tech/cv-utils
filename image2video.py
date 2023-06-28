import argparse
from pathlib import Path

import cv2

def main(img_dir:Path, output_dir:Path, video_name:str, fps:int):
    """Create video from images.
    
    input:
        img_dir: Path of the directory where images are stored.
        output_dir: Path of the directory where the result would be stored.
        video_name: File name of result.
        fps: Frame per seconds of result.
    output:
        None
    """
    sort_img_list = sorted(img_dir.iterdir())

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = str(output_dir / video_name)
    
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    ref_img = cv2.imread(str(sort_img_list[0]))
    video_h, video_w, _ = ref_img.shape
    video_writer = cv2.VideoWriter(output_path, fourcc, fps, (video_w, video_h))
    
    for img_path in sort_img_list:
        img = cv2.imread(str(img_path))
        video_writer.write(img)
    video_writer.release()


def _parser():
    """Set argments for image2video.py.
    
    --img_dir: Path of the directory where images are stored.
    --output_dir: Path of the directory where the result would be stored.
    --video_name: File name of result.
    --fps: Frame per seconds of result.
    """
    args = argparse.ArgumentParser(description="Create Video from Images.")
    args.add_argument("--img_dir", help="set directory path of images.", type=str)
    args.add_argument("--output_dir", help="set directory path of output video.", default="result/", type=str)
    args.add_argument("--video_name", help="set video name.", default="result.mp4", type=str)
    args.add_argument("--fps", help="set video fps rate.", default=30, type=int)
    return args.parse_args()

if __name__ == "__main__":
    # Configuration arguments
    args = _parser()
    img_dir = Path(args.img_dir)
    output_dir = Path(args.output_dir)
    video_name = args.video_name
    fps = args.fps

    # Run main function
    main(img_dir, output_dir, video_name, fps)
