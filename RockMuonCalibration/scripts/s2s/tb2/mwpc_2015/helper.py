
import calibration

import ROOT

import itertools
import collections
import math

def getzpos(wc, direction):
    return calibration.getzpos[wc-1], 0 
            
def gettdc(hitpos):
    return 1 if hitpos > 64 else 0
        
def project_track(b, berr, m, merr, z, zerr):
    pos = m*z + b
    # err = sqrt(x**2*dm**2 + m**2*dz**2 + berr**2)
    err = math.sqrt(z**2 * merr**2 + m**2 * zerr**2 + berr**2)
    return pos, err
    
plots = collections.defaultdict(dict)
config = dict()
               
def createplots(DrawHitPosPlots=False, DrawWireResHists=False, DrawAngleHists=False):
    nwires = 128
    residualrange = 5
    residualovererrrange = 5
    nres = 30
    nwireres = 128
    extra1d = ";residual (mm);counts"
    extra1d2 = ";position (mm);counts"
    extra2d = ";position (mm);residual (mm);counts"
    extra2d2 = ";position (mm);position (mm);counts"
    extratime = ";time (ns); counts"
    
    config["DrawHitPosPlots"] = DrawHitPosPlots
    config["DrawWireResHists"] = DrawWireResHists
    config["DrawAngleHists"] = DrawAngleHists
    
        
    # loop over all wire chambers and directions
    for i, key in enumerate(itertools.product(range(1, 5), range(2))):
        print "Key", i, key
        name = "wc%s%s" % (key[0], "x" if key[1] == 0 else "y")
        plots["residual"][key] = ROOT.TH1D("hres" + name, "hres" + name + extra1d, 
            nres, -residualrange, residualrange)
        plots["residualovererror"][key] = ROOT.TH1D("hresperr" + name, 
            "hresperr" + name + extra1d, nres, -residualovererrrange, residualovererrrange)
            
        if DrawHitPosPlots:
            # 1d plots
            plots["hitpos"][key] = ROOT.TH1D("hbeampos" + name, 
                    "hbeampos" + name + extra1d2, nwireres, 0, nwires)
            plots["hitposearly"][key] = ROOT.TH1D("hitposearly" + name, 
                    "hitposearly" + name + extra1d2, nwireres, 0, nwires)
            plots["hitposafterpulse"][key] = ROOT.TH1D("hitposafterpulse" + name, 
                    "hitposafterpulse" + name + extra1d2, nwireres, 0, nwires)
                    
            plots["hitposrec1d"][key] = ROOT.TH1D("hbeamposrec1d" + name, 
                    "hbeamposrec1d" + name + extra1d2, nwireres, 0, nwires)
            plots["hitposearlyrec"][key] = ROOT.TH1D("hitposearlyrec" + name, 
                    "hitposearlyrec" + name + extra1d2, nwireres, 0, nwires)
            plots["hitposafterpulserec"][key] = ROOT.TH1D("hitposafterpulserec" + name, 
                    "hitposafterpulserec" + name + extra1d2, nwireres, 0, nwires)
            plots["nclusters"][key] = ROOT.TH1D("hnclusters" + name, "hnclusters" + name, 5, 0, 5)
            plots["nlateclusters"][key] = ROOT.TH1D("hnlateclusters" + name, "hnlateclusters" + name, 5, 0, 5)
            tmax = 300
            plots["clusterhittime"][key] = ROOT.TH1D("hclusterhittime" + name, "hclusterhittime" + name + extratime, tmax//4, 0, tmax)
            plots["clusterhittimemulticluster"][key] = ROOT.TH1D("hclusterhittimemulticluster" + name, "hclusterhittimemulticluster" + name + extratime, tmax//4, 0, tmax)
            plots["clusterhittimelatecluster"][key] = ROOT.TH1D("hclusterhittimelatecluster" + name, "hclusterhittimelatecluster" + name + extratime, tmax//4, 0, tmax)
            
                    
            plots["secondhitdist"][key] = ROOT.TH1D("secondhitdist" + name, 
                    "secondhitdist" + name + extra1d2, nwires, 0, nwires)
            # 2d plots
            if key[1] == 0:
                namewc = "wc%s" % key[0]
                plots["hitposrec"][key[0]] = ROOT.TH2D("hbeamposrec" + namewc, 
                        "hbeamposrec" + namewc + extra2d2, nwireres, 0, nwires, 
                        nwireres, 0, nwires)
        
        if DrawWireResHists:
            plots["residual_as_func_of_pos"][key] = ROOT.TH2D("hrespos" + name, 
                "hrespos" + name + extra2d, nwireres, 0, nwires, 
                nres, -residualrange, residualrange)
            plots["residualovererror_as_func_of_pos"][key] = ROOT.TH2D("hresperrpos" + name, 
                "hresperrpos" + name + extra2d, nwireres, 0, nwires, 
                nres, -residualrange, residualrange)
                
        if DrawAngleHists:
            plots["residual_as_func_of_opp"][key] = ROOT.TH2D("hresopp" + name, 
                "hresopp" + name + extra2d, nwireres, 0, nwires, 
                nres, -residualrange, residualrange)
            plots["residualovererror_as_func_of_opp"][key] = ROOT.TH2D("hresperropp" + name, 
                "hresperropp" + name + extra2d, nwireres, 0, nwires, 
                nres, -residualrange, residualrange)
                
    #pprint.pprint(plots)
        
def saveplots(DrawHitPosPlots=False, DrawWireResHists=False, DrawAngleHists=False):
    if not DrawHitPosPlots and not DrawWireResHists and not DrawAngleHists: return
    c = dict()
    names = ["plot_residual", "plot_residualovererr"] if DrawWireResHists else []
    namesres = ("plot_residualasfuncofpos", "plot_residualovererrasfuncofpos", 
            "plot_residualasfuncofposprof", "plot_residualovererrasfuncofposprof")
    namesang = ("plot_residualasfuncofopp", "plot_residualovererrasfuncofopp", 
            "plot_residualasfuncofoppprof", "plot_residualovererrasfuncofoppprof",
            "plot_residualangleYaxisplot")
            
    namespos = ("plot_hitpos", "plot_hitposearly", 
                "plot_hitposafterpulse", "plot_hitposrec", "plot_secondhitdist",
                "plot_hitposrec1d", "plot_hitposearlyrec", 
                "plot_hitposafterpulserec", "plot_nclusters",
                "plot_clusterhittime", "plot_clusterhittimemulticluster", 
                "plot_clusterhittimelatecluster", "plot_nlateclusters") 
    onlywc = (namespos[3], )
    if DrawWireResHists: names.extend(namesres)
    if DrawAngleHists: names.extend(namesang)
    if DrawHitPosPlots: names.extend(namespos)
    for name in names:
        c[name] = ROOT.TCanvas("c_" + name, "c_" + name, 1500, 800)
        if name in onlywc:
            c[name].Divide(4)
        else: c[name].Divide(4,2)
        
    opts1d = ""
    opts2d = "colz"
    optsprof = ""
    angmessages = []
    angleoffsets = {}
    for i, key in enumerate(itertools.product(range(1, 5), range(2))):
        k = i + 1
        wc, d = key
        print "Making %s plots" % (key, )
        if DrawWireResHists:
            c[names[0]].cd(k)
            plots["residual"][key].Draw(opts1d)
            c[names[1]].cd(k)
            plots["residualovererror"][key].Draw(opts1d)
        
        
        if DrawHitPosPlots:
            # 1d plots
            # hit pos as function of time
            c[namespos[0]].cd(k)
            plots["hitpos"][key].Draw(opts1d)
            c[namespos[1]].cd(k)
            plots["hitposearly"][key].Draw(opts1d)
            c[namespos[2]].cd(k)
            plots["hitposafterpulse"][key].Draw(opts1d)
            # dist from primary hit that a second hit starts
            c[namespos[4]].cd(k)
            plots["secondhitdist"][key].Draw(opts1d)
            # reconstructed hits
            c[namespos[5]].cd(k)
            plots["hitposrec1d"][key].Draw(opts1d)
            c[namespos[6]].cd(k)
            plots["hitposearlyrec"][key].Draw(opts1d)
            c[namespos[7]].cd(k)
            plots["hitposafterpulserec"][key].Draw(opts1d)
            # number of clusters
            c[namespos[8]].cd(k)
            plots["nclusters"][key].Draw(opts1d)
            # time of cluster
            c[namespos[9]].cd(k)
            plots["clusterhittime"][key].Draw(opts1d)
            # time of cluster
            c[namespos[10]].cd(k)
            plots["clusterhittimemulticluster"][key].Draw(opts1d)
            c[namespos[11]].cd(k)
            plots["clusterhittimelatecluster"][key].Draw(opts1d)
            c[namespos[12]].cd(k)
            plots["nlateclusters"][key].Draw(opts1d)
            # 2d plots
            if d == 0:
                c[namespos[3]].cd(wc)
                plots["hitposrec"][wc].Draw(opts2d)
        
        if DrawWireResHists:
            # draw plot
            c[namesres[0]].cd(k)
            plots["residual_as_func_of_pos"][key].Draw(opts2d)
            # draw profile
            c[namesres[2]].cd(k)
            h = plots["residual_as_func_of_pos"][key].RebinX(4, "residual_as_func_of_pos_temp")
            prof = h.ProfileX()
            prof.GetYaxis().SetTitle("residual (mm)")
            prof.Draw(optsprof)
            
            # draw plot
            c[namesres[1]].cd(k)
            plots["residualovererror_as_func_of_pos"][key].Draw(opts2d)
            # draw profile
            c[namesres[3]].cd(k)
            h = plots["residualovererror_as_func_of_pos"][key].RebinX(4, "residualovererror_as_func_of_pos_temp")
            prof = h.ProfileX()
            prof.GetYaxis().SetTitle("residual (mm)")
            prof.DrawCopy(optsprof)
        if DrawAngleHists:
            # draw plot
            c[namesang[0]].cd(k)
            plots["residual_as_func_of_opp"][key].Draw(opts2d)
            # draw profile
            c[namesang[2]].cd(k)
            h = plots["residual_as_func_of_opp"][key].RebinX(4, "residual_as_func_of_opp_temp")
            prof = h.ProfileX()
            prof.GetYaxis().SetTitle("residual (mm)")
            print "Fitting pol1 on residual as function of position."
            #fit_opts = "NFQS" # Q = quiet mode, N=do not draw, F=use minuit, M=find better fit, S=return result
            result = prof.Fit("pol1", "S")
            angleoffsets[key] = (result.Value(0), result.ParError(0), result.Value(1), result.ParError(1))
            prof.DrawCopy(optsprof)
            
            # draw y shape to estimate error if the opp pos is unknown
            c[namesang[4]].cd(k)
            h = plots["residual_as_func_of_opp"][key].ProjectionY()
            angmessages.append("%s angle y plot mean=%s, rms=%s" % (key, h.GetMean(), h.GetRMS()))
            h.DrawCopy(opts1d)
            
            # draw plot
            c[namesang[1]].cd(k)
            plots["residualovererror_as_func_of_opp"][key].Draw(opts2d)
            # draw profile
            c[namesang[3]].cd(k)
            h = plots["residualovererror_as_func_of_opp"][key].RebinX(4, "residualovererror_as_func_of_opp_temp")
            prof = h.ProfileX()
            prof.GetYaxis().SetTitle("residual (mm)")
            print "Fitting pol1 on residual as function of position over err."
            prof.Fit("pol1")
            prof.DrawCopy(optsprof)
    
    for name in names:
        can = c[name]
        can.Update()
        can.Print(name + ".png")
    if DrawAngleHists:
        print "Printing angle info"
        pprint.pprint(angleoffsets)
        pprint.pprint(angmessages)
        
def drawhitpos(hit_time, key, hit_pos):
    DrawHitPosPlots = config["DrawHitPosPlots"]
    DrawWireResHists = config["DrawWireResHists"]
    DrawAngleHists = config["DrawAngleHists"]
    if DrawHitPosPlots:
        if hit_time < mintime:
            plots["hitposearly"][key].Fill(hit_pos)
        elif hit_time > maxtime:
            plots["hitposafterpulse"][key].Fill(hit_pos)
        else: 
            plots["hitpos"][key].Fill(hit_pos)
            
def drawstuff(self):
    DrawHitPosPlots = config["DrawHitPosPlots"]
    DrawWireResHists = config["DrawWireResHists"]
    DrawAngleHists = config["DrawAngleHists"]
    # plot hit positions for different time cuts in 1d
    if DrawHitPosPlots:
        for key, clusters in self.hits.items():
            if key[1] == 1: continue # skip y hits
            #if key[0] == 3: pprint.pprint( self.hits)
            
            # plots x vs y but only if a single hit
            '''if len(clusters) == 1:
                hit = clusters[0]
                hit_posx = hit.get_hit_pos()
                alt = (key[0], 1)
                try:
                    oppclusters = self.hits[alt]
                    if len(oppclusters) != 1: raise KeyError
                    else: temp = oppclusters[0]
                except KeyError: continue # skip where no y pos exists
                else: 
                    stats["DrawHisPosPlots: Have both x and y hit"] += 1
                    hit_posy = temp.get_hit_pos()
                    plots["hitposrec"][wc].Fill(hit_posx, hit_posy)'''
            alt = (key[0], 1)
            wc = key[0]
            try:
                altclusters = self.hits[alt]
            except KeyError: continue # skip where no y pos exists
            else: 
                pairs = self.getpairs(clusters, altclusters)
                #if key[0] == 3: 
                #    print key[0]
                #    pprint.pprint(pairs)
                for pair in pairs:
                    hitx, hity = pair
                    hit_posx = hitx.get_hit_pos()
                    hit_posy = hity.get_hit_pos()
                    #if key[0] == 3: 
                    #    print hit_posx, hit_posy
                    plots["hitposrec"][wc].Fill(hit_posx, hit_posy)
                  
        if DrawHitPosPlots:
            for key, clusters in self.hits.items():
                additional = []
                try: 
                    additional = self.clusters_during_tdc_timecut[key]
                except KeyError: pass
                clustersv2 = itertools.chain(clusters, additional)
                for a, b in itertools.permutations(clustersv2, 2):  
                    dist = abs(a.get_hit_pos() - b.get_hit_pos())
                    plots["secondhitdist"][key].Fill(dist)
            
        for key, clusters in itertools.chain(self.hits.items(), self.clusters_during_tdc_timecut.items()):
            for c in clusters:
                hit_pos = c.get_hit_pos()
                hit_time = c.get_hit_time()
                wc, d = key
                tkey = (wc, d, tdc)
                # apply a time cut
                mintime, maxtime = timecutinfo[tkey]
                # plot hit positions for different time cuts in 1d
                if DrawHitPosPlots:
                    if hit_time < mintime:
                        plots["hitposearlyrec"][key].Fill(hit_pos)
                    elif hit_time > maxtime:
                        plots["hitposafterpulserec"][key].Fill(hit_pos)
                    else: 
                        plots["hitposrec1d"][key].Fill(hit_pos)
                plots["clusterhittime"][key].Fill(hit_time)
                if len(clusters) > 1:
                    plots["clusterhittimemulticluster"][key].Fill(hit_time)
            plots["nclusters"][key].Fill(len(clusters))
        for key, clusters in self.clusters_during_tdc_timecut.items():
            for c in clusters:
                hit_pos = c.get_hit_pos()
                hit_time = c.get_hit_time()
                plots["clusterhittimelatecluster"][key].Fill(hit_time)
            plots["nlateclusters"][key].Fill(len(clusters))
                    
