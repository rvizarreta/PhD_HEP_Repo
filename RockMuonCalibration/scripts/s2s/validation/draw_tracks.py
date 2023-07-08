
import sys
import os
import array
import ROOT
ROOT.gROOT.SetBatch(True)
# removes stats box
ROOT.gStyle.SetOptStat(0)

plotclusters = True

def getzposition(runnumber, module):
    if runnumber < 1511: # ECAL/HCAL
        ecalpitch = (52.216 + 20) / 2 # TODO set these
        hcalpitch = 52.216
        s = 0
        for i in range(module+1):
            if module < 21: pitch = ecalpitch
            else: pitch = hcalpitch
            s += pitch
        return s
    else: # SuperHCal
        trackerpitch = 20 # mm
        hcalpitch = 52.216
        doublepitch = 80.983
        s = 0
        for i in range(module+1):
            if module < 21: pitch = trackerpitch
            elif module < 24: pitch = hcalpitch
            elif module < 28: pitch = doublepitch
            else: pitch = hcalpitch
            s += pitch
        return s

if __name__ == "__main__":
    # Get the playlist
    playlist = sys.argv[1]
    
    fnew = open(playlist, 'r')
    
    # Make the tchain
    #c = ROOT.TChain("nt")
    c = ROOT.TChain("minerva")
    i = 0
    for line in fnew:
        filename = line.strip().replace("Rock", "DST")
        c.Add(filename)
        i += 1
        if i == 50: break # TODO remove
    print "Finished adding files", i
    c1 = ROOT.TCanvas("c1", "c1", 1500, 800)
    
    try: os.mkdir("trackplots")
    except OSError: pass # already exists
    
    # Consts
    strip_pitch = 16.7386 # mm, from geom
    strip_offset = 31 # x = 0 is at this strip number
    
    for i, event in enumerate(c):
        if event.n_tracks != 1: continue # skip 0, 2+
        
        # Now loop over the event
        
        # First loop over hits
        hitx = list()
        hitz = list()
        for i in range(event.n_clusters_id):
            if event.hit_view[i] != 1: continue # skip U/V views
            module = event.hit_module[i]
            x = (event.hit_strip[i] - strip_offset) * strip_pitch 
            z = getzposition(event.ev_run, module)
            print x, z
            hitx.append(x)
            hitz.append(z)
        hits = ROOT.TGraph(len(hitz), array.array("d", hitz), array.array("d", hitx))
        hits.SetMarkerStyle(23)
        hits.SetMarkerColor(ROOT.kRed)
        
        # Then loop over clusters
        clusterx = list()
        clusterz = list()
        for i in range(event.n_clusters_id):
            print event.clus_id_lpos[i], event.clus_id_z[i], event.clus_id_view[i]
            if event.clus_id_view[i] != 1: continue # skip U/V views
            x = (event.clus_id_tpos1[i] + event.clus_id_tpos2[i]) * -0.5 # TODO what is right?
            z = event.clus_id_z[i]
            clusterx.append(x)
            clusterz.append(z)
        clusters = ROOT.TGraph(len(clusterz), array.array("d", clusterz), array.array("d", clusterx))
        clusters.SetMarkerStyle(20)
        clusters.SetMarkerColor(ROOT.kBlack)
        
        # The loop over nodes
        nodex = list()
        nodez = list()
        for i in range(event.trk_nodes[0]):
            x = event.trk_node_X[i]
            z = event.trk_node_Z[i]
            print x, z
            nodex.append(x)
            nodez.append(z)
        nodes = ROOT.TGraph(len(nodex), array.array("d", nodez), array.array("d", nodex))
        nodes.SetMarkerStyle(33)
        nodes.SetMarkerColor(ROOT.kBlue)
        
        '''hhits = ROOT.TGraph("hhits", "hhits;Z (mm);X (mm)", 50, 0, 1800, 50, -600, 600)
        # See https://root.cern.ch/doc/v608/classTAttMarker.html
        hhits.SetMarkerSyle(23)
        hclusters = ROOT.TH2D("hclusters", "hclusters;Z (mm);X (mm)", 50, 0, 1800, 50, -600, 600)
        hclusters.SetMarkerSyle(20)
        hnodes = ROOT.TH2D("hnodes", "hnodes;Z (mm);X (mm)", 50, 0, 1800, 50, -600, 600)
        hnodes.SetMarkerSyle(33)
        hnodes.SetMarkerColor(ROOT.kBlue)'''
        
        #hhits.Draw()
        #hclusters.Draw("same")
        
        rangex = (0, 1800)
        rangey = (-1000, 1000)
        
        #hits.Draw("P")
        #hits.GetYaxis().SetRangeUser(*rangey)
        #hits.GetXaxis().SetRangeUser(*rangex)
        #hits.Draw("AP")
        #clusters.Draw("P")
        #clusters.GetYaxis().SetRangeUser(*rangey)
        #clusters.GetXaxis().SetRangeUser(*rangex)
        #clusters.Draw("P")
        #nodes.Draw("AP same")
        #nodes.GetXaxis().SetRangeUser(*rangex)
        #nodes.GetYaxis().SetRangeUser(*rangey)
        #nodes.Draw("AP same")
        
        mg = ROOT.TMultiGraph()
        mg.Add(hits)
        mg.Add(clusters)
        mg.Add(nodes)
        mg.Draw("AP")
        mg.GetXaxis().SetRangeUser(*rangex)
        mg.GetYaxis().SetRangeUser(*rangey)
        mg.Draw("AP")
        
        c1.Print("trackplots/event_{0:06d}_{1:03d}_{2:03d}.png".format(event.ev_run, event.ev_sub_run, event.ev_gate))
        #exit()
    
