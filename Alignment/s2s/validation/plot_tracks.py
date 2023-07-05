
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
    c = ROOT.TChain("nt")
    #c = ROOT.TChain("minerva")
    i = 0
    for line in fnew:
        filename = line.strip() #.replace("Rock", "DST")
        c.Add(filename)
        i += 1
        if i == 300: break
    print "Finished adding files", i
    c1 = ROOT.TCanvas("c1", "c1", 1500, 800)
    
    try: os.mkdir("energy_plots")
    except OSError: pass # already exists
    try: os.mkdir("energy_plots/tracks")
    except OSError: pass # already exists
    
    c.Show(0)
    avgAmount = 1;
    c1.SetLogy()
    for i in range(0, 42):
        if i % avgAmount != 0: continue
        
        #c.Draw("st_path>>htemp(40, 0, 30)", "ev_ntracks == 1 && ev_extraEnergy <= 100.0 && st_mev != 0.0 && st_path > 0.0 && st_module < %s+%s && st_module >= %s" % (i, avgAmount, i))
        #c1.Print("energy_plots/tracks/st_path_module{0:02d}.png".format(i))
        
    #c.Draw("cl_pe:cl_module>>htemp(41, 0, 41, 40,0,40)", "", "colz")
    #if plotclusters: c.Draw("clus_id_pe:clus_id_module>>htemp(41, 0, 41, 40,0,4)", "", "colz")
    #else: c.Draw("hit_pe:hit_module>>htemp(41, 0, 41, 40,0,4)", "", "colz")
    #c1.Print("energy_plots/tracks/allmodules.png")
    #c.Draw("cl_tpos:cl_module>>htemp(41, 0, 41, 63, -550, 550)", "cl_pe", "colz")
    c1.SetLogy(False)
    c.Draw("st_strip:st_module>>htemp(41, 0, 41, 63, 0.5, 63.5)", "ev_ntracks == 1", "colz")
    c1.Print("energy_plots/tracks/ntracks.png")
    
    #c.Draw("st_strip:10.0*st_mev/st_path>>htemp(%s, 0, 10, 64, -0.5, 64 - 0.5)" % nbins, 
    #       "st_mev != 0.0 && st_path > 2.0 && ev_extraEnergy <= 100.0 && ev_ntracks == 1 && st_module == %s" % module)

    c.Draw("st_strip:st_module>>htemp(41, 0, 41, 63, 0.5, 63.5)", "ev_ntracks == 1 && ev_extraEnergy <= 100.0 && st_mev != 0.0 && st_path > 0.0", "colz")
    c1.Print("energy_plots/tracks/ntracks_aftercuts.png")
    c.Draw("st_strip:st_module>>htemp(41, 0, 41, 63, 0.5, 63.5)", "ev_extraEnergy <= 100.0", "colz")
    c1.Print("energy_plots/tracks/extraenergy.png")
    c.Draw("st_strip:st_module>>htemp(41, 0, 41, 63, 0.5, 63.5)", "st_mev != 0.0", "colz")
    c1.Print("energy_plots/tracks/mev.png")
    c.Draw("st_strip:st_module>>htemp(41, 0, 41, 63, 0.5, 63.5)", "ev_ntracks == 1 && ev_extraEnergy <= 100.0 && st_mev != 0.0", "colz")
    c1.Print("energy_plots/tracks/allbutpath.png")
    
    c.Draw("st_strip:st_module>>path(41, 0, 41, 63, 0.5, 63.5)", "st_path > 0.0", "colz")
    c1.Print("energy_plots/tracks/path.png")
    c.Draw("st_strip:st_module>>path_zeros(41, 0, 41, 63, 0.5, 63.5)", "st_path <= 0.0", "colz")
    c1.Print("energy_plots/tracks/path_zeros.png")
    c.Draw("st_strip:st_module>>path_all(41, 0, 41, 63, 0.5, 63.5)", "", "colz")
    
    
    path_all = ROOT.gDirectory.Get("path_all")
    
    path_zeros = ROOT.gDirectory.Get("path_zeros")
    ratio_path_zeros = path_zeros.Clone("ratio_path_zeros")
    ratio_path_zeros.Divide(path_all)
    ratio_path_zeros.Draw("colz")
    c1.Print("energy_plots/tracks/ratio_path_zeros.png")
    
    path = ROOT.gDirectory.Get("path")
    ratio_path = path.Clone("ratio_path")
    ratio_path.Divide(path_all)
    ratio_path.Draw("colz")
    c1.Print("energy_plots/tracks/ratio_path.png")
    
    
    c1.SetLogy()
    c.Draw("st_path>>htemp(40, 0, 30)", "ev_ntracks == 1 && ev_extraEnergy <= 100.0 && st_mev != 0.0 && st_path > -1.0")
    c1.Print("energy_plots/tracks/st_path.png")
    c.Draw("st_path>>htemp(40, 0, 30)", "ev_ntracks == 1 && ev_extraEnergy <= 100.0 && st_mev != 0.0 && st_path > -1.0 && st_module <= 21")
    c1.Print("energy_plots/tracks/st_path_tracker.png")
    c.Draw("st_path>>htemp(40, 0, 30)", "ev_ntracks == 1 && ev_extraEnergy <= 100.0 && st_mev != 0.0 && st_path > -1.0 && st_module > 21")
    c1.Print("energy_plots/tracks/st_path_hcal.png")
