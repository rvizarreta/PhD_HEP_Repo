from __future__ import division

import helper
import calibration

import collections
import pprint
import os
import itertools
import glob
import random
import itertools

import ROOT
ROOT.gROOT.SetBatch(True)

def getresiduals(filename="/minerva/data/testbeam2/run1data_newmwpc/8GeV_Pos_Pions/TB_00001461_*mwpc.root"):
    files = glob.glob(filename)
    tchain = ROOT.TChain()
    for f in files:
        tchain.Add(f + "/mwpc")
    newoffset = drawresiduals(tchain)
    calibration.updateoffsets(newoffset)
    pprint.pprint(calibration.hitoffsets)
    
def cal():
    filename = "exp_20150226091500.dat" # muons
    #filename="/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/14/07/TB_00001407_00*mwpc.dat" # idk why I'm using this, is incomplete energy subrun
    #filename="/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/14/61/TB_00001461_00*mwpc.dat" # 8 gev pos pion, run 1
    #filename="/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/15/14/TB_00001514_00*mwpc.dat" # 8 gev pos pion, run 2
    #filename="/minerva/data/testbeam2/rawdata/testbeam/raw/cosmc/00/00/17/69/TB_00001769_00*mwpc.dat" # 8 gev pos electron, run 3
    usepos = False
    quick = True
    #filename="exp_20150226091500.dat"
    #getresiduals("caldata/mwpc0.root"); exit()
    import mwpc
    import calibration
    #calibration.hitoffsets
    files = glob.glob(filename)
    #files = files[:4]
    files = files[:10]
    cals = dict()
    offsets = dict()
    means = dict()
    Ncals = 1
    for j in range(Ncals):
        mwpcfiles = []
        i = 0
        for f in files:
            out = "caldata/mwpc%s.root" % i
            mwpcfiles.append(out)
            mwpc.main(f, out)#, nmax=2000)
            i += 1
        tchain = ROOT.TChain()
        for f in mwpcfiles:
            tchain.Add(f + "/mwpc")
        tempres = drawresiduals(tchain, iter_=j, quick=quick)
        temppos = drawpositions(tchain, j, quick=quick)
        if usepos:
            avgpos = means[j] = temppos
        else:
            avgpos = means[j] = tempres
        newoffsets = dict()
        factor = 0.5 # 1/(Ncals-j)
        for i in range(2):
            for I in range(1, 5):
                key = (I, i)
                newoffsets[key] = (avgpos[key] - avgpos[(1, i)]) * factor
        #raw_input("Here are the new offsets\n%s\nPress enter to continue..." % pprint.pformat(newoffsets))
        #drawtimedist(tchain); exit()
        #newoffsets = cals[j] = drawresiduals(tchain)
        calibration.updateoffsets(newoffsets, 1)
        offsets[j] = newoffsets
        cals[j] = calibration.hitoffsets.copy()
    tchain = ROOT.TChain()
    for f in mwpcfiles:
        tchain.Add(f + "/mwpc")
    #getplots(tchain)
    #pprint.pprint(test("caldata/mwpc0.root"))
    drawresiduals(tchain, iter_=Ncals)
    drawpositions(tchain, Ncals)
    print "Means"
    pprint.pprint(means)
    print "Offsets"
    pprint.pprint(offsets)
    print "Cals"
    pprint.pprint(cals)
    
def drawpositions(tchain, iter_ = None, quick=False):
    if iter_ == None:
        label = ""
    else: label = "_" + str(iter_)
    pos = drawbymodule(tchain, "plots/positions{0}.png".format(label), "mwpc_cluster_position", "mwpc_cluster_islate==0&&mwpc_cluster_tracknum>=0&&", getmean=True) 
    if quick:
        return pos
    drawbymodule(tchain, "plots/positions_ap{0}.png".format(label), "mwpc_cluster_position", "mwpc_cluster_islate==1&&")
    drawbymodule(tchain, "plots/positions_withap{0}.png".format(label), "mwpc_cluster_position")
    pprint.pprint(pos)
    return pos
    
