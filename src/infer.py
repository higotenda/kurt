from operator import itemgetter
import torch
from mmaction.apis import init_recognizer, inference_recognizer
import download
import os
from typing import List

config_file = "i3d_imagenet-pretrained-r50_8xb8-32x2x1-100e_kinetics400-rgb.py"
checkpoint_file = (
    "i3d_imagenet-pretrained-r50_8xb8-32x2x1-100e_kinetics400-rgb_20220812-e213c223.pth"
)
label_file = "label_map_k400.txt"
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = init_recognizer(config_file, checkpoint_file, device=device)
labels = open(label_file).readlines()
labels = [x.strip() for x in labels]

def process_video(url: str) -> List[str]:
        chunk_dir = "output"
        download.download_url(url)

        labeled_video = []
        for video_file in os.listdir(chunk_dir):
            if os.path.isfile(os.path.join(chunk_dir, video_file)):
                pred_result = inference_recognizer(model, f"{chunk_dir}/{video_file}")

                pred_scores = pred_result.pred_score.tolist()
                score_tuples = tuple(zip(range(len(pred_scores)), pred_scores))
                score_sorted = sorted(score_tuples, key=itemgetter(1), reverse=True)

                labeled_video.append((labels[score_sorted[0][0]]))
        return labeled_video


if __name__ == "__main__":
    process_video("http://youtube.com/watch?v=9bZkp7q19f0")
