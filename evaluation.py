#!/usr/bin/env python

from bbox_utils import BoundingBox

def ellipse_TP_FP(groundtruth, eval_boxes, confidence_threshold):
    """
    F-measure evaluation, described in Section III of
    http://cogcomp.cs.illinois.edu/papers/AgarwalAwRo04.pdf

    A box is a match iff. it satisfies the ellipse criteria on Page 7.

    Params
    ------

    Groundtruth is a mapping, {'image-1.png': [list of BoundingBox objects]}
    eval_boxes is a mapping, {'image-1.png': [list of BoundingBox objects]},
    which is the CPU bounding boxes (or perhaps it's the HPU)

    """
    TP = 0
    FP = 0
    FN = 0
    for image_key in groundtruth.keys() + eval_boxes.keys():
        gt_bboxes = set(groundtruth.get(image_key, []))
        other_bboxes = set(eval_boxes.get(image_key, []))
        for gt_bbox in gt_bboxes:
            # Do any of their boxes match?
            match = None
            for other_box in other_bboxes:
                if gt_bbox.ellipse_matches(other_box):
                    match = other_box
            if match:
                other_bboxes.remove(match)
                TP += 1
            else:
                FN += 1
        FP += len(other_bboxes)
        # if len(other_bboxes):
        #     print "False positive on", image_key

    return {"TP": TP, "FP": FP, "FN": FN, "TN": 0}