def drawtimedist(tchain):
    drawbymodule(tchain, "plots/clustertimes.png", "mwpc_cluster_time")
    meantimes = drawbymodule(tchain, "plots/clustertimes_noap.png", "mwpc_cluster_time", "mwpc_cluster_islate==0&&", getmean=True)
    drawbymodule(tchain, "plots/clustertimes_ap.png", "mwpc_cluster_time", "mwpc_cluster_islate==1&&")
    drawbymodule(tchain, "plots/clustertimes_islower.png", "mwpc_cluster_time", "mwpc_cluster_position<=64&&")
    drawbymodule(tchain, "plots/clustertimes_isupper.png", "mwpc_cluster_time", "mwpc_cluster_position>64&&")
    drawbymodule(tchain, "plots/clustertimes_islower_ap.png", "mwpc_cluster_time", "mwpc_cluster_islate==1&&mwpc_cluster_position<=64&&")
    drawbymodule(tchain, "plots/clustertimes_isupper_ap.png", "mwpc_cluster_time", "mwpc_cluster_islate==1&&mwpc_cluster_position>64&&")
    drawbymodule(tchain, "plots/clustertimes_islower_noap.png", "mwpc_cluster_time", "mwpc_cluster_islate==0&&mwpc_cluster_position<=64&&")
    drawbymodule(tchain, "plots/clustertimes_isupper_noap.png", "mwpc_cluster_time", "mwpc_cluster_islate==0&&mwpc_cluster_position>64&&")
    
    
    pprint.pprint(meantimes)
        
    

def test(filename = "myTestmwpc.root"):
    filename = "caldata/mwpc0.root"
    
    tchain = ROOT.TChain()
    tchain.Add(filename + "/mwpc")
    
    return getplots(tchain)
    
def main(directory = "/minerva/data/testbeam2/run1data_newmwpc"): #_calauto
    tchain = ROOT.TChain()
    i = 0
    done = False
    for root, dirs, files in os.walk(directory):
        for f in files:
            if not f.endswith("mwpc.root"): continue
            fullpath = os.path.join(root, f)
            tchain.Add(fullpath + "/mwpc")
            i += 1
            if i > 100 and True: 
                done = True
                break
        if done: break
    getplots(tchain)
    print "n files", i
            
    
def getplots(tchain):
    #c = ROOT.TCanvas("c", "c", 1500, 800)
    #tchain.Draw("mwpc_track_proj_y[1]:mwpc_track_proj_x[1]", "mwpc_track_isclean", "colz")
    #c.Print("plots/proj.png")
    drawtimedist(tchain);
    drawresvschi2(tchain)
    drawntracks(tchain)
    drawntracks(tchain, "plots/ntracks.png", "Sum$(!mwpc_track_islate&&mwpc_track_direction=={direction})")
    drawntracks(tchain, "plots/ntracks_lateornot.png", "Sum$(mwpc_track_direction=={direction})")
    drawbymodule2(tchain, "plots/nclusters.png", "mwpc_bymodule_nclusters_{xy}[{moduleindex}]","")
    drawbymodule2(tchain, "plots/nlateclusters.png", "mwpc_bymodule_nlateclusters_{xy}[{moduleindex}]","")
    drawbymodule2(tchain, "plots/nlateclusters_withearlycluster.png", "mwpc_bymodule_nlateclusters_{xy}[{moduleindex}]","Sum$(mwpc_bymodule_nclusters_{xy})>=3")
    bywire, bymodule = getefficiency(tchain)
    drawwirehits(bywire)
    getefficiency(tchain, 4)
    getefficiency(tchain, 16)
    getefficiency(tchain, 64)
    getefficiency(tchain, 128)
    return drawresiduals(tchain)
    