"""
00430       minervaTree->Branch("n_tracks",&m_n_tracks,"n_tracks/I",32768);
00431       minervaTree->Branch("trk_index",&m_trackIndex,"trk_index[n_tracks]/I",32768);
00432       minervaTree->Branch("trk_type", &m_trackType, "trk_type[n_tracks]/I",32768);
00433       minervaTree->Branch("trk_patrec", &m_trackPatRec, "trk_patrec[n_tracks]/I",32768);
00434       minervaTree->Branch("trk_time_slice",&m_trackTimeSlice,"trk_time_slice[n_tracks]/I",32768);
00435       minervaTree->Branch("trk_vis_energy",&m_trackVisEnergy,"trk_vis_energy[n_tracks]/D",65536);
00436       minervaTree->Branch("trk_theta",&m_trackTheta,"trk_theta[n_tracks]/D",65536);
00437       minervaTree->Branch("trk_phi",&m_trackPhi,"trk_phi[n_tracks]/D",65536);
00438       minervaTree->Branch("trk_hits",&m_trackHits,"trk_hits[n_tracks]/I",32768);
00439       minervaTree->Branch("trk_dof",&m_trackDof,"trk_dof[n_tracks]/I",32768);
00440       minervaTree->Branch("trk_chi2perDof",&m_trackChi2,"trk_chi2perDof[n_tracks]/D",65536);
00441       minervaTree->Branch("trk_fitMass",&m_trackFitMass,"trk_fitMass[n_tracks]/D",65536);
00442       minervaTree->Branch("trk_nodes",&m_trackNodes,"trk_nodes[n_tracks]/I",32768);
00443       sprintf(leaflist,"trk_node_X[n_tracks][%i]/D",m_maxNodesOnTrack);
00445       sprintf(leaflist,"trk_node_Y[n_tracks][%i]/D",m_maxNodesOnTrack);
00447       sprintf(leaflist,"trk_node_Z[n_tracks][%i]/D",m_maxNodesOnTrack);
00449       sprintf(leaflist,"trk_node_aX[n_tracks][%i]/D",m_maxNodesOnTrack);
00451       sprintf(leaflist,"trk_node_aY[n_tracks][%i]/D",m_maxNodesOnTrack);
00453       sprintf(leaflist,"trk_node_qOverP[n_tracks][%i]/D",m_maxNodesOnTrack);
00455       sprintf(leaflist,"trk_node_chi2[n_tracks][%i]/D",m_maxNodesOnTrack);
00457       sprintf(leaflist,"trk_node_cluster_idx[n_tracks][%i]/I",m_maxNodesOnTrack);
00461         minervaTree->Branch("trk_usedFor",&m_trackUsedFor,"trk_usedFor[n_tracks]/I",32768); 
"""
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
