# !/usr/bin/env python

import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    args = parser()
    image_path = Path(args.image_path)
    text_path = Path(args.text_path)
    output_path = Path(args.output_path)

    base_image = Image.open(image_path)
    draw_image = ImageDraw.Draw(base_image)
    data_list = read_gt(text_path)
    for data in data_list:
        if int(data[0]) != int(image_path.stem):
            continue
        draw_image.rectangle(
            ((data[2], data[3]), (data[2] + data[4], data[3] + data[5])), outline=(255, 255, 255))
    result_image = output_path / image_path.name
    base_image.save(result_image)


def read_gt(text_path:Path):
    # gt.txt
    # frame_id, track_id, x, y, w, h, "not ignored", class_id, visibility, <skipped>
    gt_list = []
    for line in text_path.read_text().split("\n"):
        if not line:
            break
        line_list = line.split(",")
        for i in range(len(line_list)):
            if 1 < i < 6:
                line_list[i] = float(line_list[i])
        gt_list.append(line_list)
    return gt_list


def parser():
    _parser = argparse.ArgumentParser(description="show annotation bbox on image.")
    _parser.add_argument("--image_path", help="set base image path", default="data/exam.PNG", type=str)
    _parser.add_argument("--text_path", help="set text file path.", default="data/exam.txt", type=str)
    _parser.add_argument("--output_path", help="set output dir path.", default="output/", type=str)
    return _parser.parse_args()


if __name__ == "__main__":
    main()