def drawresvschi2(tchain):
    out = drawbymodule(tchain, "plots/resvschi2.png", "mwpc_cluster_res:mwpc_track_chi2[{direction}]","mwpc_cluster_res<20&&mwpc_cluster_res>-20&&mwpc_track_isclean&&mwpc_track_nclusters[{direction}]==4&&mwpc_cluster_direction=={direction}&&mwpc_cluster_wc=={wc}&&mwpc_cluster_res<2&&mwpc_cluster_res>-2&&", opts="colz")
    #drawbymodule(tchain, "plots/residualpererr.png", "mwpc_cluster_respererr","mwpc_cluster_respererr<4&&mwpc_cluster_respererr>-4&&mwpc_track_isclean&&mwpc_track_nclusters[0]==4&&mwpc_track_nclusters[1]==4")
    
    
    

def drawbymodule2(tchain, name, branch, cut="", opts="", hist=""):
    c = ROOT.TCanvas("c","c", 1500, 800)
    c.Divide(4,2)
    #c.SetLogy()
    for module, direction in itertools.product(range(1,5), range(2)):
        c.cd(plotpos(module, direction))
        d = dict(moduleindex=module-1, wc=module, xy="x" if direction == 0 else "y", direction=direction)
        tchain.Draw(branch.format(**d), cut.format(**d), opts)
    c.Print(name)
    
def drawwirehits(bywire):
    plotsmissing = dict()
    plotshits = dict()
    plotseff = dict()
    for wc, direction in itertools.product(range(1,5), range(2)):
        key = wc, direction
        name = "hmissing" + str(hash(str(key)))
        name2 = "hhit" + str(hash(str(key)))
        name3 = "heff" + str(hash(str(key)))
        plotsmissing[key] = ROOT.TH1D(name, name, 128, 0, 127)
        plotshits[key] = ROOT.TH1D(name2, name2, 128, 0, 127)
        plotseff[key] = ROOT.TH1D(name3, name3, 128, 0, 127)
    for key, value in bywire.items():
        wc, direction, wire = key
        newkey = wc, direction
        efficiency, nmissing, nhits = value
        plotsmissing[newkey].Fill(wire, nmissing)
        plotshits[newkey].Fill(wire, nhits)
        plotseff[newkey].Fill(wire, efficiency)
    c = ROOT.TCanvas("c","c", 1500, 800)
    c.Divide(4,2)
    c2 = ROOT.TCanvas("c2","c2", 1500, 800)
    c2.Divide(4,2)
    c3 = ROOT.TCanvas("c3","c3", 1500, 800)
    c3.Divide(4,2)
    for i, key in enumerate(itertools.product(range(1,5), range(2))):
        module, direction = key
        c.cd(plotpos(module, direction))
        plotsmissing[key].Draw()
        c2.cd(plotpos(module, direction))
        plotshits[key].Draw()
        c3.cd(plotpos(module, direction))
        plotseff[key].Draw()
    c.Print("plots/wiremissing.png")
    c2.Print("plots/wirehits.png")
    c3.Print("plots/wireeff.png")
    
def plotpos(wc, direction):
    d = {(1,0):1, (2,0):2, (3,0):3, (4,0):4, (1,1):5, (2,1):6, (3,1):7, (4,1):8}
    return d[(wc, direction)]
        
    
