import glob
import os
import subprocess
import shlex
import multiprocessing
ncpus = 23
import time
import pprint

from mergev4 import MergeError
import mergev4

# cp /minerva/app/users/kleykamp/testbeam2/Merge/* .
# python -c "import process; process.dst()"

# constants
# merging constants
# where the dsts are stored
dst_indir="/minerva/data/testbeam2/run1data"
# the directory where the merged files are placed
merge_dir="/minerva/data/testbeam2/run2datamerged_new3"
# whether to only focus on making new merged files
NEWMERGEDONLY = False

DONTMERGE = False
usemultiprocessing = True # Because it doesn't work for the initial merging...

# mwpc constants
# where the mwpc output file is put (ideally same as dst_indir)
dst_outdir="/minerva/data/testbeam2/run1data_newmwpc" #dst_indir
# where all the mwpc raw data files are stored
mwpc_rawdata="/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc"
# whether to only create new mwpc files
NEWMWPCONLY = False

newdstdir = "/minerva/data/testbeam2/run1data_new"
dst_rawdata = "/minerva/data/testbeam2/rawdata/testbeam/raw"
NEWDSTONLY = False
DSTTESTMODE = False


def dst():
    # run like, 
    # python -c "import process; process.dst()"
    
    # Note: This uses the mapping of dst_indir to decide where to put the files
    
    files = getfiles(dst_rawdata, "RawData.dat")
    filemap = mapchars()
    filed = dict()
    for f in files:
        try:
            fi = getfile(filemap, f, newdstdir)
            # remove "_RawData.dat" at the end
            fi = fi[:-12]
            if NEWDSTONLY and os.path.exists(fi): continue
            filed[f] = fi
        except KeyError: pass
    
    '''for f, fi in filed.items(): # test stuff
        pprint.pprint(f)
        pprint.pprint(fi)
        foo = os.path.split(fi)[1]
        bar = foo[0:37] # TB_00001125_0042_cosmc_v09_1503052305
        run = int(bar[3:11])
        subrun = int(bar[12:16])
        print run, subrun, bar[3:11], bar[12:16]
        exit()'''
    nfiles = 0
    p = multiprocessing.Pool(ncpus)
    calls_and_errors = p.map(makedst, filed.values())
    for call, error in calls_and_errors:
        if error is not None: continue
        nfiles += 1
        
    print "Finished processing %s files" % nfiles
    
def makedst(outputfile):
    assert not outputfile.endswith("dat") # double check that I'm not doing anything to raw files
    result = None
    error = None
    directory = os.path.split(outputfile)[0]
    if not os.path.exists(directory) and not DSTTESTMODE:
        os.makedirs(directory)
    print "Working on %s" % outputfile
    try:
        # possible options files
        # BuildRawDigits_fRawData.opts  DST-TBII.opts  filtercosmics.opts  LLBuildDST.opts  LLBuildDST_Quick.opts  Plex-TB2.opts  testbeam2-maketracks.opts
        """./makedst.sh -o ~/DST/testbeam2-maketracks.opts -r 1449 -s 5 -a"""
        foo = os.path.split(outputfile)[1]
        bar = foo[0:37] # TB_00001125_0042_cosmc_v09_1503052305
        run = int(bar[3:11])
        subrun = int(bar[12:16])
        temp = "./makedst.sh -o ~/DST/testbeam2-maketracks.opts -r %s -s %s -a -z %s" % (run, subrun, outputfile)
        if DSTTESTMODE: 
            print temp
            result = 0
        else: 
            print "command:", temp
            #result = subprocess.check_call(shlex.split(temp))
            # TODO remove shell
            result = subprocess.check_call(temp, shell=True)
    except subprocess.CalledProcessError as e:
        error = (e, outputfile)
    # return (result, error) tuple
    return (result, error)

# used for both mwpc stuff and merging stuff
def getfiles(start, end):
    # gets all the files that end with "end" in dir "start"
    print "Getting files in %s ending with %s" % (start, end)
    call = "find %s -print | grep %s$" % (start, end)
    s = subprocess.Popen(call, shell=True, stdout=subprocess.PIPE).communicate()[0]
    files = s.split()
    #print files
    """idk = os.walk(start)
    files = []
    for root, d, fl in idk:
        for f in fl:
            if f.endswith(end): 
                path = os.path.join(root, f)
                files.append(path)"""
    print "Done with search. Found %s files" % len(files)
    return files
    
