import ROOT
ROOT.gROOT.SetBatch(True)

import pprint
import array
import time
import sys
import pickle

def merge(outfilename, mainfilename):
    mainttree = "minerva"

    print "Loading ttrees for", outfilename
    # load all ttrees
    mainfile, main = loadtree(mainfilename, mainttree)
    # create new ttree
    f = ROOT.TFile(outfilename, "recreate")
    new = ROOT.TTree("minerva", "")
    
    #print "Copy branches"
    # copy over branches, also save branch info
    mainsinglebranches, mainarraybranches, mainlengthbranches = copy_branches(main, new)
    # add special branches like 'mwpc_match'
    ev_run_array = array.array("i", [0])
    ev_run_branch = new.Branch("ev_run", ev_run_array, "ev_run/I")
    
    # loop over each main entry
    start_time = time.clock()
    entries = main.GetEntries()
    print "Starting loop of", entries, "entries." 
    for i, entry in enumerate(main):
        d = locals()
        copy_values(main, new, mainsinglebranches, mainarraybranches, d)
        
        ev_run_array[0] = 1304
        
        # fill TTree
        new.Fill()
        
        # print timing info, note 1000 entries
        c = time.clock()
        elapsed_time = c - start_time 
        dt = (c - start_time) / (i + 1)
        remaining_time = (entries - i) * dt
        total_time = entries * dt
        if (i % 100 == 0 and i > 10) or i in (5, 10, 25, 50, 75):
            print "On {0: >5}, est. remaining time = {1:7.0f}s, elapsed time = {2:7.0f}s, est. total time = {3:7.0f}s".format(i, remaining_time, elapsed_time, total_time)
    
    new.Write()
    f.Close()
    
def copy_values(a, b, singlebranches, arraybranches, d):
    # d -- need to import the locals from the previous loop or else the 
    #      the arrays are recycled and you get a seg fault...
    d["a"] = a
    d["b"] = b
    g = globals()
    # copy over non-array branches.
    for branch, type_ in singlebranches.items():
        array_type = getarraytype(type_)
        default_value = getdefaultvalue(type_)
        
        # special case code for '$00_Count'
        branch_ori = branch
        if branch[0] == "$":
            branch = branch.replace("$", "S")
        
        exec("{0}_array = array.array('{1}', [{2}])".format(branch, array_type, default_value), g, d)
        # TODO if changed $00 name then branch_ori can be replaced with branch, but keep branch ori for below
        exec("{0}_branch = b.GetBranch('{1}')".format(branch, branch_ori), g, d)
        exec("{0}_branch.SetAddress({0}_array)".format(branch), g, d)
        # could have used "{0}_array[0] = a.{0}" if not for $...
        exec("{0}_array[0] = getattr(a, '{1}')".format(branch, branch_ori), g, d)
        
    # save array branches
    for branch, arraylength_andtype in arraybranches.items():
        arraylength, type_ = arraylength_andtype
        
        # get the array length, it's either an int or an array branch
        if type(arraylength) == int: 
            length = arraylength
        else: 
            t = "a.{0}".format(arraylength)
            length = eval(t)
        # we need a physical address so the length can't be 0
        final_array_length = length if length > 0 else 1
        
        # make array
        array_type = getarraytype(type_)
        default_value = getdefaultvalue(type_)
        exec("{0}_array = array.array('{1}', [{2}]*{3})".format(branch, array_type, default_value, final_array_length), g, d)
        exec("{0}_branch = b.GetBranch('{0}')".format(branch), g, d)
        #if length == 0: print branch, type_, eval("{0}_array".format(branch), g, d), eval("{0}_branch".format(branch), g, d), eval("{0}_branch.GetTitle()".format(branch), g, d), length
        exec("{0}_branch.SetAddress({0}_array)".format(branch), g, d)
        
        # loop over each value in the array
        for j in range(length):
            t = "{0}_array[{1}] = a.{0}[{1}]".format(branch, j)
            exec(t, g, d)
    
