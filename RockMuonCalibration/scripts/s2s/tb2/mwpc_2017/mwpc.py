#
# This master class for mwpc
#
#
#
# Jeffrey Kleykamp
# 11/6/2015
#
import eventloop

import ROOT
import collections
import datetime
import os
import traceback
import array
import math
import itertools
import pprint

batch=True
if batch: ROOT.gROOT.SetBatch()



INSERTFAKEHITSFORTESTING = False



LOGLEVEL = 1


USE_ERRORS_FOR_TRACK = True






class logging(object):
    @staticmethod
    def debug(*args):
        logging.log(10, *args)
    @staticmethod
    def info(*args):
        logging.log(20, *args)
    @staticmethod
    def error(*args):
        logging.log(30, *args)
    @staticmethod
    def log(level, *args):
        if level > LOGLEVEL:
            for log in args:
                print log,
            print



              
     
    

        
def main(filename=None, ttree_filename=None, file_mode="RECREATE", tree_name="mwpc", nmax=None):
    if filename is None:
        #filename = "/minerva/data/testbeam2/rawdata/unknown/raw/cosmc/00/00/08/88/UN_00000888_0009_cosmc_v09_1502050923_mwpc.dat"
        # 1.55 GeV pion beam, 10k count.
        # see http://dbweb4.fnal.gov:8080/ECL/minerva/E/show?e=41989
        #filename = "/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/11/02/TB_00001102_0001_cosmc_v09_1503030625_mwpc.dat" 
        
        # http://dbweb4.fnal.gov:8080/ECL/minerva/E/show?e=41612
        # 16 gev muon 300k
        filename = "/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/10/12/TB_00001012_0007_cosmc_v09_1502221847_mwpc.dat" 
        filename = "/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/10/13/TB_00001013_0004_cosmc_v09_1502230025_mwpc.dat"
        
        # lots of muons
        filename = "../mwpc/exp_20150226091500.dat"
        
        # actual file,
        #filename="/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/15/34/TB_00001534_0001_cosmc_v09_1504262340_mwpc.dat"
        #filename="/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/15/34/TB_00001534_0001_cosmc_v09_1504262340_mwpc.dat"
        
        # actual file
        #filename = "/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/11/25/TB_00001125_0042_cosmc_v09_1503052305_mwpc.dat"
        
        # this file has issues with the time cuts
        #filename = "/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/15/28/TB_00001528_0036_cosmc_v09_1504260400_mwpc.dat"
                
    if ttree_filename is None:
        ttree_filename = "myTestmwpc.root"
        
    logging.info("Processing %s into %s using %s mode." % (filename, ttree_filename, file_mode))
    # make the event loop which opens the file, reads it, reconstructs and saves a root files
    el = eventloop.EventLoop(ttree_filename, filename, file_mode, tree_name, nmax=nmax)
    logging.info("Done processing %s" % filename)
    
if __name__ == "__main__":
    import sys
    outdir = sys.argv[1]
    infile = sys.argv[2]
    outfile = os.path.join(outdir, os.path.splitext(os.path.basename(infile))[0] + ".root")
    main(infile, outfile)