def drawresiduals(tchain, range_=20, iter_ =None, quick=False):
    #out = drawbymodule(tchain, "plots/residual.png", "mwpc_cluster_res","mwpc_cluster_res<{0}&&mwpc_cluster_res>-{0}&&mwpc_track_isclean&&mwpc_track_nclusters[0]==4&&mwpc_track_nclusters[1]==4".format(range_), getmean=True, n=range_ * 2 * 20)
    #drawbymodule(tchain, "plots/residualpererr.png", "mwpc_cluster_respererr","mwpc_cluster_respererr<4&&mwpc_cluster_respererr>-4&&mwpc_track_isclean&&mwpc_track_nclusters[0]==4&&mwpc_track_nclusters[1]==4")
    if iter_ == None:
        label = ""
    else: label = "_" + str(iter_)
    endpoints = 9 # 20
    out = drawbymodule(tchain, "plots/residual{0}.png".format(label), "mwpc_cluster_res","mwpc_cluster_res<{endpoints}&&mwpc_cluster_res>-{endpoints}&&mwpc_track_isclean&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4&&mwpc_cluster_direction=={direction}&&mwpc_cluster_wc=={wc}&&", getmean=True, endpoints=endpoints)
    
    if quick: return out
    
    drawbymodule(tchain, "plots/residualpererr{0}.png".format(label), "mwpc_cluster_respererr","mwpc_cluster_respererr<{endpoints}&&mwpc_cluster_respererr>-{endpoints}&&mwpc_track_isclean&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4&&mwpc_cluster_direction=={direction}&&mwpc_cluster_wc=={wc}&&", endpoints=endpoints)
    
    
    drawbymodule(tchain, "plots/residualbyposition{0}.png".format(label), "mwpc_cluster_res:mwpc_cluster_position","mwpc_cluster_respererr<{endpoints}&&mwpc_cluster_respererr>-{endpoints}&&mwpc_track_isclean&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4&&mwpc_cluster_direction=={direction}&&mwpc_cluster_wc=={wc}&&mwpc_cluster_islate==0&&", opts="colz", endpoints=endpoints)
    
    # doesn't work, using drawresbyres instead
    '''opts = "colz"
    drawntracks(tchain, "plots/resbyres{0}.png".format(label), branch="MaxIf$(mwpc_cluster_res,mwpc_cluster_wc==1&&mwpc_cluster_direction=={direction}&&mwpc_cluster_res>-3&&mwpc_cluster_res<3&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4):MaxIf$(mwpc_cluster_res,mwpc_cluster_wc==3&&mwpc_cluster_direction=={direction}&&mwpc_cluster_res>-3&&mwpc_cluster_res<3&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4)", cut="mwpc_track_isclean&&mwpc_cluster_tracknum>=0&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4&&mwpc_cluster_direction=={direction}&&(mwpc_cluster_wc==1||mwpc_cluster_wc==3)&&mwpc_cluster_res>-3&&mwpc_cluster_res<3", opts=opts)
    drawbymodule(tchain, "plots/resbyreswc1vsall{0}.png".format(label), branch="MaxIf$(mwpc_cluster_res,mwpc_cluster_wc=={wc}&&mwpc_cluster_direction=={direction}&&mwpc_cluster_res>-5&&mwpc_cluster_res<5&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4):MaxIf$(mwpc_cluster_res,mwpc_cluster_wc==1&&mwpc_cluster_direction=={direction}&&mwpc_cluster_res>-5&&mwpc_cluster_res<5&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4)", cut="mwpc_track_isclean&&mwpc_cluster_tracknum>=0&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4&&mwpc_cluster_direction=={direction}&&(mwpc_cluster_wc==1||mwpc_cluster_wc=={wc})&&mwpc_cluster_res>-5&&mwpc_cluster_res<5&&", opts=opts)
    drawbymodule(tchain, "plots/resbyreswc4vsall{0}.png".format(label), branch="MaxIf$(mwpc_cluster_res,mwpc_cluster_wc=={wc}&&mwpc_cluster_direction=={direction}&&mwpc_cluster_res>-5&&mwpc_cluster_res<5&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4):MaxIf$(mwpc_cluster_res,mwpc_cluster_wc==4&&mwpc_cluster_direction=={direction}&&mwpc_cluster_res>-5&&mwpc_cluster_res<5&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4)", cut="mwpc_track_isclean&&mwpc_cluster_tracknum>=0&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4&&mwpc_cluster_direction=={direction}&&(mwpc_cluster_wc==4||mwpc_cluster_wc=={wc})&&mwpc_cluster_res>-5&&mwpc_cluster_res<5&&", opts=opts)
    
    drawbymodule(tchain, "plots/posbyposwc4vsall{0}.png".format(label), branch="MaxIf$(mwpc_cluster_position,mwpc_cluster_wc=={wc}&&mwpc_cluster_direction=={direction}&&mwpc_cluster_res>-5&&mwpc_cluster_res<5&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4):MaxIf$(mwpc_cluster_position,mwpc_cluster_wc==4&&mwpc_cluster_direction=={direction}&&mwpc_cluster_res>-5&&mwpc_cluster_res<5&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4)", cut="mwpc_track_isclean&&mwpc_cluster_tracknum>=0&&mwpc_track_nclusters[mwpc_cluster_tracknum]==4&&mwpc_cluster_direction=={direction}&&(mwpc_cluster_wc==4||mwpc_cluster_wc=={wc})&&mwpc_cluster_res>-5&&mwpc_cluster_res<5&&", opts=opts)'''
    
    
    
    drawang(tchain, "plots/resvsslope{0}.png".format(label), "slp")
    drawang(tchain, "plots/resvsintercept{0}.png".format(label), "int")
    drawang(tchain, "plots/ang.png")
    drawang(tchain, "plots/nwires.png", "nw")
    drawresbyres(tchain, "plots/resbyres_wc{{wc1}}vsall{0}.png".format(label))
    drawresbyres(tchain, "plots/posbypos_wc{{wc1}}vsall{0}.png".format(label), "pos")
    drawresbyres(tchain, "plots/diffbypos_wc{{wc1}}vsall{0}.png".format(label), "pr")
    drawresbyres(tchain, "plots/diffbypos_prof_wc{{wc1}}vsall{0}.png".format(label), "pr", "X")
    drawresbyres(tchain, "plots/resbypos_wc{{wc1}}vsall{0}.png".format(label), "rvp")
    return out
    

    
