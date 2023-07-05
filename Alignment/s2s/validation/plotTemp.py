import ROOT
ROOT.gROOT.SetBatch(True)
import glob
import array

def getChain(treename = "minerva"):
    if treename == "minerva":
        files = sorted(glob.glob("/minerva/data/testbeam2/calmuonsTemperature/*DST.root"))
    elif treename == "nt":
        files = sorted(glob.glob("/minerva/data/testbeam2/calmuonsTemperature/*Rock.root"))
    #files = files[:3]
    ch = ROOT.TChain(treename)
    map(ch.Add, files) # adds all the files as if by for loop
    return ch
    
def old():
    ch = getChain()
    
    c = ROOT.TCanvas("c", "c", 1500, 800)
    # clus_id_hits_idx, trk_node_cluster_idx
    ch.Draw("hit_norm_energy", "hit_norm_energy>=0&&n_tracks>0&&trk_node_cluster_idx>=0&&Iteration$==clus_id_hits_idx[trk_node_cluster_idx]")
    #ch.Draw("hit_norm_energy>>htemp(100, 0, 8)", "hit_norm_energy>=0")
    c.Print("energy.png")
    
def dofit(temp):
    
    function = "landau"
    # do initial fit
    myfit = ROOT.TF1("myfit", function, 0, 10);
    temp.Fit("myfit", "QRNI")
    max_ = myfit.GetMaximumX(0, 10)
    maxy = myfit.GetMaximum(0, 10)
    x = myfit.GetParameter(1)
    #a, b = max_ * 0.1, max_ * 4
    scale = 0.5
    low_bin = temp.FindFirstBinAbove( maxy*scale );
    high_bin = temp.FindLastBinAbove( maxy*scale );
    a = temp.GetBinCenter( low_bin - 1 ); # TODO make sure it's not < 0
    b = temp.GetBinCenter( high_bin + 1 );
    #print "Plotting around", a, b
    myfit2 = ROOT.TF1("myfit2", function, a, b);
    r = temp.Fit("myfit2", "QRI")
    return myfit2, int(r)
    
def main():
    ch = getChain("nt")
    
    # ev_newTemperatureSensor, ev_oldTemperatureSensor
    
    c = ROOT.TCanvas("c", "c", 1500, 800)
    # clus_id_hits_idx, trk_node_cluster_idx
    #ch.Draw("hit_norm_energy", "hit_norm_energy>=0&&n_tracks>0&&trk_node_cluster_idx>=0&&Iteration$==clus_id_hits_idx[trk_node_cluster_idx]")
    #ch.Draw("hit_norm_energy>>htemp(100, 0, 8)", "hit_norm_energy>=0")
    dt = 0.1
    mintemp = 24.4 - dt * 0.5
    means = list()
    for i in range(int(4 / dt)):
        tempmin = mintemp + i * dt
        tempmax = mintemp + (i + 1) * dt
        #print i, tempmin, tempmax
        temp = (tempmin + tempmax) * 0.5
        
        # Old sensor
        #cut = "&& (ev_gps_time * 10^-6 < 1428.6 || ev_gps_time * 10^-6 > 1428.7)"
        #ch.Draw("10.0*st_mev/st_path>>htemp(100, 0, 10)", 
        #       "st_mev != 0.0 && st_path > 2.0 && ev_extraEnergy <= 100.0 && ev_ntracks == 1 && ev_oldTemperatureSensor >= {0} && ev_oldTemperatureSensor < {1} {2}".format(tempmin, tempmax, cut))
        
        # New sensor
        cut = ""
        ch.Draw("10.0*st_mev/st_path>>htemp(100, 0, 10)", 
               "st_mev != 0.0 && st_path > 2.0 && ev_extraEnergy <= 100.0 && ev_ntracks == 1 && ev_newTemperatureSensor >= {0} && ev_newTemperatureSensor < {1} {2} && st_module==1".format(tempmin, tempmax, cut))
               
        htemp = ROOT.gDirectory.Get("htemp")
        #if htemp.GetEntries() == 0: continue
        fit, code = dofit(htemp)
        if code == 0:
            x = fit.GetParameter(1)
            xerr = fit.GetParError(1)
            chi2 = fit.GetChisquare()
            ndf = fit.GetNDF()
            foo = (temp, dt * 0.5, x, xerr, chi2, ndf, code)
            print foo
            means.append(foo)
        c.Print("temperaturePlots/energy{0:02.1f}.png".format(temp))
    #ch.Draw("10.0*st_mev/st_path:ev_oldTemperatureSensor>>htemp(10, 23, 24, 100, 0, 10)", 
    #           "st_mev != 0.0 && st_path > 2.0 && ev_extraEnergy <= 100.0 && ev_ntracks == 1", "colz")
    #c.Print("EnergyVsTemperature.png")
    print "Doing vs plot"
    n = len(means)
    import pprint
    pprint.pprint(means)
    x = array.array("d", map(lambda d: d[0], means))
    y = array.array("d", map(lambda d: d[2], means))
    xe = array.array("d", map(lambda d: d[1], means))
    ye = array.array("d", map(lambda d: d[3], means))
    t = ROOT.TGraphErrors(n, x, y, xe, ye)
    t.Draw("AP")
    t.Fit("pol1")
    c.Print("EnergyVsTemperature.png")
    

