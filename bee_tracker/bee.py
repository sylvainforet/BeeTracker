#!/usr/bin/env python

import collections


class Bee:
    '''A bee with a unique id, a set of tags, frames, and (x, y) coordinates
    '''

    UNKNOWN_TAG = 0

    def __init__(self, beeId):
        '''Initialises a empty bee object with a unique id
        '''
        self.beeId      = beeId
        self.tags       = ()
        self.frames     = ()
        self.xs         = ()
        self.ys         = ()
        self.pathStarts = []
        self.tagClass   = Bee.UNKNOWN_TAG

    def findPathStarts(self):
        '''Find the starts of contiguous successive records
        '''
        if self.pathStarts:
            self.pathStarts = []
        self.pathStarts.append(0)
        # much faster to work on a list than a numpy ndarray
        frames = list(self.frames)
        previous = frames[0]
        for frame in frames[1:]:
            if previous + 1 != frame:
                self.pathStarts.append(frame)
            previous = frame

    def mergePaths(self, maxDiff=10):
        '''Merges paths that are only separated by a few frames.
        The coordinates of the missing point are linearly extrapolated.
        maxDiff: maximim number of missing frames between paths to be merged
        '''

    def classify(self, minCount=100, consistency=0.7):
        '''Classifies the bee
        minCount: minimum number of count of known tag type
        consistency: minimum proportion of the main tag type
        '''
        tags = collections.defaultdict(int)
        for tag in self.tags:
            tags[tag] += 1
        maxCount   = 0
        totalCount = 0
        maxTag     = Bee.UNKNOWN_TAG
        for tag, count in tags:
            if tag != Bee.UNKNOWN_TAG:
                totalCount += count
                if count > maxCount:
                    maxCount = count
                    maxTag   = tag
        if maxCount > minCount and maxCount / totalCount >= consistency:
                self.tagClass = maxTag

def main():
    # TODO write some test
    pass

if __name__ == '__main__':
    import cProfile
    cProfile.run('main()')
