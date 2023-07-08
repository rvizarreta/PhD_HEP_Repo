import xml.etree.ElementTree as ET
import array
import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptTitle(1)
import math

def parse(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    i = 0
    za = list()
    rota = list()
    moda = list()
    for child in root:
        module = i
        moda.append(module)
        i += 1
        #print child, child.attrib["name"], child[0].text, child[1].text
        name = child.attrib["name"]
        z = float(child[0].text.split()[0])
        za.append(z)
        rot = float(child[1].text.split()[2])
        rota.append(rot)
    return array.array('d', moda), array.array('d', za), array.array('d', rota)
    
if __name__ == "__main__":
    #filename = 'combinedAlignment_cosmics_superhcal_2017-2-19.xml'
    #filename2 = 'combinedAlignment_cosmics_superhcal_2017-2-19_v2.xml'
    #filename = 'combinedAlignment_run1_2017-5-13_v2.xml'
    #filename2 = 'combinedAlignment_cosmics_run1_2017-5-18_divbyhvtarget_fixed_rocks_filtered.xml'
    #filename = 'combinedAlignment_2017-12-06_run1_alignment.xml'
    #filename2 = 'combinedAlignment_2017-12-07_run1_alignment.xml'
    import sys
    filename = sys.argv[1]
    filename2 = sys.argv[2]
    import pprint
    
    mod, z1, rot1 = parse(filename)
    az = ROOT.TGraph(len(mod), mod, z1)
    az.SetMarkerStyle(23)
    az.SetMarkerColor(ROOT.kRed)
    arot = ROOT.TGraph(len(mod), mod, rot1)
    arot.SetMarkerStyle(23)
    arot.SetMarkerColor(ROOT.kRed)
    
    mod, z2, rot2 = parse(filename2)
    bz = ROOT.TGraph(len(mod), mod, z2)
    bz.SetMarkerStyle(23)
    bz.SetMarkerColor(ROOT.kBlue)
    brot = ROOT.TGraph(len(mod), mod, rot2)
    brot.SetMarkerStyle(23)
    brot.SetMarkerColor(ROOT.kBlue)
    
    width = 16.7386
    diffz = array.array("d", [(z2[i] - z1[i]) / width for i in range(len(z1))])
    diffz = ROOT.TGraph(len(mod), mod, diffz)
    #diffang = array.array("d", [0.5*107*math.sin(180/math.pi*(rot2[i] - rot1[i])) / width for i in range(len(z1))])
    diffang = array.array("d", [180 / math.pi * (rot2[i] - rot1[i]) for i in range(len(z1))])
    diffang = ROOT.TGraph(len(mod), mod, diffang)
    
    c1 = ROOT.TCanvas("c1", "c1", 900, 700)
    diffz.SetTitle("Difference in X Position between Consecutive Calibration Runs for Run1")
    diffz.Draw("AP")
    diffz.GetXaxis().SetTitle("Module")
    diffz.GetYaxis().SetTitle("Difference in Strip Separations")
    diffz.SetMarkerStyle(23)
    diffz.GetYaxis().SetRangeUser(-0.1, 0.1)
    diffang.GetYaxis().SetRangeUser(-1, 1)
    diffang.SetMarkerStyle(23)
    #mg = ROOT.TMultiGraph()
    #mg.Add(diff)
    #mg.Draw("AP")
    c1.Update()
    c1.Print("ComparisonZ.png")
    
    diffang.Draw("AP")
    diffang.SetTitle("Difference in Angle between Consecutive Calibration Runs for Run1")
    diffang.GetXaxis().SetTitle("Module")
    diffang.GetYaxis().SetTitle("Angle Difference (degrees)")
    #mg = ROOT.TMultiGraph()
    #mg.Add(diffrot)
    #mg.Draw("AP")
    c1.Print("ComparisonAngle.png")