def mapchars():
    # Creates a map of the filename (ie TB_00001125_0042_cosmc_v09_1503052305)
    # with directory name (ie 4GeV_Pion).
    # This tells you basically what directory you should put it in
    # based on run and subrun number.
    out = dict()
    files = getfiles(dst_indir,"DST.root")
    for f in files:
        head, tail = os.path.split(f)
        tail = tail[0:37]
        #out[tail] = os.path.split(head)[1]
        out[tail] = head.replace(os.path.commonprefix([dst_indir + "/", head]), "")
    return out
    
def getfile(filemap, infile, outdir):
    # uses the filename to place the infile in the correct output file
    # ie /something/TB_00001125_0042_cosmc_v09_1503052305.root gets put into
    # <outdir>/<filemap directory for "TB_00001125_0042...">/infile
    head, tail = os.path.split(infile)
    # The key is something like "TB_00001125_0042_cosmc_v09_1503052305"
    key = tail[0:37]
    # Gets the directory like, 4GeV_Pion
    d = filemap[key]
    # creates the output file location
    # like <outdir>/<filemap directory for "TB_00001125_0042...">/infile 
    out = os.path.join(outdir, d, tail)
    return out

import mwpc as mwpc1
# mwpc stuff
def mwpc():
    # first gets all the mwpc data files from where the raw data is stored
    # second creates a map between the filename and directory name
    # third, loop through the files and find out if there's a directory (like 4GeV_Pion) to put the file
    # fourth, loop through each mwpc file and make it, and put in correct output location
    files = getfiles(mwpc_rawdata, "mwpc.dat")
    filemap = mapchars()
    filed = dict()
    for f in files:
        try:
            fi = getfile(filemap, f, dst_outdir)
            # remove ".dat" at the end and replace with ".root"
            fi = fi[:-3] + "root"
            filed[f] = fi
        except KeyError: pass
    nfiles = 0
    
    '''for f, fi in filed.items():
        # skip existing mwpc files if NEWMWPCONLY is true
        if NEWMWPCONLY and os.path.exists(fi): continue
        directory = os.path.split(fi)[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
        print "Making %s, %s" % (f, fi)
        try:
            mwpc.main(f, fi)
        except Exception as e: 
            print "Error:", repr(e)
            continue
        nfiles += 1'''
    p = multiprocessing.Pool(ncpus)
    calls_and_errors = p.map(domwpcstuff, filed.items())
    nfiles = len(list(filter(lambda x: x[0] is not None, calls_and_errors)))
    print "Finished processing %s files" % nfiles
    
def domwpcstuff(args):
    f, fi = args
    # skip existing mwpc files if NEWMWPCONLY is true
    if NEWMWPCONLY and os.path.exists(fi): return (None, None)
    directory = os.path.split(fi)[0]
    if not os.path.exists(directory):
        os.makedirs(directory)
    print "Making %s, %s" % (f, fi)
    try:
        mwpc1.main(f, fi)
    except Exception as e: 
        print "Error:", repr(e)
        return (None, repr(e))
    return (True, None)
    
        
def map_(files):
    out = dict([(os.path.split(f)[1][0:37], f) for f in files])
    return out
        
