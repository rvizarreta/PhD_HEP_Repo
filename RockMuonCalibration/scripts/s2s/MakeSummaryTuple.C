//==================================================================================================
// MakeSummaryTuple.C
// input: ReadNT.root, plex.root
// output: summary.root
// Takes summary histograms from ReadNT.C and creates an ntuple where each entry is one channel
// Assigns all error flags
//==================================================================================================

void MakeSummaryTuple()
{

  TFile * fplex = new TFile("plex.root", "OLD");
  TTree * plex = (TTree *) fplex->Get("plex");

  TFile * freadnt = new TFile("ReadNT.root", "OLD");
  TH2 * h_TM_energy_channel = (TH2D *) freadnt->Get("TM_energy_channel");
  TProfile2D * p_energy_channel_all = (TProfile2D *) freadnt->Get("p_energy_channel_all");
  TH2 * h_zero_fraction = (TH2D *) freadnt->Get("h_zero_fraction");
  TProfile2D * p_shifts = (TProfile2D *) freadnt->Get("shifts");

  TFile * fsummary = new TFile("summary.root", "RECREATE");

  fsummary->cd(); TTree * nts = new TTree("nts", "nts");

  int id, strip, plane, module, subdet, view, points_up;
  int link, crate, chain, croc, board, conn, pixel;
  double L, tpos, z;

  double dedx_errorTot, dedx_meanTrunc, dedx_meanTot, dedx_rmsTot;
  int dedx_nTot;
  double rms, shift, zeroFrac;
  int good, badshift, dead, badrms, badzero;
  int n_tracks;

  plex->SetBranchAddress("id", &id);
  plex->SetBranchAddress("strip", &strip);
  plex->SetBranchAddress("plane", &plane);
  plex->SetBranchAddress("module", &module);
  plex->SetBranchAddress("subdet", &subdet);
  plex->SetBranchAddress("view", &view);
  plex->SetBranchAddress("points_up", &points_up);
  plex->SetBranchAddress("link", &link);
  plex->SetBranchAddress("crate", &crate);
  plex->SetBranchAddress("chain", &chain);
  plex->SetBranchAddress("croc", &croc);
  plex->SetBranchAddress("board", &board);
  plex->SetBranchAddress("conn", &conn);
  plex->SetBranchAddress("pixel", &pixel);
  plex->SetBranchAddress("L", &L);
  plex->SetBranchAddress("tpos", &tpos);
  plex->SetBranchAddress("z", &z);
  
  nts->Branch("id", &id, "id/I");
  nts->Branch("strip", &strip, "strip/I");
  nts->Branch("plane", &plane, "plane/I");
  nts->Branch("module", &module, "module/I");
  nts->Branch("subdet", &subdet, "subdet/I");
  nts->Branch("view", &view, "view/I");
  nts->Branch("points_up", &points_up, "points_up/I");
  nts->Branch("link", &link, "link/I");
  nts->Branch("crate", &crate, "crate/I");
  nts->Branch("chain", &chain, "chain/I");
  nts->Branch("croc", &croc, "croc/I");
  nts->Branch("board", &board, "board/I");
  nts->Branch("conn", &conn, "conn/I");
  nts->Branch("pixel", &pixel, "pixel/I");
  nts->Branch("L", &L, "L/D");
  nts->Branch("tpos", &tpos, "tpos/D");
  nts->Branch("z", &z, "z/D");

  nts->Branch("dedx.meanTrunc", &dedx_meanTrunc, "dedx.meanTrunc/D");
  nts->Branch("dedx.errorTot", &dedx_errorTot, "dedx.errorTot/D");
  nts->Branch("dedx.meanTot", &dedx_meanTot, "dedx.meanTot/D");
  nts->Branch("dedx.rmsTot", &dedx_rmsTot, "dedx.rmsTot/D");
  nts->Branch("dedx.nTot", &dedx_nTot, "dedx.nTot/I");

  nts->Branch("shift", &shift, "shift/D");
  nts->Branch("rms", &rms, "rms/D");
  nts->Branch("zero_fraction", &zeroFrac, "zero_fraction/D");
  
  nts->Branch("good", &good, "good/I");
  nts->Branch("badshift", &badshift, "badshift/I");
  nts->Branch("dead", &dead, "dead/I");
  nts->Branch("badrms", &badrms, "badrms/I");
  nts->Branch("badzero", &badzero, "badzero/I");

  int ROWS = plex->GetEntries();
  printf("Creating summary tuple for %d strips\n", ROWS);
  for (int i = 0; i < ROWS; ++i) {
    if (i % 5000 == 0) printf("%d of %d\n", i, ROWS); 
    plex->GetEntry(i);

    int bin = p_energy_channel_all->FindBin(module+0.5*(plane-1), strip);
    dedx_errorTot = p_energy_channel_all->GetBinError(bin);
    dedx_nTot = p_energy_channel_all->GetBinEntries(bin);
    dedx_meanTrunc = h_TM_energy_channel->GetBinContent(bin);

    dedx_rmsTot = dedx_errorTot * sqrt(dedx_nTot);
    dedx_meanTot = p_energy_channel_all->GetBinContent(bin);

    zeroFrac = h_zero_fraction->GetBinContent(bin);

    shift = p_shifts->GetBinContent(bin);

    //----------------------------------------------------------------------------------------------
    // Define selection cuts for error channels
    //----------------------------------------------------------------------------------------------

    dead = false;
    if( dedx_nTot == 0 && dedx_meanTrunc == 0.0 ) dead = true;

    badshift = false;
    if( abs(shift) > 5 && strip != 1 && strip != 127 ) badshift = true;

    badrms = false;
    if( dedx_meanTot > 0 )
    {
      if( dedx_rmsTot/dedx_meanTrunc > 6.0 ) badrms = true;
      rms = dedx_rmsTot/dedx_meanTrunc;
    } else {
      rms = 0.0;
    }
    

    badzero = false;
    if( zeroFrac > 0.4 ) badzero = true;
    
    good = true;
    if (dead) good = false;
    if (badshift) good = false;
    if (badrms) good = false;
    if (badzero) good = false;

    nts->Fill();
  }

  printf("Write...\n");
  fsummary->cd();
  nts->Write();
}
