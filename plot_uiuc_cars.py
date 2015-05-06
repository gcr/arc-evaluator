#!/usr/bin/env python

"""
This file generates plots for
"""

import os
import re
import simplejson
import pandas
import numpy as np
from matplotlib import pyplot as plt

import evaluation
import bbox_utils
from bbox_utils import BoundingBox


print "Loading data..."

# Groundtruth data, for Team DenseMatrix
def gt_to_bbox_densematrix(gt):
    return BoundingBox(
        top = gt['y'],
        left = gt['x'],
        width = gt['width'],
        height = gt['height'],
        confidence = gt['confidence'] if 'confidence' in gt else None,
    )

with open("StudentData-UIUC-Cars/Team DenseMatrix/Experiment-1.json") as f:
    json = simplejson.load(f)
    DenseMatrix1_ground_truth = {
        os.path.basename(record["image"]):
        map(gt_to_bbox_densematrix, record['groundTruth'])
        for record in json
    }
    DenseMatrix1_CPU = {
        os.path.basename(record["image"]):
        map(gt_to_bbox_densematrix, record['cpu'])
        for record in json
    }
    DenseMatrix1_HPU = {
        os.path.basename(record["image"]):
        map(gt_to_bbox_densematrix, record['hpu']['boxes'])
        for record in json
    }
with open("StudentData-UIUC-Cars/Team DenseMatrix/Experiment-2.json") as f:
    json = simplejson.load(f)
    DenseMatrix2_CPU = {
        os.path.basename(record["image"]):
        map(gt_to_bbox_densematrix, record['cpu'])
        for record in json
    }
    DenseMatrix2_HPU = {
        os.path.basename(record["image"]):
        map(gt_to_bbox_densematrix, record['hpu']['boxes'])
        for record in json
    }
with open("StudentData-UIUC-Cars/Team DenseMatrix/Experiment-3.json") as f:
    json = simplejson.load(f)
    DenseMatrix3_CPU = {
        os.path.basename(record["image"]):
        map(gt_to_bbox_densematrix, record['cpu'])
        for record in json
    }
    DenseMatrix3_HPU = {
        os.path.basename(record["image"]):
        map(gt_to_bbox_densematrix, record['hpu']['boxes'])
        for record in json
    }


AnishShah_csv = pandas.io.parsers.read_csv("StudentData-UIUC-Cars/Team AnishShah/CPU.csv")
AnishShah_CPU = {}
for i,row in AnishShah_csv.loc[1:].iterrows():
    key = row['name'].replace("pgm","png")
    if row['x2'] != '0' and row['x1'] != '0':
        AnishShah_CPU[key] = AnishShah_CPU.get(key, []) + (
            [BoundingBox(top = int(row['y1']),
                         height = int(row['y2']) - int(row['y1']),
                         left = int(row['x1']),
                         width = int(row['x2']) - int(row['x1']),
            )])

AnishShah_csv = pandas.io.parsers.read_csv("StudentData-UIUC-Cars/Team AnishShah/HPU.csv")
AnishShah_HPU = {}
for i,row in AnishShah_csv.loc[1:].iterrows():
    key = row['name'].replace("jpg","png")
    if row['x2'] != '0' and row['x1'] != '0':
        AnishShah_HPU[key] = AnishShah_HPU.get(key, []) + (
            [BoundingBox(top = int(row['y1']),
                         height = int(row['y2']) - int(row['y1']),
                         left = int(row['x1']),
                         width = int(row['x2']) - int(row['x1']),
            )])

# I can't use @boom's data yet because it's on the multiscale dataset

## Load Team Boom's data
#import re
#def boom_parse(filename):
#    boom_results = {}
#    for line in open(filename):
#        line = line.split(" ")
#        index = int(line.pop(0))
#        time = float(line.pop(-1).strip())
#        #print boom_format.match(line.strip()).groupdict()
#        for box_str in line:
#            match = re.match(r"""\[([0-9]*),([0-9]*),([0-9]*),([0-9]*)\]""", box_str)
#            if match:
#                x,y,w,h = match.groups()
#                key = "test-%d.png" % index
#                boom_results[key] = boom_results.get(key, []) + (
#                    [BoundingBox(top = float(y),
#                                 left = float(x),
#                                 height = float(h),
#                                 width = float(w))])
#    return boom_results
#
#boom_hpu_9 = boom_parse("StudentData-UIUC-Cars/Team boom/9.txt")

