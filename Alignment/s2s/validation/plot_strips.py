import ROOT
ROOT.gROOT.SetBatch(True)
#ROOT.gStyle.SetOptStat(0);
import sys
import itertools
import os
import pprint

# Stronger error conditions
FINALS2S = True

def dofit(temp):
    
    function = "landau"
    # do initial fit
    myfit = ROOT.TF1("myfit", function, 0, 10);
    temp.Fit("myfit", "QRNI")
    max_ = myfit.GetMaximumX(0, 10)
    maxy = myfit.GetMaximum(0, 10)
    x = myfit.GetParameter(1)
    #a, b = max_ * 0.1, max_ * 4
    scale = 0.3
    low_bin = temp.FindFirstBinAbove( maxy*scale );
    high_bin = temp.FindLastBinAbove( maxy*0.2 );
    a = temp.GetBinCenter( low_bin - 1 ); # TODO make sure it's not < 0
    b = temp.GetBinCenter( high_bin + 1 );
    #print "Plotting around", a, b
    myfit2 = ROOT.TF1("myfit2", function, a, b);
    r = temp.Fit("myfit2", "QRI")
    return myfit2, int(r)

def getnbins(module):
    return (60 - 20) / (29 - 1) * module + 20 if module <= 29 else 60

def printfixeds2s(c, s2s):
    h = ROOT.TH2D("title", "New Fitted X vs S2S Const;S2S Constant;Fitted X", 40, 0.4, 1.8, 40, 1.0, 1.45)    
    TEST_THESE_MODULES = (0, 1, 10, 20, 30, 38, 40, 41)
    TEST_THESE_STRIPS = (1, 3, 63, 61, 31, 33, 8, 9, 50, 51)
    for (module, strip) in sorted(s2s):
        info = s2s[(module, strip)]
        (const, s2serr, n, chi2, chi2N, err) = info
        
        # skip if not in one of the special module/strip combos
        skip = (module not in TEST_THESE_MODULES or strip not in TEST_THESE_STRIPS)
        # but don't skip if it meets anything here.
        # TODO remove 41 cut when needed
        if module == 41: skip = False
        # Also high s2s const cuts, or really low ones
        if const + s2serr > 2.25 or const - s2serr < 0: skip = False
        # or if the ratio cut is applied
        if const != 0 and s2serr / const > 0.10: skip = False
        if skip: continue
        
        print "On", (module, strip)
        try: os.mkdir("energy_plots/fixed/module{0:02d}".format(module))
        except OSError: pass # already exists
        nbins = getnbins(module)
        c.Draw("%s*10.0*st_mev/st_path>>htemp(%s, 0, 10)" % (const, nbins), 
            "st_mev != 0.0 && st_path > 2.0 && ev_extraEnergy <= 100.0 && ev_ntracks == 1 && st_module == %s && st_strip == %s" % (module, strip))
        c.Draw("10.0*st_mev/st_path>>htemp2(%s, 0, 10)" % nbins, 
            "st_mev != 0.0 && st_path > 2.0 && ev_extraEnergy <= 100.0 && ev_ntracks == 1 && st_module == %s && st_strip == %s" % (module, strip))

        temp = ROOT.gDirectory.Get("htemp")
        myfit2, errcode = dofit(temp)
        x = myfit2.GetParameter(1)
        xerr = myfit2.GetParError(1)
        chi2 = myfit2.GetChisquare()
        ndf = myfit2.GetNDF()
        
        # want to plot s2s vs x position
        if module not in (0, 41) and err == 0: # Those modules aren't good so don't do them
            h.Fill(const, x)
        
        temp2 = ROOT.gDirectory.Get("htemp2")
        temp.SetTitle(str(info))
        temp.GetXaxis().SetTitle("(x, xerr, chi2, ndf, ecode)=" + str((x, xerr, chi2, ndf, errcode)))
        temp.GetYaxis().SetRangeUser(0, 1.1 * max(temp.GetMaximum(), temp2.GetMaximum()))
        temp.SetLineColor(2)
        temp.Draw()
        temp2.Draw("same")
        c1.Print("energy_plots/fixed/module{0:02d}/strip{1:02d}.png".format(module, strip))
    prof = h.ProfileX()
    prof.Fit("pol1")
    h.Draw("colz")
    c1.Print("energy_plots/fixed/xposVsS2S.png")
    f = ROOT.TFile("energy_plots/fixed/info.root", "recreate")
    h.Write()
    f.Close()