def merge(shfile="sh_merge.sh"):
    start_time = time.time()
    # gets a list of all the dst, camac, mwpc files
    dst = getfiles(dst_indir, "DST.root")
    camac = getfiles(dst_indir, "camac.root")
    mwpc = getfiles(dst_indir, "mwpc.root")
    # creates a map for "TB_00001125_0042..." and actual file
    dstmap = map_(dst)
    camacmap = map_(camac)
    mwpcmap = map_(mwpc)
    
    finalmap = dict()
    # creates a map for "TB_00001125_0042..." to output directory like "4GeV_Pion"
    filemap = mapchars()
    index = 0
    if not os.path.exists("temp"):
        os.makedirs("temp")
    # loop through each dst file and find the corresponding mwpc, CAMAC files
    for tail, df in dstmap.items():
        # create the output file name
        # TODO A directory within the (for example) 10GeVElectron directory won't
        # stay inside that directory after this treatment. I should really do
        # a cut of directories between /a/b/ and /a/b/c/d such that the 
        # output is c/d instead of just d.
        out = os.path.join(merge_dir, filemap[tail], tail)  + "_mergedDST.root"
        
        # skip files that already exist if that option is set
        if NEWMERGEDONLY and os.path.exists(out):
            continue
            
        # finds the mwpc file corresponding to the dst file
        mwpcf = None
        try:
            mwpcf = mwpcmap[tail]
        except KeyError: pass
        # finds the camac file corresponding to the dst file
        camacf = None
        try:
            camacf = camacmap[tail]
        except KeyError: pass
        
        # makes sure the directory exists for the output file
        directory = os.path.split(out)[0]
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        # creates an independent file to save the merge info
        tempfilename = "temp/tempmergeinfo_%s.root" % index
        if camacf is not None and mwpcf is not None:  # TODO remove None filename restriction when merge can handle
            finalmap[tail] = (out, df, camacf, mwpcf, tempfilename)
        else:
            try:
                if "pdstl" in camacf or "linjc" in camacf:
                    # skip pedestal and light injection since they won't be merged
                    continue
            except TypeError: pass # in case camacf is none
            try:
                if "pdstl" in mwpcf or "linjc" in mwpcf:
                    # skip pedestal and light injection since they won't be merged
                    continue
            except TypeError: pass
            print "One of two files doesn't exist/is-None: \n%s, \n%s" % (camacf, mwpcf)
        # ups the index used to create unique merge file names
        index += 1
    # now that we have all the files, create the merge command
    errorlog = []
    failedcalls = []
    no_merge_error = 0
    merge_error = 0
    failed_calls = 0
    #with open(shfile, "w") as f:
    calls = []
    try:
        if not usemultiprocessing:  
            for index, args in enumerate(finalmap.values()):
                # run the merge cord which gives a command
                try:
                    temp = mergev4.merge(*args)
                except MergeError as e: 
                    errorlog.append(str(("for %s:" % args[0], repr(e), str(args) ) ))
                    print "for %s:" % args[0], repr(e)
                    merge_error += 1
                else:
                    print "No MergeError for", args[0]
                    no_merge_error += 1
                    calls.append((args, temp))
        else:
            # use multiprocessing to take advantage of multiple processors
            p = multiprocessing.Pool(ncpus)
            calls_and_errors = p.map(runmergecode, enumerate(finalmap.values()))
            # finally, filter out the calls and the errors
            for call, error in calls_and_errors:
                if call is not None:
                    calls.append(call)
                    no_merge_error += 1
                if error is not None:
                    merge_error += 1
                    errorlog.append(error)
        # now do the actual merging
        print "Finished getting merge files"
        with open("allcalls.txt", "w") as f:
            f.write("\n".join(map(lambda x: x[1], calls)))
        if not DONTMERGE:
            p = multiprocessing.Pool(ncpus)
            output = p.map(process, calls)
            output = filter(lambda x: x != None, output)
            failedcalls.extend(output)
            failed_calls += len(output)
        else:
            print "I'm not merging, saved calls in allcalls.txt"
    finally:
        print "Tally."
        print "No MergeError:", no_merge_error
        print "MergeError:", merge_error
        print "FailedCall after no MergeError:", failed_calls
        with open("errors.log", "w") as f:
            f.write("\n".join(errorlog))
        with open("failedcalls.log", "w") as f:
            f.write("\n".join(failedcalls))
        print "Run time in seconds:", time.time() - start_time
        
def runmergecode(index_args):
    index, args = index_args
    out = [None, None]
    # run the merge cord which gives a command
    try:
        temp = mergev4.merge(*args)
    except MergeError as e: 
        
        out[1] = str(("for %s:" % args[0], repr(e), str(args) ) )
        print "for %s:" % args[0], repr(e)
    else:
        print "No MergeError for", args[0]
        out[0] = (args, temp)
    return tuple(out)
            
def process(idk):
    args, temp = idk
    try:
        subprocess.check_call(shlex.split(temp))
    except subprocess.CalledProcessError as e:
        errorlog.append(str(("for %s:" % args[0], repr(e), str(args))))
        print "for %s (Not MergeError):" % args[0], repr(e)
        return temp
    else:
        return None
    

#mwpc()
#merge()
