from operator import itemgetter
import torch
from mmaction.apis import init_recognizer, inference_recognizer
import download
import os

config_file = "tsn_imagenet-pretrained-r50_8xb32-1x1x8-100e_kinetics400-rgb.py"
checkpoint_file = (
    "tsn_imagenet-pretrained-r50_8xb32-1x1x8-100e_kinetics400-rgb_20220906-2692d16c.pth"
)
chunk_dir = "output"
label_file = "label_map_k400.txt"
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = init_recognizer(
    config_file, checkpoint_file, device=device
)  # or device='cuda:0'

if not os.path.exists(chunk_dir):
    download.demo()

for video_file in os.listdir(chunk_dir):
    if os.path.isfile(os.path.join(chunk_dir, video_file)):
        pred_result = inference_recognizer(model, f"{chunk_dir}/{video_file}")

        pred_scores = pred_result.pred_score.tolist()
        score_tuples = tuple(zip(range(len(pred_scores)), pred_scores))
        score_sorted = sorted(score_tuples, key=itemgetter(1), reverse=True)
        top5_label = score_sorted[:5]

        labels = open(label_file).readlines()
        labels = [x.strip() for x in labels]
        results = [(labels[k[0]], k[1]) for k in top5_label]

        print("The top-5 labels with corresponding scores are:")
        for result in results:
            print(f"{result[0]}: ", result[1])
