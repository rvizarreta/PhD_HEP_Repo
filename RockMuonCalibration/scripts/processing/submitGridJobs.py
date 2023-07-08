import time
import sqlite3
import subprocess
import os
import shutil
import optparse
import sys
import datetime
import samweb_client

parser = optparse.OptionParser()

parser.add_option("--daysago", dest="daysago", action="store", type="int", help="how many days ago did something go wrong", default=None)
parser.add_option("--year", dest="year", action="store", type="int", help="year of day you want", default=None)
parser.add_option("--month", dest="month", action="store", type="int", help="month of day you want", default=None)
parser.add_option("--day", dest="day", action="store", type="int", help="day of day you want", default=None)

(options, commands) = parser.parse_args()

if options.daysago != None and (options.year != None or options.month != None or options.day != None):
  print "ERROR: You specified days ago and a date. Don't do that"
  sys.exit(0)
if options.year != None or options.month != None or options.day != None:
  if options.year == None or options.month == None or options.day == None:
    print "ERROR: You specified some but not all of y/m/d"
    sys.exit(0)


sam = samweb_client.SAMWebClient( experiment='minerva' )

# Script will submit all data with end timestamps in a 24-hour window, on a <lag>-hour lag
# Example: For <lag> = 72, at 00:15 Thursday, all jobs with end timestamps on Sunday get submitted
lag = 24*3 # hours

# This directory
basedir = "%s/scripts" % (os.getenv("ROCKMUONCALIBRATIONROOT"))
# Location of DAQ database
daqdb = "/minerva/data/rawdata/daqdb/daqSQLiteDB_current.db"
outputdir="/pnfs/minerva/scratch/users/%s/data_processing" % (os.getenv("USER"))
# raw digits area
#prefix = "/minerva/data/rawdigits/minerva/raw/numibeam"
#output
#outputdir = "/minerva/data/users/minervacal/data_processing/grid/minerva/calib/numibeam/v10r9p1"


secs = time.time()
if options.daysago != None:
  secs -= 24*3600*options.daysago

# MINOS files indexed by month -- look this month and last
time_tuple = time.localtime(secs)

if options.year != None and options.month != None and options.day != None:
  # look up a specific day
  try:
    thedate = datetime.date(options.year, options.month, options.day)
    time_tuple = thedate.timetuple()
    #lag = -24 # Subtract -24 hours to get the END time for the plot interval
    #lag = 24*3 #use the same lag as the default submission jobs
  except ValueError:
    print "You gave a bogus date. Try again"
    sys.exit(0)

this_year  = time_tuple[0]
this_month = time_tuple[1]
this_day   = time_tuple[2]

# determine time stamp range over which to look for files
# Get seconds since epoch at 00:00 on current day
midnight = [ this_year, this_month, this_day, 0, 0, 0, time_tuple[6], time_tuple[7], time_tuple[8] ]
seconds = time.mktime(midnight)
maxtime = seconds - lag * 3600 # lag is in hours, convert to seconds
mintime = maxtime - 24 * 3600 # Subtract 24 hours to get the min time

# Make a playlist of Minerva files
connection = sqlite3.connect(daqdb)
c = connection.cursor()

playlist = open('playlist_daily_%04d-%02d-%02d.txt'%(this_year,this_month,this_day),'w')
first = True
runlist = []

for row in c.execute('SELECT * FROM runsubrun ORDER BY runsubrun'):
  if row[5] != 1 and row[5] != 4 and row[5] != 5: continue # require that run mode be numip, numil or numib
  if row[1] > mintime and row[1] < maxtime:
    runsubrun = row[0]
    run = runsubrun / 10000
    subrun = runsubrun % 10000
    query = "run_number = %d.%04d and data_tier = rawdigits and data_stream numibeam" % (run,subrun)
    flist = sam.listFiles( query )
    if len(flist) == 1:

      dict = sam.locateFile(flist[0])[0]
      if dict["location"] == "":
        print "*******************************************************************************************"
        print "*******************************************************************************************"
        print "*******************************************************************************************"
        print "*******************************************************************************************"
        print "There is a file that has no location: %s" % flist[0]
        continue

      if run not in runlist:
        if first:
          playlist.write('%d %d' % (run,subrun))
          first = False
        else: #next line for next run
          playlist.write('\n%d %d' % (run,subrun))
        runlist.append(run)
      else:
        playlist.write(',%d' % subrun)
    else:
      print "*******************************************************************************************"
      print "*******************************************************************************************"
      print "*******************************************************************************************"
      print "*******************************************************************************************"
      print "The file %d / %d is in the DAQ DB but can't be found" % (run, subrun)

connection.close()
playlist.close()

if len(runlist) == 0: # there are no Minerva subruns to process
  print 'There were no new files!'
  os.remove( 'playlist_daily_%04d-%02d-%02d.txt' % (this_year,this_month,this_day) )

  # Print a line on the web page saying there were no files
  html_page = '/nusoft/app/web/htdoc/minerva/minervacal/daily_muon_monitoring.html'

  statement = 'Found no rawdigit files on %04d-%02d-%02d\n<br><br>\n' % (this_year,this_month,this_day)

  page = open( html_page, 'r' )
  lines = page.readlines()
  page.close()
  newpage = open( html_page, 'w' )
  for i in range(5):
    newpage.write(lines[i]) #header
  newpage.write(statement)
  for i in range(5,len(lines)): # copy existing days
    newpage.write(lines[i])
  newpage.close()

else: # submit jobs to the grid
  productionscripts = os.environ['PRODUCTIONSCRIPTSROOT']
  cmd = 'python %s/data_scripts/SubmitDataRuns.py --playlist %s/playlist_daily_%04d-%02d-%02d.txt --args "--rockmumonitoring --raw_digits --use_role_calibration --nightly_subgroup --usecat --outdir %s --dst --calib_stage monitoring --memory 3GB" > %s/rockMuonSubmit.txt' % (productionscripts, basedir+'/monitoring', this_year, this_month, this_day, outputdir,os.getenv("HOME"))
  #print cmd

  # Move the playlist file to the monitoring area where the next script will wait for it
  shutil.move( 'playlist_daily_%04d-%02d-%02d.txt' % (this_year,this_month,this_day), basedir + '/monitoring' )
  print subprocess.call( cmd, shell=True )
