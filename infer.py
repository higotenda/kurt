from operator import itemgetter
from mmaction.apis import init_recognizer, inference_recognizer
import os

config_file = 'tsn_imagenet-pretrained-r50_8xb32-1x1x8-100e_kinetics400-rgb.py'
checkpoint_file = 'tsn_imagenet-pretrained-r50_8xb32-1x1x8-100e_kinetics400-rgb_20220906-2692d16c.pth'
video_file = 'demo/demo.mp4'
label_file = 'tools/data/kinetics/label_map_k400.txt'
model = init_recognizer(config_file, checkpoint_file, device='cpu')  # or device='cuda:0'

for video_file in os.listdir("output"):
    if os.path.isfile(os.path.join("output", video_file)):
        pred_result = inference_recognizer(model, video_file)

        pred_scores = pred_result.pred_score.tolist()
        score_tuples = tuple(zip(range(len(pred_scores)), pred_scores))
        score_sorted = sorted(score_tuples, key=itemgetter(1), reverse=True)
        top5_label = score_sorted[:5]

        labels = open(label_file).readlines()
        labels = [x.strip() for x in labels]
        results = [(labels[k[0]], k[1]) for k in top5_label]

        print('The top-5 labels with corresponding scores are:')
        for result in results:
            print(f'{result[0]}: ', result[1])