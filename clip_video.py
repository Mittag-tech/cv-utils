import argparse
from pathlib import Path

import cv2

def main(args):
    video_path = args.video
    output_path = Path(args.output)
    output_path.parent.mkdir(exist_ok=True, parents=True)
    start = args.start
    end = args.end

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    cap.set(cv2.CAP_PROP_POS_FRAMES, start * fps)
    frame_count = start * fps
    while cap.isOpened():    
        if end * fps > count:
            print(f"set end time in {int(count / fps)}")
            break
        if frame_count < end * fps:
            ret, frame = cap.read()
            if ret:
                video.write(frame)
            else:
                break
        else:
            break
        frame_count += 1
    video.release()
    pass


def _parser():
    parser = argparse.ArgumentParser(description="clip video any time, any range.")
    parser.add_argument("--video", help="set video path")
    parser.add_argument("--output", help="set output path")
    parser.add_argument("--start", help="set start time", type=int)
    parser.add_argument("--end", help="set end time", type=int)
    return parser.parse_args()


if __name__ == "__main__":
    args = _parser()
    main(args)