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
    filename = 'combinedAlignment_2017-12-07_run1_alignment.xml'
    import sys
    filename = sys.argv[1]
    import pprint
    
    mod, z1, rot1 = parse(filename)
    az = ROOT.TGraph(len(mod), mod, z1)
    az.SetMarkerStyle(23)
    az.SetMarkerColor(ROOT.kRed)
    arot = ROOT.TGraph(len(mod), mod, rot1)
    arot.SetMarkerStyle(23)
    arot.SetMarkerColor(ROOT.kRed)
    
    width = 16.7386
    diffz = array.array("d", [(z1[i]) / width for i in range(len(z1))])
    diffz = ROOT.TGraph(len(mod), mod, diffz)
    #diffang = array.array("d", [0.5*107*math.sin(180/math.pi*(rot2[i] - rot1[i])) / width for i in range(len(z1))])
    diffang = array.array("d", [180 / math.pi * (rot1[i]) for i in range(len(z1))])
    diffang = ROOT.TGraph(len(mod), mod, diffang)
    
    c1 = ROOT.TCanvas("c1", "c1", 900, 700)
    diffz.SetTitle("Alignment For Run1")
    diffz.Draw("AP")
    diffz.GetXaxis().SetTitle("Module")
    diffz.GetYaxis().SetTitle("Shift in Strip Separations")
    diffz.SetMarkerStyle(23)
    diffang.GetYaxis().SetRangeUser(-1, 1)
    diffang.SetMarkerStyle(23)
    #mg = ROOT.TMultiGraph()
    #mg.Add(diff)
    #mg.Draw("AP")
    c1.Update()
    c1.Print("AlignZ.png")
    
    diffang.Draw("AP")
    diffang.SetTitle("Angle Alignment For Run1")
    diffang.GetXaxis().SetTitle("Module")
    diffang.GetYaxis().SetTitle("Angle (degrees)")
    #mg = ROOT.TMultiGraph()
    #mg.Add(diffrot)
    #mg.Draw("AP")
    c1.Print("AlignAngle.png")
