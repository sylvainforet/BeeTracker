#!/usr/bin/python

import argparse

import qc_stats
import io_csv

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
    args = parser.parse_args()
    return args

def main():
    args  = parseArgs()
    bees  = io_csv.loadBeesCSV(args.input)
    stats = [qc_stats.FramesPerBee,
             qc_stats.FramesPerPath,
             qc_stats.FramesBetweenPath,
             qc_stats.BeesPerFrame,
             qc_stats.PathsPerBee]
    computeStats(stats, bees, args.outDir)

if __name__ == '__main__':
    import cProfile
    cProfile.run('main()')
