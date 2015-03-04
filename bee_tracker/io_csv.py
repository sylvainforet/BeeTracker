#!/usr/bin/env python

import sys

import pandas

from bee import Bee


def loadCSVLists(path):
    '''Loads the bee data from a CSV file as a set of vectors.
    Returns the following vectors: ids, tags, frames, x coordinates and y
    coordinates.
    '''
    beeIds = []
    tags   = []
    frames = []
    xs     = []
    ys     = []
    with open(path) as handle:
        metaData = handle.readline()
        header = handle.readline()
        for line in handle:
            fields = line.split(',')
            beeId  = int(fields[0])
            tag    = int(fields[1])
            frame  = int(fields[2])
            x      = float(fields[3])
            y      = float(fields[4])
            beeIds.append(beeId)
            tags.append(tag)
            frames.append(frame)
            xs.append(x)
            ys.append(y)
    return (beeIds, tags, frames, xs, ys)

def loadCSVDataFrame(path):
    '''Loads the bee data from a CSV file as a set of vectors.
    Returns the following vectors: ids, tags, frames, x coordinates and y
    coordinates.
    '''
    dtype = {'BeeID': int,
             'Tag'  : int,
             'Frame': int,
             'X'    : float,
             'Y'    : float}
    df    = pandas.read_csv(path,
                            engine='c',
                            comment='#',
                            dtype=dtype)
    return df

def createBeesFromList(beeIds, tags, frames, xs, ys):
    '''Creates a dictionary of bee objects indexed by bee id based on vectors
    of beeIds, tags, frames number, x and y coordinates.
    '''
    nRecords = len(beeIds)
    bees     = {}
    for i in range(nRecords):
        beeId = beeIds[i]
        if not beeId in bees:
            newBee      = Bee(beeId)
            bees[beeId] = newBee
        bee = bees[beeId]
        bee.tags.append(tags[i])
        bee.frames.append(frames[i])
        bee.xs.append(xs[i])
        bee.ys.append(ys[i])
    for beeId in bees:
        bees[beeId].findPathStarts()
    return bees

def createBeesFromDataFrame(df, minSize=0):
    '''Creates a dictionary of bee objects indexed by bee id based on vectors
    of beeIds, tags, frames number, x and y coordinates.
    '''

    nRecords = len(df)
    bees     = {}
    for beeId, subFrame in df.groupby('BeeID'):
        if len(subFrame) < minSize:
            continue
        bee             = Bee(beeId)
        bee.tags        = subFrame['Tag'].values
        bee.frames      = subFrame['Frame'].values
        bee.xs          = subFrame['X'].values
        bee.ys          = subFrame['Y'].values
        bees[bee.beeId] = bee
    for beeId in bees:
        bees[beeId].findPathStarts()
    return bees

def loadBeesCSV(path):
    '''Loads dictionary of bee objects indexed by bee id from a CSV file
    '''
    #vectors = loadCSVLists(path)
    #bees = createBeesFromList(*vectors)
    df   = loadCSVDataFrame(path)
    bees = createBeesFromDataFrame(df)
    return bees

def filterBees(bees, filterFunction, description):
    toRemove = []
    for beeId in bees:
        if not filterFunction(bees[beeId]):
            toRemove.append(beeId)
    for beeId in toRemove:
        del bees[beeId]
    sys.stderr.write('%s filter: %d bees removed\n' % (description, filterFunction))

def main():
    import os.path
    if len(sys.argv) !=2:
        sys.stderr.write('Usage: %s CSV\n' % os.path.basename(sys.argv[0]))
        sys.exit(1)
    bees = loadBeesCSV(sys.argv[1])

if __name__ == '__main__':
    import cProfile
    cProfile.run('main()')
