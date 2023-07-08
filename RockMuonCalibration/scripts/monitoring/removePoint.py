# This script will remove points from the summary plots

import ROOT
from optparse import OptionParser
import sys
import time

seconds_1995 = 788918400  # this is time 0 for ROOT for some reason

if __name__ == '__main__':

  ###############################
  # Parse Options
  ###############################
  parser = OptionParser()
  parser.add_option("--list_hists", dest="listhist", action="store_true", help="List all histograms -- don't remove anything", default=False)
  parser.add_option("--list_points", dest="listpt", help="List all points in the histogram -- don't remove anything", default=None)
  parser.add_option("--remove_point", dest="rmpt", help="Integer point number to remove from all histograms -- not a date", default=None)
  parser.add_option("--hist", dest="hist", help="Remove points from this histogram only", default=None)

  if len(sys.argv) < 2:
    parser.parse_args( "--help".split() )

  (opts,args) = parser.parse_args()

  if opts.listhist and opts.rmpt is not None:
    print "You specified list_hists and remove_point, ignoring remove_point"
    opts.rmpt = None

  if opts.listpt is not None and opts.rmpt is not None:
    print "You specified list_points and remove_point, ignoring remove_point"
    opts.rmpt = None

  # summary_plots.root is where all the X vs. time histograms are stored, in the dump directory
#  fsum = ROOT.TFile( "dump/summary_plots.root", "OLD" )
  fsum = ROOT.TFile( "summary_plots_point_removed.root", "OLD" )

  histDict = {}
  histList = [ "peak_cluster_pe", "peak_cluster_mev", "minos_deltaT_summary", "minos_RvC_summary", "rock_muons_summary", "minos_matches_summary", "minos_tracks_summary", "time_slices_summary", "protons_summary", "good_minos_matches_summary", "good_minos_tracks_summary" ]

  # Get all of the histograms and stuff them in a dictionary
  for name in histList:
    histDict[name] = fsum.Get(name)

  fsum.Close() # we're done with this file

  if opts.listpt is not None:
    if opts.listpt not in histList:
      print "%s is not a valid histogram name" % opts.listpt
      opts.listhist = True
    else:
      hist = histDict[opts.listpt]
      print "All points for histogram: %s" % opts.listpt
      for i in range(hist.GetN()):
        x = ROOT.Double(0)
        y = ROOT.Double(0)
        hist.GetPoint(i,x,y)
        timestruct = time.localtime( x+seconds_1995 )
        year = timestruct[0]
        month = timestruct[1]
        day = timestruct[2]
        print "  Point %d (%04d-%02d-%02d) has value %f" % (i, year, month, day, y)

  # List the histograms
  if opts.listhist:
    print "List of histogram names to choose from:"
    for name in histList:
      print "  %s" % name
    sys.exit()

  if opts.rmpt is not None:
    if opts.rmpt == "all":
      for name in histDict:
        while histDict[name].GetN():
          histDict[name].RemovePoint(0) # the size of the points shrinks by one until they are all gone
    else:
      try:
        pt = int(opts.rmpt)
        npts = histDict["peak_cluster_pe"].GetN()
        if pt == -1: # remove the last point from each
          for name in histDict:
            lastone = histDict[name].GetN()-1
            histDict[name].RemovePoint(lastone)          
        elif pt > npts:
          sys.exit( "You said to remove point %d, but there are only %d points!" % (pt, npts) )
        elif opts.hist is not None:
          name = opts.hist
          for i in range(pt):
            histDict[name].RemovePoint(0)
      except ValueError:
        sys.exit( "--remove_point must be an integer, and you provided \"%s\", which is not an integer" % opts.rmpt )

  out = ROOT.TFile( "summary_plots_point_removed.root", "RECREATE" )

  out.cd()
  for name in histDict:
    histDict[name].Write()

