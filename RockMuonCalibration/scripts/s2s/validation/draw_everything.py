
import sys
import os
import array
import ROOT
ROOT.gROOT.SetBatch(True)
# removes stats box
ROOT.gStyle.SetOptStat(0)

DRAW_SUMMARIES_ONLY = False
N_FILES = None

MAINDET = False

# Detector size information
if not MAINDET:
    MODULEFIRST = 0
    MODULELAST = 41
    STRIPFIRST = 1
    STRIPLAST = 63
else:
    MODULEFIRST = -5
    MODULELAST = 114
    STRIPFIRST = 1
    STRIPLAST = 120
MODULESN = MODULELAST - MODULEFIRST 
STRIPSN = STRIPLAST - STRIPFIRST 
# TODO remove
#STRIPFIRST = -120
#STRIPLAST = 120

def plot2d(tree, title, module, strip, wgt):
    d = dict(title=title, strip=strip, module=module, 
        nmodules=MODULESN, modulestart=MODULEFIRST - 0.5, moduleend=MODULELAST + 0.5, 
        nstrips=STRIPSN, stripstart=STRIPFIRST - 0.5, stripend=STRIPLAST + 0.5, )
    bininfo = "{nmodules}, {modulestart}, {moduleend}, {nstrips}, {stripstart}, {stripend}".format(**d)
    d["bininfo"] = bininfo
    tree.Draw("{strip}:{module}>>{title};Module;Strip({bininfo})".format(**d), wgt, "colz")
    
def setlabels(c1, histname, title, x, y):
    # TODO get this to work
    h = ROOT.gDirectory.Get(histname)
    h.SetTitle(title)
    print h, h.GetName(), h.GetTitle()
    h.GetXaxis().SetTitle(x)
    h.GetYaxis().SetTitle(y)
    h.Draw()
    c1.Update()
    
def col_normalize(hist):
    for x in range(1, hist.GetNbinsX() + 1):
        s = 0
        for y in range(1, hist.GetNbinsY() + 1):
            bin = hist.GetBin(x, y)
            s += hist.GetBinContent(bin)
        scale = (1 / s) if s != 0 else 1
        for y in range(1, hist.GetNbinsY() + 1):
            bin = hist.GetBin(x, y)
            s = hist.GetBinContent(bin)
            hist.SetBinContent(bin, s * scale)
    
def drawprojections(c1, hist, startbin, endbin, filename, offset=0):
    # This will draw and save histograms for each value in a projections
    for bin in range(startbin, endbin + 1):
        new = hist.ProjectionY(hist.GetName() + "%s" % bin, bin, bin)
        new.Draw()
        c1.Print(filename.format(bin - offset))
    
