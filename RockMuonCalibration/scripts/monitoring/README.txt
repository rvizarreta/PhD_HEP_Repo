This document is intended to provide instructions for maintaining the rock muon monitoring web page for shifters.

Part 1) submitting jobs
The monitoring is done using RockMuonCalibrationAlg ntuples. An options file in Tools/SystemTests/options/CalibrationProcessing/RockMuCalMonitoring.opts, runs a simple long-track reconstruction and RockMuonCalibrationAlg. The script that submits jobs is called submitGridJobs.py, in Cal/RockMuonCalibration/scripts/processing. By default, it will submit jobs with a three-day lag (for example, if called on a Friday, it will submit jobs for data collected between midnight central time on Monday night/Tuesday morning and midnight central time on Tuesday night/Wednesday morning). It can also be called with an explicit lag, or for jobs on a specific date. The --help option of the script has more information about these options.

The timestamps of the jobs are obtained from the DAQ database, in /minerva/data/rawdata/daqdb/daqSQLiteDB_current.db. This is copied at midnight by a cron job. submitGridJobs.py runs an sqlite command to get a list of run/subrun numbers and start and end times, and makes a playlist of subruns that start in a given 24-hour period (the last one will typically end in the next 24-hour period). The playlist is then moved to Cal/RockMuonCalibration/scripts/monitoring, and the SubmitDataRuns.py command is executed.

Another important step is updating the MinosFileDB. This is done by another cron job on minervacal@minervagpvm02. This tells the job which MINOS files to look in for matching tracks. When MINOS keepup jobs do not finish, you will get no MINOS tracks or matches. This was the most common failure mode of the rock muon monitoring in 2014.

submitGridJobs.py is called by master_submission_script.sh, which is run in a cron job on minervacal@minervagpvm02 at 00:10.

Part 2) making plots
After the jobs are finished, it is time to make plots. A script called master_daily_plotter.sh is run every hour via cron on minervacal@minervagpvm02. This script runs a python script make_plots.py. The first thing this does is check for a playlist that was put in the Cal/RockMuonCalibration/scripts/monitoring directory by submitGridJobs.py as described in part 1. If it does not find one, it stops, and tries again in another hour. When it does find a playlist, it first checks to see if the jobs have all finished by looking in the output directory. If the jobs haven't all finished, it stops and tries again in another hour. Once the jobs all finish, it executes MakeDailyPlots.C and moves the playlist into the playlists directory.

MakeDailyPlots.C loops over the ntuples and makes TGraphs of various quantities over the 24-hour period. It also fits the 24-hour plots to a "pol0" straight-line, and adds the result to dump/summary_plots.root. This root file sits in the dump area and is updated each night with one additional point on each plot. The plots are all written to a directory in the dump area.

Part 3) the web page
The last step in make_plots.py is to put the plots on the web page, http://nusoft.fnal.gov/minerva/minervacal/daily_muon_monitoring.html. The web page lives at /nusoft/app/web/htdoc/minerva/minervacal, and is writeable only by minervacal. Plots are copied from the dump area to the day's directory in /nusoft/app/web/htdoc/minerva/minervacal/dump. An entry is added to the html page for the day, which is just a link to a php page with the correct date. That date points to the area in the dump so that the correct plots are displayed on the web page.

All of this happens automatically via cron job, so when there are no problems, the expert does not have to do anything at all. However, sometimes there are problems.

Part 4) troubleshooting -- the most common problems:

1) The most common problem is that the MINOS keepup jobs failed for some reason, so the MINOS tracks and MINOS matches plots are all 0 for all or part of the day.

// Problem solving procedure updated at 2017.06
Currently, we won't remove points but wait for MINOS keepup jobs to succeed as first step. Once the keepup job succeeded and MinosFileDB was updated, you should remove ntuples at that day  by running remove_ntuple.py in monitoring directory. The third step is to submit processing jobs mannually by calling submitGridjobs.py and specifying --year --month --day. The fourth step is making plots again once the jobs are done. you need to remove playlist and plots that already produced before making plots again. They are in playlists/ and dump/. You can make plots by call make_plot.py. Finally, You need to mannually remove the duplicate link in rockmuon monitoring webpage. This is done by modify html file mannually in /web/sites/minerva.fnal.gov/htdocs/nusoft/minervacal/daily_muon_monitoring.html. You need to specify the date if you were making plots other than today. You should specify the date that the jobs were first submitted. For example, If Minos keepup failed for plots first shown at 2017.06.01 and was fixed someday after, you should do:
  1. python remove_ntuples.py 2017 06 01
  2. python submitGridjobs.pu --year 2017 --month 06 --day 01 (and wait till jobs finished)
  3. rm -r dump/daily_2017-06-01 and rm playlists/playlist_daily_2017-06-01.txt
  4. python make_plots.py 2017 06 01


// What stated below is old procedure, FYI
The first step is to remove the point on the plots that is incorrect. There is a script removePoint.py that does this. First make a list of the points, and then specify which point you want to remove. The --help menu will assist you. Then, you have to wait for the MINOS keepup jobs to succeed, and make sure that they are added to the MinosFileDB (which happens automatically at midnight). Then, you can submit the jobs manually, by calling submitGridJobs.py and specifying --year --month --day. Note that this is the day of the actual data, not the day that the jobs were first submitted. Once the jobs are finished, you can call make_plots.py manually by specifying optional arguments, for example "python make_plots.py 2014 10 24" will run the jobs for the playlist made on 2014-10-24. The plots will automatically be written to the web. You can go to the html page and manually remove the duplicate link.
// end of old procedure.

2) Another problem is when a MINERvA job fails. The script will send the expert an email, saying that it found an old playlist. This is because make_plots.py checked for all the jobs to be finished, and always found a job that did not finish. The easiest thing to do is just delete the playlist and re-run submitGridJobs.py. You could also figure out which job had failed, and run ProcessData.py on just that subrun with the arguments found in the submit command of submitGridJobs.py, which would be faster. Most failures are due to grid conditions, database access, etc. and not actual job problems. If there is a problem with a specific subrun due to corrupted raw digits, you can just remove that subrun from the playlist so that make_plots.py does not complain when it cannot find its output.

3) At 2017.06, the most common problem is the "missing subrun" in playlist. The monitoring script anticipates one root file for every playlist entry, but it may not be the case. The reason could be no info found in that subrun (most common), process job failed or something else. One can look at the log to figure it out. Removing the missing subruns in playlist can get rid of the problem but it is necessary to reprocess and replot if there was a problem with processing job. The procedure to reprocess/replot is introduced in 1).


4) Add more problems and their solutions here!

