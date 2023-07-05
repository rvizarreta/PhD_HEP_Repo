#include <TFile.h>
#include <TH1.h>
#include <TTree.h>
#include <TF1.h>
#include <math.h>
#include "S2SUtils.cxx"

//==================================================================================================
// DoFitCorrection.C
// input: playlist.txt, s2s ntuple files
// output: fit_corrections.txt, and FitCorrection.root just for viewing
// Determines ratio of fitted peak to truncated mean in each plane, outputs a text file of these
// corrections to be applied to the final s2s constants
//==================================================================================================

//==================================================================================================
// Declare global variables and histograms
//==================================================================================================
const int NENTRIES = 1000;

TFile * fout;
TH1D * fitplot;
TH1D * tmplot;
TH1D * chi2plot;
TH1D * ratio;
TH1D * planeEnergy[120][2];

double ratios[120][2] = {{0.0}};

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
  fout = new TFile("FitCorrection.root", "RECREATE");

  fitplot = new TH1D("fitplot", "Fitted Peak Energy/Path;Module;pseudo-MeV/cm",240,-5,115);
  tmplot = new TH1D("tmplot", "Truncated Mean Energy/Path;Module;pseudo-MeV/cm",240,-5,115);
  ratio = new TH1D("ratio", "Fit / Truncated Mean;Module",240,-5,115);
  chi2plot = new TH1D("chi2plot", "Chi2 per DoF;Module",240,-5,115);
  for( int i = -5; i < 115; i++ ) {
    for( int j = 1; j <= 2; j++ ) {
      int modidx = i+5;
      int plidx = j-1;
      planeEnergy[modidx][plidx] = new TH1D(Form("mod%03d_pl%01d",i,j),Form("Module %d Plane %d Energy;Energy (pseudo-MeV/cm)",i,j),10000,0.0,10.0);
    }
  }
}

//==================================================================================================
// Loop over rock muon tracks and fill histograms
//==================================================================================================
void LoopOverTracks(TTree * nt)
{
  const int NN = nt->GetEntries();

  int n_entries, run, subrun, ev_ntracks, gate;
  double ev_extraEnergy;
  int strip[NENTRIES], plane[NENTRIES], module[NENTRIES];
  double lpos[NENTRIES], path[NENTRIES], base[NENTRIES], E[NENTRIES];
  nt->SetBranchAddress("n_entries", &n_entries);
  nt->SetBranchAddress("ev_run", &run);
  nt->SetBranchAddress("ev_subrun", &subrun);
  nt->SetBranchAddress("ev_gate", &gate);
  nt->SetBranchAddress("ev_ntracks", &ev_ntracks);
  nt->SetBranchAddress("ev_extraEnergy", &ev_extraEnergy);
  nt->SetBranchAddress("st_strip", strip);
  nt->SetBranchAddress("st_plane", plane);
  nt->SetBranchAddress("st_module", module);
  nt->SetBranchAddress("st_lpos", lpos);
  nt->SetBranchAddress("st_path", path);
  nt->SetBranchAddress("st_base", base);
  nt->SetBranchAddress("st_mev", E);

  SetBranches( nt );

  for (int ii = 0; ii < NN; ++ii) {
    nt->GetEntry(ii);
    if( ii == 0 ) printf("Processing %d tracks for %d / %d\n", NN, run, subrun);

    if( ev_ntracks > 1 || ev_extraEnergy > 100.0 ) continue;

    for (int i = 0; i < n_entries; ++i) {

      int modidx = module[i]+5;
      int plidx = plane[i]-1;

      if( path[i] > 2.0 && E[i] != 0.0 ) planeEnergy[modidx][plidx]->Fill( 10.0*E[i]/path[i] );

    } // hits

  } // rock muons

}

