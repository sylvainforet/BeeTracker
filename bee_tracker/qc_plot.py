#!/usr/bin/python

import collections
import os.path
import sys

import matplotlib.pyplot
import numpy
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
            <style>
                table, th, td {text-align: center;
                               border: 1px solid grey;}
                .tableImg {max-width: 100%%;}
            </style>
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
        self.title      = 'Bees Per Frame'
        self.basename   = bee_tracker.qc_stats.BeesPerFrame.getOutputFileName()
        self.htmlPath   = os.path.join(self.outDir, 'bees_per_frame.html')

    def prepare(self):
        '''Compute the ranges of plots for each category accross all recordings.
        Lists all categories
        '''
        # Ranges
        self.maxVals    = collections.defaultdict(int)
        self.minVals    = collections.defaultdict(int)
        self.categories = {}
        for directory in self.directories:
            path = os.path.join(directory, self.basename)
            df   = pandas.read_csv(path)
            cats = df.category.unique()
            for cat in cats:
                maxVal               = numpy.percentile(df.counts[df.category == cat], 99)
                maxVal               = max(maxVal, self.maxVals[cat])
                self.maxVals[cat]    = maxVal
                minVal               = df.counts[df.category == cat].min()
                minVal               = numpy.percentile(df.counts[df.category == cat], 1)
                minVal               = min(minVal, self.minVals[cat])
                self.minVals[cat]    = minVal
                self.categories[cat] = 1
        # Categories
        self.categories = list(self.categories)
        self.categories.sort()

    def writeHTMLHeader(self, handle):
        QCPlots.writeHTMLHeader(self, handle)
        handle.write('<h1>Bees per Frame</h1>\n<br/>\n')

    def makeBoxPlots(self):
        '''Makes box plots and violin plots reflexing the distribution of the
        data for each recording.
        The box plots represent the whole range, while the violin plots are
        restricted to the 1-99 percentiles.
        '''
        dfs = {}
        for cat in self.categories:
            dfs[cat] = []
        for directory in self.directories:
            path    = os.path.join(directory, self.basename)
            df      = pandas.read_csv(path)
            cats    = df.category.unique()
            baseDir = os.path.basename(directory)
            for cat, catDf in df.groupby('category'):
                newDict = {'source': baseDir,
                           'counts': catDf.counts}
                newDf   = pandas.DataFrame(newDict)
                dfs[cat].append(newDf)
        if not os.path.exists(self.outDir):
            os.makedirs(outDir)
        for cat in self.categories:
            df     = pandas.concat(dfs[cat])
            miny   = numpy.percentile(df.counts.values, 1)
            maxy   = numpy.percentile(df.counts.values, 99)
            gb     = df.groupby('source', sort=False)
            data   = [x[1].counts.values for x in gb]
            labels = [x[0].replace('.csv', '') for x in gb]

            out    = os.path.join(self.outDir, '%s.boxplot.%d.png' % (self.basename, cat))
            size   = (6, 4)
            if len(self.directories) > 20:
                size = (len(self.directories) * 0.4, 4)
            fig    = matplotlib.pyplot.figure(figsize=size)
            matplotlib.pyplot.boxplot(data)
            matplotlib.pyplot.xticks(list(range(1, len(self.directories) + 1)),
                                     labels, rotation='vertical')
            #matplotlib.pyplot.ylim(miny, maxy)
            matplotlib.pyplot.savefig(out)
            matplotlib.pyplot.close()

            out    = os.path.join(self.outDir, '%s.violinplot.%d.png' % (self.basename, cat))
            size   = (6, 4)
            if len(self.directories) > 20:
                size = (len(self.directories) * 0.4, 4)
            fig    = matplotlib.pyplot.figure(figsize=size)
            try:
                matplotlib.pyplot.violinplot(data,
                                             showmeans=False,
                                             showextrema=False,
                                             showmedians=True,
                                             widths=0.9,
                                             bw_method=0.20)
                matplotlib.pyplot.xticks(list(range(1, len(self.directories) + 1)),
                                         labels, rotation='vertical')
                matplotlib.pyplot.ylim(miny, maxy)
            except:
                sys.stderr.write('[Warning] Could not plot violin plot for category %d\n' % cat)
            matplotlib.pyplot.savefig(out)
            matplotlib.pyplot.close()

    def makeBoxPlotsHTML(self, handle):
        '''Very basic HTML code around the box plots / violinplots
        '''
        handle.write('<br/>')
        for cat in self.categories:
            handle.write('<h2>Category: %d<h2/>\n' % cat)
            img = '%s.boxplot.%d.png' % (self.basename, cat)
            handle.write('<img src="%s"/>\n' % img)
        handle.write('<br/>')
        for cat in self.categories:
            handle.write('<h2>Category: %d<h2/>\n' % cat)
            img = '%s.violinplot.%d.png' % (self.basename, cat)
            handle.write('<img src="%s"/>\n' % img)
        handle.write('<br/>')

    def makeHistograms(self):
        '''Makes individual histograms for each category and each recording.
        '''
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
                out = os.path.join(subDir, '%s.hists.%d.png' % (self.basename, cat))
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
                relPath = os.path.join(subDir, '%s.hists.%d.png' % (self.basename, cat))
                if os.path.exists(relPath):
                    img = os.path.join(baseDir, '%s.hists.%d.png' % (self.basename, cat))
                    handle.write('    <td><img src="%s" class="tableImg"/></td>\n' % img)
                else:
                    handle.write('    <td>no data</td>\n')
            handle.write('  </tr>\n')
        handle.write('</table>\n')

    def makePlots(self):
        '''Makes all the plots of the number of bees per frame
        '''
        with open(self.htmlPath, "w") as handle:
            self.prepare()
            self.writeHTMLHeader(handle)
            self.makeBoxPlots()
            self.makeBoxPlotsHTML(handle)
            self.makeHistograms()
            self.makeHistogramsHTML(handle)
            self.writeHTMLFooter(handle)
