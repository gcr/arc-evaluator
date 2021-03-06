#!/usr/bin/env python
import numpy as np

from bbox_utils import BoundingBox

def calc_TP_FP(groundtruth, eval_boxes, matches_predicate, confidence_threshold=-9e999):
    """F-measure evaluation, described in Section III of
    http://cogcomp.cs.illinois.edu/papers/AgarwalAwRo04.pdf

    A box is a match iff. it satisfies the ellipse criteria on Page 7.

    For eval_boxes, only those with confidence >=
    `confidence_threshold` are kept.

    Params
    ------

    Groundtruth is a mapping, {'image-1.png': [list of BoundingBox objects]}
    eval_boxes is a mapping, {'image-1.png': [list of BoundingBox objects]},
    which is the CPU bounding boxes (or perhaps it's the HPU)
    matches_predicate is a predicate that decides whether two boxes should match.

    """
    TP = 0
    FP = 0
    FN = 0
    for image_key in groundtruth.keys() + eval_boxes.keys():
        gt_bboxes = set(groundtruth.get(image_key, []))
        other_bboxes = set(box
                           for box in eval_boxes.get(image_key, [])
                           if box.confidence >= confidence_threshold
                           or box.confidence is None
        )
        for gt_bbox in gt_bboxes:
            # Do any of their boxes match?
            match = None
            for other_box in other_bboxes:
                if matches_predicate(gt_bbox, other_box):
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

def maximum_F_score(groundtruth, eval_boxes, match_mode="ellipse"):
    """Given a groundtruth mapping and a set of detected boxes to
    evaluate, this function returns a measure of accuracy: the point
    along the precision/recall curve that has the highest F-measure.

    Note: eval_boxes SHOULD be annotated with confidence information.
    If a box has a value of None (for example, because it is a human
    judgment), then it will always be used.
    """
    if match_mode=="ellipse":
        matcher = lambda gt,other: gt.ellipse_matches(other)
    elif match_mode=="iou":
        matcher = lambda gt,other: gt.iou_score(other) >= 0.5
    all_confidences = {box.confidence
                       for boxes in eval_boxes.values()
                       for box in boxes}
    if len(all_confidences) > 50:
        all_confidences = set(np.random.choice(list(all_confidences), 50, replace=False))
    if all_confidences:
        return max([
            F1_score(**calc_TP_FP(groundtruth, eval_boxes, matcher, confidence))
            for confidence in all_confidences
        ])
    else:
        return 0

def precision(TP, FP, TN, FN):
    if TP>0:
        return float(TP) / (float(TP + FP))
    return 0.0

def recall(TP, FP, TN, FN):
    if TP+FN>0:
        return float(TP) / (float(TP + FN))
    return 0.0

def F1_score(TP, FP, TN, FN):
    p = precision(TP, FP, TN, FN)
    r = recall(TP, FP, TN, FN)
    if r+p > 0:
        return 2*r*p / (r+p)
    else:
        return 0

def make_accuracy_plot(ax,
                       groundtruth_boxes,
                       hpu_boxes,
                       cpu_boxes,
                       hpu_strategy,
                       label,
                       N=10,
                       num_graph_points=20,
                       match_mode="ellipse",
):
    """Make an accuracy plot by using `HPU_strategy` to mix `hpu_boxes`
    and `cpu_boxes`, and comparing that to `groundtruth_boxes`. Plot
    the result on `ax`.

    X axis: Average *HUMAN* time per image
    Y axis: Accuracy, defined as the maximum F-Measure across all CPU
            confidence scores.

    Params
    ------
    ax: An Axes
    groundtruth_boxes: A apping, {"img key": [bbox, ...]}; the gold standard
    hpu_boxes: Another mapping, representing the boxes that we got
               from a web interface
    cpu_boxes: Another mapping, representing the boxes that we got
               from the CPU algorithm
    HPU_strategy: a function (boxes, boxes, fraction) -> (human_time, boxes),
                  that mixes CPU and HPU boxes together.
    """
    print "Making plot for", repr(label)
    print "TODO: this should graph seconds per image"
    mix_fractions = np.linspace(0, 1.0, num_graph_points)
    # Plot confidence intervals
    min_ci = []
    max_ci = []
    mean_accs = []
    stderr_accs = []
    for mix_fraction in mix_fractions:
        accuracies = [
            maximum_F_score(
                groundtruth_boxes,
                hpu_strategy(hpu_boxes, cpu_boxes, mix_fraction),
                match_mode=match_mode,
            )
            for _ in xrange(N)
        ]
        mean_accs.append(np.mean(accuracies))
        stderr_accs.append(np.std(accuracies, ddof=1) / np.sqrt(N))
        #print mix_fraction, np.mean(accuracies)
    ax.errorbar(mix_fractions, mean_accs, stderr_accs, label=label)
    ax.set_xlabel("Fraction of HPU-labeled images")
    ax.set_ylabel("Maximum F-score")


