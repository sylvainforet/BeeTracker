#!/usr/bin/python

import argparse
import multiprocessing
import os.path
import sys

import matplotlib
matplotlib.use('Agg')
import pandas

import bee_tracker.io_csv
import bee_tracker.qc_plot
import bee_tracker.qc_stats


class StatsWorker:

    def __init__(self, args):
        self.args = args

    def work(self, path):
        stats  = [bee_tracker.qc_stats.BeesPerFrame,
                  bee_tracker.qc_stats.FramesPerBee,
                  bee_tracker.qc_stats.FramesPerPath,
                  bee_tracker.qc_stats.FramesBetweenPaths,
                  bee_tracker.qc_stats.PathsPerBee,
                  bee_tracker.qc_stats.Classification]
        name   = os.path.basename(path)
        outDir = os.path.join(args.outDir, name)
        if not os.path.exists(outDir):
            os.makedirs(outDir)
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
    parser.add_argument('-l',
                        '--noPlot',
                        action='store_true',
                        help='Do not plot, only compute the data')
    parser.add_argument('-a',
                        '--noData',
                        action='store_true',
                        help='Dont compute the data, only plot')
    args = parser.parse_args()
    return args

def computeData(args):
    worker = StatsWorker(args)
    if args.processes < 1:
        for path in args.input:
            worker.work(path)
    else:
        pool = multiprocessing.Pool(processes=args.processes)
        pool.map(worker.work, args.input, chunksize=1)

def makePlots(args):

    def dirKey(key):
        return int(key.replace('.csv', ''))

    basenames   = [os.path.basename(x) for x in args.input]
    basenames   = sorted(basenames, key=dirKey)
    directories = [os.path.join(args.outDir, x) for x in basenames]
    index       = bee_tracker.qc_plot.IndexHTML(bee_tracker.qc_stats.QCStatistic,
                                                directories,
                                                args.outDir)
    path        = os.path.join(args.outDir, 'index.html')
    with open(path, "w") as handle:
        index.writeHTMLHeader(handle)
        p = bee_tracker.qc_plot.CountsPerCategoryPlots(bee_tracker.qc_stats.BeesPerFrame,
                                                       directories,
                                                       args.outDir,
                                                       logScale=False)
        p.makePlots()
        index.addPlotsLink(p, handle)
        p = bee_tracker.qc_plot.CountsPerCategoryPlots(bee_tracker.qc_stats.FramesPerBee,
                                                       directories,
                                                       args.outDir,
                                                       logScale=True)
        p.makePlots()
        index.addPlotsLink(p, handle)
        p = bee_tracker.qc_plot.CountsPerCategoryPlots(bee_tracker.qc_stats.FramesPerPath,
                                                       directories,
                                                       args.outDir,
                                                       logScale=True)
        p.makePlots()
        index.addPlotsLink(p, handle)
        p = bee_tracker.qc_plot.CountsPerCategoryPlots(bee_tracker.qc_stats.FramesBetweenPaths,
                                                       directories,
                                                       args.outDir,
                                                       logScale=False)
        p.makePlots()
        index.addPlotsLink(p, handle)
        p = bee_tracker.qc_plot.CountsPerCategoryPlots(bee_tracker.qc_stats.PathsPerBee,
                                                       directories,
                                                       args.outDir,
                                                       logScale=False)
        p.makePlots()
        index.addPlotsLink(p, handle)
        p = bee_tracker.qc_plot.ClassificationPlots(bee_tracker.qc_stats.Classification,
                                                    directories,
                                                    args.outDir,
                                                    minCount=10)
        p.makePlots()
        index.addPlotsLink(p, handle)
        index.writeHTMLFooter(handle)

def main(args):
    if not args.noData:
        computeData(args)
    if not args.noPlot:
        makePlots(args)

if __name__ == '__main__':
    args  = parseArgs()
    if args.profile:
        import cProfile
        cProfile.run('main(args)')
    else:
        main(args)
