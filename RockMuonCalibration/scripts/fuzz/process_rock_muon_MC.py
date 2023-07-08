#!/bin/env python

import os,sys,glob,re,time,calendar
from optparse import OptionParser
from tempfile import NamedTemporaryFile
import samweb_client

if __name__ == '__main__':

  try:
    x = os.environ["MINERVA_RELEASE"]
    x = os.environ["PRODUCTIONSCRIPTSROOT"]
  except Exception, e:
    sys.exit( "You must setup the environment for RockMuonCalibration." )
    
  
  run_periods = { "Downstream1" : "846/2", "Downstream2": "1025/1", "Minerva1": "2000/1", "Minerva2": "2491/1", "Minerva3": "2542/1", "Minerva4": "2567/2", "Minerva5": "2621/1", "Minerva6": "3099/1", "Minerva7": "3141/2", "Minerva8": "3317/2", "Minerva9": "3345/3", "Minerva10": "3415/2", "Minerva11": "3504/1", "Minerva12": "3515/1", "Minerva13": "3543/1" }

  ################################
  # Parse Options
  ###############################
  default_mcdir = "/minerva/data/users/%s/fuzzStudy/mc_nt/" % os.getenv("USER")
  default_opts  = "%s/options/MuonFuzzStudyMC.opts" % ( os.getenv("ROCKMUONCALIBRATIONROOT") )
  parser = OptionParser()
  parser.add_option("--indir", dest="indir",     help="Top-level directory to search for rock muon files (required)", default="")
  parser.add_option("--mcdir", dest="mcdir",     help="Top-level directory for output of MEU MC ntuples (default = %s)." % default_mcdir,    default=default_mcdir )
  parser.add_option("--opts", dest="opts_file",  help="Template options file (default = %s)." % default_opts,    default=default_opts )
  parser.add_option("--run_period", "--run_periods", dest="run_periods", default=None, help="Run period or comma separated list of run periods (default is all run periods)")
  parser.add_option("--test", dest="test", default=False, action="store_true", help="Run a single job interactively, with 100 events")

  if len(sys.argv) < 2:
    parser.parse_args( "--help".split() )
    
  (opts,args) = parser.parse_args()

  if opts.indir == "":
    sys.exit( "ERROR: You must specify an input directory (--indir)" )

  template_opts = open( opts.opts_file )
  template_lines = template_opts.readlines()
  template_opts.close()

  baseCmd    = "python %s/mc_scripts/ProcessMC.py --meu --use_jobsub_client --run 13 " % ( os.getenv("PRODUCTIONSCRIPTSROOT") )

  runPeriodNameList = []
  if opts.run_periods == None:
    sys.exit( "You must specify a run period" )
  else:
    opts.run_periods = opts.run_periods.split(',')
    #print opts.run_periods
    for name in opts.run_periods :
      if name in runPeriodNameList : sys.exit( 'ERROR: Duplicate run period \"%s\" specified.' % name )
      if name in run_periods: runPeriodNameList.append( name )
      else : sys.exit( 'ERROR: Run period name \"%s\" not recognized.' % name )

  if len( runPeriodNameList ) == 0 :
    sys.exit( "No run periods to be processed.  Exiting." )

  if not os.path.isdir( opts.mcdir ):
    os.makedirs( opts.mcdir )

  # Use SAM to retrieve GPS time
  samweb = samweb_client.SAMWebClient(experiment='minerva')

  #loop over run periods again and use ProcessMC to submit the MC jobs
  for rpName in runPeriodNameList :
    print " =======> Submitting MEU MC for run period: %s" % str( rpName )
    muondirRP = os.path.join( opts.indir, rpName )
    nfilesRP  = len( glob.glob( os.path.join( muondirRP,"*.txt" ) ) )
    if( nfilesRP == 0 ):
      print 'No MEU RockMuon files found for run period %s.  Skipping this run period.' % rpName
      continue
    if opts.test :
      nfilesRP = 1

    print 'Found %d rock muon files for %s' % ( nfilesRP, rpName )
    mcdirRP = os.path.join( opts.mcdir, rpName )

    #copy the template options file and add a new default GPS time for ReadoutAlg.
    #  Since gps time isn't normally changed, we must add a new line to choose it.
    tmp_opts = NamedTemporaryFile(delete=False)
    for line in template_lines:
      tmp_opts.write( line )

    # Retrieve GPS time for start of run period
    run = int(run_periods[rpName].split("/")[0])
    sub = int(run_periods[rpName].split("/")[1])
    rawFile = None
    for file in list(samweb.listFiles("run_number %d.%d" % ( run, sub ) ) ) :
      if re.search( 'RawData.dat$', file ) or re.search( 'RawEvents.root$', file ) :
        rawFile = file
        break

    if rawFile == None:
      print 'Could not retrieve raw data file from SAM for start %s of MEU run period %s.  Skipping this run period.' % ( rp.startRun, rp.name )
      continue

    metaData = samweb.getMetadata( rawFile )
    gpsTime = time.strptime(metaData["start_time"][:19],'%Y-%m-%dT%H:%M:%S')
    gpsTime = calendar.timegm( gpsTime )
    print 'gpsTime = %d' % gpsTime
    # Add a half-hour to the run period start gps time (seconds) to ensure calibrations within the run period are retrieved
    gpsTime += 1800
    tmp_opts.write( "ReadoutAlg.DefaultGPStime = %d;\n" % gpsTime )
    tmp_opts.close()
    
    cmd = baseCmd + " -f 1 -l %d --no_dag --outdir %s --outtag %s --rockdir %s --opts %s --os SL6" \
        % ( nfilesRP, mcdirRP, rpName, muondirRP, tmp_opts.name )

    if opts.test:
      #cmd = cmd + " --interactive --n_events 100"
      print "testing"

    if "Downstream" in rpName :
      cmd = cmd + " --det frozen"

    print cmd
    os.system( cmd )

    os.unlink( tmp_opts.name )
