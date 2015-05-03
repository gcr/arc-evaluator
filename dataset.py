#!/usr/bin/env python
import os
import simplejson
import skimage
from skimage import io

class DatasetRecord(object):
    def __init__(self, filename, groundtruth, label):
        self.filename = filename
        self.groundtruth = groundtruth
        self.label = label

    def __repr__(self):
        return "<DatasetRecord: %r, label: %r, groundtruth: %r>" % (
            self.filename, self.groundtruth, self.label
        )

    @property
    def image(self):
        return skimage.img_as_float(io.imread(self.filename))

class Dataset(list):
    def __init__(self, _name, _folder, _records):
        self._name = _name
        self._folder = _folder
        list.__init__(self, _records)

    def __repr__(self):
        return "<Dataset: %r, %d images, labels: %r>" % (
            self._name,
            len(self),
            self.label_hist
        )

    @property
    def label_hist(self):
        """ Return a count of {label: number of occurrences, ...} """
        hist = {}
        for record in self:
            hist[record.label] = 1 + hist.get(record.label, 0)
        return hist

    @property
    def only_label(self, label):
        """ Return only the positive images in the dataset """
        return Dataset(self._folder,
                       [record
                        for record in self
                        if record.label == label])