def copydefaults(b, singlebranches, arraybranches, d, lengthbranches):
    # d -- need to import the locals from the previous loop or else the 
    #      the arrays are recycled and you get a seg fault...
    d["b"] = b
    d["a"] = None
    g = globals()
    # copy over non-array branches.
    for branch, type_ in singlebranches.items():
        array_type = getarraytype(type_)
        default_value = getdefaultvalue(type_)
        if branch in lengthbranches and type_ == "I":
            default_value = 0
        
        # special case code for '$00_Count'
        branch_ori = branch
        if branch[0] == "$":
            branch = branch.replace("$", "S")
        
        exec("{0}_array = array.array('{1}', [{2}])".format(branch, array_type, default_value), g, d)
        # TODO if changed $00 name then branch_ori can be replaced with branch, but keep branch ori for below
        exec("{0}_branch = b.GetBranch('{1}')".format(branch, branch_ori), g, d)
        exec("{0}_branch.SetAddress({0}_array)".format(branch), g, d)
        # could have used "{0}_array[0] = a.{0}" if not for $...
        exec("{0}_array[0] = {1}".format(branch, pprint.pformat(default_value)), g, d)
        
    # save array branches
    for branch, arraylength_andtype in arraybranches.items():
        arraylength, type_ = arraylength_andtype
        
        # get the array length, it's either an int or an array branch
        if type(arraylength) == int: 
            length = arraylength
        else: 
            length = 0
        # we need a physical address so the length can't be 0
        final_array_length = length if length > 0 else 1
        
        # make array
        array_type = getarraytype(type_)
        default_value = getdefaultvalue(type_)
        exec("{0}_array = array.array('{1}', [{2}]*{3})".format(branch, array_type, default_value, final_array_length), g, d)
        exec("{0}_branch = b.GetBranch('{0}')".format(branch), g, d)
        #if length == 0: print branch, type_, eval("{0}_array".format(branch), g, d), eval("{0}_branch".format(branch), g, d), eval("{0}_branch.GetTitle()".format(branch), g, d), length
        exec("{0}_branch.SetAddress({0}_array)".format(branch), g, d)
        
        # loop over each value in the array
        for j in range(length):
            t = "{0}_array[{1}] = {2}".format(branch, j, pprint.pformat(default_value))
            exec(t, g, d)
            
def getarraytype(type_):
    # type names ROOT, https://root.cern.ch/root/html/TTree.html#TTree:Branch@3
    # type names python, https://docs.python.org/2/library/array.html
    if type_ == "I": return "i"
    if type_ == "D": return "d"
    if type_ == "d": return "d" # TODO is 'd' equivalent to 'D'?
    if type_ == "i": return "I"
    raise ValueError("getarraytype: %s is not supported" % type_)
def getdefaultvalue(type_):
    if type_ == "I": return -9999
    if type_ == "D": return -9999
    if type_ == "d": return -9999
    if type_ == "i": return 99999999 # unsigned int
    raise ValueError("getdefaultvalue: %s is not supported" % type_)
    
    
    
def copy_branches(a, b):
    # copy branches from TTree a to TTree b
    l = a.GetListOfBranches()
    singlebranches = dict()
    arraybranches = dict()
    lengthbranches = set()
    for branch in l:
        name = branch.GetName()
        title = branch.GetTitle()
        if name == "ev_run": continue # skip this since we're replacing it 
        # TODO do I want to change $00_Count to S00_Count here?
        # make the branch in TTree b
        b.Branch(name, 0, title)
        if "[" in title:
            # it's an array
            type_ = getbranchtype(title)
            size = getbranchsize(title)
            if type(size) == str:
                lengthbranches.add(size)
            arraybranches[name] = size, type_
        else:
            # it's not an array
            type_ = getbranchtype(title)
            singlebranches[name] = type_
            
    # example output:
    # singlebranches = {'ev_cal_settings': 'I',
    # 'ev_det_config': 'I',
    # 'ev_detector': 'I', ... }
    # arraybranches = {'board': ('n_febs', 'I'),
    # 'chain': ('n_febs', 'I'),
    # 'crate': ('n_febs', 'I'), ... }
    return singlebranches, arraybranches, lengthbranches
            
def getbranchtype(branch_title):
    # take 'feb_id[n_febs]/I' in and return I
    return branch_title.split("/")[1]
def getbranchsize(branch_title):
    # take 'feb_id[n_febs]/I' in and return 'n_febs'
    temp = branch_title.split("[")[1]
    out = temp.split("]")[0]
    # if the length is an int, turn it into an int
    try: out = int(out)
    except ValueError: pass # clearly not an int
    return out
    
    
def loadtree(filename, ttreename):
    f = ROOT.TFile(filename)
    t = f.Get(ttreename)
    return f, t

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print "Doing the thing!"
        outfilename = "/minerva/data/users/kleykamp/superhcal_with_different_run_number.root"
        mainfilename = "/minerva/data/testbeam2/cosmics_superhcal_2017-2-7_test2/Cosmic_00001512_0001_DST.root"
        merge(outfilename, mainfilename)
