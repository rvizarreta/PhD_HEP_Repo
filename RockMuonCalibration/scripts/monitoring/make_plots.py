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

if os.isatty(sys.stdin.fileno()):
  cron=False

time_cap = 'Daily'
time_dir = 'today'
time_scale = 'daily'

#prefix = '/minerva/data/users/minervacal/data_processing/grid/minerva/calib/numibeam'
prefix = '/pnfs/minerva/scratch/users/%s/data_processing/grid/minerva/calib/numibeam' % (os.getenv("USER"))
sver = os.getenv("MINERVA_RELEASE")
plot_dump="dump"
plot_dir="/minerva/data/users/minervacal/Monitoring_plots"

# Look for today's playlist
try:
  playlist = open( 'playlist_%s_%04d-%02d-%02d.txt' % (time_scale,this_year,this_month,this_day), 'r' )
  out = open( 'playlist_%s.txt' % time_scale, 'w' )  
  name = '%s/%s' % (plot_dump,time_dir)
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
      # figure out which are missing
      if len(found_subruns) > len(subruns):
        print "Found more subruns than I was expecting.  That is really strange."
      else:
        missing = ""
        for s in subruns:
          if s not in found_subruns:
            missing += "%d " % s
        print "Missing subruns from run %d: %s" % (int(run.split()[0]),missing)
        
      allOK = False
      if (not cron) and (1.0*len(missing)/len(subruns) < 0.1) :
        s=raw_input("Ignore missing subruns < 10 percent? Answer yes to Continue:").lower()
        if s=="yes":
          allOK = True
        else :
          exit(1)

except IOError: # could not find the playlist
  print 'Could not open playlist_%s_%04d-%02d-%02d.txt' % (time_scale,this_year,this_month,this_day)

finally:
  out.close()
  playlist.close()
  
if allOK: # MAKE THE PLOTS!!!
  shutil.move( 'playlist_%s_%04d-%02d-%02d.txt' % (time_scale,this_year,this_month,this_day), 'playlists/playlist_%s_%04d-%02d-%02d.txt' % (time_scale,this_year,this_month,this_day) )
  cmd = 'root -l -q -b Make%sPlots_v2.C+' % time_cap
  subprocess.call( cmd.split() )

  new_dir_name =  '%s/%s_%04d-%02d-%02d' % (plot_dir,time_scale, this_year, this_month, this_day)
  if (not cron) and (os.access(new_dir_name,os.R_OK)):
    shutil.rmtree(new_dir_name)
  shutil.move( '%s/%s' % (plot_dump,time_dir), new_dir_name)
  shutil.move( 'bad_data_list.txt', new_dir_name )
  shutil.copy( '%s/summary_plots.root' % plot_dump , new_dir_name )
  # move to the web
  webpage.plots_to_web( this_year, this_month, this_day )
  #webpage.minos_live_percent( this_year, this_month, this_day )
  os.remove( 'playlist_%s.txt' % time_scale ) # get rid of the playlist fed to MakeDailyPlots.C


# If the date was determined automatically, look for old files, and send Chris email if you find one
if not manual:
  print 'Looking for old files...'

  try_day = this_day - 1
  try_month = this_month
  try_year = this_year
  while try_day > 0:
    if os.path.exists( 'playlist_%s_%04d-%02d-%02d.txt' % (time_scale,try_year,try_month,try_day) ):
      text = 'Found file playlist_%s_%04d-%02d-%02d.txt but today is %04d-%02d-%02d' % (time_scale,try_year,try_month,try_day,this_year,this_month,this_day)
      expertEmail.sendMail( 'monitoringWizard@fnal.gov','has137@pitt.edu', 'There is an old file!', text )
      shutil.move( 'playlist_%s_%04d-%02d-%02d.txt' % (time_scale,try_year,try_month,try_day), 'playlists' )
    try_day -= 1

  try_month -= 1
  if try_month == 0:
    try_month = 12
    try_year -= 1
  try_day = 31
  while try_day > 0:
    if os.path.exists( 'playlist_%s_%04d-%02d-%02d.txt' % (time_scale,try_year,try_month,try_day) ):
      text = 'Found file playlist_%s_%04d-%02d-%02d.txt but today is %04d-%02d-%02d' % (time_scale,try_year,try_month,try_day,this_year,this_month,this_day)
      expertEmail.sendMail( 'monitoringWizard@fnal.gov', 'has137@pitt.edu', 'There is an old file!', text )
      shutil.move( 'playlist_%s_%04d-%02d-%02d.txt' % (time_scale,try_year,try_month,try_day), 'playlists' )
    try_day -= 1

# If no email was sent, that means there are no old files still around or the expert manually ran this script