# Load Team @yash's data
def parse_team_yash(filename):
    yash_results = {}
    for line in open(filename).readlines():
        idx = int(line.split(":")[0])
        key = "test-%d.png" % idx
        for (y_s,x_s) in re.findall(r"""\(([0-9]*) ([0-9]*)\)""", line):
            yash_results[key] = yash_results.get(key, []) + (
                [BoundingBox(top = int(y_s),
                             left = int(x_s),
                             width = 100,
                             height = 40)])
    return yash_results

yash_cpu = parse_team_yash("StudentData-UIUC-Cars/Team yash/foundLocations_cascade5.txt")


def show_plot():
    print "Generating plots ..."

    fig,ax = plt.subplots()
    ax.set_color_cycle([plt.cm.rainbow(i)
                        for i in np.linspace(0, 1, 9)])

    evaluation.make_accuracy_plot(ax,
        DenseMatrix1_ground_truth, DenseMatrix1_HPU, DenseMatrix1_CPU, evaluation.HPU_strategy_random_mix,
        "Team DenseMatrix, Experiment-1\nRandom mix of HPU+CPU"
    )
    # evaluation.make_accuracy_plot(ax,
    #     ground_truth, ground_truth, CPU, evaluation.HPU_strategy_random_mix,
    #     "Team DenseMatrix, Experiment-1\nRandom mix of groundtruth+CPU"
    # )
    evaluation.make_accuracy_plot(ax,
        DenseMatrix1_ground_truth, DenseMatrix1_HPU, DenseMatrix1_CPU, evaluation.HPU_strategy_increasing_lowest_confidence_mix,
        "Team DenseMatrix: Experiment-1\nMix of HPU+CPU, by increasing CPU confidence",
    )

    evaluation.make_accuracy_plot(ax,
        DenseMatrix1_ground_truth, DenseMatrix2_HPU, DenseMatrix2_CPU, evaluation.HPU_strategy_random_mix,
        "Team DenseMatrix, Experiment-2\nRandom mix of HPU+CPU"
    )
    evaluation.make_accuracy_plot(ax,
        DenseMatrix1_ground_truth, DenseMatrix2_HPU, DenseMatrix2_CPU, evaluation.HPU_strategy_increasing_lowest_confidence_mix,
        "Team DenseMatrix: Experiment-2\nMix of HPU+CPU, by increasing CPU confidence",
    )

    evaluation.make_accuracy_plot(ax,
        DenseMatrix1_ground_truth, DenseMatrix3_HPU, DenseMatrix3_CPU, evaluation.HPU_strategy_random_mix,
        "Team DenseMatrix, Experiment-3\nRandom mix of HPU+CPU"
    )
    evaluation.make_accuracy_plot(ax,
        DenseMatrix1_ground_truth, DenseMatrix3_HPU, DenseMatrix3_CPU, evaluation.HPU_strategy_increasing_lowest_confidence_mix,
        "Team DenseMatrix: Experiment-3\nMix of HPU+CPU, by increasing CPU confidence",
    )

    evaluation.make_accuracy_plot(ax,
        DenseMatrix1_ground_truth, AnishShah_HPU, AnishShah_CPU, evaluation.HPU_strategy_random_mix,
        "Team AnishShah\nRandom mix of HPU+CPU"
    )
    evaluation.make_accuracy_plot(ax,
        DenseMatrix1_ground_truth, AnishShah_HPU, DenseMatrix1_CPU, evaluation.HPU_strategy_increasing_lowest_confidence_mix,
        "Mix DenseMatrix-CPU with AnishShah-HPU"
    )

    evaluation.make_accuracy_plot(ax,
        DenseMatrix1_ground_truth, AnishShah_HPU, yash_cpu, evaluation.HPU_strategy_random_mix,
        "Mix Yash-CPU with AnishShah-HPU"
    )

    ax.set_title("HPU+CPU Hybrid Accuracy")
    ax.legend(loc='lower right')

    plt.show()



if __name__ == "__main__":
    show_plot()
