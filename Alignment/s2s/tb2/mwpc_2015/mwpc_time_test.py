

import ROOT
import glob
import pprint
import itertools
import os

class SpillInfo(object):
    def __init__(self, spillnum):
        self.t_spill_start = None
        self.t_spill_end = None
        self.t_spill_avg = None
        self.t_spill_length = None
        self.t_n_events = None
        self.dt_avg = None
        self.dt_max = None
        self.dt_min = None
        self.dt_n_events = None
        self.spill_number = spillnum
    def __repr__(self):
        s = "SpillInfo(Spill#=%s" % str(self.spill_number)
        out = [s]
        out.append("t_start=%s" % str(self.t_spill_start))
        out.append("t_end=%s" % str(self.t_spill_end))
        out.append("t_spill_length=%s" % str(self.t_spill_length))
        out.append("t_avg=%s" % str(self.t_spill_avg))
        out.append("t_n=%s" % str(self.t_n_events))
        out.append("\n            dt_avg=%s" % str(self.dt_avg))
        out.append("dt_n=%s" % str(self.dt_n_events))
        out.append("dt_min=%s" % str(self.dt_min))
        out.append("dt_max=%s" % str(self.dt_max))
        return ", ".join(out) + ")"
        
def compute_variables(a):
    if len(a) == 0:
        return None, 0, None, None
    sum_ = sum(a)
    avg = None
    if len(a) > 0:
        avg = sum_ / float(len(a))
    min_, max_ = min(a), max(a)
    return avg, len(a), min_, max_

def compute(tree, time, spill, filt=None):

    out = []
    
    # declare some variables
    current_spill = None
    current_spill_number = None
    dt_array = []
    time_array = []
    current_time = None
    
    # loop over each event in the ttree
    for event in tree: #mwpcchain:
        # decide if the event needs to be filtered (ie camac.in_spill < 0.5)
        if filt is not None and filt(event): continue
        # if the spill numbers don't match
        if current_spill_number != spill(event): 
            # here we want to finalize the previous spill, and start the next spill
            
            if current_spill != None:
                c = current_spill
                c.dt_avg, c.dt_n_events, c.dt_min, c.dt_max = compute_variables(dt_array)
                c.t_spill_avg, c.t_n_events, c.t_spill_start, c.t_spill_end = compute_variables(time_array)
                c.t_spill_length = c.t_spill_end - c.t_spill_start
                # finally add the spill to the output
                out.append(current_spill)
            
            # reset all variables
            current_spill_number = int(spill(event))
            current_spill = SpillInfo(current_spill_number)
            dt_array = []
            time_array = []
            current_time = None
        # add number of running average
        last_time = current_time
        current_time = time(event)
        time_array.append(current_time)
        if last_time != None:
            dt = current_time - last_time
            dt_array.append(dt)
    return out
    
def makemap(files):
    out = dict()
    for f in files:
        name = os.path.basename(f)
        key = name[0:37]
        out[key] = f
    return out
    
def loadttree(filename, ttree):
    f = ROOT.TFile(filename)
    out = f.Get(ttree)
    return f, out
    
def makedict(spills):
    out = dict()
    for s in spills:
        out[s.spill_number] = s
    return out

