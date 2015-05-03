#!/usr/bin/env python
import dataset

def load(view):
    """Load the UIUC Car Dataset"""
    assert view in {"train", "test"}

    folder = "CarData"

    if view == "train":
        positive_image_filenames = [
            "%s/TrainImages/pos-%d.pgm" % (folder, i)
            for i in xrange(550) # specified by readme
        ]
        negative_image_filenames = [
            "%s/TrainImages/neg-%d.pgm" % (folder, i)
            for i in xrange(500) # specified by readme
        ]

    records = [
        dataset.DatasetRecord(filename, None, "positive")
        for filename in positive_image_filenames
    ] + [
        dataset.DatasetRecord(filename, None, "negative")
        for filename in negative_image_filenames
    ]

    return dataset.Dataset(_name = "UIUC Cars", _folder = folder, _records = records)