def HPU_strategy_random_mix(hpu_boxes, cpu_boxes, fraction):
    """This strategy corresponds to an HPU that flips a coin before
    detecting all boxes in an image.

    For each image i:
    - With probability `fraction`, we send the box to a human
      annotator, who returns the results in `hpu_boxes`
    - With probability 1-`fraction`, we send the box to a CPU
      annotator, who returns the corresponding result from `cpu_boxes`

    This happens per-image.
    """
    return {
        img_key: (hpu_boxes.get(img_key, [])
                  if np.random.rand() <= fraction
                  else cpu_boxes.get(img_key, []))
        for img_key in set(hpu_boxes.keys() + cpu_boxes.keys())
    }

def HPU_strategy_increasing_confidence_mix(hpu_boxes, cpu_boxes, measure, fraction):
    """This strategy corresponds to an HPU that runs a CPU detector on all
    images, and re-labels `fraction` of the LEAST confident IMAGES.

    If a CPU did not detect *any* boxes in an image, this image is
    assumed to have a confidence value of 0.

    This happens per-image.

    """
    # All image names, sorted by confidence
    all_image_keys = np.random.permutation(list(set(hpu_boxes.keys() + cpu_boxes.keys())))

    image_confidences = {
        img_key: measure([box.confidence for box in cpu_boxes.get(img_key, [])])
        for img_key in all_image_keys
    }
    sorted_image_keys = sorted(all_image_keys, key=lambda i: image_confidences[i])

    # print image_confidences
    # print "----------"
    how_many_to_relabel = int(len(sorted_image_keys) * fraction)

    which_to_relabel = set(sorted_image_keys[:how_many_to_relabel])
    # print [image_confidences[i] for i in sorted_image_keys]

    # print [image_confidences[i] for i in which_to_relabel]

    # print fraction, how_many_to_relabel

    return {
        img: hpu_boxes.get(img, [])
        if img in which_to_relabel else cpu_boxes.get(img, [])
        for img in all_image_keys
    }

def HPU_strategy_increasing_average_confidence_mix(hpu_boxes, cpu_boxes, fraction):
    return HPU_strategy_increasing_confidence_mix(
        hpu_boxes,
        cpu_boxes,
        measure = lambda xs: np.mean(xs) if len(xs) else 0,
        fraction=fraction
    )

def HPU_strategy_increasing_lowest_confidence_mix(hpu_boxes, cpu_boxes, fraction):
    return HPU_strategy_increasing_confidence_mix(
        hpu_boxes,
        cpu_boxes,
        measure = lambda xs: np.min(xs) if len(xs) else 0,
        fraction=fraction,
    )

def HPU_strategy_increasing_median_confidence_mix(hpu_boxes, cpu_boxes, fraction):
    return HPU_strategy_increasing_confidence_mix(
        hpu_boxes,
        cpu_boxes,
        measure = lambda xs: np.median(xs) if len(xs) else 0,
        fraction=fraction,
    )
