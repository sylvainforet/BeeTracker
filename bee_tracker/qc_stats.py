#!/usr/bin/env python

import collections
import os.path

import pandas

import bee_tracker.bee


class QCStatistic:
    '''Parent class for all the classes that extract QC statistics
    '''

    name        = 'qc_statistic'
    description = 'Bee Tracking QC'
    extension   = '.txt'

    def __init__(self, bees):
        self.bees        = bees
        self.result      = None

    @classmethod
    def getOutputFileName(cls):
        return cls.name + cls.extension

    def compute(self):
        raise Exception('Not implemented')

    def write(self, outDir):
        if not self.result is None and not self.result.empty:
            path = os.path.join(outDir, self.getOutputFileName())
            self.result.to_csv(path, index=False)

class BeesPerFrame(QCStatistic):

    name        = 'bees_per_frame'
    description = 'Number of bees per frame'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees)

    def compute(self):
        beeCounts = {}
        for bee in self.bees.values():
            if not bee.category in beeCounts:
                beeCounts[bee.category] = collections.defaultdict(int)
            for frame in bee.frames:
                beeCounts[bee.category][frame] += 1
        categories = list(beeCounts.keys())
        dfs        = []
        for category in categories:
            counts = {'category': category,
                      'counts'  : list(beeCounts[category].values())}
            df     = pandas.DataFrame(counts)
            dfs.append(df)
        self.result = pandas.concat(dfs)

class FramesPerBee(QCStatistic):

    name        = 'frames_per_bee'
    description = 'Number of frames per bee'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees)

    def compute(self):
        frameCounts = collections.defaultdict(list)
        for bee in self.bees.values():
            start = bee.frames[0]
            end   = bee.frames[-1]
            frameCounts[bee.category].append(end - start + 1)
        categories = list(frameCounts.keys())
        dfs        = []
        for category in categories:
            counts = {'category': category,
                      'counts'  : list(frameCounts[category])}
            df     = pandas.DataFrame(counts)
            dfs.append(df)
        self.result = pandas.concat(dfs)

class FramesPerPath(QCStatistic):

    name        = 'frames_per_path'
    description = 'Number of frames per path'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees)

    def compute(self):
        frameCounts = collections.defaultdict(list)
        for bee in self.bees.values():
            start = bee.frames[0]
            for i in bee.pathStarts[1:]:
                end = bee.frames[i - 1]
                frameCounts[bee.category].append(end - start + 1)
            end = bee.frames[-1]
            frameCounts[bee.category].append(end - start + 1)
        categories = list(frameCounts.keys())
        dfs        = []
        for category in categories:
            counts = {'category': category,
                      'counts'  : list(frameCounts[category])}
            df     = pandas.DataFrame(counts)
            dfs.append(df)
        self.result = pandas.concat(dfs)

class FramesBetweenPaths(QCStatistic):

    name        = 'frames_between_paths'
    description = 'Number of frames between paths'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees)

    def compute(self):
        frameCounts = collections.defaultdict(list)
        for bee in self.bees.values():
            for i in bee.pathStarts[1:]:
                start = bee.frames[i - 1]
                end   = bee.frames[i]
                frameCounts[bee.category].append(end - start - 1)
        categories = list(frameCounts.keys())
        dfs        = []
        for category in categories:
            counts = {'category': category,
                      'counts'  : list(frameCounts[category])}
            df     = pandas.DataFrame(counts)
            dfs.append(df)
        self.result = pandas.concat(dfs)

class PathsPerBee(QCStatistic):

    name        = 'paths_per_bee'
    description = 'Number of paths per bee'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees)

    def compute(self):
        pathCounts = collections.defaultdict(list)
        for bee in self.bees.values():
            nPath = len(bee.pathStarts)
            pathCounts[bee.category].append(nPath)
        categories = list(pathCounts.keys())
        dfs        = []
        for category in categories:
            counts = {'category': category,
                      'counts'  : list(pathCounts[category])}
            df     = pandas.DataFrame(counts)
            dfs.append(df)
        self.result = pandas.concat(dfs)

class Classification(QCStatistic):

    name        = 'classification'
    description = 'Tag classification'

    def __init__(self, bees):
        QCStatistic.__init__(self, bees)

    def compute(self):
        # Deal with arbitrary number of categories
        tags = {}
        for bee in self.bees.values():
            for tag in bee.tags:
                if not tag in tags:
                    tags[tag] = 1
        classifications = {}
        for tag in tags:
            classifications[tag] = []
        idx = 0
        for bee in self.bees.values():
            for tag in tags:
                classifications[tag].append(0)
            for tag in bee.tags:
                classifications[tag][idx] += 1
            idx += 1
        self.result = pandas.DataFrame(classifications)

def computeStats(stats, bees, outDir):
    for stat in stats:
        instance = stat(bees)
        instance.compute()
        instance.write(outDir)
