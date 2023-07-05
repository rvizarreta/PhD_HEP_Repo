from __future__ import division

import helper
import calibration

import collections
import pprint
import os
import itertools

import ROOT
ROOT.gROOT.SetBatch(True)


def test():
    filename = "myTest.root"
    
    tchain = ROOT.TChain()
    tchain.Add(filename + "/mwpc")
    
    getplots(tchain)
    
def main(directory = "/minerva/data/testbeam2/run1data_newmwpc_calauto"):
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
    
    bywire, bymodule = getefficiency(tchain)
    drawwirehits(bywire)
    getefficiency(tchain, 4)
    getefficiency(tchain, 16)
    getefficiency(tchain, 64)
    getefficiency(tchain, 128)
    drawresiduals(tchain)
    
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
        
    
def drawresiduals(tchain):
    drawbymodule(tchain, "plots/residual.png", "mwpc_cluster_res","mwpc_cluster_res<3&&mwpc_cluster_res>-3&&mwpc_track_isclean")
    drawbymodule(tchain, "plots/residualpererr.png", "mwpc_cluster_respererr","mwpc_cluster_respererr<4&&mwpc_cluster_respererr>-4&&mwpc_track_isclean")

def drawbymodule(tchain, name, branch, cut="", opts="", hist=""):
    c = ROOT.TCanvas("c","c", 1500, 800)
    c.Divide(4,2)
    c.SetLogy()
    if len(cut) > 0: cut += "&&"
    for module, direction in itertools.product(range(1,5), range(2)):
        c.cd(plotpos(module, direction))
        extra = "mwpc_cluster_wc=={0}&&mwpc_cluster_direction=={1}".format(module, direction)
        tchain.Draw(branch, cut + extra, opts)
    c.Print(name)
    
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
    main()