def gets2s(c):

    print "Number of entries:", c.GetEntries()
    #c.Scan("st_strip:st_mev:st_path:ev_extraEnergy:ev_ntracks:st_module", "st_module<20")
    
    # landau function params:
    # param 0: scale
    # param 1: x position ~ max
    # param 2: idk
    # note: max / x ~ 0.935752140929
    
    TEST_THESE_MODULES = (0, 27, 28, 41) # TODO remove #(1, 20, 29)# (0, 1, 20, 29, 40, 41)
    TEST_THESE_STRIPS = ()#(1, 3, 32, 63, 50)# (1, 3, 63, 61, 31, 33, 8, 9, 50, 51)
    
    d = dict()
    
    # Define some error limits
    NLIMIT = 100
    CHI2LIMIT = 25 # TODO find good limit
    CHI2LIMIT2 = 0.1
    RATIOCUT = 0.1 # If ds2s > 10% then it's a problem channel. 10% is based on looking at plots
    for module in range(0, 42): # module goes from 0 to 41
        #if module > 1: continue
        #if not 23 < module < 27: continue
        #if module != 29: continue
        if len(TEST_THESE_MODULES) != 0 and module not in TEST_THESE_MODULES: continue
        print "On module", module
        
        
        nbins = getnbins(module)
        # TODO st_path is usually in, but removed bc st_path is zero in tracker of SuperHCal for many events.
        #c.Draw("st_strip:10.0*st_mev/st_path>>htemp(%s, 0, 10, 64, -0.5, 64 - 0.5)" % nbins, 
        #   "st_mev != 0.0 && st_path > 2.0 && ev_extraEnergy <= 100.0 && ev_ntracks == 1 && st_module == %s" % module)
        c.Draw("st_strip:10.0*st_mev>>htemp(%s, 0, 10, 64, -0.5, 64 - 0.5)" % nbins, 
           "st_mev != 0.0 && ev_extraEnergy <= 100.0 && ev_ntracks == 1 && st_module == %s" % module)
            
        h = ROOT.gDirectory.Get("htemp")
        print h, h.GetEntries()
        try: os.mkdir("energy_plots/strips/module{0:02d}".format(module))
        except OSError: pass # already exists
        for strip in range(1, 64): # strip goes from 1 to 63
            if len(TEST_THESE_STRIPS) != 0 and strip not in TEST_THESE_STRIPS: continue
            pos = (module, strip)
            print "Drawing strip", strip
            bin = h.GetYaxis().FindBin(strip)
            temp = h.ProjectionX("module{0:02d}_strip{1:02d}".format(module, strip), bin, bin)
            if temp.GetEntries() == 0: 
                print "Zero entries, skipping module", module, "strip", strip
                info = (1.0, 0, 0, 0, 0, 100)
                d[pos] = info
                continue
                
            if pos == (6, 20):  # TODO temp, skill due to gsl: qags.c:563: ERROR: integral is divergent, or slowly convergent
                info = (1.0, 0, 0, 0, 0, 100)
                d[pos] = info
                continue
                
            temp.Draw()
            c1.Print("energy_plots/strips/module{0:02d}/strip{1:02d}.png".format(module, strip))
            continue;
            
            myfit2, errcode = dofit(temp)
            
            #print temp, temp.GetEntries()
            n = int(temp.GetEntries())
            x = myfit2.GetParameter(1)
            xerr = myfit2.GetParError(1)
            chi2 = myfit2.GetChisquare()
            ndf = myfit2.GetNDF() 	
            if ndf == 0: 
                print "Warning n == 0", (module, strip), n, x, xerr, chi2
                info = (1.0, 0, 0, 0, 0, 100)
                d[pos] = info
                continue
            s2s = 1/x if x != 0 else 1.0
            xerr = xerr/x**2 if x != 0 else 0.0
            # Holds the error code
            err = 0
            chi2N = chi2/ndf
            
            # Check if there's a problem with this strip
            # TODO remove module 41 cut peds are fixed
            if errcode != 0 or module == 41:
                err += 1
            ratio = (xerr / s2s) if xerr != 0 else 0
            if FINALS2S and (chi2N >= CHI2LIMIT or chi2N < CHI2LIMIT2 or ratio > RATIOCUT): 
                err += 10
            if n <= NLIMIT: 
                err += 100
            if s2s < 0 or (FINALS2S and s2s - xerr < 0): # close to or below zero 
                if s2s < 0:
                    s2s = 1
                err += 1000
               
            # save all info
            info = (s2s, xerr, n, chi2, chi2N, err)
            d[pos] = info
            
            # Draw stuff
            temp.SetTitle("(s2s, xerr, n, chi2, chi2/100, err)=" + str(info))
            temp.Draw()
            c1.Print("energy_plots/module{0:02d}/strip{1:02d}.png".format(module, strip))
            if err != 0:
                temp.Draw()
                c1.Print("energy_plots/errors/module{0:02d}_strip{1:02d}.png".format(module, strip))
                
            c1.Clear()
    return d
    