def main(nfiles = None):
    mwpcchain = ROOT.TChain()
    camacchain = ROOT.TChain()
    dir_ = "/minerva/data/testbeam2/run1data/"
    
    mwpcfiles = sorted(glob.glob(dir_ + "*/*mwpc.root"))
    camacfiles = sorted(glob.glob(dir_ + "*/*camac.root"))
    
    mwpcmap = makemap(mwpcfiles)
    camacmap = makemap(camacfiles)
    
    # we only want files that exist for both mwpc and camac
    s1 = set(mwpcmap)
    s2 = set(camacmap)
    temp = s1 ^ s2
    n_non_common_files = len(temp)
    n_non_common_files_mwpc = len(temp & s1)
    n_non_common_files_camac = len(temp & s2)
    common_files = sorted(s1 & s2)
    #print s1 ^ s2
    # cut length if needed
    if nfiles is not None:
        common_files = common_files[:nfiles]
        
    total_camac_n = 0
    total_mwpc_n = 0
    total_both_n = 0
    total_both_n_mwpc = 0
    total_both_n_camac = 0
    total_camac_spills = 0
    total_mwpc_spills = 0
    total_both_spills = 0
    no_mwpc = 0
    no_camac = 0
    mwpc_extra_spill = 0
    mwpc_off = 0
    mwpc_camac_dn = 0
    file_and_spills_for_camac_and_mwpc = 0
    ratio_sum = 0
    ratio_n = 0
    dt_sum_camac = 0
    dt_sum_mwpc = 0
    dt_n = 0
    
    # now add the remaining files
    for key in common_files:
        #print "On", key
        #mwpcchain.Add(mwpcmap[key] + "/mwpc")
        #camacchain.Add(camacmap[key] + "/CAMACTree")
        
        f1, mwpcchain = loadttree(mwpcmap[key], "mwpc")
        f2, camacchain = loadttree(camacmap[key], "CAMACTree")
        
        mwpcspills = compute(mwpcchain, lambda x: float(x.mwpc_event_time), lambda x: int(x.mwpc_spill_num))
        # TODO add Good_event flag,
        # It's Good_event == 1. One caveat is that before March 6th at 4:30 it was reversed. That is, Good_event == 0 meant it was a good event. For v2 and beyond it's fixed. Is the version number in the camac root files? No idea.
        camacspills = compute(camacchain, lambda x: float(x.Time), lambda x: int(x.Spill_number), lambda x: x.In_spill < 0.5)
    
        #print "mwpc spills:"
        #pprint.pprint(mwpcspills)
        #print "camac spills:"
        #pprint.pprint(camacspills)
        
        if len(mwpcspills) == 0:
            if len(camacspills) == 0: 
                print "no camac nor mwpc spills for", key
                continue
            print "no mwpc spills for", key, "; there are %s camac spills" % len(camacspills)
            no_mwpc += 1
            continue
        
        if len(camacspills) == 0:
            print "no camac spills for", key
            no_camac += 1
            continue
            
        file_and_spills_for_camac_and_mwpc += 1
        
        
        # turn it into a dict
        mwpcspilldict = makedict(mwpcspills)
        camacspilldict = makedict(camacspills)
        #pprint.pprint(mwpcspilldict)
        #pprint.pprint(camacspilldict)
        minmwpc = min(mwpcspilldict)
        mincamac = min(camacspilldict)
        mwpccamacdifference = minmwpc - mincamac
        if mwpccamacdifference == 0: mwpccamacdifference = None
        else: mwpc_off += 1
        # code below catches 'one extra mwpc spill'
        if mwpccamacdifference == None: 
            if mwpcspilldict[minmwpc].t_n_events == 1 and camacspilldict[minmwpc].t_n_events != 1: 
                mwpccamacdifference = 1
                mwpc_extra_spill += 1
                #print "Doing that thing", mwpccamacdifference
            #else: continue
        if mwpccamacdifference != None: #minmwpc != mincamac:
            #print minmwpc, " != ", mincamac, key
            #mwpccamacdifference = minmwpc - mincamac
            mwpcspilldict = dict(map(lambda n: (n[0]-mwpccamacdifference, n[1]), mwpcspilldict.items()))
            minmwpc = min(mwpcspilldict)
            #print minmwpc, " ?= ", mincamac
        #else: continue
        mwpcset = set(mwpcspilldict)
        camacset = set(camacspilldict)
        #if minmwpc == mincamac: continue
        '''if minmwpc != mincamac:
            print "minmwpc != mincamac", minmwpc, mincamac
            print "mwpc:", mwpcspilldict[minmwpc]
            print "camac:", camacspilldict[mincamac]
        if mwpcset != camacset:
            s = mwpcset ^ camacset
            print "mwpcset != camacset", s
            for n in s:
                if n in mwpcset:
                    print "mwpc:", mwpcspilldict[n]
                if n in camacset:
                    print "camac:", camacspilldict[n]'''
        same_n = True
        for s in mwpcset & camacset:
            if mwpcspilldict[s].t_n_events != camacspilldict[s].t_n_events:
                same_n = False
                break
                
        # do 'if <condition>: continue' here
        if same_n: continue # worry about spills with different numbers of events
        #if mwpcset == camacset: continue # worry about spills different numbers of spills
                    
        all_spills = mwpcset | camacset
        last = 100000
        form = "{0:>12}|{1:>12}|{2:>15}|{3:>15}|{4:>10}|{5:>15}|{6:>15}|{7:>15}|{8:>15}|{9:>15}|{10:>15}|"
        print key
        #print form.format("mwpc spill", "camac spill", "mwpc start T", "camac start T", "c-m dt", "mwpc end T", "camac end T", "c-m dt", "mwcp spill t", "camac spill t", "c-m dt")
        print form.format("mwpc spill", "camac spill", "mwpc start T", "camac start T", "c-m dt", "mwcp spill t", "camac spill t", "ratio", "mwpc n", "camac n", "c-m dn")
        for s in all_spills:
            try: mwpcspill = mwpcspilldict[s]
            except KeyError: mwpcspill = SpillInfo(None)
            try: camacspill = camacspilldict[s]
            except KeyError: camacspill = SpillInfo(None)
            args = [mwpcspill.spill_number, camacspill.spill_number]
            # start time
            camacmpwcstartdt = None
            try: camacmpwcstartdt = camacspill.t_spill_start - mwpcspill.t_spill_start
            except Exception: pass
            mwpcstartt = mwpcspill.t_spill_start % last if mwpcspill.t_spill_start != None else None
            camacstartt = camacspill.t_spill_start % last if camacspill.t_spill_start != None else None
            args.extend([mwpcstartt, camacstartt, camacmpwcstartdt])
            # end time
            '''camacmpwcstartdt = None
            try: camacmpwcstartdt = camacspill.t_spill_end - mwpcspill.t_spill_end
            except Exception: pass
            mwpcstartt = mwpcspill.t_spill_end % last if mwpcspill.t_spill_end != None else None
            camacstartt = camacspill.t_spill_end % last if camacspill.t_spill_end != None else None
            args.extend([mwpcstartt, camacstartt, camacmpwcstartdt])'''
            # spill length time
            args.append(mwpcspill.t_spill_length)
            args.append(camacspill.t_spill_length)
            try: 
                #args.append(camacspill.t_spill_length - mwpcspill.t_spill_length)
                if mwpcspill.t_spill_length != 0:
                    idk = camacspill.t_spill_length/mwpcspill.t_spill_length
                    if camacspill.t_n_events == mwpcspill.t_n_events and mwpcspill.t_n_events > 10:
                        ratio_sum += idk
                        ratio_n += 1
                    if camacspill.dt_n_events == mwpcspill.dt_n_events and mwpcspill.dt_n_events > 10:
                        dt_sum_camac += camacspill.dt_avg * camacspill.dt_n_events
                        dt_sum_mwpc += mwpcspill.dt_avg * mwpcspill.dt_n_events
                        dt_n += mwpcspill.dt_n_events
                else: idk = 0
                args.append(idk)
            except TypeError: args.append(None)
            # n events
            args.append(mwpcspill.t_n_events)
            args.append(camacspill.t_n_events)
            try: args.append(camacspill.t_n_events - mwpcspill.t_n_events)
            except TypeError: args.append(None)
            print form.format(*args)
            
            # track stats
            if camacspill.t_n_events != None:
                total_camac_n += camacspill.t_n_events
                total_camac_spills += 1
            if mwpcspill.t_n_events != None:
                total_mwpc_n += mwpcspill.t_n_events
                total_mwpc_spills += 1
            if camacspill.t_n_events != None and mwpcspill.t_n_events != None :
                if mwpcspill.t_n_events == camacspill.t_n_events:
                    total_both_n += mwpcspill.t_n_events
                total_both_n_mwpc += mwpcspill.t_n_events
                total_both_n_camac += camacspill.t_n_events
                mwpc_camac_dn += abs(camacspill.t_n_events - mwpcspill.t_n_events)
                    
                total_both_spills += 1
                
    print "total_camac_n", total_camac_n
    print "total_mwpc_n", total_mwpc_n
    print "total_both_n", total_both_n
    print "total_both_n_mwpc", total_both_n_mwpc
    print "total_both_n_camac", total_both_n_camac
    print "total_camac_spills", total_camac_spills
    print "total_mwpc_spills", total_mwpc_spills
    print "total_both_spills", total_both_spills
    print "mwpc_extra_spill (mwpc has 1 event spill at first)", mwpc_extra_spill 
    print "mwpc_off (ie mwpc min is diff from camac min)", mwpc_off 
    print "mwpc_camac_dn", mwpc_camac_dn
    print "no_mwpc spills in file", no_mwpc
    print "no_camac spills in file", no_camac
    print "file_and_spills_for_camac_and_mwpc", file_and_spills_for_camac_and_mwpc
    print "n_non_common_files", n_non_common_files
    print "n_non_common_files_mwpc", n_non_common_files_mwpc 
    print "n_non_common_files_camac", n_non_common_files_camac
    print
    print "Ratio average:", ratio_sum / float(ratio_n)
    print "Ratio n:", ratio_n
    print
    print "Average camac dt:", dt_sum_camac / float(dt_n)
    print "Average mwpc dt:", dt_sum_mwpc / float(dt_n)
    print "dt n:", dt_n
    
    # In theory the mwpc time is based on the number of ticks
    # so the lengths might not be the same
    # So this is the ratio of the spill lengths (camac / mwpc)
    # for spills with equal number of camac and mwpc events
    # and more than 10 events.
    # Here the average is the ratio sum / number of spills which qualify.
    ''' Run 1 average:
    Ratio average: 0.997425190672
    Ratio n: 4030'''
    
    ''' Run 2 average:
    Ratio average: 0.997436409122
    Ratio n: 3498'''
    
    ''' Run 3 average:
    Ratio average: 0.997439748704
    Ratio n: 1030'''
    
    
    '''l1, l2 = c, f 
    
    print "Lengths", len(l1), len(l2)
    offset = 1435365600
    #offset = 1435367432.59
    i, j = 1, 1
    #for i, k in zip(a, d):
    form = "{0:15}|{1:15}|{2:15}|{3:10}|{4:10}|"
    print form.format("dt", "mwpc t", "camac t", "mwpc spill", "camac spill")
    while i < len(l1) and j < len(l2):
        #print i, k
        spill, t1 = l1[i] 
        spill2, t2 = l2[j]
        if spill < spill2:
            # catchup mwpc
            i += 1
        elif spill > spill2:
            # catchup camac
            j += 1
        else:
            # spills match
            assert(spill == spill2)
            print form.format(t1 - t2, t1-offset, t2-offset, spill, spill2)
            # increment counters
            i += 1
            j += 1
    
    # want mwpc_event_time, mwpc_spill_num
    # want Time, Spill_number, In_spill'''
    
main()
