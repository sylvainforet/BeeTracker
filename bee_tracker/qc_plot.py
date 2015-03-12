#!/usr/bin/python

import collections
import os.path

import matplotlib.pyplot
import pandas

import bee_tracker.qc_stats


class QCPlots:

    def __init__(self, directories, outDir):
        self.directories = directories
        self.outDir      = outDir
        self.title       = 'QCPlots'

    def makePlots(self):
        raise Exception('Not implemented')

    def writeHTMLHeader(self, handle):
        header = '''<html>
        <head>
            <title>%s</title>
        </head>
        <body>\n''' % self.title
        handle.write(header)

    def writeHTMLFooter(self, handle):
        footer = '''</body>
        </html>\n'''
        handle.write(footer)

class BeesPerFramePlots(QCPlots):

    def __init__(self, directories, outDir):
        QCPlots.__init__(self, directories, outDir)
        self.title    = 'Bees Per Frame'
        self.basename = bee_tracker.qc_stats.BeesPerFrame.getOutputFileName()

    def computeRange(self):
        self.maxVals    = collections.defaultdict(int)
        self.minVals    = collections.defaultdict(int)
        self.categories = {}
        for directory in self.directories:
            path = os.path.join(directory, self.basename)
            df   = pandas.read_csv(path)
            cats = df.category.unique()
            for cat in cats:
                maxVal               = df.counts[df.category == cat].max()
                maxVal               = max(maxVal, self.maxVals[cat])
                self.maxVals[cat]    = maxVal
                minVal               = df.counts[df.category == cat].min()
                minVal               = min(minVal, self.minVals[cat])
                self.minVals[cat]    = minVal
                self.categories[cat] = 1
        self.categories = list(self.categories)
        self.categories.sort()

    def makeHistogramPerCategoryPlot(self):
        for directory in self.directories:
            path    = os.path.join(directory, self.basename)
            df      = pandas.read_csv(path)
            cats    = df.category.unique()
            baseDir = os.path.basename(directory)
            subDir  = os.path.join(self.outDir, baseDir)
            if not os.path.exists(subDir):
                os.makedirs(subDir)
            for cat, catDf in df.groupby('category'):
                matplotlib.pyplot.figure()
                catDf.counts.hist(bins=20, range=(self.minVals[cat], self.maxVals[cat]))
                out = os.path.join(subDir, '%s.%d.png' % (self.basename, cat))
                matplotlib.pyplot.savefig(out)

    def makeHistogramPerCategoryHTML(self):
        path = os.path.join(self.outDir, 'bees_per_frame.html')
        with open(path, "w") as handle:
            self.writeHTMLHeader(handle)
            handle.write('<table>\n')
            handle.write('<tr>\n')
            for cat in self.categories:
                handle.write('<td>%s</td>\n' % str(cat))
            handle.write('</tr>\n')
            for directory in self.directories:
                handle.write('  <tr>\n')
                baseDir = os.path.basename(directory)
                for cat in self.categories:
                    img  = os.path.join(baseDir, '%s.%d.png' % (self.basename, cat))
                    handle.write('    <td><img src="%s"/></td>\n' % img)
                handle.write('  </tr>\n')
            handle.write('</table>\n')
            self.writeHTMLFooter(handle)

    def makePlots(self):
        self.computeRange()
        self.makeHistogramPerCategoryPlot()
        self.makeHistogramPerCategoryHTML()
