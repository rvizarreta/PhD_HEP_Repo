import pprint
import ROOT
ROOT.gROOT.SetBatch(True)
import array
import os
import itertools
import math
import collections
import pickle

TESTING = False
MAXTIMEOFFSET = 5e-3 #1e-1 #0.001

PLOTDT = False

MAX_MISMATCH = 3

class MergeError(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        self.args = args
        self.kwargs = kwargs
        
    def __repr__(self):
        if len(self.args) == 0 and len(self.kwargs) == 0:
            return "MergeError(%s)" % pprint.pformat(self.msg)
        out = ["MergeError(%s, " % pprint.pformat(self.msg)]
        
        out.append("*%s, " % pprint.pformat(self.args))
        out.append("**%s)" % pprint.pformat(self.kwargs))
        return "\n".join(out)
        
    def __str__(self):
        return repr(self)


# -------------- pair matching code -------------------------------------------
def algorithm(l1,l2):
    # Finds all pairs (tx, ty) in the l1, l2 resp.
    # where l1 and l2 are sorted
    # such that,
    # for all ti in l1, abs(ti-ty) > abs(tx-ty) and
    # for all tj in l2, abs(tx-tj) > abs(tx-ty)
    # returns list of tuples (t1, t2, diff)
    # as well as two lists of unmatched l1 and l2 elements resp.
    # 
    # handles the special case where two elements share a time by picking
    # the last time
    
    assert l1 == sorted(l1)
    assert l2 == sorted(l2)
    
    i, j = 0, 0
    pairs = []
    l1unmatched = []
    l2unmatched = []
    spec1 = 0
    spec2 = 0
    while i < len(l1) and j < len(l2):
        b = check(l1, l2, i, j)
        if b == 1:
            dt = (l2[j]-l1[i])
            # skip all events that are too far separated
            if abs(dt) > MAXTIMEOFFSET:
                pass
            else: pairs.append((i, j, dt))
            i += 1
            j += 1
        elif b == 2: 
            i += 1 # special case where l1[i] == l2[i+1]
            spec1 += 1
        elif b == 3: 
            j += 1 # special case where l1[i] == l2[i+1]
            spec2 += 1
        elif l1[i] > l2[j]:
            l2unmatched.append(l2[j])
            j += 1
        elif l2[j] > l1[i]:
            l1unmatched.append(l1[i])
            i += 1
        else: 
            #pass
            print i, j
            print pairs
            raise Exception("This can't happen")
    return pairs, l1unmatched, l2unmatched
        
def check(l1, l2, i, j):
    # we return 2, 3 in an edge case where the next number is the same
    # l1 = [0, 1, 1, 2]
    # l2 = [0, 1, 2, 3]
    # there might be another edge case where the next numbers in both lists
    # is the same,
    # l1 = [0, 1, 1, 2]
    # l2 = [0, 1, 1, 3]
    # in which case we'd want to match the first with the first and
    # second with second.
    t1, t2 = l1[i], l2[j]
    diff = abs(t1 - t2)
    try:
        diff1 = abs(l1[i+1]-t2)
        if diff1 < diff: return 0
        elif diff1 == diff: return 2
    except IndexError:
        pass
    try:
        diff1 = abs(t1-l2[j+1])
        if diff1 < diff: return 0
        elif diff1 == diff: return 3
    except IndexError:
        pass
    return 1

def findallpairs(l1, l2, max_level=0):
    out = []
    ol1, ol2 = l1, l2
    while len(l1) > 0 and len(l2) > 0 and len(out) <= max_level:
        # time pairs are i, j, l2[j]-l1[i]
        timepairs, l1, l2 = algorithm(l1, l2)
        out.append(timepairs)
    return out
    
# -------------- saving code --------------------------------------------------
def makedict(pairs_by_level, maxlevels=-1):
    out = dict()
    for level, pairs in enumerate(pairs_by_level):
        if level > maxlevels and maxlevels >= 0: 
            break
        for i, j, dt in pairs:
            out[i] = (j, dt, level)
    return out
    
def savepairs(f, pairs):
    d = makedict(pairs)
    pickle.dump(d, f)
    
# -------------- camac matching code ------------------------------------------
def makecamacmatches(camactree, maintimes, offset = None, index=None):
    # This is very simple because camac times are a near perfect match of main 
    # detector time.
    
    getcamactime = lambda event: event.Time
    
    # special code for offset (which isn't needed for camac)
    if offset != None: getcamactime = lambda event: event.Time + offset
    
    # get the event times which is all that's needed
    camactimes = map(getcamactime, camactree)
    # match the camac times with the main detector times
    camacpairs = findallpairs(maintimes, camactimes)
    
    if PLOTDT:
        if offset != None: print "Offset =", offset,
        plot(camacpairs, "camac" if offset == None else "camac-%s-%s" % (index, offset))
        
    if len(camacpairs) == 0: raise MergeError("Found no camac pairs at all!")
    #print "Found %s camac pairs" % len(camacpairs[0])
        
    return camacpairs
    
# -------------- plotting code ------------------------------------------------
def plot(pairs_by_level, name="plot"):
    if len(pairs_by_level) == 0:
        raise MergeError("There's nothing to plot")
    pairs = pairs_by_level[0]
    func = lambda x: x[2]
    mindt, maxdt = func(min(pairs, key=func)), func(max(pairs, key=func))
    print "min,max =", (mindt, maxdt)
    import ROOT
    ROOT.gROOT.SetBatch(True)
    mindt, maxdt = (-0.03, 0.03)
    hist = ROOT.TH1D("dt_plot", "dt_plot", 100, float(mindt), float(maxdt))
    for pair in pairs:
        hist.Fill(func(pair))
    c = ROOT.TCanvas("c", "c")
    hist.Draw()
    c.Print(name + ".png")
    del c
    del hist
        
    
# -------------- merging code -------------------------------------------------
def merge(outputfilename, dstfilename, camacfilename=None, mwpcfilename=None, tempfilename=None):
    # return a command that merges the files
    out = ""
    
    print "Trying", 
    print outputfilename
    
    # sanity checks
    if tempfilename is None:
        tempfilename = "tempmergeinfofile.root"
    if camacfilename is None:
        raise MergeError("Camac file is None, that's not supported yet: dst=%s" % dstfilename)
    elif not os.path.exists(camacfilename):
        raise MergeError("camac file '%s' doesn't exist" % camacfilename)
    if mwpcfilename is None:
        raise MergeError("mwpc file is None, that's not supported yet: dst=%s" % dstfilename)
    elif not os.path.exists(mwpcfilename):
        raise MergeError("mwpc file '%s' doesn't exist" % mwpcfilename)
    #print "Sanity checks done", outputfilename
    
    # loads the main detector ttree
    mainfile = ROOT.TFile(dstfilename, "read")
    maintree = mainfile.Get("minerva")
    if maintree == None:
        raise MergeError("Main tree doesn't exist in %s" % camacfilename)
    #print "Loaded main ttree for", outputfilename
    
    # define some functions that get the times
    getmaintime = lambda event: event.ev_gps_time_sec + event.ev_gps_time_usec * 1e-6
    
    # get the event times which is all that's needed
    maintimes = map(getmaintime, maintree)
    
    # find all the pairs of the camac file
    camacpairs = None
    camactree = None
    if camacfilename is not None:
        # load the camac ttree
        camacfile = ROOT.TFile(camacfilename, "read")
        camactree = camacfile.Get("CAMACTree")
    
        # sanity check
        if camactree == None:
            raise MergeError("CAMAC tree doesn't exist in %s" % camacfilename)
        
        # all the camac matching code is contained in a tiny function bc it is easy
        camacpairs = makecamacmatches(camactree, maintimes)
        
    #print "Starting mwpc for", outputfilename
    # find all the pairs of the mwpc file
    mwpcpairs = None
    mwpctree = None
    if mwpcfilename is not None and camacpairs is not None:
        # load the mwpc ttree
        mwpcfile = ROOT.TFile(mwpcfilename, "read")
        mwpctree = mwpcfile.Get("mwpc")
        
        # sanity checks on mwpc and camac trees
        if mwpctree == None:
            raise MergeError("mwpc tree doesn't exist in %s" % mwpcfilename)
        if camactree == None:
            raise MergeError("Need camac tree for mwpc time matching")
            
        mwpcpairs = makemwpcmatches(mwpctree, camactree, camacpairs, maintree)
        
    if mwpcpairs == None:
        if camacpairs == None:
            raise MergeError("There are no mwpc and camac pairs")
        raise MergeError("There are no mwpc pairs")
    if camacpairs == None:
        raise MergeError("There are no camac pairs")
        
    assert type(camacpairs) == list
    assert type(mwpcpairs) == list
        
    temp  = outputfilename.rfind("/")
    if temp < 0: temp = 0
    print "There are", len(camacpairs[0]), "camac pairs,", len(mwpcpairs[0]), "mwpc pairs for", outputfilename[temp:]
    
    #print "Saving for", outputfilename
    with open(tempfilename, "wb") as f:
        # finally output the pairs to a save file
        pickle.dump(outputfilename, f)
        pickle.dump(dstfilename, f)
        pickle.dump(camacfilename, f)
        pickle.dump(mwpcfilename, f)
        savepairs(f, camacpairs)
        savepairs(f, mwpcpairs)
    
    #print "Finishing", outputfilename
    # now create the command that would do the merging
    out = " ".join(("python", "pymerge.py", tempfilename))
    return out
    
# -------------- new mwpc merging code ----------------------------------------
def makemwpcmatches(mwpctree, camactree, camacpairs, maintree):
    ''' First split camac and mwpc data into spill time, by spill. So have 2 dicts, each with list of event number and spill number tuples.
    Then for each spill, pick 1 offset choice.
    Calculate matches for that offset choice.
    Save number of matches and sum dt**2 for offset choice.
    For each spill, pick the best offset choice choice. I think highest N matches is best choice.
    Now recombine matches into one master list and make it ready for merging. '''
    
    # first split into spill, is dict of (spill:list(entry number, time)) pairs.
    mwpc_by_spill = split_by_spill_mwpc(mwpctree)
    camac_by_spill = split_by_spill_camac(camactree)
    
    if len(mwpc_by_spill) == 0:
        if len(camac_by_spill) == 0:
            raise MergeError("There are no camac nor mwpc spills")
        raise MergeError("There are no mwpc spills")
    if len(camac_by_spill) == 0:
        raise MergeError("There are no camac spills")
        
    minmwpc = min(mwpc_by_spill)
    mincamac = min(camac_by_spill)
    
    mwpccamacdifference = minmwpc - mincamac
    # check if there is an offset in mwpc and camac spill numbers
    if mwpccamacdifference == 0: mwpccamacdifference = None
    if mwpccamacdifference == None: 
        # check if there is an extra mwpc spill
        if len(mwpc_by_spill[minmwpc]) == 1 and len(camac_by_spill[minmwpc]) != 1: 
            mwpccamacdifference = 1
    # remap if there's a difference in spill numbers
    if mwpccamacdifference != None: 
        mwpc_by_spill = dict(map(lambda n: (n[0]-mwpccamacdifference, n[1]), mwpc_by_spill.items()))
        minmwpc = min(mwpc_by_spill)
        
    # check if the event numbers are the same between events
    mwpcset = set(mwpc_by_spill)
    camacset = set(camac_by_spill)
    same_n = True
    diffn = dict()
    commonspills = mwpcset & camacset
    for s in commonspills:
        if len(mwpc_by_spill[s]) != len(camac_by_spill[s]):
            same_n = False
            diffn[s] = (len(mwpc_by_spill[s]), len(camac_by_spill[s]), 
                        len(mwpc_by_spill[s]) - len(camac_by_spill[s]))
    total_dn = 0
    diff_spill = None
    for spill, idk in diffn.items():
        a, b, dn = idk
        total_dn += abs(dn)
        diff_spill = spill
    if total_dn > 1:
        temp = "mwpc and camac spill numbers different\n    {camac spill number: (mwpc len, camac len, m-c diff)}:\n"
        idk = pprint.pformat(diffn)
        temp += idk
        raise MergeError(temp)
    elif total_dn == 1:
        print "Cutting out different spill numbers on spill", diff_spill,". len(mwpc) =", len(mwpc_by_spill[diff_spill]), ". len(camac) =", len(camac_by_spill[diff_spill])
        del mwpc_by_spill[diff_spill]
        del camac_by_spill[diff_spill]
        commonspills.remove(diff_spill)
        
        
    # now we have two dicts where the events match exactly 1 to 1.
    # So we now have to match each mwpc with each main tree event.
    camacpairs = camacpairs[0] # Remove the level system, now we have main
    
    # so camacpairs is (main event number, camac event number, dt) list
    # I want to swap to camac event number to main event number dict
    camac_to_main_map = dict(map(lambda e: (e[1], e[0]), camacpairs))
    
    # now I need a list of all mwpc events and which camac event goes with it
    camac_mwpc_pairs = []
    for s in commonspills:
        # a list of (event number, time) pairs
        list_of_mwpc_events_and_time_in_spill = mwpc_by_spill[s]
        list_of_camac_events_and_time_in_spill = camac_by_spill[s]
        # cut down the list of event numbers for this spill
        list_of_mwpc_events_in_spill = map(lambda e: e[0], list_of_mwpc_events_and_time_in_spill)
        list_of_camac_events_in_spill = map(lambda e: e[0], list_of_camac_events_and_time_in_spill)
        # from the code above, this should always work
        assert len(list_of_mwpc_events_in_spill) == len(list_of_camac_events_in_spill)
        # do a 1 to 1 matching
        camac_mwpc_pairs_in_spill = zip(list_of_camac_events_in_spill, list_of_mwpc_events_in_spill)
        # add matches to total list
        camac_mwpc_pairs.extend(camac_mwpc_pairs_in_spill)
        
    # finally remap camac to main event numbers, and add the dt
    main_mwpc_pairs = []
    for camac, mwpc in camac_mwpc_pairs:
        try:
            # get the main event number
            main_event_number = camac_to_main_map[camac]
        except KeyError: continue # camac_to_main_map doesn't have the event, skip
        else:
            # get the entries to calc dt
            mwpctree.GetEntry(mwpc)
            maintree.GetEntry(main_event_number)
            # calc dt
            dt = mwpctree.mwpc_event_time - (maintree.ev_gps_time_sec + maintree.ev_gps_time_usec * 1e-6)
            # add the info to output
            info = (main_event_number, mwpc, dt)
            main_mwpc_pairs.append(info) 
            
    return [main_mwpc_pairs] # make pairs at level 0
    
class NoSpill(Exception):
    pass
    
def split_by_spill_mwpc(tree):
    spill_func = lambda x: x.mwpc_spill_num
    time_func = lambda x: x.mwpc_event_time
    return split_by_spill(tree, spill_func, time_func)
    
def split_by_spill_camac(tree):
    def spill_func(x):
        if x.In_spill == 1:
            return x.Spill_number
        else: raise NoSpill()
    time_func = lambda x: x.Time
    return split_by_spill(tree, spill_func, time_func)
    
def split_by_spill(tree, spill_func, time_func):
    # returns a dictionary of spill, list of times pairs
    # the times are (tree entry number, time)
    out = collections.defaultdict(list)
    # make sure we're at the begining
    tree.GetEntry(0)
    for i, event in enumerate(tree):
        try:
            spill = spill_func(event)
        # skip events that don't happen in spill
        except NoSpill: continue
        else:
            time = time_func(event)
            tup = (i, time)
            out[spill].append(tup)
    # now reset the tree
    tree.GetEntry(0)
    return dict((spill, l) for spill, l in out.items())
    
    
# -------------- testing code -------------------------------------------------
def testmerge():
    filename = "/minerva/data/testbeam2/prelim_run_dst/DST_4GeV_Pos_Pions/TB_00001125_0042_cosmc_v09_1503052305_DST.root"
    camacfilename = "/minerva/data/testbeam2/prelim_run_dst/DST_4GeV_Pos_Pions/TB_00001125_0042_cosmc_v09_1503052305_camac.root"
    mwpcfilename = "../mwpc/myTest.root"
    filename = "/minerva/data/testbeam2/run2data/10GeV_Neg_Pions/TB_00001538_0005_cosmc_v09_1504271107_DST.root"
    camacfilename = "/minerva/data/testbeam2/run2data/10GeV_Neg_Pions/TB_00001538_0005_cosmc_v09_1504271107_camac.root"
    mwpcfilename = "/minerva/data/testbeam2/run2data/10GeV_Neg_Pions/TB_00001538_0005_cosmc_v09_1504271107_mwpc.root"
    #filename = "/minerva/data/testbeam2/run2data/16GeV_Pos_Pions/TB_00001534_0004_cosmc_v09_1504262359_DST.root"
    #camacfilename = "/minerva/data/testbeam2/run2data/16GeV_Pos_Pions/TB_00001534_0004_cosmc_v09_1504262359_camac.root"
    #mwpcfilename = "/minerva/data/testbeam2/run2data/16GeV_Pos_Pions/TB_00001534_0004_cosmc_v09_1504262359_mwpc.root"
    #mwpcfilename = "myTest.root"
    outfilename = "test.root"
    command = merge(outfilename, filename, camacfilename, mwpcfilename)
    print command
        
if __name__ == "__main__":
    try:
        testmerge()
    except MergeError as e:
        print e
    #testalgorithm()
    
