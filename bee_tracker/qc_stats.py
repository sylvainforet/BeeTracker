#!/usr/bin/env python

import collections
import os.path


class QCStatistic:

    @staticmethod
    def getOutputFileName():
        raise Exception('Not implemented')

    def __init__(self, bees, description=''):
        self.bees        = bees
        self.description = description
        self.result      = []

    def compute(self):
        raise Exception('Not implemented')

    def write(self, outDir):
        values = [str(x) for x in self.result]
        values.append('')
        values = '\n'.join(values)
        path   = os.path.join(outDir, self.getOutputFileName())
        with open(path, "w") as handle:
            handle.write(values)

class BeesPerFrame(QCStatistic):

    @staticmethod
    def getOutputFileName():
        return 'bees_per_frame.txt'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees,
                             'Distribution of number of bees per frame')
        self.result      = []

    def compute(self):
        if self.result:
            self.result = []
        beeCounts = collections.defaultdict(int)
        for bee in self.bees.values():
            for frame in bee.frames:
                beeCounts[frame] += 1
        self.result = list(beeCounts.values())
        self.result.sort()

class FramesPerBee(QCStatistic):

    @staticmethod
    def getOutputFileName():
        return 'frames_per_bee.txt'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees,
                             'Distribution of number of frames per bee')
        self.result      = []

    def compute(self):
        if self.result:
            self.result = []
        for bee in self.bees.values():
            start = bee.frames[0]
            end   = bee.frames[-1]
            self.result.append(end - start + 1)
        self.result.sort()

class FramesPerPath(QCStatistic):

    @staticmethod
    def getOutputFileName():
        return 'frames_per_path.txt'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees,
                             'Distribution of number of frames per path')
        self.result      = []

    def compute(self):
        if self.result:
            self.result = []
        for bee in self.bees.values():
            start = bee.pathStarts[0]
            for i in bee.pathStarts[1:]:
                end = bee.frames[i - 1]
                self.result.append(end - start + 1)
            end = bee.frames[-1]
            self.result.append(end - start + 1)
        self.result.sort()

class PathsPerBee(QCStatistic):

    @staticmethod
    def getOutputFileName():
        return 'paths_per_bee.txt'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees,
                             'Distribution of number of paths per bee')
        self.result      = []

    def compute(self):
        if self.result:
            self.result = []
        for bee in self.bees.values():
            self.result.append(len(bee.pathStarts))
        self.result.sort()

class FramesBetweenPath(QCStatistic):

    @staticmethod
    def getOutputFileName():
        return 'frames_between_paths.txt'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees,
                             'Distribution of number of frames between path')
        self.result      = []

    def compute(self):
        if self.result:
            self.result = []
        for bee in self.bees.values():
            for i in bee.pathStarts[1:]:
                start = bee.frames[i - 1]
                end = bee.frames[i]
                self.result.append(end - start - 1)
        self.result.sort()

def computeStats(stats, bees, outDir):
    for stat in stats:
        instance = stat(bees)
        instance.compute()
        instance.write(outDir)
