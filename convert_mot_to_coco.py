import argparse
import numpy as np
import json
from pathlib import Path

import cv2


# Use the same script for MOT16
EXTS = [".jpg", ".jpeg", ".png", ".PNG"]

def json_encode(obj):
    if isinstance(obj, Path):
        return obj.as_posix()
    
def set_category(label_txt:Path):
    label_list = label_txt.read_text().split("\n")
    category_list = []
    for i, label in enumerate(label_list):
        category_dict = {}
        category_dict["id"] = i + 1
        category_dict["name"] = label
        category_list.append(category_dict)
    return category_list

def arg_parser():
    parser = argparse.ArgumentParser(description="convert mot format to coco format.")
    parser.add_argument("--data", help="set directory path of dataset.", default="datasets/")
    parser.add_argument("--output", help="set directory name of output.", default="annotations")
    parser.add_argument("--splits", help="set split direstory.", default=['train', 'val', 'test'], nargs="*")
    parser.add_argument("--label_txt", "-l", help="set labels.txt path")
    return parser.parse_args()


if __name__ == '__main__':
    args = arg_parser()
    data = Path(args.data)
    output = data / args.output
    splits = args.splits
    category = set_category(Path(args.label_txt))
    print(
        f"""set argments
        DATA_PATH: {str(data)}
        OUT_OATH : {str(output)}
        SPLITS   : {splits}
        CATEGORY : {category}
        """
    )

    output.mkdir(exist_ok=True)

    for split in splits:
        data_path = data / split
        if not data_path.exists():
            print(f"{data_path} is not exists.")
            continue
        out_path = output / '{}.json'.format(split)
        out = {'images': [], 'annotations': [], 'videos': [],
               'categories': category}
        seqs = [seq for seq in data_path.iterdir() if seq.is_dir()]
        image_cnt = 0
        ann_cnt = 0
        video_cnt = 0
        for seq in sorted(seqs):
            video_cnt += 1  # video sequence number.
            out['videos'].append({'id': video_cnt, 'file_name': seq})
            img_path = seq / 'img1'
            ann_path = seq / 'gt/gt.txt'
            images = [img for img in sorted(img_path.iterdir()) if img.suffix in EXTS]
            num_images = len(images)  # half and half

            for i in range(num_images):
                img = cv2.imread(str(images[i]))
                height, width = img.shape[:2]
                image_info = {'file_name': '{}'.format(str(images[i]).strip(str(data_path))),  # image name.
                              'id': image_cnt + i + 1,  # image number in the entire training set.
                              'frame_id': i + 1,  # image number in the video sequence, starting from 1.
                              'prev_image_id': image_cnt + i if i > 0 else -1,  # image number in the entire training set.
                              'next_image_id': image_cnt + i + 2 if i < num_images - 1 else -1,
                              'video_id': video_cnt,
                              'height': height,
                              'width': width}
                out['images'].append(image_info)
            print('{}: {} images'.format(seq.stem, num_images))

            if split != 'test':
                anns = np.loadtxt(str(ann_path), dtype=np.float32, delimiter=',')
                for i in range(anns.shape[0]):
                    frame_id = int(anns[i][0])
                    track_id = int(anns[i][1])
                    cat_id = int(anns[i][7])
                    ann_cnt += 1
                    category_id = int(anns[i][7])
                    ann = {'id': ann_cnt,
                           'category_id': category_id,
                           'image_id': image_cnt + frame_id,
                           'track_id': track_id,
                           'bbox': anns[i][2:6].tolist(),
                           'conf': float(anns[i][6]),
                           'iscrowd': 0,
                           'area': float(anns[i][4] * anns[i][5])}
                    out['annotations'].append(ann)
                print('{}: {} ann images'.format(seq.stem, int(anns[:, 0].max())))

            image_cnt += num_images
        print('loaded {} for {} images and {} samples'.format(split, len(out['images']), len(out['annotations'])))
        json.dump(out, open(str(out_path), 'w'), default=json_encode)