def drawresbyres(tchain, name, plot="res", prof=None):
    c = ROOT.TCanvas("c", "c", 1500, 800)
    c.Divide(4, 2)
    if plot == "res":
        rangelow, rangehigh = -5, 5
        n = 100
        args = n, rangelow, rangehigh, n, rangelow, rangehigh
    elif plot == "pos":
        rangelow, rangehigh = 0, 128  
        n = 128 
        args = n, rangelow, rangehigh, n, rangelow, rangehigh
    elif plot == "pr":
        rangelow, rangehigh = 0, 128  
        n = 128   
        args = n, rangelow, rangehigh, 101, -5, 5    
    elif plot == "rvp":
        rangelow, rangehigh = 0, 128  
        n = 128   
        args = n, rangelow, rangehigh, 101, -5, 5  
    else: raise ValueError("'%s' not supported" % plot)
    idk = [(wc2 + 4 * direction, direction, wc2) for direction, wc2 in itertools.product(range(2), range(1, 5))]
    for wc in range(1, 5):
        print "On wc", wc, "length", tchain.GetEntries()
        hists = dict()
        for cd, direction, wc2 in idk:
            hists[cd] = ROOT.TH2D("hres%s" % str((wc2, direction)), "hres%s" % str((wc2, direction)), *args)
        for entry in tchain:
            # skip if not a clean track
            if not entry.mwpc_track_isclean: continue
            # we really only want 1 track per direction
            if entry.mwpc_track_ntracks_x != 1: continue
            if entry.mwpc_track_ntracks_y != 1: continue
            l = entry.mwpc_number_of_clusters
            for i, j in itertools.product(range(l), range(l)):
                # skip if wc is not specific wc
                if entry.mwpc_cluster_wc[i] != wc: continue
                #if entry.mwpc_cluster_wc[j] != wc2: continue
                wc2 = entry.mwpc_cluster_wc[j]
                #if wc == wc2 and (entry.mwpc_cluster_wc[i] == wc or entry.mwpc_cluster_wc[j] == wc2):
                #    print i, j, wc, entry.mwpc_cluster_wc[i], entry.mwpc_cluster_wc[j], entry.mwpc_cluster_res[i], entry.mwpc_cluster_res[j]
                # skip if clusters aren't part of track
                if entry.mwpc_cluster_tracknum[i] < 0: continue
                if entry.mwpc_cluster_tracknum[j] < 0: continue
                # check there's only 1 wire per cluster
                if entry.mwpc_cluster_nwire[i] != 1: continue
                if entry.mwpc_cluster_nwire[j] != 1: continue
                # skip if clusters aren't part of same track
                if entry.mwpc_cluster_tracknum[i] != entry.mwpc_cluster_tracknum[j]: continue
                # skip if cluster direction is not current direction
                direction = entry.mwpc_cluster_direction[j]
                if entry.mwpc_cluster_direction[i] != direction: continue
                if entry.mwpc_cluster_direction[j] != direction: continue
                # we want each track to have four clusters
                if entry.mwpc_track_nclusters[entry.mwpc_cluster_tracknum[i]] != 4: continue
                if entry.mwpc_track_nclusters[entry.mwpc_cluster_tracknum[j]] != 4: continue
                #if entry.mwpc_track_nclusters[entry.mwpc_cluster_tracknum] != 4: continue # SystemError: error return without exception set
                cd = wc2 + 4 * direction
                if wc == wc2: 
                    assert i == j, (i,j, entry.mwpc_cluster_wc[i], entry.mwpc_cluster_wc[j], wc, l)
                    #print i, j, entry.mwpc_cluster_wc[i], wc, entry.mwpc_cluster_res[i], entry.mwpc_cluster_res[j]
                if plot == "res":
                    hists[cd].Fill(entry.mwpc_cluster_res[i], entry.mwpc_cluster_res[j])
                elif plot == "pos":
                    hists[cd].Fill(entry.mwpc_cluster_position[i], entry.mwpc_cluster_position[j])
                elif plot == "pr":
                    hists[cd].Fill(entry.mwpc_cluster_position[i], entry.mwpc_cluster_position[j] - entry.mwpc_cluster_position[i])
                elif plot == "rvp":
                    hists[cd].Fill(entry.mwpc_cluster_position[i], entry.mwpc_cluster_res[j])
                else: raise ValueError("%s is not supported" % plot)

                
        for cd, direction, wc2 in idk:
            c.cd(cd)
            if prof is None:
                hists[cd].Draw("colz")
            elif prof == "X":
                h = hists[cd].ProfileX()
                h.Draw()
            elif prof == "Y":
                h = hists[cd].ProfileY()
                h.Draw()
            else: ValueError("I don't know what to do with prof=%s" % prof)
        c.Print(name.format(direction=direction, wc1=wc, wc2=wc2))
        for h in hists.values():
            h.Delete()
            
