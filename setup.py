#!/usr/bin/env python

import glob

from distutils.core import setup

scripts=glob.glob('bin/*')

setup(name='Distutils',
      version='0.0.1',
      description='Bee tracking utilities',
      author='Sylvain FORET',
      author_email='sylvain.foret@anu.edu.au',
      url='http://dna.anu.edu.au',
      packages=['bee_tracker'],
      scripts=scripts)
