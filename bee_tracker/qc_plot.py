#!/usr/bin/python

import collections
import math
import os.path

import matplotlib.pyplot
import numpy
import pandas


class PlotRange:

    def __init__(self, min, max):
        self.min = min
        self.max = max

    def update(self, array):
        self.min = min(self.min, array.min())
        self.max = max(self.max, array.max())

    def updateWithPercentile(self, array, minPercentile, maxPercentile):
        self.min = min(self.min, numpy.percentile(array, minPercentile))
        self.max = max(self.max, numpy.percentile(array, maxPercentile))

    def asTuple(self):
        return (self.min, self.max)

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

class IndexHTML(QCPlots):
    '''Simple class to generate an index with links to the the other QC files
    '''

    def __init__(self, qcStatistic, directories, outDir):
        QCPlots.__init__(self, qcStatistic, directories, outDir)

    def addPlotsLink(self, qcPlots, handle):
        '''Adds a link to an html page with a set of plots
        '''
        href = qcPlots.htmlPath
        txt  = qcPlots.qcStatistic.description
        handle.write('<a href="%s">%s</a>\n' % (href, txt))
        handle.write('<br/>\n')

class CountDataWithLabels:

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
        self.ranges = {}
        self.data   = collections.defaultdict(CountDataWithLabels)
        categories  = {}
        for directory in self.directories:
            path   = os.path.join(directory, self.qcStatistic.getOutputFileName())
            df     = pandas.read_csv(path)
            folder = os.path.basename(directory)
            label  = folder.replace('.csv', '')
            for cat, catDf in df.groupby('category'):
                data            = catDf.counts.values
                self.data[cat].data.append(data)
                self.data[cat].labels.append(label)
                self.data[cat].dirs.append(folder)
                if not cat in self.ranges:
                    self.ranges[cat] = PlotRange(numpy.Inf, 0)
                self.ranges[cat].updateWithPercentile(data, 1, 99)
                categories[cat] = 1
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
            ##### WARNING This is a hack because the violin plot does seem
            ##### to work on the log scale when the scale is set with  yscale.
            data = self.data[cat].data
            if len(data) < 2:
                continue
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
            if self.logScale:
                matplotlib.pyplot.ylabel('$log_{10}$(counts)')
            else:
                matplotlib.pyplot.ylim(self.ranges[cat].min,
                                       self.ranges[cat].max)
            matplotlib.pyplot.savefig(out)
            matplotlib.pyplot.close()

    def makeBoxPlotsHTML(self, handle):
        '''Very basic HTML code around the box plots
        '''
        handle.write('<br/>\n')
        for cat in self.categories:
            handle.write('<h2>Category: %d</h2>\n' % cat)
            img = '%s.boxplot.%d.png' % (self.qcStatistic.name, cat)
            handle.write('<img src="%s"/>\n' % img)
        handle.write('<br/>\n')

    def makeViolinPlotsHTML(self, handle):
        '''Very basic HTML code around the violin plots
        '''
        handle.write('<br/>\n')
        for cat in self.categories:
            handle.write('<h2>Category: %d</h2>\n' % cat)
            img  = '%s.violinplot.%d.png' % (self.qcStatistic.name, cat)
            path = os.path.join(self.outDir, img)
            if os.path.exists(path):
                handle.write('<img src="%s"/>\n' % img)
            else:
                handle.write('<p>Not enough data</p>\n')
        handle.write('<br/>\n')

    def makeHistograms(self):
        '''Makes individual histograms for each category and each recording.
        '''
        for cat in self.categories:
            for i in range(len(self.data[cat].data)):
                data   = self.data[cat].data[i]
                folder = self.data[cat].dirs[i]
                matplotlib.pyplot.figure()
                matplotlib.pyplot.hist(data,
                                       bins=20,
                                       range=self.ranges[cat].asTuple(),
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
                    src = os.path.join(baseDir, img)
                    handle.write('    <td><img src="%s" class="tableImg"/></td>\n' % src)
                else:
                    handle.write('    <td>no data</td>\n')
            handle.write('  </tr>\n')
        handle.write('</table>\n')

    def makePlots(self):
        '''Makes all the plots and the associated HTML
        '''
        self.prepare()
        # Create the output directory if it does not exist
        if not os.path.exists(self.outDir):
            os.makedirs(outDir)
        with open(self.htmlPath, "w") as handle:
            self.writeHTMLHeader(handle)
            self.makeBoxPlots()
            self.makeBoxPlotsHTML(handle)
            self.makeViolinPlots()
            self.makeViolinPlotsHTML(handle)
            self.makeHistograms()
            self.makeHistogramsHTML(handle)
            self.writeHTMLFooter(handle)

class ClassificationData:

    def __init__(self,
                 directory,
                 total,
                 totalKnown,
                 totalKnownProp,
                 maxKnownProp,
                 knownCat):
        self.directory      = directory
        self.total          = total
        self.totalKnown     = totalKnown
        self.totalKnownProp = totalKnownProp
        self.maxKnownProp   = maxKnownProp
        self.knownCat       = knownCat

class ClassificationPlots(QCPlots):

    def __init__(self, qcStatistic, directories, outDir, minCount=0):
        QCPlots.__init__(self, qcStatistic, directories, outDir)
        self.minCount = minCount

    def prepare(self):
        '''Compute the ranges of plots for each category accross all recordings
        and lists all the categories.
        '''
        # Load data and compute ranges
        categories               = {}
        self.data                = []
        for directory in self.directories:
            path   = os.path.join(directory, self.qcStatistic.getOutputFileName())
            df     = pandas.read_csv(path)
            cats   = list(df)
            ### WARNING: strong assumption that column 0 contains the unknown tags
            for cat in cats:
                categories[cat] = 1
            matrix          = df.as_matrix()
            total           = matrix.sum(axis=1)
            if self.minCount > 0:
                matrix = matrix[total > self.minCount]
                total  = matrix.sum(axis=1)
            knownMatrix     = matrix[:,1:]
            knownCat        = knownMatrix.argmax(axis=1)
            maxKnown        = knownMatrix[range(len(matrix)), knownCat]
            totalKnown      = knownMatrix.sum(axis=1)
            maxKnownProp    = maxKnown / totalKnown
            totalKnownProp  = totalKnown / total
            data            = ClassificationData(os.path.basename(directory),
                                                 total,
                                                 totalKnown,
                                                 totalKnownProp,
                                                 maxKnownProp,
                                                 knownCat + 1)
            self.data.append(data)
        self.categories  = [int(x) for x in categories.keys()]
        self.categories.sort()

    def plotTotalKnownProp(self):
        for data in self.data:
            matplotlib.pyplot.figure()
            matplotlib.pyplot.hexbin(data.total,
                                     data.totalKnownProp,
                                     xscale='log',
                                     marginals=False,
                                     gridsize=20,
                                     bins='log')
            cb = matplotlib.pyplot.colorbar()
            cb.set_label('lo10(counts)')
            img = '%s.totalKnownProp.png' % (self.qcStatistic.name)
            out = os.path.join(self.outDir,
                               data.directory,
                               img)
            matplotlib.pyplot.savefig(out)
            matplotlib.pyplot.close()

    def plotMaxKnownProp(self):

        def plotHexBin(x, y, directory, img):
            matplotlib.pyplot.figure()
            matplotlib.pyplot.hexbin(x,
                                     y,
                                     xscale='log',
                                     marginals=False,
                                     gridsize=20,
                                     bins='log')
            cb  = matplotlib.pyplot.colorbar()
            cb.set_label('lo10(counts)')
            out = os.path.join(self.outDir,
                               directory,
                               img)
            matplotlib.pyplot.savefig(out)
            matplotlib.pyplot.close()

        for data in self.data:
            img = '%s.maxKnownProp.png' % (self.qcStatistic.name)
            plotHexBin(data.totalKnown,
                       data.maxKnownProp,
                       data.directory,
                       img)
            for cat in self.categories[1:]:
                img   = '%s.maxKnownProp.%d.png' % (self.qcStatistic.name, cat)
                where = (data.knownCat == cat) & (data.totalKnown > 0)
                totalKnownCat = data.totalKnown[where]
                if len(totalKnownCat) > 0:
                    plotHexBin(totalKnownCat,
                               data.maxKnownProp[where],
                               data.directory,
                               img)

    def writePropTableHTML(self, handle):
        handle.write('<table>\n')
        handle.write('  <tr>\n')
        handle.write('    <th>Source</th>\n')
        handle.write('    <th>% Kown categories</th>\n')
        handle.write('    <th>Max cat. % (all cat.)</th>\n')
        for cat in self.categories[1:]:
            handle.write('    <th>Max cat. %% (cat. %d)</th>\n' % cat)
        handle.write('  <tr>\n')
        for data in self.data:
            handle.write('  <tr>\n')
            handle.write('    <td>%s</td>\n' % data.directory)
            img = '%s.totalKnownProp.png' % (self.qcStatistic.name)
            src = os.path.join(data.directory, img)
            handle.write('    <td><img src="%s" class="tableImg"/></td>\n' % src)
            img = '%s.maxKnownProp.png' % (self.qcStatistic.name)
            src = os.path.join(data.directory, img)
            handle.write('    <td><img src="%s" class="tableImg"/></td>\n' % src)
            for cat in self.categories[1:]:
                img  = '%s.maxKnownProp.%d.png' % (self.qcStatistic.name, cat)
                path = os.path.join(self.outDir, data.directory, img)
                if os.path.exists(path):
                    src = os.path.join(data.directory, img)
                    handle.write('    <td><img src="%s" class="tableImg"/></td>\n' % src)
                else:
                    handle.write('    <td>No data</td>\n')
            handle.write('  </tr>\n')
        handle.write('</table>\n')

    def makePlots(self):
        '''Makes all the plots and the associated HTML
        '''
        self.prepare()
        # Create the output directory if it does not exist
        if not os.path.exists(self.outDir):
            os.makedirs(outDir)
        with open(self.htmlPath, "w") as handle:
            self.writeHTMLHeader(handle)
            self.plotTotalKnownProp()
            self.plotMaxKnownProp()
            self.writePropTableHTML(handle)
            self.writeHTMLFooter(handle)
