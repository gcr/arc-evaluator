#!/usr/bin/env python

class BoundingBox(object):
    def __init__(self, top,left,height,width):
        self.top = top
        self.left = left
        self.height = height
        self.width = width

    def __repr__(self):
        return "<Box: %s,%s + %sx%s>"%(self.left, self.top, self.width, self.height)

    @property
    def area(self):
        """ In pixels """
        return self.height * self.width

    def intersect(self, other):
        """Return a new bounding box that contains the intersection of
        'self' and 'other', or None if there is no intersection
        """
        raise NotImplementedError("TODO")