def getolds2s(oldfilename):
    out = dict()
    if oldfilename == None: return out
    with open(oldfilename) as f:
        lines = list(f)
        lines = map(lambda x: x.strip(), lines)
        for line in lines:
            if line[0] == "#": continue
            (detstr, subdetstr, modstr, planestr, stripstr, s2sstr, ds2sstr, entriesstr, errorstr) = line.split()
            det = int(detstr)
            subdet = int(subdetstr)
            module = int(modstr)
            plane = int(planestr)
            strip = int(stripstr)
            const = float(s2sstr)
            ds2s = float(ds2sstr)
            entries = int(entriesstr)
            error = int(errorstr)
            # if error code, fill with 1.0
            if error != 0: const = 1.0
            # Fill dict
            out[(module, strip)] = const
    return out

if __name__ == "__main__":
    # Get the playlist
    playlist = sys.argv[1]
    olds2s = None
    if len(sys.argv) > 2:
        olds2s = sys.argv[2]
    old = getolds2s(olds2s)
    
    fnew = open(playlist, 'r')
    
    # Make the tchain
    c = ROOT.TChain("nt")
    i = 0
    for line in fnew:
        #run, sub, filename = line.split()
        filename = line.strip()
        c.Add(filename)
        if i == 50: break
        i += 1
    print "Finished adding files", i
    c1 = ROOT.TCanvas("c1", "c1", 1500, 800)
    
    try: os.mkdir("energy_plots/strips")
    except OSError: pass # already exists
    
    d = gets2s(c)
    exit()
    
    # Get the avg
    avg = 0.0
    N = 0
    new = dict()
    for pos, info in d.items():
        s2s, s2serr, n, chi2, chi2N, err = info
        # multiply by previous iteration of s2s
        if old is not None:
            oldconst = 1.0
            try: oldconst = old[pos]
            except KeyError: pass # not in old
            news2s = s2s * oldconst
        if err == 0: 
            avg += s2s
            N += 1
        else:
            print pos, info
        new[pos] = (news2s, s2serr, n, chi2, chi2N, err)
    new2 = d
    d = new
    # Print info for debugging
    if (N != 0): 
        avg = avg / float(N)
        print "avg", avg
        const = 1 / float(avg)
        print "const", const
    else:
        print "Error: N channels == 0"
        const = 1
    
    # Loop to make the consts
    bar = dict()
    for pos, info in d.items():
        s2s, s2serr, n, chi2, chi2N, err = info
        s2s *= const
        bar[pos] = (s2s, s2serr, n, chi2, chi2N, err)
        new2[pos] = (new2[pos][0] * const, s2serr, n, chi2, chi2N, err)
        
    # Finally write the output
    with open("energy_plots/s2s_constants_1304.txt", "w") as f:
        f.write("""# begin   1428362995270207 Mon Apr 06 18:29:55 2015
# end     1429619911664765 Tue Apr 21 07:38:31 2015
# elapsed 20948606576.0 min
# min occ 1 hits
# detector subdet module plane strip s2s ds2s entries error
""")    
        # Write info on each strip
        for pos, info in sorted(bar.items()):
            l = list(pos)
            l.extend(info)
            module, strip = pos
            # module 21 is first HCal module
            l.append(4 if module < 21 else 5)
            # TODO add plane and detector info if needed
            idk = "0 {8} {0} 1 {1} {2} {3} {4:d} {7}\n".format(*l)
            f.write(idk)
            
            # Finally write the output
    with open("energy_plots/s2s_constants_new.txt", "w") as f:
        f.write("""# begin   1428362995270207 Mon Apr 06 18:29:55 2015
# end     1429619911664765 Tue Apr 21 07:38:31 2015
# elapsed 20948606576.0 min
# min occ 1 hits
# detector subdet module plane strip s2s ds2s entries error
""")    
        # Write info on each strip
        for pos, info in sorted(new2.items()):
            l = list(pos)
            l.extend(info)
            module, strip = pos
            # module 21 is first HCal module
            l.append(4 if module < 21 else 5)
            # TODO add plane and detector info if needed
            idk = "0 {8} {0} 1 {1} {2} {3} {4:d} {7}\n".format(*l)
            f.write(idk)
    exit() # TODO remove
    printfixeds2s(c, new2)
        
    

        
