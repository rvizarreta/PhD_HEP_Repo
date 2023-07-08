import shutil
import os
import time
import sys

months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

plotlist = [ 'protons_per_pulse', 'time_slices_per_pot', 'rock_muons_per_pot', 'minos_tracks_per_pot', 'minos_matches_per_pot', 'minerva_cluster_pe', 'minos_deltaT', 'minos_gate_deltaT', 'minos_prange_vs_pcurvature', 'time_btw_gates', 'fraction_dead_time', 'dead_vs_intensity', 'peak_cluster_pe', 'protons_summary', 'time_slices_summary', 'rock_muons_summary', 'minos_tracks_summary', 'minos_matches_summary', 'good_minos_tracks_per_pot', 'good_minos_matches_per_pot', 'good_minos_tracks_summary', 'good_minos_matches_summary' , 'rock_mu-_per_pot_by_energy','rock_mu+_per_pot_by_energy', 'minos_rockmuon_E','Muminus_HE_summary','Muminus_ME_summary','Muminus_LE_summary','Muplus_HE_summary','Muplus_ME_summary','Muplus_LE_summary']

# web page files
#web_dir = '/nusoft/app/web/htdoc/minerva/minervacal' # old version
web_dir = '/web/sites/minerva.fnal.gov/htdocs/nusoft/minervacal/NXtest'
plot_dir_base = '/minerva/data/users/minervacal/Monitoring_plots'

def plots_to_web( this_year, this_month, this_day ):

  html_page = web_dir + '/daily_muon_monitoring.html'

  # where the plots are
  plot_dir = plot_dir_base+'/daily_%04d-%02d-%02d' % (this_year, this_month, this_day)

  dest_dir = web_dir + '/dump/daily_%04d-%02d-%02d' % (this_year, this_month, this_day)
  if not os.access( dest_dir, os.R_OK ): os.mkdir(dest_dir)

  # copy files to the web area, plot_NN.png is assumed by rockmuonmonitoring.php
  for i,plot in enumerate(plotlist):
    if os.path.isfile( "%s/%s.png" % (plot_dir, plot) ):
      shutil.copy( "%s/%s.png" % (plot_dir, plot), "%s/plot_%02d.png" % (dest_dir, i) )
    else :
      print "%s.png not found." % (plot) 

  # update html page to include link for today
  link = '<a href=\"http://minerva-exp.fnal.gov/nusoft/minervacal/NXtest/rockmuonmonitoring.php?year=%04d&month=%02d&day=%02d\" target="_blank">%02d %s %04d<a>\n<br><br>\n' % (this_year, this_month, this_day, this_day, months[this_month-1], this_year)

  page = open( html_page, 'r' )
  lines = page.readlines()
  page.close()
  newpage = open( html_page, 'w' )
  for i in range(6):
    newpage.write(lines[i]) #header
  newpage.write(link)
  for i in range(6,len(lines)): # copy existing days
    newpage.write(lines[i])
  newpage.close()

def minos_live_percent( year, month, day ):
  f = open( plot_dir_base+'/daily_%04d-%02d-%02d/minos_live_percent.txt' % (year,month,day), 'r' )
  lines = f.readlines()
  daystr = lines[0]
  string = lines[1]
  pct = float(string)
  syear = int(daystr.split()[0])
  smonth = int(daystr.split()[1])
  sday = int(daystr.split()[2])

  thingtowrite = '%04d-%02d-%02d: %3.2f\n<br><br>\n' % (syear, smonth, sday, pct)

  html_page = web_dir+'/minoslive.html'

  page = open( html_page, 'r' )
  lines = page.readlines()
  page.close()
  newpage = open( html_page, 'w' )
  for i in range(5):
    newpage.write(lines[i]) #header
  newpage.write(thingtowrite)
  for i in range(5,len(lines)): # copy existing days
    newpage.write(lines[i])
  newpage.close()

# The This function are obsolete as Jan 2018
def plots_to_web_aem( year, month, day ):
  months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

  html_page = web_dir + '/plots_for_AEM.html'

  # where the plots are
  rmcr = os.environ['ROCKMUONCALIBRATIONROOT']
  plot_dir = rmcr + '/scripts/monitoring/aemPlots/AEM_%04d-%02d-%02d' % (year, month, day)

  dest_dir = web_dir + '/dump/aem_%04d-%02d-%02d' % (year, month, day)
  if not os.access( dest_dir, os.R_OK ): os.mkdir(dest_dir)

  # copy files to the web area, plot_NN.png is assumed by rockmuonmonitoring.php
  shutil.copy( plot_dir+'/protons_per_pulse.png', dest_dir+'/plot_00.png' )
  shutil.copy( plot_dir+'/time_slices_per_pot.png', dest_dir+'/plot_01.png' )
  shutil.copy( plot_dir+'/rock_muons_per_pot.png', dest_dir+'/plot_02.png' )
  shutil.copy( plot_dir+'/minos_tracks_per_pot.png', dest_dir+'/plot_03.png' )
  shutil.copy( plot_dir+'/minos_matches_per_pot.png', dest_dir+'/plot_04.png' )

  # update html page to include link for today
  link = '<a href=\"http://nusoft.fnal.gov/minerva/minervacal/aemplots.php?year=%04d&month=%02d&day=%02d\">%02d %s %04d<a>\n<br><br>\n' % (year, month, day, day, months[month-1], year)

  page = open( html_page, 'r' )
  lines = page.readlines()
  page.close()
  newpage = open( html_page, 'w' )
  for i in range(5):
    newpage.write(lines[i]) #header
  newpage.write(link)
  for i in range(5,len(lines)): # copy existing days
    newpage.write(lines[i])
  newpage.close()

if __name__ == "__main__":
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
  
  plots_to_web(this_year,this_month,this_day)
  #minos_live_percent(this_year,this_month,this_day)


  