def plot1d(tree, savedir, savetitle, c1, module, strip, var, nvar, varlow, varhigh, wgt):
    # TODO make a script that plots var per module, and then per strip
    # Save in savedir/savetitle_bymodule/module{0:02d}.png
    # Or savedir/savetitle_bystrip/module/strip{0:02d}.png
    # Also create a 2d summary of var vs module# and strip vs module, wgt=var.
    # Save as savedir/summary_savetitle_vsmod.png, savedir/summary_savetitle_wgtd_svm.png
    
    # TODO Need bin info for each
    
    if tree.GetEntries() == 0: 
        print tree, "is empty. Skipping"
        return
    
    EXT = ".png"
    
    # Draw var vs module
    bininfo = MODULESN, MODULEFIRST - 0.5, MODULELAST + 0.5, nvar, varlow, varhigh
    title = savetitle + "vsmod"
    xaxis = module
    yaxis = var
    tree.Draw("{yaxis}:{xaxis}>>{title}{bininfo}".format(**locals()), wgt, "colz")
    c1.Print(os.path.join(savedir, "summary_%s_vsmod.png" % savetitle))
    hist = ROOT.gDirectory.Get(title)
    col_normalize(hist)
    c1.Print(os.path.join(savedir, "summary_%s_colnorm_vsmod.png" % savetitle))
    setlabels(c1, title, var + " vs Module", "Module", var)
    
    # Draw strip vs module, wgt = var + wgt
    bininfo = MODULESN, MODULEFIRST - 0.5, MODULELAST + 0.5, STRIPSN, STRIPFIRST - 0.5, STRIPLAST + 0.5
    title = savetitle + "svm"
    xaxis = module
    yaxis = strip
    tree.Draw("{yaxis}:{xaxis}>>{title}{bininfo}".format(**locals()), "(%s)*(%s)" % (var, wgt), "colz")
    c1.Print(os.path.join(savedir, "summary_%s_wgtd_svm.png" % savetitle))
    
    # Draw stip vs module, no energy weighting
    #c1.SetLogz(False) # TODO remove
    bininfo = MODULESN, MODULEFIRST - 0.5, MODULELAST + 0.5, STRIPSN, STRIPFIRST - 0.5, STRIPLAST + 0.5
    title = savetitle + "nowgt"
    xaxis = module
    yaxis = strip
    tree.Draw("{yaxis}:{xaxis}>>{title}{bininfo}".format(**locals()), wgt, "colz")
    c1.Print(os.path.join(savedir, "summary_%s_nhits.png" % savetitle))
    
    # Loop over modules
    for modulenum in range(MODULEFIRST, MODULELAST+1):
        #break # TODO remove
        #if modulenum not in (5, 6, 10, 20, 27, 28, 30): continue
    
        # TODO replace below with vsmod above projected in single bins
        # draw all in module
        bininfo = nvar, varlow, varhigh
        xaxis = var
        title = savetitle + "_module{0:02d}".format(modulenum)
        tree.Draw("{xaxis}>>{title}{bininfo}".format(**locals()), "({wgt})*({module}=={modulenum})".format(**locals()))
        
        # First make sure dir exists
        try: os.makedirs(os.path.join(savedir, "module"))
        except OSError: pass # already exists
        # Now save
        c1.Print(os.path.join(savedir, "module", title + EXT))
        
        bininfo = STRIPSN, STRIPFIRST, STRIPLAST, nvar, varlow, varhigh
        xaxis = strip
        yaxis = var
        title = "summary_" + savetitle + "_module{0:02d}".format(modulenum)
        tree.Draw("{yaxis}:{xaxis}>>{title}{bininfo}".format(**locals()), "({wgt})*({module}=={modulenum})".format(**locals()), "colz")
        
        # TODO make a 2d summary of var vs strip in module X.
        # Now project this in bins of strip Y instead of doing the slow thing below
        try: os.makedirs(os.path.join(savedir, "module{0:02d}".format(modulenum)))
        except OSError: pass # already exists
        try: os.makedirs(os.path.join(savedir, "strip_summary"))
        except OSError: pass # already exists
        try: os.makedirs(os.path.join(savedir, "strip_summary_colnorm"))
        except OSError: pass # already exists
        # Now save
        c1.Print(os.path.join(savedir, "strip_summary", title + EXT))
        hist = ROOT.gDirectory.Get(title)
        col_normalize(hist)
        c1.Print(os.path.join(savedir, "strip_summary_colnorm", title + EXT))
        
        if DRAW_SUMMARIES_ONLY:
            continue # skips drawing individual strips
        
        striphist = ROOT.gDirectory.Get(title)
        drawprojections(c1, striphist, 1, 63, os.path.join(savedir, "module{0:02d}".format(modulenum), savetitle + "_strip{0:02d}" + EXT))
        
        # Draw 2d summary per strip
        for stripnum in range(STRIPFIRST, STRIPLAST+1):
            # Draw all in strip
            
            # draw all in module
            bininfo = nvar, varlow, varhigh
            xaxis = var
            title = savetitle + "_strip{0:02d}".format(stripnum)
            tree.Draw("{xaxis}>>{title}{bininfo}".format(**locals()), "({wgt})*({module}=={modulenum}&&{strip}=={stripnum})".format(**locals()))
            
            # First make sure dir exists
            try: os.makedirs(os.path.join(savedir, "module{0:02d}".format(modulenum)))
            except OSError: pass # already exists
            
            # Now save
            c1.Print(os.path.join(savedir, "module{0:02d}".format(modulenum), title + EXT))
       
       
       