def drawang(tchain, name, plot="ang"):
    c = ROOT.TCanvas("c", "c", 1500, 800)
    c.Divide(4, 2)
    rangelow, rangehigh = 0, 128  
    n = 128   
    if plot == "ang":
        args = n, rangelow, rangehigh, 101, -5, 5
        oppositedirection = True
    elif plot == "nw":
        oppositedirection = False
        args = n, rangelow, rangehigh, 6, 0, 5 
    elif plot == "slp":
        oppositedirection = False
        rangelow, rangehigh = -5, 5  
        n = 100   
        args = 101, -0.003, 0.003, n, rangelow, rangehigh
    elif plot == "int":
        oppositedirection = False
        rangelow, rangehigh = -5, 5  
        n = 100   
        args = 128, 0, 128, n, rangelow, rangehigh, 
    else: raise ValueError("%s not valid" % plot)
    idk = [(wc2 + 4 * direction, direction, wc2) for direction, wc2 in itertools.product(range(2), range(1, 5))]
    print "ang tchain length", tchain.GetEntries()
    hists = dict()
    for cd, direction, wc2 in idk:
        hists[cd] = ROOT.TH2D("hres%s" % str((wc2, direction)), "hres%s" % str((wc2, direction)), *args)
    for entry in tchain:
        # skip if not a clean track
        if not entry.mwpc_track_isclean: continue
        if entry.mwpc_track_ntracks_x != 1: continue
        if entry.mwpc_track_ntracks_y != 1: continue
        l = entry.mwpc_number_of_clusters
        for i, j in itertools.product(range(l), range(l)):
            # skip if wc is not specific wc
            wc2 = entry.mwpc_cluster_wc[j]
            if entry.mwpc_cluster_wc[i] != wc2: continue
            direction = entry.mwpc_cluster_direction[i]
            if oppositedirection:
                # skip if cluster direction is not the *opposite* direction
                if entry.mwpc_cluster_direction[j] == direction: continue
            else:
                # skip if cluster direction is not the *same* direction
                if entry.mwpc_cluster_direction[j] != direction: continue
            # skip if clusters aren't part of track
            if entry.mwpc_cluster_tracknum[i] < 0: continue
            if entry.mwpc_cluster_tracknum[j] < 0: continue
            # we want each track to have four clusters
            if entry.mwpc_track_nclusters[entry.mwpc_cluster_tracknum[i]] != 4: continue # TODO IndexError
            '''Also check:
              File "tests.py", line 369, in drawang
                if entry.mwpc_track_nclusters[entry.mwpc_cluster_tracknum[i]] != 4: continue
            IndexError: buffer index out of range'''
            if entry.mwpc_track_nclusters[entry.mwpc_cluster_tracknum[j]] != 4: continue
            #if entry.mwpc_track_nclusters[entry.mwpc_cluster_tracknum] != 4: continue # SystemError: error return without exception set
            cd = wc2 + 4 * direction
            if plot == "ang":
                hists[cd].Fill(entry.mwpc_cluster_position[i], entry.mwpc_cluster_res[j])
            elif plot == "nw":
                hists[cd].Fill(entry.mwpc_cluster_position[i], entry.mwpc_cluster_nwire[j])
            elif plot == "slp":
                hists[cd].Fill(entry.mwpc_track_m[entry.mwpc_cluster_tracknum[i]], entry.mwpc_cluster_res[j])
            elif plot == "int":
                hists[cd].Fill(entry.mwpc_track_b[entry.mwpc_cluster_tracknum[i]], entry.mwpc_cluster_res[j])
                

                
    for cd, direction, wc2 in idk:
        c.cd(cd)
        hists[cd].Draw("colz")
    c.Print(name)
    for h in hists.values():
        h.Delete()
    
