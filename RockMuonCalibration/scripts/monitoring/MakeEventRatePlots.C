#include <time.h>
#include <string.h>
#include <map>

// ROOT's time uses seconds since 1995 for some reason
const unsigned int seconds_1995 = 788918400 - 6*3600; // 00:00:00 1 January 1995 UTC
const double six_hours = 6. * 3600; // correct to UTC
const double one_day = 24. * 3600;

void MakeEventRatePlots()
{

  // Get current playlist of runs -- quit if no playlist exists
  FILE * playlist = fopen( "playlist_AEM.txt", "r" );
  if( playlist == NULL ) exit(0);

  TChain * gates = new TChain( "gates", "gates" );

  int r0 = 0; int s0 = 0; int r1 = 0; int s1 = 0;
  bool first = true;
  while( !feof(playlist) ) {
    int run, subrun;
    char name[1000];
    fscanf( playlist, "%d %d %s", &run, &subrun, &name );

    if( first ) {
      r0 = run;
      s0 = subrun;
      first = false;
    }
    if( run == r1 && subrun == s1 ) break; // it adds the last one twice for some reason
    r1 = run;
    s1 = subrun;
    TFile * test_file = new TFile( name, "OLD" );
    if( test_file == NULL ) {
      delete test_file;
      continue;
    }
    TTree * test_tree = test_file->Get( "gates" );
    if( test_tree == NULL ) {
      delete test_tree;
      continue;
    }

    gates->Add( name );

    delete test_tree;
    test_file->Close();
    delete test_file;
   
  }
  fclose( playlist );
  printf("Created chain for runs %d/%d - %d/%d\n",r0,s0,r1,s1);

  TFile * fout = new TFile( "AEM_plots.root", "RECREATE" );

  TGraphErrors * rock_muons_per_pot = new TGraphErrors();
  rock_muons_per_pot->SetName( "rock_muons_per_pot" );

  TGraphErrors * minos_tracks_per_pot = new TGraphErrors();
  minos_tracks_per_pot->SetName( "minos_tracks_per_pot" );

  TGraphErrors * minos_matches_per_pot = new TGraphErrors();
  minos_matches_per_pot->SetName( "minos_matches_per_pot" );

  TGraphErrors * slices_per_pot = new TGraphErrors();
  slices_per_pot->SetName( "slices_per_pot" );

  TGraphErrors * protons_per_pulse = new TGraphErrors();
  protons_per_pulse->SetName( "protons_per_pulse" );

  int NG = gates->GetEntries();
  int num, minos_tracks, n_slices, grun, gsub, minerva_rocks, minos_matches, isAnalyzable, has_minos;
  double gpstime, time_btw, pot;
  gates->SetBranchAddress( "gate_gate", &num );
  gates->SetBranchAddress( "gate_run", &grun );
  gates->SetBranchAddress( "gate_subrun", &gsub );
  gates->SetBranchAddress( "gate_nPOT", &pot );
  gates->SetBranchAddress( "gate_gps", &gpstime );
  gates->SetBranchAddress( "gate_nslices", &n_slices );
  gates->SetBranchAddress( "gate_nMinosTracks", &minos_tracks );
  gates->SetBranchAddress( "gate_nRocks", &minerva_rocks );
  gates->SetBranchAddress( "gate_nMatch", &minos_matches );
  gates->SetBranchAddress( "gate_timeToPrev", &time_btw );
  gates->SetBranchAddress( "gate_isAnalyzable", &isAnalyzable );
  gates->SetBranchAddress( "gate_hasMINOS", &has_minos );

  double total_pot = 0;
  double total_good_minos_pot = 0;

  // Fill a point for every day
  gates->GetEntry(0);
  double current_day = floor((gpstime - six_hours)/one_day); // days since epoch
  double bin_start = gpstime;
  double bin_end = gpstime;
  double bin_pot = 0;
  int bin_nslices = 0;
  int bin_nMinosTracks = 0;
  int bin_nRockMuons = 0;
  int bin_nMinosMatches = 0;
  int bin_nPulses = 0;
  for( int ii = 0; ii < NG; ++ii ) {
    gates->GetEntry( ii );
    if( ii % 10000 == 0 ) printf("Processing gate %d of %d...\n", ii, NG );
    total_pot += pot/1.0E13;
    if( has_minos ) total_good_minos_pot += pot/1.0E13;
    double days = (gpstime-six_hours)/one_day;
    if( days - current_day < 1.000 ) { // we are still in the same day as the previous entry
      bin_pot += pot/1.0E13; // convert to e13
      bin_nslices += n_slices;
      bin_nMinosTracks += minos_tracks;
      bin_nRockMuons += minerva_rocks;
      bin_nMinosMatches += minos_matches;
      bin_end = gpstime;
      ++bin_nPulses;
    } else { // today is a new day!
      current_day = floor((gpstime - six_hours)/one_day);
      double bin_error = (bin_end - bin_start) / 2.0;
      double bin_center = bin_start + bin_error - seconds_1995;

      int NBINS = minos_tracks_per_pot->GetN();
      minos_tracks_per_pot->SetPoint( NBINS, bin_center, bin_nMinosTracks/bin_pot );
      minos_tracks_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nMinosTracks)/bin_pot );

      rock_muons_per_pot->SetPoint( NBINS, bin_center, bin_nRockMuons/bin_pot );
      rock_muons_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nRockMuons)/bin_pot );

      minos_matches_per_pot->SetPoint( NBINS, bin_center, bin_nMinosMatches/bin_pot );
      minos_matches_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nMinosMatches)/bin_pot );

      slices_per_pot->SetPoint( NBINS, bin_center, bin_nslices/bin_pot );
      slices_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nslices)/bin_pot );

      protons_per_pulse->SetPoint( NBINS, bin_center, bin_pot*10.0/bin_nPulses );
      protons_per_pulse->SetPointError( NBINS, bin_error, sqrt(bin_nPulses)*bin_pot*10.0/(bin_nPulses*bin_nPulses) );

      // reset
      bin_pot = pot/1.0E13;
      bin_nslices = n_slices;
      bin_nMinosTracks = minos_tracks;
      bin_nRockMuons = minerva_rocks;
      bin_nMinosMatches = minos_matches;
      bin_start = gpstime;
      bin_end = gpstime;
      bin_nPulses = 0;
    }
  }

  double good_minos_percent = 100.0 * total_good_minos_pot / total_pot;

  minos_tracks_per_pot->SetTitle( Form("MINOS gate match for %3.2f%% of total POT;Month-Day;MINOS tracks / 10^{13} POT", good_minos_percent) );
  minos_matches_per_pot->SetTitle( Form("MINOS gate match for %3.2f%% of total POT;Month-Day;MINOS-matched rock muon tracks / 10^{13} POT", good_minos_percent) );
  rock_muons_per_pot->SetTitle( ";Month-Day;Rock muons / 10^{13} POT" );
  slices_per_pot->SetTitle( ";Month-Day;Time slices / 10^{13} POT" );
  protons_per_pulse->SetTitle( ";Month-Day;Protons per pulse (10^{12})" );

  minos_tracks_per_pot->GetXaxis()->SetTimeDisplay(1);
  minos_tracks_per_pot->GetXaxis()->SetTimeFormat("%m-%d");
  minos_tracks_per_pot->GetXaxis()->SetTimeOffset(0, "local");
  minos_matches_per_pot->GetXaxis()->SetTimeDisplay(1);
  minos_matches_per_pot->GetXaxis()->SetTimeFormat("%m-%d");
  minos_matches_per_pot->GetXaxis()->SetTimeOffset(0, "local");
  rock_muons_per_pot->GetXaxis()->SetTimeDisplay(1);
  rock_muons_per_pot->GetXaxis()->SetTimeFormat("%m-%d");
  rock_muons_per_pot->GetXaxis()->SetTimeOffset(0, "local");
  slices_per_pot->GetXaxis()->SetTimeDisplay(1);
  slices_per_pot->GetXaxis()->SetTimeFormat("%m-%d");
  slices_per_pot->GetXaxis()->SetTimeOffset(0, "local");
  protons_per_pulse->GetXaxis()->SetTimeDisplay(1);
  protons_per_pulse->GetXaxis()->SetTimeFormat("%m-%d");
  protons_per_pulse->GetXaxis()->SetTimeOffset(0, "local");

  // Write the file
  fout->cd();
  rock_muons_per_pot->Write();
  minos_matches_per_pot->Write();
  minos_tracks_per_pot->Write();
  slices_per_pot->Write();
  protons_per_pulse->Write();

  // Print pngs of all the plots
  TCanvas * c1 = new TCanvas("c2","c2", 800, 400);
  minos_tracks_per_pot->SetMarkerSize(0.5);
  minos_tracks_per_pot->Draw("APZ");
  c1->Print("aemPlots/tmp/minos_tracks_per_pot.png");
  slices_per_pot->SetMarkerSize(0.5);
  slices_per_pot->Draw("APZ");
  c1->Print("aemPlots/tmp/time_slices_per_pot.png");
  rock_muons_per_pot->SetMarkerSize(0.5);
  rock_muons_per_pot->Draw("APZ");
  c1->Print("aemPlots/tmp/rock_muons_per_pot.png");
  minos_matches_per_pot->SetMarkerSize(0.5);
  minos_matches_per_pot->Draw("APZ");
  c1->Print("aemPlots/tmp/minos_matches_per_pot.png");
  protons_per_pulse->SetMarkerSize(0.5);
  protons_per_pulse->Draw("APZ");
  c1->Print("aemPlots/tmp/protons_per_pulse.png");
  delete c1;
}

