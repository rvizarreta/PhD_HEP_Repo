
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
        if i == 300: break # TODO remove
    print "Finished adding files", i
    c1 = ROOT.TCanvas("c1", "c1", 1500, 800)
    
    try: os.mkdir("clusterplots")
    except OSError: pass # already exists
    
    c.Draw("clus_id_z>>htemp(41, 0, 1800)", "clus_id_view == 1", "")
    c1.Print("clusterplots/cluster_z.png")
    
    c.Draw("clus_id_lpos>>htemp(63, -800, 800)", "clus_id_view == 1", "")
    c1.Print("clusterplots/cluster_y.png")
    
    c.Draw("clus_id_lpos:clus_id_z>>htemp(41, 0, 1800, 63, -800, 800)", "clus_id_view == 1", "colz")
    c1.Print("clusterplots/cluster_yz.png")
    
    c.Draw("clus_id_lpos:clus_id_z>>htemp(41, 0, 1800, 150, -1800, 1800)", "clus_id_view == 1", "colz")
    c1.Print("clusterplots/cluster_yz_zoomout.png")
    
    c.Draw("(clus_id_tpos1+clus_id_tpos2)/2>>htemp(63, -800, 800)", "clus_id_view == 1", "")
    c1.Print("clusterplots/cluster_x.png")
    
    c.Draw("(clus_id_tpos1+clus_id_tpos2)/2:clus_id_z>>htemp(41, 0, 1800, 63, -800, 800)", "clus_id_view == 1", "colz")
    c1.Print("clusterplots/cluster_xz.png")
    
    #c.Scan("clus_id_module:clus_id_view")
    c.Draw("clus_id_module>>htemp(41, 0, 41)", "clus_id_view == 1")
    c1.Print("clusterplots/cluster_module.png")

    #c1.SetLogx()
    c1.SetLogy()
    c.Draw("clus_id_energy>>htemp(41, 0.1, 12)", "clus_id_module==28 && clus_id_strip == 45")
    c1.Print("clusterplots/cluster_energy_module28strip45.png")
    c.Draw("clus_id_energy>>htemp(41, 0.1, 12)", "clus_id_module==28 && clus_id_strip == 44")
    c1.Print("clusterplots/cluster_energy_module28strip44.png")
    
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
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
