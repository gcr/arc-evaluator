#!/usr/bin/env python
import dataset
import os
import bbox_utils

def load(bounding_box_folder = "Pedestrian/groundTruth"):
    """Load the Caltech Pedestrian Dataset"""

    img_folder = "Pedestrian/images"
    bounding_box_folder = bounding_box_folder

    img_file_dict = {}
    bbbox_lists_dict = {}

    for file in os.listdir(img_folder):
        img_file_dict[os.path.splitext(file)[0]] = img_folder +"/"+ file
    
    if bounding_box_folder == "Pedestrian/groundTruth":
        for file in os.listdir(bounding_box_folder):
            bounding_boxes = []
            i = 0
            filename = bounding_box_folder +"/"+file
            for line in open(filename).readlines():
                l = line.split()
                if i == 0:
                    pass
                else:
                    left, top, width, height = [int(l[i]) for i in range(1,5)]
                    bounding_boxes.append(bbox_utils.BoundingBox(top, left, height, width, confidence = None))
                i += 1
            bbbox_lists_dict[os.path.splitext(file)[0]] = bounding_boxes

    if bounding_box_folder == "Pedestrian/cpu":
        for file in os.listdir(bounding_box_folder):
            bounding_boxes = []
            filename = bounding_box_folder +"/"+file
            for line in open(filename).readlines():
                l = line.split()
                left, top, width, height = [int(float(l[i])) for i in range(0,4)]
                bounding_boxes.append(bbox_utils.BoundingBox(top, left, height, width, confidence = None))
            bbbox_lists_dict[os.path.splitext(file)[0]] = bounding_boxes
    return bbbox_lists_dict, img_file_dict

    # records = [
    #     dataset.DatasetRecord(filename, None, "positive")
    #     for filename in positive_image_filenames
    # ] + [
    #     dataset.DatasetRecord(filename, None, "negative")
    #     for filename in negative_image_filenames
    # ]

    # return dataset.Dataset(_name = "UIUC Cars", _folder = folder, _records = records)
