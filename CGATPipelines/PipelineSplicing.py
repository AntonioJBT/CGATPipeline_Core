#########################################################################
#
#   MRC FGU Computational Genomics Group
#
#   $Id: cgat_script_template.py 2871 2010-03-03 10:20:44Z andreas $
#
#   Copyright (C) 2009 Andreas Heger
#
#   This program is free software; you can redistribute it and/or
#   modify it under the terms of the GNU General Public License
#   as published by the Free Software Foundation; either version 2
#   of the License, or (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
##########################################################################
'''
PipelineSplicing.py - wrap various differential expression tools
===========================================================

:Author: Andreas Heger
:Release: $Id$
:Date: |today|
:Tags: Python

Purpose
-------

This module provides tools for differential splicing analysis
for a variety of methods.

Methods implemented are:

   DEXSeq
   rMATS

The aim of this module is to run these individual tools and
output a table in a common format.

Usage
-----

Documentation
-------------

Requirements:

* DEXSeq >= ?
* rMATS >= ?



'''

import sys
import rpy2
import re
from rpy2.robjects import r as R
import rpy2.robjects as ro
from rpy2.robjects import pandas2ri
from rpy2.robjects.packages import importr
from rpy2.robjects.vectors import FloatVector
from ruffus import *
import os
import glob
import sqlite3
import CGAT.BamTools as BamTools
import CGAT.Experiment as E
import CGAT.Counts as Counts
import CGAT.Expression as Expression
import CGATPipelines.Pipeline as P
import CGATPipelines.PipelineTracks as PipelineTracks


class Splicer(object):
    ''' base clase for DS experiments '''

    def __init__(self, gtf=None, executable=None):
        if gtf:
            self.gtf = gtf
        if executable:
            self.executable = executable

    def __call__(self):
        ''' call DS and generate an initial results table '''
        self.callDifferentialSplicing()

    def splicer(self, outfile):
        ''' Custom DS functions '''
        return ""

    def visualise(self, outfile):
        ''' Visualise results using plots'''
        return ""

    def cleanup(self, outfile):
        ''' Visualise results using plots'''
        return ""

    def build(self, outfile):
        '''run mapper

        This method combines the output of the :meth:`preprocess`,
        :meth:`mapper`, :meth:`postprocess` and :meth:`clean` sections
        into a single statement.

        Arguments
        ---------
        infiles : list
             List of input filenames
        outfile : string
             Output filename

        Returns
        -------
        statement : string
             A command line statement. The statement can be a series
             of commands separated by ``;`` and/or can be unix pipes.

        '''
        cmd_splicer = self.splicer(outfile)
        cmd_visualise = self.visualise(outfile)
        cmd_clean = self.cleanup(outfile)

        assert cmd_splicer.strip().endswith(";"),\
            "missing ';' at end of command %s" % cmd_splicer.strip()
        if cmd_visualise:
            assert cmd_visualise.strip().endswith(";"),\
                "missing ';' at end of command %s" % cmd_visualise.strip()
        if cmd_clean:
            assert cmd_clean.strip().endswith(";"),\
                "missing ';' at end of command %s" % cmd_clean.strip()

        statement = " checkpoint; ".join((cmd_splicer,
                                          cmd_visualise,
                                          cmd_clean))

        return statement


