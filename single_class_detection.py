## The following code is a part of object detection metrics post at the Carla simulator research blog - https://carlasimblog.wordpress.com/2023/10/03/object-detection-metrics-in-computer-vision/.
## Feel free to show your support via requested, suggestions and interesting ideas for future research material.


import os
import glob
import numpy as np

# TP = predicted positive and ground truth positive
# FP = predicted positive and ground truth negative
# TN = predicted negative and ground truth negative - irrelevant for object detection
# FN = predicted negative and ground truth positive
#
## precision = TP / (TP+FP)
## recall = TP / (TP + FN)

relevant_class = 0
min_iou = 0.5
min_conf = 0.5

# YOLO format parser
def parse_yolo_format(line):
    data = line.strip().split()
    class_id = int(data[0])
    coords = [float(data[1]), float(data[2]), float(data[3]), float(data[4])]
    try:
        conf = float(data[-1])
    except:
        conf = []
    return class_id, coords, conf

# Intersection over Union (IoU) calculation
def calculate_iou(box1, box2):
    x1, y1, w1, h1 = box1
    x2, y2, w2, h2 = box2

    x1 = max(x1 - w1 / 2, 0)
    y1 = max(y1 - h1 / 2, 0)
    x2 = max(x2 - w2 / 2, 0)
    y2 = max(y2 - h2 / 2, 0)

    intersection = max(0, min(x1 + w1, x2 + w2) - max(x1, x2)) * max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    union = w1 * h1 + w2 * h2 - intersection

    return intersection / union

# Folder paths for ground truth and detection output
ground_truth_folder = "path_to_ground_truth"
detection_output_folder = "path_to_detection_folder"

# Initialize counters
true_positives = 0
false_positives = 0
false_negatives = 0
ground_truth_objects = 0
avg_conf = 0
avg_iou = 0

# Read detection output files
detection_files = glob.glob(os.path.join(detection_output_folder, "*.txt"))
gt_files = glob.glob(os.path.join(ground_truth_folder, "*.txt"))
for file_num in range(len(gt_files)):
    with open(gt_files[file_num], "r") as f:
        gt_data, detection_data = [], []
        gt_lines = f.readlines()

    for gt_line in gt_lines:
        gt_class_id, gt_box, _ = parse_yolo_format(gt_line)
        gt_data.append([gt_class_id, gt_box])

    filename = os.path.split(gt_files[file_num])[1]
    ## we check if the detection file exists.
    # if not, we check if there are detection in the ground truth file and mark them as false negative
    if os.path.exists(os.path.join(detection_output_folder, filename)):
        with open(os.path.join(detection_output_folder, filename), "r") as f:
            detection_lines = f.readlines()
        for detection_line in detection_lines:
            detection_class_id, detection_box, detection_conf = parse_yolo_format(detection_line)
            detection_data.append([detection_class_id, detection_box, detection_conf])

        ## we compare between the ground truth and detections
        for gt_bb in gt_data:
            ## check if class is relevant
            if gt_bb[0] == relevant_class:
                ground_truth_objects += 1
                bb_found = False
                ## check all bb in detection lines to see if it's the same object (> min iou)
                for detection_bb in detection_data:
                    ## check if same class + > min iou
                    if detection_bb[0] == relevant_class and calculate_iou(gt_bb[1], detection_bb[1]) > min_iou and detection_bb[2] > min_conf:
                        true_positives += 1
                        bb_found = True
                        avg_conf += detection_bb[2]
                        avg_iou += calculate_iou(gt_bb[1], detection_bb[1])
                if not bb_found:
                    false_positives += 1

    else:
        ## count how many objects of relevant class exist and mark them as false negetive
        for gt_bb in gt_data:
            if gt_bb[0] == relevant_class:
                false_negatives += 1

precision = true_positives / (true_positives+false_positives)
recall = true_positives / (true_positives + false_negatives)

print(f'ground_truth_objects: {ground_truth_objects}')
print(f'precision: {np.round(precision, 3)}')
print(f'recall: {np.round(recall, 3)}')
print(f'avg iou of detected objects: {np.round(avg_iou / true_positives, 3)}')
print(f'avg confidence of detected objects: {np.round(avg_conf / true_positives, 3)}')

