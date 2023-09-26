#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from pathlib import Path
import shutil

from PIL import Image


def main(dataset_path:Path, deg:float):
    split_list = ["test", "train", "val"]
    for split in split_list:
        split_dir = dataset_path / split
        if not split_dir.exists():
            continue
        for data_dir in sorted(split_dir.iterdir()):
            if not data_dir.is_dir():
                continue
            gt_dir = data_dir / "gt"
            gt_file = gt_dir / "gt.txt"
            gt_list = read_gt(gt_file)
            img_dir = data_dir / "img1"
            save_gt_list = []
            save_path = split_dir / f"{data_dir.stem}_{deg}"
            save_img_dir = save_path / "img1"
            save_txt_dir = save_path / "gt"
            save_img_dir.mkdir(exist_ok=True, parents=True)
            save_txt_dir.mkdir(exist_ok=True, parents=True)
            for i, img_path in enumerate(sorted(img_dir.iterdir())):
                img = Image.open(str(img_path))
                save_img_path = save_img_dir / f"{img_path.stem}{img_path.suffix}"
                rotate_image(img, deg, save_img_path)
                gt_fixed = fix_gt(img, gt_list[i], deg)
                save_gt_list.append(gt_fixed)
            save_txt_path = save_txt_dir / "gt.txt"
            context = "\n".join(save_gt_list)
            save_txt_path.write_text(context)
            label_file = gt_dir / "labels.txt"
            to_label_file = save_txt_dir / "labels.txt"
            shutil.copy(label_file, to_label_file)


def rotate_image(img, deg, save_img_path):
    img = img.rotate(deg, resample=Image.Resampling.BICUBIC, expand=True)
    img.save(str(save_img_path))


def read_gt(text_path:Path):
    # gt.txt
    # frame_id, track_id, top_x, top_y, w, h, "not ignored", class_id, visibility, <skipped>
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


def fix_gt(img, gt, deg):
    top_x, top_y, w, h = gt[2:6]
    if deg == 90:
        gt[2] = top_y
        gt[3] = img.width - (top_x + w)
        gt[4] = h
        gt[5] = w
    elif deg == 180:
        gt[2] = img.width - (top_x + w)
        gt[3] = img.height - (top_y + h)
    elif deg == 270 or deg == -90:
        gt[2] = img.height - (top_y + h)
        gt[3] = top_x
        gt[4] = h
        gt[5] = w
    gt = [str(x) for x in gt]
    return ",".join(gt)


if __name__ == "__main__":
    deg_list = [90, 180, 270]
    current_dir = Path.cwd()
    dataset_path = current_dir / "dataset"
    for deg in deg_list:
        main(dataset_path, deg)