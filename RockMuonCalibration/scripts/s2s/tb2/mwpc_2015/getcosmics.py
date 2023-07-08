import ROOT
ROOT.gROOT.SetBatch(True)

import math, random
import subprocess

TESTDST = "/minerva/data/testbeam2/run1data_new/Cosmics/TB_00001497_0003_cosmc_v09_1504210927_DST.root"
MUONPID = 13
MUONMASS = 105.6583715 #(35) MeV
MeV = 1
GeV = 1000 * MeV

def gettree(filename=TESTDST):
    #call = ["ls", "/minerva/data/testbeam2/run1data_new/*/*.root"]
    call = "find %s -print | grep %s$" % ("/minerva/data/testbeam2/run1data_new/", "root")
    s = subprocess.Popen(call, shell=True, stdout=subprocess.PIPE).communicate()[0]
    files = s.split()
    out = ROOT.TChain()
    for f in files:
        out.Add(f + "/minerva")
    #f = ROOT.TFile(filename)
    #t = f.Get("minerva")
    #return f, t
    return None, out

class Track(object):
    def __init__(self, pos, theta, phi, gof):
        self.pos = pos
        self.theta = theta
        self.phi = phi
        self.gof = gof
        # I'm not sure what's in the DST to save
        
def signthrow(chance = 0.5):
    return 1 if random.random() < chance else -1
        
class Throw(object):
    def __init__(self, track, seed=None):
        self.pos = track.pos
        self.theta = track.theta
        self.phi = track.phi
        self.energy = self.getenergyasfunctionofangle(self.theta, self.phi)
        self.pid = MUONPID * signthrow() # 50/50 positive and negative signs
        self.mass = self.getmass(self.pid)
        self.momentum = self.getmomentum(self.mass, self.energy)
        self.momentum_vector = self.getvector(self.momentum, self.theta, self.phi)
        
    def __str__(self):
        # want "PID0 x0 y0 z0 px0 py0 pz0 E0"
        # pdg       x       y       z          px          py          pz           E
        out = []
        out.append(self.pid)
        out.extend(map(lambda x: round(x, 1), self.pos))
        out.extend(map(lambda x: round(x, 3), self.momentum_vector))
        out.append(round(self.energy, 3))
        #return "\t".join(map(str, out))
        "# pdg       x       y       z          px          py          pz           E"
        # "{0:>12}|{1:>12}|{2:>15}|{3:>15}|{4:>10}|{5:>15}|{6:>15}|{7:>15}|{8:>15}|{9:>15}|{10:>15}|"
        s = "{0:>5}{1:>8}{2:>8}{3:>8}{4:>12}{5:>12}{6:>12}{7:>12}"
        return s.format(*map(str, out))
        
    def getenergyasfunctionofangle(self, theta, phi, chirkin=True, guan=True):
        # Cosmic spectrum
        lowP = 500.0*MeV
        highP = 4000*MeV #20000*MeV
        
        # TODO implement proper parameterization
        return random.uniform(lowP, highP)
        
    def getmomentum(self, mass, energy):
        return math.sqrt(energy**2 - mass**2)
        
    def getvector(self, length, theta, phi):
        x = length * math.cos(theta) * math.sin(phi)
        y = length * math.sin(theta) * math.sin(phi)
        z = length * math.cos(phi)
        return x, y, z
    
    def getmass(self, pid):
        if abs(pid) == 13:
            return MUONMASS
        else: raise ValueError("pid = %s not supported" % pid)
    
        

def gettracks(tree):
    tracks = []
    for event in tree:
        if event.n_tracks == 1 and event.ev_trigger_type == 8:
            assert event.trk_nodes > 0
            theta = event.trk_theta[0]
            phi = event.trk_phi[0]
            x = event.trk_node_X[0]
            y = event.trk_node_Y[0]
            z = event.trk_node_Z[0]
            gof = event.trk_chi2perDof[0]
            pos = (x, y, z)
        
            track = Track(pos, theta, phi, gof)
            tracks.append(track)
    return tracks
            
def getthrows(tracks, nthrows=1):
    #nthrows = 1 # eventually we might want to use 1 track and do multiple throws
    throws = []
    for track in tracks:
        for i in range(nthrows):
            throw = Throw(track)
            throws.append(throw)
    return throws
            
def thingy(tree, outfilename):
    tracks = gettracks(tree)
    throws = getthrows(tracks)
    with open(outfilename, "w") as f:
        f.write("# pdg       x       y       z          px          py          pz           E\n")
        for t in throws:
            f.write(str(t) + "\n")
def test():
    f, tree = gettree()
    thingy(tree, "test.txt")
    
def draw_energy2():
    f, tree = gettree()
    c = ROOT.TCanvas("c", "c", 1500, 800)
    #tree.Draw("clus_id_pe:clus_id_module", "n_tracks==1&&ev_trigger_type==8", "colz")
    tree.Draw("hit_pe:hit_module", "n_tracks==1&&ev_trigger_type==8&&hit_module>0", "colz")
    c.Print("cosmics_pe_vs_module.png")
    
def draw_energy():
    f, tree = gettree()
    tree.Show(0)
    # event.n_tracks == 1&&event.ev_trigger_type == 8
    c = ROOT.TCanvas("c", "c", 1500, 800)
    c.cd()
    h = ROOT.TH1D("h", "h;hits_total_pe;n events", 30, 0, 2000)
    tree.Draw("hits_total_pe[0]>>h", "n_tracks==1&&ev_trigger_type==8&&hits_total_pe>0.1")
    c.Print("cosmics_total_pe.png")
    #Sum$(hit_norm_energy)
    h1 = ROOT.TH1D("h1", "h1;hit_norm_energy;n events", 30, 0, 20)
    tree.Draw("hit_norm_energy>>h1", "n_tracks==1&&ev_trigger_type==8&&hit_norm_energy>0")
    c.Print("cosmics_hit_norm_energy.png")
    
    #clus_id_energy
    h2 = ROOT.TH1D("h2", "h2;clus_id_energy;n events", 30, 0, 20)
    tree.Draw("clus_id_energy>>h2", "n_tracks==1&&ev_trigger_type==8&&clus_id_energy>0")
    c.Print("cosmics_clus_id_energy.png")
    
    # clus_id_pe
    h3 = ROOT.TH1D("h3", "h3;clus_id_pe;n events", 30, 0, 50)
    tree.Draw("clus_id_pe>>h3", "n_tracks==1&&ev_trigger_type==8&&clus_id_pe>0")
    c.Print("cosmics_clus_id_pe.png")
    
if __name__ == "__main__":
    draw_energy2()