def drawntracks(tchain, name = "plots/nlatetracks.png", branch="Sum$(mwpc_track_islate)",cut="mwpc_track_ntracks>0", opts=""):
    if cut != "": cut += "&&"
    c = ROOT.TCanvas("c","c", 1500, 800)
    c.Divide(2,1)
    #c.SetLogy()
    c.cd(1)
    tchain.Draw(branch.format(direction=0, xy="x"), cut.format(direction=0, xy="x") + "mwpc_track_direction==0", opts)
    c.cd(2)
    tchain.Draw(branch.format(direction=1, xy="y"), cut.format(direction=1, xy="y") + "mwpc_track_direction==1", opts)
    c.Print(name)

def drawbymodule(tchain, name, branch, cut="", opts="", hist="", getmean=False, n=None, endpoints=None):
    if endpoints == None:
        endpoints == ""
    c = ROOT.TCanvas("c","c", 1500, 800)
    c.Divide(4,2)
    c.SetLogy()
    if getmean:
        out = dict()
    for module, direction in itertools.product(range(1,5), range(2)):
        c.cd(plotpos(module, direction))
        extra = "mwpc_cluster_wc=={0}&&mwpc_cluster_direction=={1}".format(module, direction)
        
        d = dict(moduleindex=module-1, wc=module, xy="x" if direction == 0 else "y", direction=direction, endpoints=endpoints)
        hname = histname = "reshist" + name.replace(".", "").replace("/", "") + str(module) + str(direction) + str(random.uniform(0,100000000))
        if n != None:
            hname += "(%s)" % n
        tchain.Draw(branch.format(**d) + ">>" + hname, cut.format(**d) + extra, opts)
        if getmean:
            hist = ROOT.gDirectory.Get(histname)
            mean = 0
            assert hist != None
            if hist != None:
                if module == 4:
                    result = hist.Fit("gaus", "QS")
                    mean = result.Parameter(1)
                else:
                    mean = hist.GetMean()
                    #print module, direction, mean, hist.GetRMS()
            out[(module, direction)] = mean
    c.Print(name)
    if getmean:
        pprint.pprint(out)
        return out
    
