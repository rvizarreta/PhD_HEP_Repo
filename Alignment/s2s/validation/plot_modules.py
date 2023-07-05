
import sys
import os
import ROOT
ROOT.gROOT.SetBatch(True)

plotclusters = True

if __name__ == "__main__":
    # Get the playlist
    playlist = sys.argv[1]
    
    fnew = open(playlist, 'r')
    
    # Make the tchain
    #c = ROOT.TChain("nt")
    c = ROOT.TChain("minerva")
    i = 0
    for line in fnew:
        filename = line.strip().replace("Rock", "DST")
        c.Add(filename)
        i += 1
        if i == 300: break
    print "Finished adding files", i
    c1 = ROOT.TCanvas("c1", "c1", 1500, 800)
    
    try: os.mkdir("energy_plots")
    except OSError: pass # already exists
    try: os.mkdir("energy_plots/modules")
    except OSError: pass # already exists
    
    c.Show(0)
    avgAmount = 1;
    for i in range(0, 42):
        if i % avgAmount != 0: continue
        #c.Draw("cl_pe>>htemp(40,0,40)", "cl_module==%s" % i)
        #c.Draw("cl_pe>>htemp(40,0,40)", "cl_module<%s+%s&&cl_module>=%s" % (i, 10, i)) # Draws 10 modules combined
        if plotclusters: c.Draw("clus_id_pe>>htemp(40,0,4)", "clus_id_module<%s+%s&&clus_id_module>=%s" % (i, avgAmount, i)) # Draws 10 modules combined
        else: c.Draw("hit_pe>>htemp(40,0,4)", "hit_module<%s+%s&&hit_module>=%s" % (i, avgAmount, i)) # Draws 10 modules combined
        c1.Print("energy_plots/modules/module{0:02d}.png".format(i))
        
    #c.Draw("cl_pe:cl_module>>htemp(41, 0, 41, 40,0,40)", "", "colz")
    if plotclusters: c.Draw("clus_id_pe:clus_id_module>>htemp(41, 0, 41, 40,0,4)", "", "colz")
    else: c.Draw("hit_pe:hit_module>>htemp(41, 0, 41, 40,0,4)", "", "colz")
    c1.Print("energy_plots/modules/allmodules.png")
    #c.Draw("cl_tpos:cl_module>>htemp(41, 0, 41, 63, -550, 550)", "cl_pe", "colz")
    if plotclusters: c.Draw("clus_id_strip:clus_id_module>>htemp(41, 0, 41, 63, 0.5, 63.5)", "clus_id_pe", "colz")
    else: c.Draw("hit_strip:hit_module>>htemp(41, 0, 41, 63, 0.5, 63.5)", "hit_pe", "colz")
    c1.Print("energy_plots/modules/illumination.png")
    # TODO, apply pitches to module numbers to get true position then plot that