void generateCorrections()
{

  //------------------------------------------------------------------------------------------------
  // Fit each plane and write to text file
  //------------------------------------------------------------------------------------------------

  double TM[120][2] = {{0.0}};
  printf("Determining truncated mean\n");
  for( int it = 0; it < 8; it++ ) {
    for( int mod = 0; mod < 120; mod++ ) {
      for( int pl = 0; pl < 2; pl++ ) {
        double upper = 1.5 * TM[mod][pl];
        double lower = 0.5 * TM[mod][pl];
        if( it == 0 ) upper = 10.0;
        if( planeEnergy[mod][pl]->GetEntries() > 0 ) {
          planeEnergy[mod][pl]->GetXaxis()->SetRangeUser(lower,upper); // refine range
          TM[mod][pl] = planeEnergy[mod][pl]->GetMean(); // new mean for next iteration
        } else TM[mod][pl] = 0.0; // kills this channel forever and ever
      } // plane
    } // module
  } // iteration
  for( int m = -5; m <= 114; m++ ) {
    for( int p = 1; p <= 2; p++ ) {

      int modidx = m+5;
      int plidx = p-1;

      int bin = tmplot->FindBin( m + 0.5*(p-1) );

      if( planeEnergy[modidx][plidx]->GetEntries() == 0 ) continue;

      double tm = planeEnergy[modidx][plidx]->GetMean();
      double sig = planeEnergy[modidx][plidx]->GetRMS();
      int nent = planeEnergy[modidx][plidx]->GetEntries();

      double dtm = sqrt(tm*tm + sig*sig)/nent;

      tmplot->SetBinContent( bin, tm );
      tmplot->SetBinError( bin, dtm );

    }
  }

  printf("Fitting...\n");
  for( int m = -5; m <= 114; m++ ) {
    for( int p = 1; p <= 2; p++ ) {

      int modidx = m+5;
      int plidx = p-1;

      if( planeEnergy[modidx][plidx]->GetEntries() < 100000 ) continue;

      int bin = fitplot->FindBin( m + 0.5*(p-1) );

      planeEnergy[modidx][plidx]->Rebin( 20 );

      double pk, dpk, chi2pdof;
      doFit( planeEnergy[modidx][plidx], pk, dpk, chi2pdof );

      chi2plot->Fill( bin, chi2pdof );

      fitplot->SetBinContent( bin, pk );
      fitplot->SetBinError( bin, dpk );

      double tm = tmplot->GetBinContent( bin );
      double dtm = tmplot->GetBinError( bin );

      double rat = pk/tm;
      double drat = sqrt( pow(dpk/tm,2)+pow(pk*dtm/(tm*tm),2) );

      ratio->SetBinContent( bin, rat );
      ratio->SetBinError( bin, drat ); 

      ratios[modidx][plidx] = rat;

    }
  }

}

//==================================================================================================
// Main execution: read ROOT files in from playlist and loop over ntuples
//==================================================================================================
void DoFitCorrection()
{

  //------------------------------------------------------------------------------------------------
  // Read playlist of ROOT files and loop
  //------------------------------------------------------------------------------------------------

  BookHistos();

  std::vector<std::string> fnames;
  int min_run, max_run;
  GetFilenames( fnames, min_run, max_run );

  for( unsigned int i = 0; i < fnames.size(); ++i ) {

    // See if the TFile is OK for the file name
    TFile * test_file = new TFile( fnames[i].c_str(), "OLD" );
    if( test_file == NULL ) {
      delete test_file;
      continue;
    }

    // See if the nt tree is OK
    TTree * tree = (TTree*)test_file->Get( "nt" );
    if( tree == NULL ) continue;

    LoopOverTracks( tree );

    test_file->Close();
    delete test_file;
  }

  generateCorrections();

  FILE * fcorr = fopen("fit_corrections.txt", "w");
  fprintf( fcorr, "# module plane correction\n" );

  double center = 0.0;
  int nplanes = 0;
  for( int m = 0; m < 120; m++ ) {
    for( int p = 0; p < 2; p++ ) {
      if( ratios[m][p] == 0.0 ) continue; // not a real plane
      center += (1.0/ratios[m][p]);
      nplanes++;
    }
  }
  center /= nplanes; // center is now the average of 1/ratio

  for( int m = 0; m < 120; m++ ) {
    for( int p = 0; p < 2; p++ ) {
      if( ratios[m][p] == 0.0 ) continue; // not a real plane
      int module = m - 5;
      int plane = p + 1;
      double corr = (1.0/ratios[m][p])/center;
      fprintf( fcorr, "%d %d %f\n", module, plane, corr );
    }
  }

  fclose( fcorr );

  //------------------------------------------------------------------------------------------------
  // Save output to FitCorrection.root
  //------------------------------------------------------------------------------------------------
  fout->cd();
  fitplot->Write();
  tmplot->Write();
  ratio->Write();
  chi2plot->Write();
  for( int m = -5; m <= 114; m++ ) {
    for( int p = 1; p <= 2; p++ ) {
      int modidx = m+5;
      int plidx = p-1;
      planeEnergy[modidx][plidx]->Write();
    }
  }

}

int main()
{
  DoFitCorrection();
  return 0;
}


