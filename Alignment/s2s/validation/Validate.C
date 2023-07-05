#include "TFile.h"
#include "TH1.h"
#include "TTree.h"
#include "TF1.h"
#include "TCanvas.h"

//==================================================================================================
// Validate.C
// input: playlist.txt, s2s ntuple files
// output: plane-to-plane peak energy plots
//==================================================================================================

//==================================================================================================
// Declare global variables and histograms
//==================================================================================================
const int NENTRIES = 1000;

TFile * fout;
TH1D * fitplot;
TH1D * planeEnergy[120][2];

//==================================================================================================
// Function to implement the fit
//==================================================================================================
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


//==================================================================================================
// Book histograms
//==================================================================================================
void BookHistos()
{
  fout = new TFile("validation.root", "RECREATE");

  fitplot = new TH1D("fitplot", "Fitted Peak Energy/Path;Module;MeV/cm",240,-5,115);
  for( int i = -5; i < 115; i++ ) {
    for( int j = 1; j <= 2; j++ ) {
      int modidx = i+5;
      int plidx = j-1;
      planeEnergy[modidx][plidx] = new TH1D(Form("mod%03d_pl%01d",i,j),Form("Module %d Plane %d Energy;Energy (MeV/cm)",i,j),500,0.0,10.0);
    }
  }
}

//==================================================================================================
// Loop over rock muon tracks and fill histograms
//==================================================================================================
void LoopOverTracks(TTree * nt)
{
  int NN = nt->GetEntries();

  int n_entries, run, subrun;
  int strip[NENTRIES], plane[NENTRIES], module[NENTRIES];
  double lpos[NENTRIES], path[NENTRIES], base[NENTRIES], E[NENTRIES];
  nt->SetBranchAddress("n_entries", &n_entries);
  nt->SetBranchAddress("ev_run", &run);
  nt->SetBranchAddress("ev_subrun", &subrun);
  nt->SetBranchAddress("st_strip", strip);
  nt->SetBranchAddress("st_plane", plane);
  nt->SetBranchAddress("st_module", module);
  nt->SetBranchAddress("st_lpos", lpos);
  nt->SetBranchAddress("st_path", path);
  nt->SetBranchAddress("st_base", base);
  nt->SetBranchAddress("st_mev", E);

  for (int ii = 0; ii < NN; ++ii) {
    nt->GetEntry(ii);
    if( ii == 0 ) printf("Processing %d tracks for %d / %d\n", NN, run, subrun);

    for (int i = 0; i < n_entries; ++i) {

      int modidx = module[i]+5;
      int plidx = plane[i]-1;

      if( path[i] > 2.0 && E[i] != 0.0 ) planeEnergy[modidx][plidx]->Fill( 10.0*E[i]/path[i] );

    } // hits

  } // rock muons

}

void doFitting()
{

  //------------------------------------------------------------------------------------------------
  // Fit each plane and write to text file
  //------------------------------------------------------------------------------------------------

  printf("Fitting...\n");
  for( int m = -5; m <= 114; m++ ) {
    for( int p = 1; p <= 2; p++ ) {

      int modidx = m+5;
      int plidx = p-1;

      if( planeEnergy[modidx][plidx]->GetEntries() < 100000 ) continue;

      int bin = fitplot->FindBin( m + 0.5*(p-1) );

      double pk, dpk, chi2pdof;
      doFit( planeEnergy[modidx][plidx], pk, dpk, chi2pdof );

      fitplot->SetBinContent( bin, pk );
      fitplot->SetBinError( bin, dpk );
    }
  }

}

//==================================================================================================
// Main execution: read ROOT files in from playlist and loop over ntuples
//==================================================================================================
void Validate()
{

  //------------------------------------------------------------------------------------------------
  // Read playlist of ROOT files and loop
  //------------------------------------------------------------------------------------------------
  FILE * fp = fopen("playlist.txt", "r");
  if (fp == 0)
  {
    printf("no playlist.txt found\n");
    exit(0);
  }

  BookHistos();

  while (!feof(fp))
  {
    int run, sub;
    char name[1000];
    fscanf(fp, "%d %d %s\n", &run, &sub, &name);
    if( run == 6137 && sub == 27 ) continue;
    TFile * test_file = new TFile( name, "OLD" );
    if( test_file == NULL ) {
      delete test_file;
      continue;
    }
    TTree * test_tree = (TTree*)test_file->Get( "nt" );
    if( test_tree == NULL ) {
      delete test_tree;
      continue;
    }
    
    LoopOverTracks( test_tree );

    delete test_tree;
    test_file->Close();
    delete test_file;

  }

  doFitting();

  // Print book of outputs
  TCanvas * c = new TCanvas("c","c");
  c->Print("validation.pdf[");
  fitplot->Draw();
  c->Print("validation.pdf");
  for( int m = -5; m <= 114; m++ ) {
    for( int p = 1; p <= 2; p++ ) {
      int modidx = m+5;
      int plidx = p-1;
      if( planeEnergy[modidx][plidx]->GetEntries() < 100000 ) continue;
      planeEnergy[modidx][plidx]->GetFunction("poly5")->SetLineColor(kRed);
      planeEnergy[modidx][plidx]->Draw();
      c->Print("validation.pdf");
    }
  }
  c->Print("validation.pdf]");

  //------------------------------------------------------------------------------------------------
  // Save output to FitCorrection.root
  //------------------------------------------------------------------------------------------------
  fout->cd();
  fitplot->Write();
  for( int m = -5; m <= 114; m++ ) {
    for( int p = 1; p <= 2; p++ ) {
      int modidx = m+5;
      int plidx = p-1;
      planeEnergy[modidx][plidx]->Write();
    }
  }

}

