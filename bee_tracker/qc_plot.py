#!/usr/bin/python

import collections
import math
import os.path
import sys

import matplotlib.pyplot
import numpy
import pandas

import bee_tracker.qc_stats


class QCPlots:
    '''The parent class for all the classes that plot QC statistics
    '''

    def __init__(self, qcStatistic, directories, outDir):
        self.qcStatistic = qcStatistic
        self.directories = directories
        self.outDir      = outDir
        self.htmlPath    = os.path.join(self.outDir,
                                        self.qcStatistic.name + '.html')

    def makePlots(self):
        raise Exception('Not implemented')

    def writeHTMLHeader(self, handle):
        header = '''<html>
        <head>
            <title>%s</title>
            <style>
                table, th, td {text-align: center;
                               border: 1px solid grey;}
                .tableImg {max-width: 100%%;}
            </style>
        </head>
        <body>\n''' % self.qcStatistic.description
        handle.write(header)
        handle.write('<h1>%s</h1>\n<br/>\n' % self.qcStatistic.description)

    def writeHTMLFooter(self, handle):
        footer = '''</body>
        </html>\n'''
        handle.write(footer)

class DataWithLabels:

    def __init__(self):
        self.data   = []
        self.labels = []
        self.dirs   = []

class CountsPerCategoryPlots(QCPlots):
    '''Class that can be used to plot any data made of counts per category
    '''

    def __init__(self, qcStatistic, directories, outDir, logScale=False):
        QCPlots.__init__(self, qcStatistic, directories, outDir)
        self.logScale = logScale

    def prepare(self):
        '''Compute the ranges of plots for each category accross all recordings
        and lists all the categories.
        '''
        # Load data and compute ranges
        self.maxVals = collections.defaultdict(int)
        self.minVals = collections.defaultdict(int)
        self.data    = collections.defaultdict(DataWithLabels)
        categories   = {}
        for directory in self.directories:
            path   = os.path.join(directory, self.qcStatistic.getOutputFileName())
            df     = pandas.read_csv(path)
            folder = os.path.basename(directory)
            label  = folder.replace('.csv', '')
            for cat, catDf in df.groupby('category'):
                data                  = catDf.counts.values
                self.data[cat].data.append(data)
                self.data[cat].labels.append(label)
                self.data[cat].dirs.append(folder)
                maxVal                = numpy.percentile(data, 99)
                maxVal                = max(maxVal, self.maxVals[cat])
                self.maxVals[cat]     = maxVal
                minVal                = numpy.percentile(data, 1)
                minVal                = min(minVal, self.minVals[cat])
                self.minVals[cat]     = minVal
                categories[cat]       = 1
        # Categories
        self.categories = list(categories.keys())
        self.categories.sort()

    def makeBoxPlots(self):
        '''Makes box plots plots showing the distribution of the data for each
        recording.
        The full range of the data is shown
        '''
        for cat in self.categories:
            # Box plots
            img    = '%s.boxplot.%d.png' % (self.qcStatistic.name, cat)
            out    = os.path.join(self.outDir, img)
            size   = (6, 4)
            if len(self.directories) > 20:
                size = (len(self.directories) * 0.4, 4)
            matplotlib.pyplot.figure(figsize=size)
            matplotlib.pyplot.boxplot(self.data[cat].data)
            if self.logScale:
                matplotlib.pyplot.yscale('log')
            matplotlib.pyplot.xticks(list(range(1, len(self.data[cat].labels) + 1)),
                                     self.data[cat].labels,
                                     rotation='vertical')
            matplotlib.pyplot.savefig(out)
            matplotlib.pyplot.close()

    def makeViolinPlots(self):
        '''Makes violin plots plots showing the distribution of the data for
        each recording.
        Only the 1-99 percentile range is shown.
        '''
        for cat in self.categories:
            img  = '%s.violinplot.%d.png' % (self.qcStatistic.name, cat)
            out  = os.path.join(self.outDir, img)
            size = (6, 4)
            if len(self.directories) > 20:
                size = (len(self.directories) * 0.4, 4)
            matplotlib.pyplot.figure(figsize=size)
            try:
                ##### WARNING This is a hack because the violin plot does seem
                ##### to work on the log scale when the scale is set with  yscale.
                data = self.data[cat].data
                if self.logScale:
                    data = [numpy.log10(x) for x in self.data[cat].data]
                matplotlib.pyplot.violinplot(data,
                                             showmeans=False,
                                             showextrema=False,
                                             showmedians=True,
                                             widths=0.9,
                                             bw_method=0.20)
                matplotlib.pyplot.xticks(list(range(1, len(self.data[cat].labels) + 1)),
                                         self.data[cat].labels,
                                         rotation='vertical')
                if not self.logScale:
                    matplotlib.pyplot.ylim(self.minVals[cat],
                                           self.maxVals[cat])
            except Exception as e:
                sys.stderr.write('[Warning] Failed to plot violin plot for category %d: %s\n' % (cat, str(e)))
            matplotlib.pyplot.savefig(out)
            matplotlib.pyplot.close()

    def makeBoxPlotsHTML(self, handle):
        '''Very basic HTML code around the box plots
        '''
        handle.write('<br/>')
        for cat in self.categories:
            handle.write('<h2>Category: %d<h2/>\n' % cat)
            img = '%s.boxplot.%d.png' % (self.qcStatistic.name, cat)
            handle.write('<img src="%s"/>\n' % img)
        handle.write('<br/>')

    def makeViolinPlotsHTML(self, handle):
        '''Very basic HTML code around the violin plots
        '''
        handle.write('<br/>')
        for cat in self.categories:
            handle.write('<h2>Category: %d<h2/>\n' % cat)
            img = '%s.violinplot.%d.png' % (self.qcStatistic.name, cat)
            handle.write('<img src="%s"/>\n' % img)
        handle.write('<br/>')

    def makeHistograms(self):
        '''Makes individual histograms for each category and each recording.
        '''
        for cat in self.categories:
            minx = self.minVals[cat]
            maxx = self.maxVals[cat]
            for i in range(len(self.data[cat].data)):
                data   = self.data[cat].data[i]
                folder = self.data[cat].dirs[i]
                matplotlib.pyplot.figure()
                matplotlib.pyplot.hist(data,
                                       bins=20,
                                       range=(minx, maxx),
                                       log=self.logScale)
                img = '%s.hists.%d.png' % (self.qcStatistic.name, cat)
                out = os.path.join(self.outDir, folder, img)
                matplotlib.pyplot.savefig(out)
                matplotlib.pyplot.close()

    def makeHistogramsHTML(self, handle):
        '''HTML code for the table with the individual histograms
        '''
        handle.write('<table>\n')

        handle.write('<tr>\n')
        handle.write('<th>Category</th>\n')
        for cat in self.categories:
            handle.write('<th>%d</th>\n' % cat)
        handle.write('</tr>\n')

        handle.write('<tr>\n')
        handle.write('<th>Source</th>\n')
        for cat in self.categories:
            handle.write('<td></td>\n')
        handle.write('</tr>\n')

        for directory in self.directories:
            handle.write('  <tr>\n')
            handle.write('    <td>%s</td>\n' % os.path.basename(directory))
            baseDir = os.path.basename(directory)
            subDir  = os.path.join(self.outDir, baseDir)
            for cat in self.categories:
                img  = '%s.hists.%d.png' % (self.qcStatistic.name, cat)
                path = os.path.join(subDir, img)
                if os.path.exists(path):
                    relPath = os.path.join(baseDir, img)
                    handle.write('    <td><img src="%s" class="tableImg"/></td>\n' % relPath)
                else:
                    handle.write('    <td>no data</td>\n')
            handle.write('  </tr>\n')
        handle.write('</table>\n')

    def makePlots(self):
        '''Makes all the plots and the associated HTML
        '''
        # Create the output directory if it does not exist
        if not os.path.exists(self.outDir):
            os.makedirs(outDir)
        with open(self.htmlPath, "w") as handle:
            self.prepare()
            self.writeHTMLHeader(handle)
            self.makeBoxPlots()
            self.makeBoxPlotsHTML(handle)
            self.makeViolinPlots()
            self.makeViolinPlotsHTML(handle)
            self.makeHistograms()
            self.makeHistogramsHTML(handle)
            self.writeHTMLFooter(handle)
