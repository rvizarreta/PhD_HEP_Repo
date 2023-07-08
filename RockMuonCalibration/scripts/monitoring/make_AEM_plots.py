import time
import os
import shutil
import subprocess
import expertEmail
import sys
import webpage

# Use the playlists in ../monitoring/playlists since they have all the run numbers
# 4-day lag, so for Thursday's data need Monday's date

# month is [1,12], but if it's january and you go backwards you get december so put 31 for 0
month_days = [ 31, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]

right_now = time.localtime()

this_year   = right_now[0]
this_month  = right_now[1]
this_day    = right_now[2]
day_of_week = right_now[6] # Monday is 0

# Doubtful the DOE will approve Minerva to run until 2100 but just to be sure
if this_year % 4 == 0: month_days[3] = 29
if this_year % 100 == 0: month_days[3] = 28
if this_year % 400 == 0: month_days[3] = 29

# On Sundays after about 4 AM you can do the period ending that week
# It might crash if you run it on Sunday before about 4 AM
# But if that's the case you have bigger problems
days_to_last_monday = day_of_week
if day_of_week < 6: days_to_last_monday += 7

start_year = this_year
start_month = this_month
start_day = this_day - days_to_last_monday
if start_day < 1:
  start_month -= 1
  start_day += month_days[start_month]
  if start_month == 0:
    start_month = 12
    start_year -= 1

# AEM meeting is on Monday, one week after the "start_day" -- need this later
aem_year = start_year
aem_month = start_month
aem_day = start_day + 7
if aem_day > month_days[aem_month]:
  aem_month += 1
  aem_day -= month_days[aem_month]
  if aem_month == 13:
    aem_month = 1
    aem_year += 1

tmpname = 'aemPlots/tmp'
if not os.access(tmpname, os.R_OK): os.mkdir(tmpname)

prefix = '/minerva/data/users/minervacal/data_processing/grid/minerva/calib/numibeam'
sver = 'v10r7p3'

# Loop through the 7 daily simple playlists and make a full path playlist for the week
out = open( 'playlist_AEM.txt', 'w' )
year = start_year
month = start_month
day = start_day
allOK = True
for i in range(7):  
  try:
    playlist = open( 'playlists/playlist_daily_%04d-%02d-%02d.txt' % (year,month,day), 'r' )
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
        break
    playlist.close()
    day += 1
    if day > month_days[month]:
      day = 1
      month += 1
    if month > 12:
      month = 1
      year += 1
  except IOError: # could not find the playlist
    allOK = False
    print 'Could not find playlists/playlist_daily_%04d-%02d-%02d.txt' % (year,month,day)

out.close()

if allOK: # MAKE THE PLOTS!!!
  cmd = 'root -l -q -b MakeEventRatePlots.C'
  subprocess.call( cmd.split() )
  shutil.move( tmpname, 'aemPlots/AEM_%04d-%02d-%02d' % (aem_year, aem_month, aem_day) )
  shutil.move( 'AEM_plots.root', 'aemPlots/AEM_%04d-%02d-%02d/AEM_%04d-%02d-%02d.root' % (aem_year, aem_month, aem_day, aem_year, aem_month, aem_day) )
  # move to the web
  webpage.plots_to_web_aem( aem_year, aem_month, aem_day )
  os.remove( 'playlist_AEM.txt' ) # get rid of playlist used by MakeEventRatePlots
else:
  text = 'And you have to fix it.  On a Sunday.'
  expertEmail.sendMail( 'monitoringWizard@fnal.gov', 'marshall@pas.rochester.edu', 'AEM plots failed!!!', text )

