import time
import os
import shutil
import subprocess
import expertEmail
import sys
import webpage

# Get time
manual = True
this_year  = time.localtime()[0]
this_month = time.localtime()[1]
this_day   = time.localtime()[2]
try:
  this_year  = int(sys.argv[1])
  this_month = int(sys.argv[2])
  this_day   = int(sys.argv[3])
except IndexError:
  manual = False

timeCap = 'Daily'
timeDir = 'today'
timescale = 'daily'

prefix = '/pnfs/minerva/scratch/users/%s/data_processing/grid/minerva/calib/numibeam' % os.getenv("USER")
sver = os.getenv("MINERVA_RELEASE")
plotdump='dump/'

# Look for today's playlist
try:
  playlist = open( 'playlist_%s_%04d-%02d-%02d.txt' % (timescale,this_year,this_month,this_day), 'r' )
  out = open( 'playlist_%s.txt' % timescale, 'w' )  
  name = 'dump/%s' % timeDir
  if not os.access(name, os.R_OK): os.mkdir(name)

  allOK = True # every file in the playlist must exist, or something crashed
  runs = playlist.readlines()
  for run in runs:
    runno = int(run.split(' ')[0])
    rundir = prefix + '/' + sver + '/%02d/%02d/%02d/%02d' % ( runno/1000000, (runno%1000000)/10000, (runno%10000)/100, runno%100 )
    if not os.access(rundir, os.R_OK): # fail
      print 'Could not find %s' % rundir
      allOK = False
      break

    subrunsstr = run.split(' ')[1].split(',')
    subruns = []
    for sub in subrunsstr: subruns.append( int(sub) )

    found_subruns = [] # files in the rundir
    runlist = os.listdir(rundir)
    runlist.sort()
    for ntuple in runlist:
      subrun = int(ntuple[12:16])
      if subrun in subruns:
        found_subruns.append(subrun)
        out.write(str(runno) + ' ' + str(subrun) + ' ' + rundir + '/' + ntuple + '\n')
    if len(found_subruns) != len(subruns): # missing subrun
      print 'Found %d subruns for run %d, expecting %d' % (len(found_subruns),runno, len(subruns))
      allOK = False
      # figure out which are missing
      if len(found_subruns) > len(subruns):
        print "Found more subruns than I was expecting.  That is really strange."
      else:
        missing = ""
        for s in subruns:
          if s not in found_subruns:
            missing += "%d " % s
        print "Missing subruns from run %d: %s" % (int(run.split()[0]),missing)
        if len(missing)/len(subruns) < 0.1 :
          allOK = True
          print "Ignore missing subruns < 10 percent."
      

  out.close()
  playlist.close()
  if allOK: # MAKE THE PLOTS!!!
    if os.path.isfile('playlists/playlist_%s_%04d-%02d-%02d.txt' %(timescale,this_year,this_month,this_day)):
      os.remove('playlists/playlist_%s_%04d-%02d-%02d.txt' %(timescale,this_year,this_month,this_day))
    shutil.move( 'playlist_%s_%04d-%02d-%02d.txt' % (timescale,this_year,this_month,this_day), 'playlists' )
    cmd = 'root -l -q -b Make%sPlots_v2.C+' % timeCap
    subprocess.call( cmd.split() )
    newname = '%s%s_%04d-%02d-%02d' % (plotdump,timescale, this_year, this_month, this_day)
    if (os.access(newname,os.R_OK)):
      shutil.rmtree(newname)
    os.rename( '%s%s' % (plotdump,timeDir), newname)
    shutil.move( 'bad_data_list.txt', newname)
    shutil.copy( '%ssummary_plots.root' % plotdump, newname)
    # move to the web
    webpage.plots_to_web( this_year, this_month, this_day )
    webpage.minos_live_percent( this_year, this_month, this_day )
  os.remove( 'playlist_%s.txt' % timescale ) # get rid of the playlist fed to MakeDailyPlots.C
except IOError: # could not find the playlist
  print 'Could not open playlist_%s_%04d-%02d-%02d.txt' % (timescale,this_year,this_month,this_day)
  print 'Maybe you already moved it, but I\'ll keep trying anyway'

# If the date was determined automatically, look for old files, and send Chris email if you find one
# if not manual:
#  print 'Looking for old files...'
#
#  try_day = this_day - 1
#  try_month = this_month
#  try_year = this_year
#  while try_day > 0:
#    if os.path.exists( 'playlist_%s_%04d-%02d-%02d.txt' % (timescale,try_year,try_month,try_day) ):
#      text = 'Found file playlist_%s_%04d-%02d-%02d.txt but today is %04d-%02d-%02d' % (timescale,try_year,try_month,try_day,this_year,this_month,this_day)
#      expertEmail.sendMail( 'monitoringWizard@fnal.gov','rogerschrodinger@gmail.com', 'There is an old file!', text )
#      shutil.move( 'playlist_%s_%04d-%02d-%02d.txt' % (timescale,try_year,try_month,try_day), 'playlists' )
#    try_day -= 1
#
#  try_month -= 1
#  if try_month == 0:
#    try_month = 12
#    try_year -= 1
#  try_day = 31
#  while try_day > 0:
#    if os.path.exists( 'playlist_%s_%04d-%02d-%02d.txt' % (timescale,try_year,try_month,try_day) ):
#      text = 'Found file playlist_%s_%04d-%02d-%02d.txt but today is %04d-%02d-%02d' % (timescale,try_year,try_month,try_day,this_year,this_month,this_day)
#      expertEmail.sendMail( 'monitoringWizard@fnal.gov', 'rogerschrodinger@gmail.com', 'There is an old file!', text )
#      shutil.move( 'playlist_%s_%04d-%02d-%02d.txt' % (timescale,try_year,try_month,try_day), 'playlists' )
#    try_day -= 1

# If no email was sent, that means there are no old files still around or the expert manually ran this script
