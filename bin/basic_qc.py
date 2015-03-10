#!/usr/bin/python

import argparse
import multiprocessing
import os.path
import sys

import bee_tracker.qc_stats
import bee_tracker.io_csv


class Worker:

    def __init__(self, args):
        self.args = args

    def work(self, path):
        stats  = [bee_tracker.qc_stats.BeesPerFrame,
                  bee_tracker.qc_stats.FramesPerBee,
                  bee_tracker.qc_stats.FramesPerPath,
                  bee_tracker.qc_stats.FramesBetweenPath,
                  bee_tracker.qc_stats.PathsPerBee,
                  bee_tracker.qc_stats.Classification]
        name   = os.path.basename(path)
        outDir = os.path.join(args.outDir, name)
        try:
            os.makedirs(outDir)
        except FileExistsError:
            sys.stderr.write('Output directory "%s" already exists\n' % outDir)
        bees  = bee_tracker.io_csv.loadBeesCSV(path)
        for bee in bees.values():
            bee.classify()
        bee_tracker.qc_stats.computeStats(stats, bees, outDir)

def parseArgs():
    parser = argparse.ArgumentParser(description='Compute basic QC stats for bee movie')
    parser.add_argument('input',
                        metavar='FILE',
                        nargs='+',
                        help='The input CSV file')
    parser.add_argument('-o',
                        '--outDir',
                        default='.',
                        metavar='DIR',
                        help='Output directory')
    parser.add_argument('-p',
                        '--processes',
                        type=int,
                        default=0,
                        metavar='N',
                        help='Number of parallel processes')
    parser.add_argument('-r',
                        '--profile',
                        action='store_true',
                        help='Output profiling information')
    args = parser.parse_args()
    return args

def main(args):
    worker = Worker(args)
    if args.processes < 1:
        for path in args.input:
            worker.work(path)
    else:
        pool = multiprocessing.Pool(processes=args.processes)
        pool.map(worker.work, args.input, chunksize=1)

if __name__ == '__main__':
    args  = parseArgs()
    if args.profile:
        import cProfile
        cProfile.run('main(args)')
    else:
        main(args)
