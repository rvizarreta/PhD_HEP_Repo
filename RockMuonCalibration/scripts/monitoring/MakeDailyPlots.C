#include <time.h>
#include <string.h>

// Fill an entry every this number of gates
const int NGATES = 500;
const unsigned int seconds_mnv1 = 1269311633;
const unsigned int seconds_1995 = 788918400; // 00:00:00 1 January 1995 UTC
//const double six_hours = 6. * 3600; // correct to UTC
const double one_day = 24. * 3600;
const unsigned int muon_high_energy_cut = 50; //GeV

// doFit fits the cluster pe or mev histogram
void doFit( TH1D * hist, double &pk, double &dpk, double &chi2pdof )
{

  TF1 * poly2 = new TF1("poly2","[0] + [2]*pow(x-[1],2)");

  double maxY = hist->GetBinContent( hist->GetMaximumBin() );
  double maxX = hist->GetBinCenter( hist->GetMaximumBin() );
  poly2->SetParameter( 0, maxY );
  poly2->SetParameter( 1, maxX );

  int low_bin = hist->FindFirstBinAbove( maxY/2.0 );
  int high_bin = hist->FindLastBinAbove( maxY/2.0 );
  double fit_low = hist->GetBinCenter( low_bin - 1 );
  double fit_high = hist->GetBinCenter( high_bin + 1 );

  poly2->SetParLimits( 1, fit_low, fit_high );
  hist->Fit("poly2","Q","Q",fit_low,fit_high);

  TF1 * poly5 = new TF1("poly5","[0] + [2]*pow(x-[1],2) + [3]*pow(x-[1],3) + [4]*pow(x-[1],4) + [5]*pow(x-[1],5)");

  poly5->SetParameter( 1, poly2->GetParameter(1) );
  poly5->SetParLimits( 1, fit_low, fit_high );
  poly5->SetParameter( 2, poly2->GetParameter(2) );
  poly5->SetParLimits( 2, 10*(poly2->GetParameter(2)), 0 );
  hist->Fit("poly5","Q","Q",fit_low,fit_high);

  double chi2 = poly5->GetChisquare();
  int ndf = poly5->GetNDF();

  chi2pdof = chi2/ndf;

  pk = poly5->GetParameter(1);
  dpk = poly5->GetParError(1);

}