if __name__ == "__main__":
    # Get the playlist
    playlist = sys.argv[1]
    
    # Make the tchains
    rocks = ROOT.TChain("nt")
    # rocks = ROOT.TChain("nt;3")
    dst = ROOT.TChain("minerva")
    i = 0
    with open(playlist, 'r') as fnew:
        for line in fnew:
            filename2 = line.strip().replace("DST", "Rock")
            rocks.Add(filename2)
            if "/nt/" in line: filename = line.strip().replace("/nt/", "/dst/").replace("RockMuonCalibration", "DST")
            else: filename = line.strip().replace("Rock", "DST").replace("_rocksonly", "")
            # TODO delete, temporary
            #filename = "/minerva/data/users/kleykamp/tb2_meu-run2_2017-3-1_smallsample/mc_nt/tb2_run2/nogrid/testbeam/dst/v10r8p7/SuperHCal/TB_00000013_0001_MC_DST_v10r8p7_tb2_run2.root"
            dst.Add(filename)
            i += 1
            if i == N_FILES: break
    print "Finished adding files", i
    print "Entries:", rocks.GetEntries()
    print "Entries:", dst.GetEntries()
    
    # Get the playlist name without directory information nor extension
    # foo/bar/playlist1.txt -> playlist1
    playlistname = os.path.splitext(os.path.basename(playlist))[0]
    # Now make the save directory
    savedir = os.path.join("draw_everything", playlistname)
    # Now make sure that directory exists
    try: os.makedirs(savedir)
    except OSError: pass # already exists
    
    # Now make a canvas for drawing
    c1 = ROOT.TCanvas("c1", "c1", 1500, 800)
    c1.SetLogz()
    
    module = "st_module"
    strip = "st_strip"
    allcuts = "st_mev != 0.0 && st_path > 2.0 && ev_extraEnergy <= 100.0 && ev_ntracks == 1"
    plot1d(rocks, savedir, "cosmic_energy", c1, module, strip, "st_mev", 30, 0, 6, allcuts)
    plot1d(rocks, savedir, "cosmic_pe", c1, module, strip, "st_pe", 30, 0, 18, allcuts)
    plot1d(rocks, savedir, "cosmic_q", c1, module, strip, "st_q", 30, 0, 3000, allcuts)
    plot1d(rocks, savedir, "st_base", c1, module, strip, "st_base", 31, -17, 17, "(st_mev)*(" + allcuts+ ")")
     
    
    # Here I'm removing the extra energy, and n tracks cuts in case they're the problem.
    module = "st_module"
    strip = "st_strip"
    allcuts = "st_mev != 0.0 && st_path > 2.0"
    plot1d(rocks, savedir, "removedcuts_cosmic_energy", c1, module, strip, "st_mev", 30, 0, 6, allcuts)
    plot1d(rocks, savedir, "removedcuts_cosmic_pe", c1, module, strip, "st_pe", 30, 0, 18, allcuts)
    plot1d(rocks, savedir, "removedcuts_cosmic_q", c1, module, strip, "st_q", 30, 0, 3000, allcuts)
    
    #'''
    module = "cl_module"
    strip = "cl_tpos"
    allcuts = "1" # Need something as wgt
    plot1d(rocks, savedir, "cosmic_cluster_energy", c1, module, strip, "cl_recoE", 30, 0, 7, allcuts)
    plot1d(rocks, savedir, "cosmic_cluster_pe", c1, module, strip, "cl_pe", 120, 0, 18*2, allcuts) #'''
    
    
    module = "hit_module"
    strip = "hit_strip"
    allcuts = "hit_norm_energy>0.01"
    plot1d(dst, savedir, "hit_energy", c1, module, strip, "hit_norm_energy", 30, 0, 0.6, allcuts)
    plot1d(dst, savedir, "hit_pe", c1, module, strip, "hit_pe", 30, 0, 2, allcuts) #'''
    plot1d(dst, savedir, "hit_q", c1, module, strip, "hit_q", 30, 0, 150, allcuts)
    plot1d(dst, savedir, "hit_qhi", c1, module, strip, "hit_qhi", 30, 0, 150, allcuts)
    plot1d(dst, savedir, "hit_unzoom_qhi", c1, module, strip, "hit_qhi", 100, 0, 3100, allcuts)
    plot1d(dst, savedir, "hit_medzoom_qhi", c1, module, strip, "hit_qhi", 100, 0, 500, allcuts)
 
    # DST doesn't exist for MEU MC
    #'''
    module = "clus_id_module"
    strip = "clus_id_strip"
    allcuts = "1" # Need something as wgt
    plot1d(dst, savedir, "cluster_energy", c1, module, strip, "clus_id_energy", 30, 0, 1, allcuts)
    plot1d(dst, savedir, "cluster_pe", c1, module, strip, "clus_id_pe", 30, 0, 2, allcuts)
    
    module = "clus_id_module[trk_node_cluster_idx]"
    strip = "clus_id_strip[trk_node_cluster_idx]"
    allcuts = "trk_node_cluster_idx>=0" # Need something as wgt
    plot1d(dst, savedir, "track_cluster_energy", c1, module, strip, "clus_id_energy", 30, 0, 1, allcuts)
    plot1d(dst, savedir, "track_cluster_pe", c1, module, strip, "clus_id_pe", 30, 0, 2, allcuts)
    
    
    
    
    
    # Old stuff
    
    '''
    # Hit stuff
    module = "hit_module"
    strip = "hit_strip"
    plot2d(dst, "Hit Module vs Strip", module, strip, "")
    c1.Print(os.path.join(savedir, "2d_hit_module_vs_strip.png"))
    plot2d(dst, "Hit Module vs Strip, Energy Weighted", module, strip, "hit_norm_energy")
    c1.Print(os.path.join(savedir, "2d_hit_module_vs_strip_energy.png"))
    plot2d(dst, "Hit Module vs Strip, PE Weighted", module, strip, "hit_pe")
    c1.Print(os.path.join(savedir, "2d_hit_module_vs_strip_pe.png"))
    
    # Cluster stuff
    module = "clus_id_module"
    strip = "clus_id_strip"
    plot2d(dst, "Cluster Module vs Strip", module, strip, "")
    c1.Print(os.path.join(savedir, "2d_cluster_module_vs_strip.png"))
    plot2d(dst, "Cluster Module vs Strip, Energy Weighted", module, strip, "clus_id_energy")
    c1.Print(os.path.join(savedir, "2d_cluster_module_vs_strip_energy.png"))
    plot2d(dst, "Cluster Module vs Strip, PE Weighted", module, strip, "clus_id_pe")
    c1.Print(os.path.join(savedir, "2d_cluster_module_vs_strip_pe.png"))
    
    # Cosmic track stuff (used in calibrations)
    module = "st_module"
    strip = "st_strip"
    plot2d(rocks, "Cosmic Module vs Strip", module, strip, "")
    c1.Print(os.path.join(savedir, "2d_cosmic_module_vs_strip.png"))
    plot2d(rocks, "Cosmic Module vs Strip, Energy Weighted", module, strip, "st_mev")
    c1.Print(os.path.join(savedir, "2d_cosmic_module_vs_strip_energy.png"))
    plot2d(rocks, "Cosmic Module vs Strip, Energy Per Path Weighted", module, strip, "st_path>2.0&&(st_mev/st_path)")
    c1.Print(os.path.join(savedir, "2d_cosmic_module_vs_strip_energy_perpath.png"))
    plot2d(rocks, "Cosmic Module vs Strip, PE Weighted", module, strip, "st_pe")
    c1.Print(os.path.join(savedir, "2d_cosmic_module_vs_strip_pe.png"))
    
    plot2d(rocks, "Cosmic Module vs Strip", module, strip, allcuts + "1")
    c1.Print(os.path.join(savedir, "2d_cosmic_allcuts_module_vs_strip.png"))
    plot2d(rocks, "Cosmic Module vs Strip, Energy Weighted", module, strip, allcuts + "st_mev")
    c1.Print(os.path.join(savedir, "2d_cosmic_allcuts_module_vs_strip_energy.png"))
    plot2d(rocks, "Cosmic Module vs Strip, Energy Per Path Weighted", module, strip, allcuts + "(st_mev/st_path)")
    c1.Print(os.path.join(savedir, "2d_cosmic_allcuts_module_vs_strip_energy_perpath.png"))
    plot2d(rocks, "Cosmic Module vs Strip, PE Weighted", module, strip, allcuts + "st_pe")
    c1.Print(os.path.join(savedir, "2d_cosmic_allcuts_module_vs_strip_pe.png")) #'''
    
    
    
    
    
    
    
    
    
    
    
    
