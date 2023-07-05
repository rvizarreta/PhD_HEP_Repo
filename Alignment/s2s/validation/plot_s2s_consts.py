import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0);
import sys
import os

if __name__ == "__main__":
    try: os.mkdir("plots")
    except OSError: pass # already exists
    s2sfile = sys.argv[1]
    fnew = open(s2sfile, 'r')
    nstrips = 63
    nmodules = 42
    modulestart, moduleend = -0.5, 41.5
    stripstart, stripend = 0.5, 63.5
    args = (nmodules, modulestart, moduleend, nstrips, stripstart, stripend)
    n = ROOT.TH2D("n", "N hits;module;strip", *args)
    c = ROOT.TH2D("const", "S2S constant;module;strip", *args)
    d = ROOT.TH2D("ds2s", "dS2S;module;strip", *args)
    ratio = ROOT.TH2D("ratio", "dS2S/S2S;module;strip", *args)
    err = ROOT.TH2D("err", "Has error code;module;strip", *args)
    err1 = ROOT.TH2D("err1", "Has error code 1;module;strip", *args)
    err10 = ROOT.TH2D("err10", "Has error code 10;module;strip", *args)
    err100 = ROOT.TH2D("err100", "Has error code 100;module;strip", *args)
    err1000 = ROOT.TH2D("err1000", "Has error code 1000;module;strip", *args)
    errmixed = ROOT.TH2D("errm", "Has more than one error code;module;strip", *args)
    notmixed = (0, 1, 10, 100, 1000, 10000)
    
    if "new.txt" in s2sfile:
        consts1d = ROOT.TH1D("consts1d", "Change in S2S From Last Iteration;S2S Current / S2S Last Iteration;Number of Strips", 51, 0.95, 1.05)
    else:
        consts1d = ROOT.TH1D("consts1d", "S2S Const;S2S Const;Number of Strips", 51, 0, 5)
        
    
    avg = 0
    ns2s = 0
    onepercent = 0
    twopercent = 0
    threepercent = 0
    total = 0
    totalerr = 0
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
        
        if "new.txt" in s2sfile and error == 0:
            if abs(const - 1) < 0.01:
                onepercent += 1
            if abs(const - 1) < 0.02:
                twopercent += 1
            if abs(const - 1) < 0.03:
                threepercent += 1
        if error == 0: total += 1
        else: totalerr += 1
        
        n.Fill(module, strip, entries)
        # Skill error strips
        if error == 0:
            c.Fill(module, strip, const)
            consts1d.Fill(const)
        else:
            c.Fill(module, strip, 1.0)
        d.Fill(module, strip, ds2s)
        if ds2s != 0 and ds2s > 0 and const > 0: ratio.Fill(module, strip, ds2s / const)
        err.Fill(module, strip, 1 if error > 0 else 0)
        err1.Fill(module, strip, 1 if (error // 1) % 10 != 0 else 0)
        err10.Fill(module, strip, 1 if (error // 10) % 10 != 0 else 0)
        err100.Fill(module, strip, 1 if (error // 100) % 10 != 0 else 0)
        err1000.Fill(module, strip, 1 if (error // 1000) % 10 != 0 else 0)
        errmixed.Fill(module, strip, 1 if not (error in notmixed) else 0)
        if error == 0:
            avg += const
            ns2s += 1
    if "new.txt" in s2sfile:
        print "Number of strips within 1%:", onepercent / float(total)
        print "Number of strips within 2%:", twopercent / float(total)
        print "Number of strips within 3%:", threepercent / float(total)
        print "Number of strips", total
        print "Number of error strips", totalerr
    c1 = ROOT.TCanvas("c1", "c1", 900, 700)
    n.Draw("colz")
    c1.Print("plots/n.png")
    c.Draw("colz")
    c1.Print("plots/consts_nolimit.png")
    c.GetZaxis().SetRangeUser(0, 3)
    c.Draw("colz")
    c1.Print("plots/consts.png")
    c.GetZaxis().SetRangeUser(0.90, 1.1)
    c.Draw("colz")
    c1.Print("plots/consts_limited.png")
    c.GetZaxis().SetRangeUser(0.98, 1.02)
    c.Draw("colz")
    c1.Print("plots/consts_twopercent.png")
    c.GetZaxis().SetRangeUser(0.95, 1.05)
    c.Draw("colz")
    c1.Print("plots/consts_fivepercent.png")
    d.Draw("colz")
    c1.Print("plots/ds2s_nolimit.png")
    d.GetZaxis().SetRangeUser(0, 3)
    d.Draw("colz")
    c1.Print("plots/ds2s.png")
    ratio.Draw("colz")
    c1.Print("plots/ratio_nolimit.png")
    ratio.GetZaxis().SetRangeUser(0, 0.2)
    ratio.Draw("colz")
    c1.Print("plots/ratio.png")
    err.Draw("colz")
    c1.Print("plots/err.png")
    c1.SetLogy(False)
    err1.Draw("colz")
    c1.Print("plots/err1.png")
    err10.Draw("colz")
    c1.Print("plots/err10.png")
    err100.Draw("colz")
    c1.Print("plots/err100.png")
    err1000.Draw("colz")
    c1.Print("plots/err1000.png")
    errmixed.Draw("colz")
    c1.Print("plots/errmixed.png")
    consts1d.Draw()
    c1.Print("plots/consts1d.png")
    print "Sum s2s:", avg
    avg /= ns2s
    print "N s2s without error:", ns2s
    print "Average s2s:", avg
