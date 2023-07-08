# This script remove the ntuples from dcache, requiered when you want to resubmit jobs
import time
import os
import sys
import glob

prefix = '/pnfs/minerva/scratch/users/%s/data_processing/grid/minerva' % os.getenv("USER")
sver = os.getenv("MINERVA_RELEASE")


def removeStuff( ftype, this_year, this_month, this_day ):
    # Look for today's playlist
    playlist = open( 'playlists/playlist_daily_%04d-%02d-%02d.txt' % (this_year,this_month,this_day), 'r' )

    runs = playlist.readlines()
    fcount = 0
    for run in runs:
        runno = int(run.split()[0])
        rundir = "%s/%s/numibeam/%s/%02d/%02d/%02d/%02d" % (prefix,ftype, sver,runno/1000000,(runno%1000000)/10000, (runno%10000)/100, runno%100)
        files = os.listdir(rundir)
        delete_subs_strs = (run.split()[1]).split(",")
        delete_subs = [int(sub) for sub in delete_subs_strs]
        for f in files:
            if ftype == "calib" or ftype == "dst":
                subno = int(f.split("_")[2])
                if subno in delete_subs:
                    os.remove("%s/%s"%(rundir,f))
                    fcount += 1
            elif ftype == "logfiles" or ftype == "opts":
                os.remove("%s/%s"%(rundir,f))
                fcount += 1
    print "Removed %d root files from dcahe: %d / %d / %d" % (fcount, this_year, this_month, this_day)

if __name__ == "__main__":
    # Get Time
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

    removeStuff( "calib", this_year, this_month, this_day )
    removeStuff( "dst", this_year, this_month, this_day )
    removeStuff( "logfiles", this_year, this_month, this_day )
    removeStuff( "opts", this_year, this_month, this_day)


