import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0);
import sys
import os

def drawratio(a, b, name, limits = None):
    ext = ".png" if limits == None else "_limited.png"
    filename = os.path.join("ratio", name + ext)
    a.Divide(b)
    if limits != None:
        a.GetZaxis().SetRangeUser(*limits)   
    c1 = ROOT.TCanvas("c1", "c1", 1500, 800)
    a.Draw("colz") 
    c1.Print(filename)

if __name__ == "__main__":
    try: os.mkdir("ratio")
    except OSError: pass # already exists
    da = dict()
    db = dict()
    # first set
    s2sfile = sys.argv[1]
    fnew = open(s2sfile, 'r')
    nstrips = 63
    nmodules = 42
    modulestart, moduleend = -0.5, 41.5
    stripstart, stripend = 0.5, 63.5
    args = (nmodules, modulestart, moduleend, nstrips, stripstart, stripend)
    '''n = ROOT.TH2D("n", "N hits;module;strip", *args)
    c = ROOT.TH2D("const", "S2S constant;module;strip", *args)
    d = ROOT.TH2D("ds2s", "dS2S;module;strip", *args)
    ratio = ROOT.TH2D("ratio", "dS2S/S2S;module;strip", *args)
    err = ROOT.TH2D("err", "Has error code;module;strip", *args)
    err1 = ROOT.TH2D("err1", "Has error code 1;module;strip", *args)
    err10 = ROOT.TH2D("err10", "Has error code 10;module;strip", *args)
    err100 = ROOT.TH2D("err100", "Has error code 100;module;strip", *args)
    err1000 = ROOT.TH2D("err1000", "Has error code 1000;module;strip", *args)
    errmixed = ROOT.TH2D("errm", "Has more than one error code;module;strip", *args)'''
    notmixed = (0, 1, 10, 100, 1000, 10000)
    a = dict()
    for line in fnew:
        if line[0]=='#':
            #print >>fout, line[0:-1] # Get rid of end of line character--python's print adds one
            continue
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
        pos = (module, strip)
        info = (const, ds2s, entries, error)
        da[pos] = info
        '''n.Fill(module, strip, entries)
        c.Fill(module, strip, const)
        d.Fill(module, strip, ds2s)
        if ds2s != 0 and ds2s > 0 and const > 0: ratio.Fill(module, strip, ds2s / const)
        err.Fill(module, strip, 1 if error > 0 else 0)
        err1.Fill(module, strip, 1 if (error // 1) % 10 != 0 else 0)
        err10.Fill(module, strip, 1 if (error // 10) % 10 != 0 else 0)
        err100.Fill(module, strip, 1 if (error // 100) % 10 != 0 else 0)
        err1000.Fill(module, strip, 1 if (error // 1000) % 10 != 0 else 0)
        errmixed.Fill(module, strip, 1 if not (error in notmixed) else 0)'''
    # second set,
    s2sfile = sys.argv[2]
    fnew = open(s2sfile, 'r')
    nstrips = 63
    nmodules = 42
    modulestart, moduleend = -0.5, 41.5
    stripstart, stripend = 0.5, 63.5
    args = (nmodules, modulestart, moduleend, nstrips, stripstart, stripend)
    '''na = ROOT.TH2D("na", "N hits;module;strip", *args)
    ca = ROOT.TH2D("consta", "S2S constant;module;strip", *args)
    da = ROOT.TH2D("ds2sa", "dS2S;module;strip", *args)
    ratioa = ROOT.TH2D("ratioa", "dS2S/S2S;module;strip", *args)
    erra = ROOT.TH2D("erra", "Has error code;module;strip", *args)
    err1a = ROOT.TH2D("err1a", "Has error code 1;module;strip", *args)
    err10a = ROOT.TH2D("err10a", "Has error code 10;module;strip", *args)
    err100a = ROOT.TH2D("err100a", "Has error code 100;module;strip", *args)
    err1000a = ROOT.TH2D("err1000a", "Has error code 1000;module;strip", *args)
    errmixeda = ROOT.TH2D("errma", "Has more than one error code;module;strip", *args)'''
    notmixed = (0, 1, 10, 100, 1000, 10000)
    a = dict()
    for line in fnew:
        if line[0]=='#':
            #print >>fout, line[0:-1] # Get rid of end of line character--python's print adds one
            continue
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
        pos = (module, strip)
        info = (const, ds2s, entries, error)
        db[pos] = info
        '''na.Fill(module, strip, entries)
        ca.Fill(module, strip, const)
        da.Fill(module, strip, ds2s)
        if ds2s != 0 and ds2s > 0 and const > 0: ratioa.Fill(module, strip, ds2s / const)
        erra.Fill(module, strip, 1 if error > 0 else 0)
        err1a.Fill(module, strip, 1 if (error // 1) % 10 != 0 else 0)
        err10a.Fill(module, strip, 1 if (error // 10) % 10 != 0 else 0)
        err100a.Fill(module, strip, 1 if (error // 100) % 10 != 0 else 0)
        err1000a.Fill(module, strip, 1 if (error // 1000) % 10 != 0 else 0)
        errmixeda.Fill(module, strip, 1 if not (error in notmixed) else 0)'''
    '''drawratio(n, na, "n")
    drawratio(c, ca, "const")
    drawratio(c, ca, "const", (0.4, 1.6))
    drawratio(d, da, "ds2s")
    drawratio(d, da, "ds2s", (0.0, 2))
    drawratio(ratio, ratioa, "frac")
    drawratio(d, da, "frac", (0.0, 200))
    drawratio(err, erra, "err")'''
    
    a = set(da)
    b = set(db)
    const = ROOT.TH2D("const", "S2S Constant Ratio;module;strip", *args)
    ds = ROOT.TH2D("ds", "dS2S Ratio;module;strip", *args)
    n = ROOT.TH2D("n", "N Ratio;module;strip", *args)
    for pos in sorted(a & b):
        try:
            infoa = da[pos]
        except KeyError:
            print pos, "not in", s2s.argv[1]
            continue # don't need to check b
        try:
            infob = db[pos]
        except KeyError:
            print pos, "not in", s2s.argv[2]
            continue 
        ratios = [c / float(d) if d != 0 else 0 for c, d in zip(infoa, infob)]
        module, strip = pos
        const.Fill(module, strip, ratios[0] / 0.8253608363) # TODO remove 0.8253608363, is correction factor for no-hv-gains file. 
        ds.Fill(module, strip, ratios[1]) 
        n.Fill(module, strip, ratios[2]) 
        #print pos, "is", ratios, infoa, infob
    c1 = ROOT.TCanvas("c1", "c1", 1500, 800)
    const.Draw("colz")
    c1.Print("ratio/s2s_nolimit.png")
    const.GetZaxis().SetRangeUser(0.9, 1.1) 
    const.Draw("colz")
    c1.Print("ratio/s2s.png")
    const.GetZaxis().SetRangeUser(0, 2) 
    const.Draw("colz")
    c1.Print("ratio/s2s_unzoom.png")
    const.GetZaxis().SetRangeUser(0.95, 1.05) 
    const.Draw("colz")
    c1.Print("ratio/s2s_zoom.png")
    const.GetZaxis().SetRangeUser(0.97, 1.03) 
    const.Draw("colz")
    c1.Print("ratio/s2s_zoom_3percent.png")
    const.GetZaxis().SetRangeUser(0.98, 1.02) 
    const.Draw("colz")
    c1.Print("ratio/s2s_zoom_2percent.png")
    #const.GetZaxis().SetRangeUser(0.95, 1.05) 
    ds.Draw("colz")
    c1.Print("ratio/ds2s_nolimit.png") 
    ds.GetZaxis().SetRangeUser(0, 2) 
    ds.Draw("colz")
    c1.Print("ratio/ds2s.png")
    n.Draw("colz")
    c1.Print("ratio/n_nolimit.png")
    n.GetZaxis().SetRangeUser(0.95, 1.05) 
    n.Draw("colz")
    c1.Print("ratio/n.png")
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
