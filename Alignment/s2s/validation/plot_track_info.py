
import sys
import os
import ROOT
ROOT.gROOT.SetBatch(True)

plotclusters = True

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
    
    try: os.mkdir("energy_plots")
    except OSError: pass # already exists
    try: os.mkdir("energy_plots/trackinfo")
    except OSError: pass # already exists
    
    c.Show(0)
    avgAmount = 1;
    for i in range(0, 42):
        if i % avgAmount != 0: continue
        #c.Draw("cl_pe>>htemp(40,0,40)", "cl_module==%s" % i)
        #c.Draw("cl_pe>>htemp(40,0,40)", "cl_module<%s+%s&&cl_module>=%s" % (i, 10, i)) # Draws 10 modules combined
        #if plotclusters: c.Draw("clus_id_pe>>htemp(40,0,4)", "clus_id_module<%s+%s&&clus_id_module>=%s" % (i, avgAmount, i)) # Draws 10 modules combined
        #else: c.Draw("hit_pe>>htemp(40,0,4)", "hit_module<%s+%s&&hit_module>=%s" % (i, avgAmount, i)) # Draws 10 modules combined
        #c1.Print("energy_plots/trackinfo/module{0:02d}.png".format(i))
        
    c.Draw("trk_node_Z>>htemp(100, 0, 1800)", "", "")
    c1.Print("energy_plots/trackinfo/z.png")
        
    c.Draw("trk_node_Y>>htemp(100, -1000, 1000)", "", "")
    c1.Print("energy_plots/trackinfo/y.png")
        
    c.Draw("trk_node_X>>htemp(100, -1000, 1000)", "", "")
    c1.Print("energy_plots/trackinfo/x.png")
        
    c.Draw("trk_node_Y>>htemp(100, -1000, 1000)", "trk_node_Z<400", "")
    c1.Print("energy_plots/trackinfo/tracker_y.png")
        
    c.Draw("trk_node_X>>htemp(100, -1000, 1000)", "trk_node_Z<400", "")
    c1.Print("energy_plots/trackinfo/tracker_x.png")
        
    c.Draw("trk_hits>>htemp(25, 0, 75)", "", "")
    c1.Print("energy_plots/trackinfo/trk_hits.png")
    c.Draw("trk_hits>>htemp(25, 0, 75)", "trk_node_Z<400", "")
    c1.Print("energy_plots/trackinfo/trk_hits_tracker.png")
    
    c.Draw("trk_node_chi2>>htemp(40, 0, 20)", "", "")
    c1.Print("energy_plots/trackinfo/trk_node_chi2.png")
    c.Draw("trk_node_chi2>>htemp(40, 0, 20)", "trk_node_Z<400", "")
    c1.Print("energy_plots/trackinfo/trk_node_chi2_tracker.png")
    
    c.Draw("trk_chi2perDof>>htemp(20, 0, 5)", "", "")
    c1.Print("energy_plots/trackinfo/trk_chi2perDof.png")
    c.Draw("trk_chi2perDof>>htemp(20, 0, 5)", "trk_node_Z<400", "")
    c1.Print("energy_plots/trackinfo/trk_chi2perDof_tracker.png")
    
    c.Draw("trk_nodes>>htemp(20, 0, 20)", "", "")
    c1.Print("energy_plots/trackinfo/trk_nodes.png")
    c.Draw("trk_nodes>>htemp(20, 0, 20)", "Min$(trk_node_Z)<400", "")
    c1.Print("energy_plots/trackinfo/trk_nodes_tracker.png")
    c.Draw("trk_nodes>>htemp(20, 0, 20)", "Min$(trk_node_Z)>400", "")
    c1.Print("energy_plots/trackinfo/trk_nodes_hcal.png")
    
    h = ROOT.TH1D("h", "h", 50, 0, 500)
    for event in c:
        if event.n_tracks != 1: continue # skip 0, 2+
        for i in range(event.trk_nodes[0]-1):
            dz = event.trk_node_Z[i+1] - event.trk_node_Z[i]
            #print event.trk_node_Z[i+1], event.trk_node_Z[i], dz
            h.Fill(dz)
    h.Draw()
    #c.Draw("trk_node_Z[Iteration$+1]-trk_node_Z[Iteration$]>>htemp(50, 0, 500)", "Iteration$+1<trk_nodes", "")
    c1.Print("energy_plots/trackinfo/dz.png")
    
    h = ROOT.TH1D("h", "h", 50, 0, 500)
    for event in c:
        if event.n_tracks != 1: continue # skip 0, 2+
        for i in range(event.trk_nodes[0]-1):
            if event.trk_node_Z[i] > 400: continue
            dz = event.trk_node_Z[i+1] - event.trk_node_Z[i]
            #print event.trk_node_Z[i+1], event.trk_node_Z[i], dz
            if dz > 500: print event.trk_node_Z[i+1], event.trk_node_Z[i], dz 
            #if dz < 10: print event.trk_node_Z[i+1], event.trk_node_Z[i], dz 
            h.Fill(dz)
    h.Draw()
    #c.Draw("trk_node_Z[Iteration$+1]-trk_node_Z[Iteration$]>>htemp(50, 0, 500)", "Iteration$+1<trk_nodes", "")
    c1.Print("energy_plots/trackinfo/dz_tracker.png")
    
    
    c.Draw("trk_node_X:trk_node_Z>>htemp(100, 0000, 2000, 100, -1000, 1000)", "", "colz")
    c1.Print("energy_plots/trackinfo/2d.png")
    
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
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