def drawTempVsTimeCosmics():
    ch = getChain()
    
    c = ROOT.TCanvas("c", "c", 1500, 800)
    
    h = ROOT.TH2D("name", "name", 100, 1428200000, 1429800000, 100, 22.5, 28)
    #h.Fill(1428200000, 22.5)
    h.Draw("AXIS")
    
    #ch.Draw("mtest2_measuredTemperatureNewSensor:ev_gps_time_sec+ev_gps_time_usec*10^-6>>htemp(10000, 1428200000, 1429800000, 100, 22.5, 28)", "", "same")
    ch.Draw("mtest2_measuredTemperatureNewSensor:ev_gps_time_sec+ev_gps_time_usec*10^-6", "", "same")
    #htemp = ROOT.gDirectory.Get("htemp")
    #print htemp, htemp.GetEntries()
    #htemp.GetYaxis().SetRangeUser(22.5, 28)
    #htemp.Draw("")
    c.Print("temperaturesNew.png")
    
    h.Draw("AXIS")
    ch.Draw("mtest2_measuredTemperatureOldSensor:ev_gps_time_sec+ev_gps_time_usec*10^-6", "", "same")
    #ch.Draw("mtest2_measuredTemperatureOldSensor:ev_gps_time_sec+ev_gps_time_usec*10^-6>>htemp(10000, 1428200000, 1429800000, 100, 22.5, 28)", "", "")
    #ch.Draw("mtest2_measuredTemperatureOldSensor:ev_gps_time_sec+ev_gps_time_usec*10^-6>>htemp(10000, 1428200000, 1429800000, 100, 22.5, 28)", "", "")
    #htemp = ROOT.gDirectory.Get("htemp1")
    #htemp = ROOT.gPad.GetPrimitive("htemp")
    #htemp.GetYaxis().SetRangeUser(22.5, 28)
    #htemp.Draw("")
    c.Print("temperatures.png")
    
    # Get the difference
    ch.Draw("mtest2_measuredTemperatureOldSensor - mtest2_measuredTemperatureNewSensor:ev_gps_time_sec+ev_gps_time_usec*10^-6>>htemp2(10000, 1428200000, 1429800000, 100, -2, 0)", "", "")
    c.Print("temperatureDifference.png")
    ch.Draw("(mtest2_measuredTemperatureOldSensor - mtest2_measuredTemperatureNewSensor) / 4:ev_gps_time_sec+ev_gps_time_usec*10^-6>>htemp2(10000, 1428200000, 1429800000, 100, -0.5, 0)", "", "")
    c.Print("temperatureDifferenceFraction.png")
    
def drawTempsFromFile(name = "OldSensorSmoothed"):
    ch = ROOT.TChain(name)
    ch.Add("/minerva/app/users/kleykamp/testbeam2/temperature/temperature.root")
    c = ROOT.TCanvas("c", "c", 1500, 800)
    ch.Draw("temperature:time")
    c.Print("Temps" + name + ".png")
    
if __name__ == "__main__":
    main()
    #drawTempVsTimeCosmics()
    #drawTempVsTimeCosmics()
    #drawTempsFromFile()
    #drawTempsFromFile("NewSensorSmoothed")