void MakeDailyPlots()
{

  gStyle->SetNumberContours(999);
  Double_t stops[7] = { 0.00, 0.05, 0.23, 0.45, 0.60, 0.85, 1.00 };
  Double_t red[7]   = { 1.00, 0.00, 0.00, 0.00, 1.00, 1.00, 0.33 };
  Double_t green[7] = { 1.00, 1.00, 0.30, 0.40, 1.00, 0.00, 0.00 };
  Double_t blue[7]  = { 1.00, 1.00, 1.00, 0.00, 0.00, 0.00, 0.00 };
  TColor::CreateGradientColorTable(7, stops, red, green, blue, 999);

  // Get current playlist of runs -- quit if no playlist exists
  FILE * playlist = fopen( "playlist_daily.txt", "r" );
  if( playlist == NULL ) exit(0);

  // TChains for main ntuple and header
  TChain * nt = new TChain( "nt", "nt" );
  TChain * header = new TChain( "header", "header" );
  TChain * gates = new TChain( "gates", "gates" );

  FILE * bad_data = fopen("bad_data_list.txt", "w");

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
      fprintf( bad_data, "%d %d\n", run, subrun );
      delete test_file;
      continue;
    }
    TTree * test_tree = test_file->Get( "nt" );
    if( test_tree == NULL ) {
      fprintf( bad_data, "%d %d\n", run, subrun );
      delete test_tree;
      continue;
    }

    nt->Add( name );
    header->Add( name );
    gates->Add( name );

    //delete test_file;
    //delete test_tree;
   
  }
  fclose( playlist );
  printf("Created chain for runs %d/%d - %d/%d\n",r0,s0,r1,s1);
  fclose( bad_data );

  // Output file for plots -- file name gives run range
  TFile * fout = new TFile( Form("dump/today/daily_plots_r%04d_s%02d_to_r%04d_s%02d.root",r0,s0,r1,s1), "RECREATE" );

  // not to be confused with the track deltaT (which is in nanoseconds), the gate match deltaT
  TH1D * minos_gate_deltaT = new TH1D( "minos_gate_deltaT", ";MINERvA - MINOS gate #DeltaT (seconds)", 300, -1.5, 1.5 );

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

  TH1D * time_btw_gates = new TH1D( "time_btw_gates", ";Time between gates (s)", 100, 0.0, 10.0 );
  TH2D * plot_of_death = new TH2D( "plot_of_death", "Fraction of 10 #mus spill when channel is dead;Module number;Strip number", 240, -5.0, 115.0, 127, 0.5, 127.5 );
  TProfile * dead_profile = new TProfile( "dead_profile", ";Beam intensity (10^{12} ppp);Average dead time fraction", 25, 0.0, 50.0 );

  // Only count POT when MINOS is live
  TGraphErrors * good_minos_tracks_per_pot = new TGraphErrors();
  good_minos_tracks_per_pot->SetName( "good_minos_tracks_per_pot" );

  TGraphErrors * good_minos_matches_per_pot = new TGraphErrors();
  good_minos_matches_per_pot->SetName( "good_minos_matches_per_pot" );

  int NG = gates->GetEntries();
  int num, minos_tracks, rock_muons, minos_matches, n_slices, has_minos, n_strips;
  double gpstime, time_btw, pot, gate_deltaT, death;
  gates->SetBranchAddress( "gate_gate", &num );
  gates->SetBranchAddress( "gate_nPOT", &pot );
  gates->SetBranchAddress( "gate_gps", &gpstime );
  gates->SetBranchAddress( "gate_nslices", &n_slices );
  gates->SetBranchAddress( "gate_nMinosTracks", &minos_tracks );
  gates->SetBranchAddress( "gate_nRocks", &rock_muons );
  gates->SetBranchAddress( "gate_nMatch", &minos_matches );
  gates->SetBranchAddress( "gate_timeToPrev", &time_btw );
  gates->SetBranchAddress( "gate_hasMINOS", &has_minos );
  gates->SetBranchAddress( "gate_minosGateDeltaT", &gate_deltaT );
  gates->SetBranchAddress( "gate_deadTimeFrac", &death );

  // For time bounds
  long int overall_start = 9999999999.9;
  long int overall_end = 0.0;

  double total_pot = 0;
  double total_good_minos_pot = 0;

  // Fill a point for every NGATES gates, n_gates keeps count
  int n_gates = 0;
  double bin_start = 0; // start seconds for the current bin
  double bin_pot = 0;
  double bin_good_pot = 0;
  int bin_nslices = 0;
  int bin_nMinosTracks = 0;
  int bin_nRocks = 0;
  int bin_nMatch = 0;
  for( int ii = 0; ii < NG; ++ii ) {
    if( ii % 10000 == 0 ) printf( "Processing gate %d of %d...\n", ii, NG );
    gates->GetEntry( ii );

    if( gpstime > overall_end ) overall_end = (long int)gpstime;
    if( gpstime < overall_start ) overall_start = (long int)gpstime;

    if( has_minos ) minos_gate_deltaT->Fill( gate_deltaT );

    if( pot / 1.0E12 < 1.0 ) continue; // throw out A9 with no beam
    dead_profile->Fill( pot / 1.0E12, death );

    if( num != 1 ) time_btw_gates->Fill( time_btw ); // skip first gate because it doesn't know about previous time
    if( n_gates == 1 ) bin_start = gpstime;

    if( has_minos ) {
      bin_good_pot += pot / 1.0E13;
      total_good_minos_pot += pot / 1.0E13;
    }
    total_pot += pot / 1.0E13;
    bin_pot += pot / 1.0E13; // convert to e13
    bin_nslices += n_slices;
    bin_nMinosTracks += minos_tracks;
    bin_nRocks += rock_muons;
    bin_nMatch += minos_matches;

    if( n_gates == NGATES ) { // we've reached the end of this bin
      double bin_end = gpstime;
      double bin_error = (bin_end - bin_start) / 2.0;
      double bin_center = bin_start + bin_error - seconds_1995;

      // 10e13 is a few gates worth of POT at normal intensity, but if there are target scans or something then don't fill point
      if( bin_pot > 10.0 ) {
        int NBINS = minos_tracks_per_pot->GetN();
        minos_tracks_per_pot->SetPoint( NBINS, bin_center, bin_nMinosTracks/bin_pot );
        minos_tracks_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nMinosTracks)/bin_pot );

        rock_muons_per_pot->SetPoint( NBINS, bin_center, bin_nRocks/bin_pot );
        rock_muons_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nRocks)/bin_pot );

        minos_matches_per_pot->SetPoint( NBINS, bin_center, bin_nMatch/bin_pot );
        minos_matches_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nMatch)/bin_pot );

        slices_per_pot->SetPoint( NBINS, bin_center, bin_nslices/bin_pot );
        slices_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nslices)/bin_pot );

        protons_per_pulse->SetPoint( NBINS, bin_center, bin_pot / NGATES );
        protons_per_pulse->SetPointError( NBINS, bin_error, sqrt( bin_pot ) / NGATES );
      }
      if( bin_good_pot > 10.0 ) {
        int NBINS = good_minos_tracks_per_pot->GetN();
        good_minos_tracks_per_pot->SetPoint( NBINS, bin_center, bin_nMinosTracks/bin_good_pot );
        good_minos_tracks_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nMinosTracks)/bin_good_pot );

        good_minos_matches_per_pot->SetPoint( NBINS, bin_center, bin_nMatch/bin_good_pot );
        good_minos_matches_per_pot->SetPointError( NBINS, bin_error, sqrt(bin_nMatch)/bin_good_pot );
      }

      // reset
      n_gates = 0;
      bin_pot = 0.0;
      bin_good_pot = 0.0;
      bin_nslices = 0;
      bin_nMinosTracks = 0;
      bin_nRocks = 0;
      bin_nMatch = 0;
    }

    ++n_gates;
  }

  // plot of death from the header tree
  int module[30000], plane[30000], strip[30000], n_strips;
  double deadFrac[30000], total_POT;
  header->SetBranchAddress( "n_strips", &n_strips );
  header->SetBranchAddress( "total_POT", &total_POT );
  header->SetBranchAddress( "module", module );
  header->SetBranchAddress( "plane", plane );
  header->SetBranchAddress( "strip", strip );
  header->SetBranchAddress( "fractionOfDeath", deadFrac );
  int NH = header->GetEntries();
  double totaltotal_POT = 0.0;
  for( int h = 0; h < NH; ++h ) {
    header->GetEntry(h);
    for( int st = 0; st < n_strips; ++st ) plot_of_death->Fill( module[st]+0.5*(plane[st]-1), strip[st], deadFrac[st]*total_POT );
    totaltotal_POT += total_POT;
  }
  plot_of_death->Scale( 1.0 / totaltotal_POT );

  double minos_live_percent = 100.0 * total_good_minos_pot / total_pot;

  // Death to time zones, death to daylight savings time
  TTimeStamp s( overall_start, 0 ); // s, ns
  unsigned int sdate = s.GetDate( false ); // yyyymmdd
  unsigned int stime = s.GetTime( false ); // hhmmss
  int ys = sdate/10000;
  int ms = (sdate%10000)/100;
  int ds = sdate%100;
  int hs = stime/10000;
  int Ms = (stime%10000)/100;
  int ss = stime%100;

  TTimeStamp e( overall_end, 0 );
  unsigned int edate = e.GetDate( false ); // yyyymmdd
  unsigned int etime = e.GetTime( false ); // hhmmss
  int ye = edate/10000;
  int me = (edate%10000)/100;
  int de = edate%100;
  int he = etime/10000;
  int Me = (etime%10000)/100;
  int se = etime%100;

  minos_tracks_per_pot->SetTitle( Form("Start: %04d-%02d-%02d %02d:%02d:%02d End: %04d-%02d-%02d %02d:%02d:%02d;Hour (Central time);MINOS tracks / 10^{13} POT",ys,ms,ds,hs,Ms,ss,ye,me,de,he,Me,se) );
  rock_muons_per_pot->SetTitle( Form("Start: %04d-%02d-%02d %02d:%02d:%02d End: %04d-%02d-%02d %02d:%02d:%02d;Hour (Central time);Rock muon tracks / 10^{13} POT",ys,ms,ds,hs,Ms,ss,ye,me,de,he,Me,se) );
  minos_matches_per_pot->SetTitle( Form("Start: %04d-%02d-%02d %02d:%02d:%02d End: %04d-%02d-%02d %02d:%02d:%02d;Hour (Central time);MINOS-matched rock muons / 10^{13} POT",ys,ms,ds,hs,Ms,ss,ye,me,de,he,Me,se) );
  slices_per_pot->SetTitle( Form("Start: %04d-%02d-%02d %02d:%02d:%02d End: %04d-%02d-%02d %02d:%02d:%02d;Hour (Central time);Time slices / 10^{13} POT",ys,ms,ds,hs,Ms,ss,ye,me,de,he,Me,se) );
  protons_per_pulse->SetTitle( Form("Start: %04d-%02d-%02d %02d:%02d:%02d End: %04d-%02d-%02d %02d:%02d:%02d;Hour (Central time);Protons per pulse / 10^{13}",ys,ms,ds,hs,Ms,ss,ye,me,de,he,Me,se) );
  if( good_minos_tracks_per_pot->GetN() ) {
    good_minos_tracks_per_pot->SetTitle( Form("Start: %04d-%02d-%02d %02d:%02d:%02d End: %04d-%02d-%02d %02d:%02d:%02d;Hour (Central time);MINOS tracks / 10^{13} POT",ys,ms,ds,hs,Ms,ss,ye,me,de,he,Me,se) );
    good_minos_matches_per_pot->SetTitle( Form("Start: %04d-%02d-%02d %02d:%02d:%02d End: %04d-%02d-%02d %02d:%02d:%02d;Hour (Central time);MINOS-matched rock muons / 10^{13} POT",ys,ms,ds,hs,Ms,ss,ye,me,de,he,Me,se) );
  }

  minos_tracks_per_pot->GetXaxis()->SetTimeDisplay(1);
  minos_tracks_per_pot->GetXaxis()->SetTimeFormat("%H");
  minos_tracks_per_pot->GetXaxis()->SetTimeOffset(0, "local");
  rock_muons_per_pot->GetXaxis()->SetTimeDisplay(1);
  rock_muons_per_pot->GetXaxis()->SetTimeFormat("%H");
  rock_muons_per_pot->GetXaxis()->SetTimeOffset(0, "local");
  minos_matches_per_pot->GetXaxis()->SetTimeDisplay(1);
  minos_matches_per_pot->GetXaxis()->SetTimeFormat("%H");
  minos_matches_per_pot->GetXaxis()->SetTimeOffset(0, "local");
  slices_per_pot->GetXaxis()->SetTimeDisplay(1);
  slices_per_pot->GetXaxis()->SetTimeFormat("%H");
  slices_per_pot->GetXaxis()->SetTimeOffset(0, "local");
  protons_per_pulse->GetXaxis()->SetTimeDisplay(1);
  protons_per_pulse->GetXaxis()->SetTimeFormat("%H");
  protons_per_pulse->GetXaxis()->SetTimeOffset(0, "local");

  if( good_minos_tracks_per_pot->GetN() ) {
    good_minos_tracks_per_pot->GetXaxis()->SetTimeDisplay(1);
    good_minos_tracks_per_pot->GetXaxis()->SetTimeFormat("%H");
    good_minos_tracks_per_pot->GetXaxis()->SetTimeOffset(0, "local");
    good_minos_matches_per_pot->GetXaxis()->SetTimeDisplay(1);
    good_minos_matches_per_pot->GetXaxis()->SetTimeFormat("%H");
    good_minos_matches_per_pot->GetXaxis()->SetTimeOffset(0, "local");
  }

  // Declare histograms
  TH1D * minos_deltaT = new TH1D( "minos_deltaT", ";MINOS - MINERvA #DeltaT (ns)", 100, -200.0, 200.0 );
  TH1D * minos_RvC = new TH1D( "minos_RvC", ";#frac{1}{p_{range}} - #frac{1}{p_{curv}} (MeV^{-1}c)", 100, -0.0004, 0.0004 );
  TH1D * minos_RvC_byrange = new TH1D( "minos_RvC_bycurve", ";#frac{1}{p_{range}} - #frac{1}{p_{curv}} (MeV^{-1}c)", 100, -0.0004, 0.0004 );
  TH1D * minos_RvC_bycurve = new TH1D( "minos_RvC_byrange", ";#frac{1}{p_{range}} - #frac{1}{p_{curv}} (MeV^{-1}c)", 100, -0.0004, 0.0004 );
  TH1D * cluster_pe = new TH1D( "cluster_pe", ";Muon cluster PE;Fraction per 0.5 PE", 100.0, 0.0, 50.0 );
  TH1D * cluster_mev = new TH1D( "cluster_mev", ";Muon cluster energy (MeV);Fraction per 0.1 MeV", 100.0, 0.0, 10.0 );
  TH1D * minos_muon_energy = new TH1D("minos_muon_energy","Minos muon energy (GeV)" , 100, 0, muon_high_energy_cut);
  TH1D * minos_muonp_energy = new TH1D("minos_muonp_energy","Minos muon energy (GeV)" , 100, 0, muon_high_energy_cut);
  TH1D * minos_muonm_energy = new TH1D("minos_muonm_energy","Minos muon energy (GeV)" , 100, 0, muon_high_energy_cut);
  
  
  int N = nt->GetEntries();
  int n_clusters, ev_ntracks, ev_minosMatch, ev_minosRecoByRange;
  double ev_minosPrange, ev_minosPcurve, ev_minosP, ev_minosMatchDeltaT, ev_extraEnergy, ev_muonE,ev_muonCharge;
  double cl_pe[240], cl_recoE[240];

  nt->SetBranchAddress( "n_clusters", &n_clusters );
  nt->SetBranchAddress( "ev_minosMatch", &ev_minosMatch );
  nt->SetBranchAddress( "ev_ntracks", &ev_ntracks );
  nt->SetBranchAddress( "ev_minosPcurve", &ev_minosPcurve );
  nt->SetBranchAddress( "ev_minosPrange", &ev_minosPrange );
  nt->SetBranchAddress( "ev_minosRecoByRange", &ev_minosRecoByRange );
  nt->SetBranchAddress( "ev_minosP", &ev_minosP );
  nt->SetBranchAddress( "ev_minosMatchDeltaT", &ev_minosMatchDeltaT );
  nt->SetBranchAddress( "ev_extraEnergy", &ev_extraEnergy );
  nt->SetBranchAddress( "cl_pe", cl_pe );
  nt->SetBranchAddress( "cl_recoE", cl_recoE );
  nt->SetBranchAddress( "ev_muonE", &ev_muonE);
  nt->SetBranchAddress( "ev_muonCharge",&ev_muonCharge);

  nt->SetBranchStatus( "*", 0 );
  nt->SetBranchStatus( "n_clusters", 1 );
  nt->SetBranchStatus( "ev_minosMatch", 1 );
  nt->SetBranchStatus( "ev_ntracks", 1 );
  nt->SetBranchStatus( "ev_minosPcurve", 1 );
  nt->SetBranchStatus( "ev_minosPrange", 1 );
  nt->SetBranchStatus( "ev_minosRecoByRange", 1 );
  nt->SetBranchStatus( "ev_minosP", 1 );
  nt->SetBranchStatus( "ev_minosMatchDeltaT", 1 );
  nt->SetBranchStatus( "ev_extraEnergy", 1 );
  nt->SetBranchStatus( "cl_pe", 1 );
  nt->SetBranchStatus( "cl_recoE", 1 );
  nt->SetBranchStatus( "ev_muonE", 1);
  nt->SetBranchStatus( "ev_muonCharge", 1);

  for( int ii = 0; ii < N; ++ii ) {
    if( ii % 10000 == 0 ) printf( "Processing event %d of %d...\n", ii, N );
    nt->GetEntry(ii);

    // MEU-style plots require MINOS match
    if( ev_minosMatch == 0 || ev_ntracks > 1 ) continue;

    if (ev_muonE<muon_high_energy_cut*1000) {
      minos_muon_energy->Fill(ev_muonE/1000);// Convert to GeV
      if (ev_muonCharge >0 ) {
	minos_muonp_energy->Fill(ev_muonE/1000);
      } else {
	minos_muonm_energy->Fill(ev_muonE/1000);
      }
    }
    
    minos_deltaT->Fill( ev_minosMatchDeltaT );
    if( ev_minosPcurve > 0.0 && ev_minosPrange > 0.0 ) {
      minos_RvC->Fill( 1.0/ev_minosPrange - 1.0/ev_minosPcurve );
      if( ev_minosRecoByRange ) minos_RvC_byrange->Fill( 1.0/ev_minosPrange - 1.0/ev_minosPcurve );
      else minos_RvC_bycurve->Fill( 1.0/ev_minosPrange - 1.0/ev_minosPcurve );
    }

    if( ev_extraEnergy > 100.0 ) continue;
    for( int i = 0; i < n_clusters; ++i ) {
      cluster_pe->Fill( cl_pe[i] );
      cluster_mev->Fill( cl_recoE[i] );
    } // clusters

  } // rock muon tracks

  // These require MINOS match -- no MINOS means no plots
  double pe_pk = -1; double pe_dpk = -1; double pe_chi2 = -1;
  double mev_pk = -1; double mev_dpk = -1; double mev_chi2 = -1;

  if( cluster_pe->GetEntries() > 1000 ) {

    // set both bins and errors correctly
    double peNorm = 1.0 / cluster_pe->Integral();
    double mevNorm = 1.0 / cluster_mev->Integral();
    for( int b = 1; b <= cluster_pe->GetNbinsX(); ++b ) {
      double content = cluster_pe->GetBinContent(b);
      cluster_pe->SetBinContent( b, content * peNorm );
      cluster_pe->SetBinError( b, sqrt(content) * peNorm );
    }
    for( int b = 1; b <= cluster_mev->GetNbinsX(); ++b ) {
      double content = cluster_mev->GetBinContent(b);
      cluster_mev->SetBinContent( b, content * mevNorm );
      cluster_mev->SetBinError( b, sqrt(content) * mevNorm );
    }

    doFit( cluster_pe, pe_pk, pe_dpk, pe_chi2 );

    doFit( cluster_mev, mev_pk, mev_dpk, mev_chi2 );
  }

  // color the by range and by curvature red and blue
  minos_RvC_byrange->SetLineColor( kRed );
  minos_RvC_bycurve->SetLineColor( kBlue );
  minos_muon_energy->SetLineColor( kBlack );
  minos_muonp_energy->SetLineColor( kRed );
  minos_muonm_energy->SetLineColor( kBlue );
  

  // Write the file for just this data
  fout->cd();
  minos_deltaT->Write();
  minos_RvC->Write();
  minos_RvC_byrange->Write();
  minos_RvC_bycurve->Write();
  cluster_pe->Write();
  cluster_mev->Write();
  rock_muons_per_pot->Write();
  minos_tracks_per_pot->Write();
  minos_matches_per_pot->Write();
  good_minos_tracks_per_pot->Write();
  good_minos_matches_per_pot->Write();
  slices_per_pot->Write();
  protons_per_pulse->Write();
  minos_gate_deltaT->Write();
  plot_of_death->Write();
  dead_profile->Write();
  minos_muon_energy->Write();
  minos_muonp_energy->Write();
  minos_muonm_energy->Write();

  // For some reason if I don't print the TPaveText by itself on a canvas first, it won't
  // show up on the plots later
  TCanvas * asdf = new TCanvas("asdf","asdf");
  TPaveText * tpt = new TPaveText( 0.2, 0.86, 0.8, 0.92 );
  tpt->AddText( Form("MINOS gate match for %3.2f%% of total POT",minos_live_percent) );
  tpt->SetBorderSize( 0.0 );
  tpt->Draw();
  asdf->Print("dump/today/MINOSLIVETIME.png");
  delete asdf;

  FILE * mlive = fopen( "dump/today/minos_live_percent.txt", "w" );
  fprintf( mlive, "%04d %02d %02d\n", ys, ms, ds );
  fprintf( mlive, "%3.2f\n", minos_live_percent );
  fclose( mlive );

  TCanvas * c1 = new TCanvas("c2","c2");
  c1->SetGridx(1);

  rock_muons_per_pot->SetMarkerSize(0.5);
  rock_muons_per_pot->Draw("APZ");
  c1->Print("dump/today/rock_muons_per_pot.png");
  minos_tracks_per_pot->SetMarkerSize(0.5);
  minos_tracks_per_pot->Draw("APZ");
  c1->Print("dump/today/minos_tracks_per_pot.png");
  minos_matches_per_pot->SetMarkerSize(0.5);
  minos_matches_per_pot->Draw("APZ");
  c1->Print("dump/today/minos_matches_per_pot.png");
  slices_per_pot->SetMarkerSize(0.5);
  slices_per_pot->Draw("APZ");
  c1->Print("dump/today/time_slices_per_pot.png");
  protons_per_pulse->SetMarkerSize(0.5);
  protons_per_pulse->Draw("APZ");
  c1->Print("dump/today/protons_per_pulse.png");
  if( good_minos_tracks_per_pot->GetN() ) {
    good_minos_tracks_per_pot->SetMarkerSize(0.5);
    good_minos_tracks_per_pot->Draw("APZ");
    tpt->Draw();
    c1->Print("dump/today/good_minos_tracks_per_pot.png");
    good_minos_matches_per_pot->SetMarkerSize(0.5);
    good_minos_matches_per_pot->Draw("APZ");
    tpt->Draw();
    c1->Print("dump/today/good_minos_matches_per_pot.png");
  }

  // Get summary peak pe plot and add new points
  TFile * fsum = new TFile( "dump/summary_plots.root", "OLD" );

  TGraphErrors * sumpe = (TGraphErrors*) fsum->Get("peak_cluster_pe");
  TGraphErrors * summev = (TGraphErrors*) fsum->Get("peak_cluster_mev");
  TGraphErrors * sumDT = (TGraphErrors*) fsum->Get("minos_deltaT_summary");
  TGraphErrors * sumPrc = (TGraphErrors*) fsum->Get("minos_RvC_summary");

  TGraphErrors * sum_rocks = (TGraphErrors*) fsum->Get("rock_muons_summary");
  TGraphErrors * sum_match = (TGraphErrors*) fsum->Get("minos_matches_summary");
  TGraphErrors * sum_minos = (TGraphErrors*) fsum->Get("minos_tracks_summary");
  TGraphErrors * sum_slices = (TGraphErrors*) fsum->Get("time_slices_summary");
  TGraphErrors * sum_protons = (TGraphErrors*) fsum->Get("protons_summary");
  TGraphErrors * sum_match_good = (TGraphErrors*) fsum->Get("good_minos_matches_summary");
  TGraphErrors * sum_minos_good = (TGraphErrors*) fsum->Get("good_minos_tracks_summary");

  double error = (overall_end - overall_start)/2.0;
  double bin_center = overall_start + error - seconds_1995;

  int n = sumpe->GetN();
  if( pe_pk > 0 ) {
    sumpe->SetPoint( n, bin_center, pe_pk ); // starts with ME monitoring
    sumpe->SetPointError( n, error, pe_dpk );
  } else {
    sumpe->SetPoint( n, bin_center, 0.0 );
    sumpe->SetPointError( n, error, 0.0 );
  }

  if( mev_pk > 0 ) {
    summev->SetPoint( n, bin_center, mev_pk );
    summev->SetPointError( n, error, mev_dpk );
  } else {
    summev->SetPoint( n, bin_center, 0.0 );
    summev->SetPointError( n, error, 0.0 );
  }

  sumDT->SetPoint( n, bin_center, minos_deltaT->GetMean() );
  sumDT->SetPointError( n, error, minos_deltaT->GetRMS() ); // really it's sigma

  sumPrc->SetPoint( n, bin_center, minos_RvC->GetMean() );
  sumPrc->SetPointError( n, error, minos_RvC->GetRMS() );

  rock_muons_per_pot->Fit( "pol0", "Q", "Q" );
  sum_rocks->SetPoint( n, bin_center, rock_muons_per_pot->GetFunction("pol0")->GetParameter(0) );
  sum_rocks->SetPointError( n, error, rock_muons_per_pot->GetFunction("pol0")->GetParError(0) );

  if( good_minos_tracks_per_pot->GetN() ) {
    minos_matches_per_pot->Fit( "pol0", "Q", "Q" );
    sum_match->SetPoint( n, bin_center, minos_matches_per_pot->GetFunction("pol0")->GetParameter(0) );
    sum_match->SetPointError( n, error, minos_matches_per_pot->GetFunction("pol0")->GetParError(0) );

    minos_tracks_per_pot->Fit( "pol0", "Q", "Q" );
    sum_minos->SetPoint( n, bin_center, minos_tracks_per_pot->GetFunction("pol0")->GetParameter(0) );
    sum_minos->SetPointError( n, error, minos_tracks_per_pot->GetFunction("pol0")->GetParError(0) );
  } else {
    sum_match->SetPoint( n, bin_center, 0.0 );
    sum_match->SetPointError( n, error, 0.0 );
    sum_minos->SetPoint( n, bin_center, 0.0 );
    sum_minos->SetPointError( n, error, 0.0 );
  }

  slices_per_pot->Fit( "pol0", "Q", "Q" );
  n = sum_slices->GetN();
  sum_slices->SetPoint( n, bin_center, slices_per_pot->GetFunction("pol0")->GetParameter(0) );
  sum_slices->SetPointError( n, error, slices_per_pot->GetFunction("pol0")->GetParError(0) );

  protons_per_pulse->Fit( "pol0", "Q", "Q" );
  n = sum_protons->GetN();
  sum_protons->SetPoint( n, bin_center, protons_per_pulse->GetFunction("pol0")->GetParameter(0) );
  sum_protons->SetPointError( n, error, protons_per_pulse->GetFunction("pol0")->GetParError(0) );

  if( good_minos_tracks_per_pot->GetN() ) {
    good_minos_matches_per_pot->Fit( "pol0", "Q", "Q" );
    sum_match_good->SetPoint( n, bin_center, good_minos_matches_per_pot->GetFunction("pol0")->GetParameter(0) );
    sum_match_good->SetPointError( n, error, good_minos_matches_per_pot->GetFunction("pol0")->GetParError(0) );

    good_minos_tracks_per_pot->Fit( "pol0", "Q", "Q" );
    sum_minos_good->SetPoint( n, bin_center, good_minos_tracks_per_pot->GetFunction("pol0")->GetParameter(0) );
    sum_minos_good->SetPointError( n, error, good_minos_tracks_per_pot->GetFunction("pol0")->GetParError(0) );
  } else {
    sum_match_good->SetPoint( n, bin_center, 0.0 );
    sum_match_good->SetPointError( n, error, 0.0 );
    sum_minos_good->SetPoint( n, bin_center, 0.0 );
    sum_minos_good->SetPointError( n, error, 0.0 );
  }

  sumpe->GetXaxis()->SetTimeDisplay(1);
  sumpe->GetXaxis()->SetTimeFormat( "%m-%d" );
  sumpe->GetXaxis()->SetTimeOffset( 0, "local" );
  summev->GetXaxis()->SetTimeDisplay(1);
  summev->GetXaxis()->SetTimeFormat( "%m-%d" );
  summev->GetXaxis()->SetTimeOffset( 0, "local" );
  sumDT->GetXaxis()->SetTimeDisplay(1);
  sumDT->GetXaxis()->SetTimeFormat( "%m-%d" );
  sumDT->GetXaxis()->SetTimeOffset( 0, "local" );
  sumPrc->GetXaxis()->SetTimeDisplay(1);
  sumPrc->GetXaxis()->SetTimeFormat( "%m-%d" );
  sumPrc->GetXaxis()->SetTimeOffset( 0, "local" );
  sum_rocks->GetXaxis()->SetTimeDisplay(1);
  sum_rocks->GetXaxis()->SetTimeFormat( "%m-%d" );
  sum_rocks->GetXaxis()->SetTimeOffset( 0, "local" );
  sum_match->GetXaxis()->SetTimeDisplay(1);
  sum_match->GetXaxis()->SetTimeFormat( "%m-%d" );
  sum_match->GetXaxis()->SetTimeOffset( 0, "local" );
  sum_minos->GetXaxis()->SetTimeDisplay(1);
  sum_minos->GetXaxis()->SetTimeFormat( "%m-%d" );
  sum_minos->GetXaxis()->SetTimeOffset( 0, "local" );
  sum_slices->GetXaxis()->SetTimeDisplay(1);
  sum_slices->GetXaxis()->SetTimeFormat( "%m-%d" );
  sum_slices->GetXaxis()->SetTimeOffset( 0, "local" );
  sum_protons->GetXaxis()->SetTimeDisplay(1);
  sum_protons->GetXaxis()->SetTimeFormat( "%m-%d" );
  sum_protons->GetXaxis()->SetTimeOffset( 0, "local" );

  sum_match_good->GetXaxis()->SetTimeDisplay(1);
  sum_match_good->GetXaxis()->SetTimeFormat( "%m-%d" );
  sum_match_good->GetXaxis()->SetTimeOffset( 0, "local" );
  sum_minos_good->GetXaxis()->SetTimeDisplay(1);
  sum_minos_good->GetXaxis()->SetTimeFormat( "%m-%d" );
  sum_minos_good->GetXaxis()->SetTimeOffset( 0, "local" );
  
  // Print pngs of all the plots
  sumpe->SetMarkerSize(0.5);
  sumpe->Draw("APZ");  
  c1->Print("dump/today/cluster_pe_vs_time.png");
  sum_rocks->SetMarkerSize(0.5);
  sum_rocks->Draw("APZ");
  c1->Print("dump/today/rock_muons_per_pot_summary.png");
  if( good_minos_tracks_per_pot->GetN() ) {
    sum_minos->SetMarkerSize(0.5);
    sum_minos->Draw("APZ");
    c1->Print("dump/today/minos_tracks_per_pot_summary.png");
    sum_match->SetMarkerSize(0.5);
    sum_match->Draw("APZ");
    c1->Print("dump/today/minos_matches_per_pot_summary.png");
  }
  sum_slices->SetMarkerSize(0.5);
  sum_slices->Draw("APZ");
  c1->Print("dump/today/time_slices_per_pot_summary.png");
  if( good_minos_tracks_per_pot->GetN() ) {
    sum_minos_good->SetMarkerSize(0.5);
    sum_minos_good->Draw("APZ");
    c1->Print("dump/today/good_minos_tracks_per_pot_summary.png");
    sum_match_good->SetMarkerSize(0.5);
    sum_match_good->Draw("APZ");
    c1->Print("dump/today/good_minos_matches_per_pot_summary.png");
  }  
  sum_protons->SetMarkerSize(0.5);
  sum_protons->Draw("APZ");
  c1->Print("dump/today/protons_per_pulse_summary.png");

  // turn off grid
  c1->SetGridx(0);
  if( cluster_pe->GetEntries() > 1000 ) {
    cluster_pe->SetMarkerSize(0.5);
    cluster_pe->GetFunction("poly5")->SetLineColor(kRed);
    cluster_pe->Draw();
    c1->Print("dump/today/minerva_cluster_pe.png");
    cluster_mev->SetMarkerSize(0.5);
    cluster_mev->GetFunction("poly5")->SetLineColor(kRed);
    cluster_mev->Draw();
    c1->Print("dump/today/minerva_cluster_energy.png");
  }
  minos_RvC->Draw();
  minos_RvC_byrange->Draw("same");
  minos_RvC_bycurve->Draw("same");
  TLegend * rvcleg = new TLegend( 0.155, 0.6, 0.45, 0.845 );
  rvcleg->AddEntry( minos_RvC, "All tracks", "l" );
  rvcleg->AddEntry( minos_RvC_byrange, "By range", "l" );
  rvcleg->AddEntry( minos_RvC_bycurve, "By curvature", "l" );
  rvcleg->Draw();
  c1->Print("dump/today/minos_prange_vs_pcurvature.png");
  plot_of_death->Draw("COLZ");
  c1->Print("dump/today/fraction_dead_time.png");
  dead_profile->Draw();
  c1->Print("dump/today/dead_vs_intensity.png");
  c1->SetLogy();
  time_btw_gates->Draw();
  c1->Print("dump/today/time_between_gates.png");
  minos_deltaT->Draw();
  c1->Print("dump/today/minos_deltaT.png");
  minos_gate_deltaT->SetMinimum(0.5); // make sure you can see a bin with 1 event
  minos_gate_deltaT->Draw();
  c1->Print("dump/today/minos_gate_deltaT.png");
  
  c1->SetLogy(0);
  minos_muon_energy->Draw();
  minos_muonp_energy->Draw("same");
  minos_muonm_energy->Draw("same");
  
  TLegend *eleg = new TLegend( 0.6, 0.7, 0.75, 0.85 );
  eleg->AddEntry( minos_muon_energy, "All muon", "l");
  eleg->AddEntry( minos_muonp_energy, "Mu+", "l");
  eleg->AddEntry( minos_muonm_energy, "Mu-", "l");
  eleg->Draw();
  c1->Print("dump/today/minos_rockmuon_E.png");

  delete c1;

  // overwrite old file with new one containing new data point
  TFile * fnew = new TFile( "dump/summary_plots.root", "RECREATE" );
  fnew->cd();
  sumpe->Write();
  summev->Write();
  sumDT->Write();
  sumPrc->Write();
  sum_rocks->Write();
  sum_match->Write();
  sum_minos->Write();
  sum_slices->Write();
  sum_protons->Write();
  sum_match_good->Write();
  sum_minos_good->Write();
  fnew->Close();

}

