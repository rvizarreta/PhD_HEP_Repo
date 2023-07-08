#include <TFile.h>
#include <TH1.h>
#include <TProfile.h>
#include <TTree.h>
#include <TCanvas.h>
#include <TPaveLabel.h>
#include <map>
#include <math.h>
#include <fstream>
#include <sstream>
#include <string>
#include "S2SUtils.cxx"

// ---
// --- global variables
// ---

const int NENTRIES = 1000;
const int MAXERRORS = 1000;

TFile * fout;
int nerrors = 0;
std::map<int,int> errorMap;
int error_module[MAXERRORS];
int error_plane[MAXERRORS];
int error_strip[MAXERRORS];
int error_error[MAXERRORS];
float error_dedx[MAXERRORS];
float error_zero[MAXERRORS];
float error_shift[MAXERRORS];
float error_rms[MAXERRORS];
TH1 * h_error_shift[MAXERRORS];
TH1 * h_error_energy[MAXERRORS];
TProfile * p_error_energyperpath_run[MAXERRORS];

// ---
// --- Booking
// --- 

void BookHistos( int min_run, int max_run )
{
  fout = new TFile("ErrorPlots.root", "RECREATE");
  
  std::ifstream ifs("error_strips.txt");

  nerrors = 0;
  if( ifs.is_open() ){

    std::string s;
    while( getline(ifs,s) ){
      if(s[0]=='#') continue;

      int module, plane, strip, error;
      float dedx, rms, shift, zero;

      std::istringstream sin(s);
      sin >> module >> plane >> strip >> error >> dedx >> rms >> shift >> zero;

      error_module[nerrors] = module;
      error_plane[nerrors] = plane;
      error_strip[nerrors] = strip;
      error_error[nerrors] = error;
      error_dedx[nerrors] = dedx;
      error_zero[nerrors] = zero;
      error_rms[nerrors] = rms;
      error_shift[nerrors] = shift;
      int hash = 10000*module + 1000*plane + strip;
      errorMap[hash] = nerrors; // index to this error strip

      h_error_shift[nerrors] = new TH1D( Form("shift_%03d_%d_%03d",module,plane,strip), ";base (mm);MeV-weighted entries", 17, -17, 17 );
      if( dedx > 0 ) h_error_energy[nerrors] = new TH1D( Form("energy_%03d_%d_%03d",module,plane,strip), ";Energy/path (MeV/cm)", 100, 0.0, dedx*(1+2*rms) );
      else h_error_energy[nerrors] = new TH1D( Form("energy_%03d_%d_%03d",module,plane,strip), ";Energy/path (MeV/cm)", 100, 0.0, 1.0 );
      p_error_energyperpath_run[nerrors] = new TProfile( Form("vsrun_%03d_%d_%03d",module,plane,strip), ";run number;Average energy/path (MeV/cm)", max_run-min_run+1, min_run, max_run+1);

      ++nerrors;
    }
  }      
}


// ---
// --- Filling
// ---

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

  SetBranches( nt );

  for (int ii = 0; ii < NN; ++ii) {
    nt->GetEntry(ii);
    if( ii == 0 ) printf("Processing %d tracks for %d / %d \n", NN, run, subrun);
    for( int i = 0; i < n_entries; ++i ) {
      double path_cm = 0.1 * path[i];
      if( path_cm < 0.2 ) continue;

      int hash = 10000*module[i] + 1000*plane[i] + strip[i];
      if( errorMap.find(hash) == errorMap.end() ) continue;
          
      // Fill error strip plots without truncation
      int j = errorMap[hash];
      double Cs = (17-fabs(base[i]))/path[i]; // correction factor for normal incidence
      h_error_shift[j]->Fill(base[i], E[i]*Cs);
      if( E[i] != 0.0 ) {
        h_error_energy[j]->Fill(E[i]/*/path_cm*/);
        p_error_energyperpath_run[j]->Fill(run, E[i]/*/path_cm*/);
      }

    } // loop over hits
  } // loop over rock muons

}

// ---
// --- Main
// ---

void MakeErrorPlots()
{

  int min_run, max_run;

  std::vector<std::string> fnames;
  GetFilenames( fnames, min_run, max_run );
  BookHistos(min_run, max_run);

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
  
  // ---
  // --- save output ---
  // ---
  fout->cd();
  for (int j = 0; j < nerrors; ++j)
  {
    h_error_shift[j]->Write();
    h_error_energy[j]->Write();
    p_error_energyperpath_run[j]->Write();
  }

  // ---
  // --- graphics output ---
  // ---
  
  TCanvas * c1 = new TCanvas("c1", "c1", 640, 480);
  c1->Divide(2, 2);
  c1->Print("ErrorPlotsBook.pdf[");
  for (int j = 0; j < nerrors; ++j) {
    char string[200];
    char errorstring[200];
    char info[200];
    sprintf(string, "Module %d Plane %d Strip %d", error_module[j], error_plane[j], error_strip[j]);
    TPaveLabel pl(0, 0.5, 1, 1, string);
    int err = error_error[j];

    std::string zero = "";
    std::string dead = "";
    std::string shift = "";
    std::string low = "";
    std::string rms = "";
    std::string example = "";
    if ( (err/10000)%2 ) dead = "Dead";
    if ( (err/1000)%2 ) shift = "Shift";
    if ( (err/100)%2 ) rms = "RMS";
    if ( (err/10)%2 ) zero = "Zero";
    if ( (err/1)%2 ) low = "LowE";
    if ( err == 0 ) example = "Example";

    sprintf(errorstring, "%s %s %s %s %s %s", dead.c_str(), shift.c_str(), rms.c_str(), zero.c_str(), low.c_str(), example.c_str());
    sprintf(info, "dEdX = %3.2f RMS = %3.2f Shift = %3.2f Zero = %2.0f%%", error_dedx[j], error_rms[j], error_shift[j], error_zero[j]);

    TPaveLabel pl2(0, 0.25, 1, 0.5, errorstring);
    TPaveLabel pl3(0, 0, 1, 0.25, info);
    c1->cd(1); pl.Draw(); pl2.Draw(); pl3.Draw();
    c1->cd(3); h_error_shift[j]->Draw();
    c1->cd(2); h_error_energy[j]->Draw();
    c1->cd(4); p_error_energyperpath_run[j]->Draw();
    c1->Print("ErrorPlotsBook.pdf");
  }
  c1->Print("ErrorPlotsBook.pdf]");
}

int main()
{
  MakeErrorPlots();
  return 0;
}

