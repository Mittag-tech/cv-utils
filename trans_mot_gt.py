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


def fix_gt(img, gt, deg):
    bbox_pos = calc_rotation(img.size, gt[2:6], deg)
    for i, pos in enumerate(bbox_pos):
        gt[i + 2] = str(pos)
    return ",".join(gt)

def calc_rotation(orig_size, row, roll, gyro_center=0.5):
    # row = [x, y, w, h]
    shift_center_x = orig_size[0] * gyro_center
    shift_center_y = orig_size[1] * gyro_center
    quadrant_pos_x = row[0] - shift_center_x
    quadrant_pos_y = row[1] - shift_center_y
    roll_theta = math.radians(roll)
    top_left, top_right, bottom_left, bottom_right = calc_tlbr(quadrant_pos_x, quadrant_pos_y, row[2], row[3])
    orig_bbox_data = [(quadrant_pos_x, quadrant_pos_y), top_left, top_right, bottom_left, bottom_right]
    roll_bbox_data = []
    for pos in orig_bbox_data:
        radius = math.sqrt(pos[0] ** 2 + pos[1] ** 2)
        base_theta = math.atan2(pos[1], pos[0])
        theta = base_theta + roll_theta
        result_x = radius * math.cos(theta) + shift_center_x
        result_y = radius * math.sin(theta) + shift_center_y
        roll_bbox_data.append((result_x, result_y))
    roll_center_x = roll_bbox_data[0][0]
    roll_center_y = roll_bbox_data[0][1]
    roll_width = abs(roll_bbox_data[1][0] - roll_bbox_data[4][0])
    roll_height = abs(roll_bbox_data[2][1] - roll_bbox_data[3][1])
    return roll_center_x, roll_center_y, roll_width, roll_height


def calc_tlbr(x, y, w, h):
    left = x - w / 2
    right = x + w / 2
    top = y - h / 2
    bottom = y + h / 2
    top_left = (left, top)
    top_right = (right, top)
    bottom_left = (left, bottom)
    bottom_right = (right, bottom)
    return top_left, top_right, bottom_left, bottom_right


if __name__ == "__main__":
    deg_list = [90]
    current_dir = Path.cwd()
    dataset_path = current_dir / "dataset"
    for deg in deg_list:
        main(dataset_path, deg)