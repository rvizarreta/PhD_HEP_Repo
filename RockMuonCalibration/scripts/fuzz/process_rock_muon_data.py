#!/bin/env python

import os,sys
from optparse import OptionParser

if __name__ == '__main__':

  try:
    x = os.environ["MINERVA_RELEASE"]
    x = os.environ["PRODUCTIONSCRIPTSROOT"]
  except Exception, e:
    sys.exit( "You must setup the environment for RockMuonCalibration." )


  ################################
  # Parse Options
  ###############################
  default_datadir = "/minerva/data/users/%s/fuzzStudy/data_nt/" % os.getenv("USER")
  default_opts  = "%s/options/MuonFuzzStudy.opts" % ( os.getenv("ROCKMUONCALIBRATIONROOT") )
  parser = OptionParser()
  parser.add_option("--datadir", dest="datadir",     help="Top-level directory for output of muon fuzz data ntuples (default = %s)." % default_datadir,    default=default_datadir )
  parser.add_option("--opts", dest="opts_file",  help="Template options file (default = %s)." % default_opts,    default=default_opts )
  parser.add_option("--playlist", dest="playlist", default=None, help="/full/path/to/playlist/file.txt")
  parser.add_option("--first_run",dest="first_run", default=None, help="Lower bound run number to process")
  parser.add_option("--last_run",dest="last_run", default=None, help="Upper bound run number to process")
  parser.add_option("--test",dest="test", default=False, action="store_true", help="Submit 100 events interactively")

  if len(sys.argv) < 2:
    parser.parse_args( "--help".split() )
    
  (opts,args) = parser.parse_args()

  template_opts = open( opts.opts_file )
  template_lines = template_opts.readlines()
  template_opts.close()

  if opts.playlist == None and not opts.test and (opts.first_run == None or opts.last_run == None):
    raise Exception( "You have to supply either a playlist or a run range. Try again" )

  if opts.playlist != None and (opts.first_run != None or opts.last_run != None):
    raise Exception( "You specified a playlist and a run range! Pick one" )

  if opts.first_run < 2000 and opts.last_run >= 2000:
    raise Exception( "Run range can't span two geometries" )

  baseCmd    = "python %s/data_scripts/SubmitDataRuns.py " % ( os.getenv("PRODUCTIONSCRIPTSROOT") )

  if opts.playlist != None:
    baseCmd += "--playlist %s " % ( opts.playlist )
  else: # use run range
    baseCmd += "--first_run %s --last_run %s " % ( opts.first_run, opts.last_run )

  args = "--muon --opts %s --os SL6 --calib_stage val --use_jobsub_client" % ( opts.opts_file )

  if opts.playlist != None and not opts.test:
    if "downstream" in opts.playlist:
      args += " --det frozen"
  elif not opts.test:
    if opts.last_run < 2000:
      args += " --det frozen"

  if opts.test:
    cmd = "python %s/data_scripts/ProcessData.py --muon --interactive --calib_stage val --opts %s --run 3543 --subrun 3 --n_events 100" % (os.getenv("PRODUCTIONSCRIPTSROOT"), opts.opts_file )
    print cmd
    os.system(cmd)
  else:
    cmd = baseCmd + "--args \"%s\"" % ( args )
    print cmd
    os.system( cmd )