class rMATS(Splicer):
    '''DEExperiment object to generate differential splicing events
       using rMATS
    '''

    def __init__(self, design, pvalue=0.05,
                 *args, **kwargs):
        Splicer.__init__(self, *args, **kwargs)
        self.pvalue = pvalue
        self.design = Expression.ExperimentalDesign(design)

    def splicer(self, outfile):
        design = self.design
        group1 = ",".join(
            ["%s.bam" % x for x in design.getSamplesInGroup(design.groups[0])])
        group2 = ",".join(
            ["%s.bam" % x for x in design.getSamplesInGroup(design.groups[1])])
        readlength = BamTools.estimateTagSize(design.samples[0]+".bam")
        pvalue = self.pvalue
        gtf = self.gtf

        statement = '''rMATS
        -b1 %(group1)s
        -b2 %(group2)s
        -gtf %(gtf)s
        -o %(outfile)s
        -len %(readlength)s
        -c %(pvalue)s
        ''' % locals()

        # Specify paired design
        if design.has_pairs:
            statement += "-analysis P "

        # Get Insert Size Statistics if Paired End Reads
        if BamTools.isPaired(design.samples[0]+".bam"):
            inserts1 = [BamTools.estimateInsertSizeDistribution(sample+".bam", 10000)
                        for sample in design.getSamplesInGroup(design.groups[0])]
            inserts2 = [BamTools.estimateInsertSizeDistribution(sample+".bam", 10000)
                        for sample in design.getSamplesInGroup(design.groups[1])]
            r1 = ",".join(map(str, [item[0] for item in inserts1]))
            sd1 = ",".join(map(str, [item[1] for item in inserts1]))
            r2 = ",".join(map(str, [item[0] for item in inserts2]))
            sd2 = ",".join(map(str, [item[1] for item in inserts2]))

            statement += '''-t paired
            -r1 %(r1)s -r2 %(r2)s
            -sd1 %(sd1)s -sd2 %(sd2)s''' % locals()

        statement += "; "

        return statement

    def visualise(self, outfile):

        Design = self.design
        if len(Design.groups) != 2:
            raise ValueError("Please specify exactly 2 groups per experiment.")

        g1 = Design.getSamplesInGroup(Design.groups[0])
        g2 = Design.getSamplesInGroup(Design.groups[1])

        if len(g1) != len(g2):
            g1 = g1[:min(len(g1), len(g2))]
            g2 = g2[:min(len(g1), len(g2))]
            E.info("The two groups compared were of unequal size. For  " +
                   "visual display using sashimi they have been truncated " +
                   "to the same length")

        group1 = ",".join(["%s.bam" % x for x in g1])
        group2 = ",".join(["%s.bam" % x for x in g2])
        group1name = Design.groups[0]
        group2name = Design.groups[1]
        gtffile = self.gtf
        outfile2 = outfile + "/sashimi"
        if not os.path.exists(outfile):
            os.makedirs(outfile)

        statement = ""
        splice_events = ["SE", "A5SS", "A3SS", "MXE", "RI"]

        for event in splice_events:
            results = outfile + "/MATS_output/%s.MATS.JunctionCountOnly.txt"\
                      % event
            statement += '''rmats2sashimiplot
            -b1 %(group1)s
            -b2 %(group2)s
            -t %(event)s
            -e %(results)s
            -l1 %(group1name)s
            -l2 %(group2name)s
            -o %(outfile2)s; checkpoint;
            ''' % locals()

        return statement

    def cleanup(self, outfile):
        statement = ""
        return statement


class DEXSeq(Splicer):
    '''DEExperiment object to generate differential splicing events
       using DEXSeq
    '''

    def __init__(self, design, countsdir, model=None, *args, **kwargs):
        Splicer.__init__(self, *args, **kwargs)
        self.countsdir = os.path.abspath(countsdir)
        self.model = model
        self.design = design

    def splicer(self, outfile):
        design = self.design
        countsdir = self.countsdir
        model = self.model
        gff = self.gtf
        dexseq_fdr = 0.05

        statement = '''
        python %%(scriptsdir)s/counts2table.py
        --design-tsv-file=%(design)s
        --output-filename-pattern=%(outfile)s/
        --log=%(outfile)s/DEXSeq.log
        --method=dexseq
        --fdr=%(dexseq_fdr)s
        --model=%(model)s
        --dexseq-counts-dir=%(countsdir)s
        --dexseq-flattened-file=%(gff)s;
        ''' % locals()

        return statement