def getefficiency(tchain, combine=1):
    assert combine > 0
    
    n3bywire = collections.defaultdict(int)
    n3bymodule = collections.defaultdict(int)
    n4bywire = collections.defaultdict(int)
    n4 = 0
    
    for event in tchain:
        if not event.mwpc_track_isclean: continue
        for i in range(event.mwpc_track_ntracks):
            if event.mwpc_track_nclusters[i] == 4: 
                n4 += 1
                for missing in range(1,5):
                    # there is no missing module
                    direction = event.mwpc_track_direction[i]
                    key = (missing, direction)
                    # get track infomation
                    m = event.mwpc_track_m[i]
                    b = event.mwpc_track_b[i]
                    merr = event.mwpc_track_merr[i]
                    berr = event.mwpc_track_berr[i]
                    # get the position of the missing module
                    zpos, zerr = helper.getzpos(missing, direction)
                    # project the track
                    proj, projerr = helper.project_track(b, berr, m, merr, zpos, zerr)
                    offset = calibration.getoffset(key)
                    # get the wire number by undoing the offset
                    wire = int(round(proj - offset)/combine)
                    
                    # tag each wire and each module
                    idk = (missing, direction, wire)
                    n4bywire[idk] += 1
                
            if event.mwpc_track_nclusters[i] == 3: 
                # get the missing module
                missing = event.mwpc_track_missingmodule[i]
                direction = event.mwpc_track_direction[i]
                key = (missing, direction)
                # get track infomation
                m = event.mwpc_track_m[i]
                b = event.mwpc_track_b[i]
                merr = event.mwpc_track_merr[i]
                berr = event.mwpc_track_berr[i]
                # get the position of the missing module
                zpos, zerr = helper.getzpos(missing, direction)
                # project the track
                proj, projerr = helper.project_track(b, berr, m, merr, zpos, zerr)
                offset = calibration.getoffset(key)
                # get the wire number by undoing the offset
                wire = int(round(proj - offset)/combine)
                
                # tag each wire and each module
                idk = (missing, direction, wire)
                n3bywire[idk] += 1
                n3bymodule[key] += 1
    efficiencies_bywire = dict()
    efficiencies_bymodule = dict()
    for key, value in n3bywire.items():
        try:
            efficiencies_bywire[key] = (1 - value / (value + n4bywire[key]), value, n4bywire[key])
        except ZeroDivisionError:
            efficiencies_bywire[key] = (0, value, 0)
    for key, value in n3bymodule.items():
        efficiencies_bymodule[key] = (1 - value / (value + n4), value)
    pprint.pprint(efficiencies_bywire)
    pprint.pprint(efficiencies_bymodule)
    
    histbywire = ROOT.TH2D("efficiency_by_wire", "efficiency_by_wire;module+direction/2;wire number",8,1,5,int(128/combine),0,127)
    for key, value in efficiencies_bywire.items():
        wc, direction, wire = key
        efficiency, num3, num4 = value
        x = wc + direction / 2
        y = wire * combine
        histbywire.Fill(x, y, efficiency)
        
    c = ROOT.TCanvas("c", "c", 1500, 800)
    ROOT.gStyle.SetPaintTextFormat("1.3f")
    histbywire.SetMarkerSize(3 if combine > 32 else 2) # see https://root.cern.ch/phpBB3/viewtopic.php?t=4932
    histbywire.Draw("colz" if combine < 16 else "colz text" if combine < 64 else "colz text90")
    name = "plots/efficiencybywire.png" if combine == 1 else "plots/efficiencybywire_combine{0}.png".format(combine)
    c.Print(name)
    
    print "n4", n4
    
    return efficiencies_bywire, efficiencies_bymodule


if __name__ == "__main__":
    cal()
