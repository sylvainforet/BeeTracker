#!/usr/bin/python

import argparse

import bee_tracker.qc_stats
import bee_tracker.io_csv

def parseArgs():
    parser = argparse.ArgumentParser(description='Compute basic QC stats for bee movie')
    parser.add_argument('input',
                        metavar='FILE',
                        help='The input CSV file')
    parser.add_argument('-o',
                        '--outDir',
                        default='.',
                        metavar='DIR',
                        help='Output directory')
    parser.add_argument('-p',
                        '--profile',
                        action='store_true',
                        help='Output profiling information')
    args = parser.parse_args()
    return args

def main(args):
    bees  = bee_tracker.io_csv.loadBeesCSV(args.input)
    for bee in bees.values():
        bee.classify()
    stats = [bee_tracker.qc_stats.BeesPerFrame,
             bee_tracker.qc_stats.FramesPerBee,
             bee_tracker.qc_stats.FramesPerPath,
             bee_tracker.qc_stats.FramesBetweenPath,
             bee_tracker.qc_stats.PathsPerBee,
             bee_tracker.qc_stats.Classification]
    bee_tracker.qc_stats.computeStats(stats, bees, args.outDir)

if __name__ == '__main__':
    args  = parseArgs()
    if args.profile:
        import cProfile
        cProfile.run('main(args)')
    else:
        main(args)
