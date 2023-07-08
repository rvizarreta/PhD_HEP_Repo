#include <time.h>
#include <string.h>
#include <vector>
#include <iostream>
#include "TFile.h"
#include "TChain.h"
#include "TH1D.h"
#include "TGraphErrors.h"
#include "TTimeStamp.h"
#include "TCanvas.h"
#include "TPaveText.h"
#include "TProfile.h"
#include "TH2D.h"
#include "TColor.h"
#include "TStyle.h"
#include "TLegend.h"
#include "TF1.h"
#include "TMultiGraph.h"

using namespace std;

//Abstract classes
class GraphProcessor {
  
public:
  virtual void createGraph()=0;
  virtual void fillGraph()=0;
  virtual void printGraph(TCanvas * c1)=0;
  virtual void writeRoot( TFile* fout )=0;
  virtual void cleanup()=0;
};

class BranchDB {
public:
  BranchDB(const char * name){
    chain = new TChain(name,name);
    i = 0;
  }

  void addFileToChain(const char * filename) {
    chain->Add(filename);
  }

  virtual void initChainStatus() {
    chain->SetBranchStatus("*",0);
  }

  bool update() {
    if (i<chain->GetEntries()) {
      chain->GetEntry(i);
      i++;
      if (i%10000 ==0) {
	std::cout<< "Processing "<<i << " of " << chain->GetEntries() << " Entries.\n"; 
      }
      return true;
    } else {
      return false;
    }
  }

  const unsigned int getI() {
    return i;
  }

  void cleanup() {
    delete chain;
    chain = NULL;
  } 
  
protected:
  void setBranch(const char * branch, int* pointer) {
    chain->SetBranchStatus(branch, 1);
    chain->SetBranchAddress(branch, pointer);
  }

  void setBranch(const char * branch, double * pointer) {
    chain->SetBranchStatus(branch, 1);
    chain->SetBranchAddress(branch, pointer);
  }
private:
  TChain * chain;
  unsigned int i;
};

class TreeProcessor {
public:
  virtual void createGraphies() =0;
  virtual void loopOverTree() =0;
  
  virtual void addFileToChain(char * name) {
    DB->addFileToChain(name);
  }
  
  virtual void printGraphies() {
    TCanvas * c1 = new TCanvas("c1","c1");
    for (int i=0; i < graphies.size(); i++) {
      graphies[i]->printGraph(c1);
    }
    delete c1;
  }

  virtual void writeRootFile(TFile * fout) {
    for (int i=0; i < graphies.size(); i++) {
      graphies[i]->writeRoot(fout);
    }
  }

  virtual void cleanup() {
    while(!graphies.empty()) graphies.back()->cleanup(), delete graphies.back(), graphies.pop_back();
    DB->cleanup();
  }
  
protected:
  vector<GraphProcessor*> graphies;
  BranchDB * DB;
};

// Classes that provide Interface of root entries.
class GateTreeDB : public BranchDB {
public:
  GateTreeDB():BranchDB("gates"){}

  void initChainStatus() {
    BranchDB::initChainStatus();
    setBranch("gate_gate",&num);
    setBranch("gate_nPOT",&pot);
    setBranch("gate_gps",&gpstime);
    setBranch("gate_nslices",&n_slices);
    setBranch("gate_nRocks",&rock_muons);
    setBranch("gate_timeToPrev",&time_btw);
    setBranch("gate_minosGateDeltaT",&gate_deltaT);
    setBranch("gate_hasMINOS",&has_minos);
    setBranch("gate_nMinosTracks",&minos_tracks);
    setBranch("gate_nMatch", &minos_matches );
    setBranch("gate_deadTimeFrac",&death);
    setBranch("gate_mup_E",mu_plus);
    setBranch("gate_mum_E",mu_minus);
  }
  
  int num,rock_muons, n_slices,has_minos, minos_tracks, minos_matches,mu_plus[3],mu_minus[3];
  double gpstime, time_btw, pot, gate_deltaT, death;
};

class HeaderTreeDB: public BranchDB {
public:
  HeaderTreeDB():BranchDB("header"){}

  void initChainStatus() {
    BranchDB::initChainStatus();
    setBranch( "n_strips", &n_strips );
    setBranch( "total_POT", &total_POT );
    setBranch( "module", module );
    setBranch( "plane", plane );
    setBranch( "strip", strip );
    setBranch( "fractionOfDeath", deadFrac );
  }

  int module[30000], plane[30000], strip[30000], n_strips;
  double deadFrac[30000], total_POT;
};

class NTTreeDB : public BranchDB {
public:
  NTTreeDB():BranchDB("nt"){}

  void initChainStatus(){
    BranchDB::initChainStatus();
    setBranch( "n_clusters", &n_clusters );
    setBranch( "ev_minosMatch", &ev_minosMatch );
    setBranch( "ev_ntracks", &ev_ntracks );
    setBranch( "ev_minosPcurve", &ev_minosPcurve );
    setBranch( "ev_minosPrange", &ev_minosPrange );
    setBranch( "ev_minosRecoByRange", &ev_minosRecoByRange );
    setBranch( "ev_minosP", &ev_minosP );
    setBranch( "ev_minosMatchDeltaT", &ev_minosMatchDeltaT );
    setBranch( "ev_extraEnergy", &ev_extraEnergy );
    setBranch( "cl_pe", cl_pe );
    setBranch( "cl_recoE", cl_recoE );
    setBranch( "ev_muonE", &ev_muonE);
    setBranch( "ev_muonCharge",&ev_muonCharge);
  }

  int n_clusters, ev_ntracks, ev_minosMatch, ev_minosRecoByRange;
  double ev_minosPrange, ev_minosPcurve, ev_minosP, ev_minosMatchDeltaT, ev_extraEnergy, ev_muonE,ev_muonCharge;
  double cl_pe[240], cl_recoE[240];
};

// Classes that provide fit & print tools
class Printer {
public:
  const static void timeDependPrint(TGraphErrors * graph, TCanvas * c1) {
    c1->Clear();
    c1->SetGridx(1);
    graph->GetXaxis()->SetTimeDisplay(1);
    graph->GetXaxis()->SetTimeFormat("%H");
    graph->GetXaxis()->SetTimeOffset(0, "local");
    c1->SetLogy(0);
    graph->SetMarkerSize(0.5);
    graph->Draw("APZ");
    Printer::Print(c1,graph->GetName());
  }

  const static void multiGraphPrint(TMultiGraph * graph, TCanvas * c1, TLegend * lgd) {
    c1->Clear();
    c1->SetGridx(1);
    c1->SetLogy(0);
    graph->Draw("APZ");
    lgd->Draw();
    graph->GetXaxis()->SetTimeDisplay(1);
    graph->GetXaxis()->SetTimeFormat("%H");
    graph->GetXaxis()->SetTimeOffset(0, "local");
    Printer::Print(c1,graph->GetName());
  }
  
  const static void HistPrint(TH1D * graph, TCanvas * c1, int log = 0) {
    c1->Clear();
    c1->SetGridx(0);
    c1->SetLogy(log);
    graph->Draw();
    Printer::Print(c1,graph->GetName());  
  }

  const static void sumPrint(TGraphErrors * graph, TCanvas * c1) {
    c1->Clear();
    c1->SetGridx(1);
    graph->GetXaxis()->SetTimeDisplay(1);
    graph->GetXaxis()->SetTimeFormat( "%m-%d" );
    graph->GetXaxis()->SetTimeOffset( 0, "local" );
    graph->SetMarkerSize(0.5);
    graph->Draw("APZ");
    Printer::Print(c1,graph->GetName());
  }

  const static void GoodPrint(TGraphErrors * graph, TCanvas * c1, TPaveText * tpt) {
    c1->Clear();
    c1->SetGridx(1);
    graph->GetXaxis()->SetTimeDisplay(1);
    graph->GetXaxis()->SetTimeFormat("%H");
    graph->GetXaxis()->SetTimeOffset(0, "local");
    c1->SetLogy(0);
    graph->SetMarkerSize(0.5);
    graph->Draw("APZ");
    tpt->Draw();
    Printer::Print(c1,graph->GetName());
  }

  const static void Print(TCanvas * c1, const char * name) {
    string str("dump/today/");
    str+=name;
    str+=".png";
    c1->Print(str.c_str());
  }
  
  const static void writeRoot(TGraphErrors * graph, TFile * fout) {
    fout->cd();
    graph->Write();
  }

  const static void writeRoot(TH1D* graph, TFile* fout) {
    fout->cd();
    graph->Write();
  }

  const static void writeRoot(TH2D* graph, TFile* fout) {
    fout->cd();
    graph->Write();
  }
  
};

class PlotCombiner {
public:
  PlotCombiner(char * name) {
    TMG =new TMultiGraph();
    TMG->SetName(name);
  }

  void addTGE(vector<TGraphErrors*> plots, char * options) {
    
  }
private:
  
  TMultiGraph * TMG;
};

class Fit{
public:
  const static void doFit( TH1D * hist, double &pk, double &dpk, double &chi2pdof ) {
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

  const static void reNorm(TH1D * hist) {
    double norm = 1.0/hist->Integral();
    for( int b = 1; b <= hist->GetNbinsX(); ++b ) {
      double content = hist->GetBinContent(b);
      hist->SetBinContent( b, content * norm );
      hist->SetBinError( b, sqrt(content) * norm );
    }
  }

  const static void FitAve(TGraphErrors * graph, double &ave, double &err) {
    graph->Fit("pol0","Q","Q");
    ave = graph->GetFunction("pol0")->GetParameter(0);
    err = graph->GetFunction("pol0")->GetParError(0);
  }
  
};

// Class that fill graph with timing info
class TimeDependFiller {
public:
  TimeDependFiller() {
    bin_value =0;
    bin_normalizer = 0;
    NPoints = 0;
    total_value = 0;;
    total_normalizer=0;
  }

  static void update(double gpstime) {
    if( gpstime > overall_end ) overall_end = gpstime;
    if( gpstime < overall_start ) overall_start = gpstime;
    counter++;
    if (counter == 1) bin_start = gpstime;
    if (counter == NGATES) {
      bin_end = gpstime;
      bin_error = (bin_end-bin_start)/2.0;
      bin_center = bin_start+bin_error-seconds_1995;
      counter =0;
    }
  }
  
  bool fill(double value,double norm) {
    bin_value+=value;
    bin_normalizer+=norm;
    total_value+=value;
    total_normalizer+=norm;
    return (counter==0) ? true : false;
  }

  void addPoint(TGraphErrors * graph, int good = 0) {
    if ((!good) && (bin_normalizer > 10.0)) {
      graph->SetPoint(NPoints,bin_center,bin_value/bin_normalizer);
      graph->SetPointError(NPoints,bin_error,sqrt(bin_value)/bin_normalizer);
      NPoints+=1;
    }
    reset();
  }

  const double getTotalValue(){
    return total_value;
  }

  const double getTotalNormalizer(){
    return total_normalizer;
  }
  
  static const char* toString() {
    
    TTimeStamp s ( overall_start, 0 ); // s, ns
    unsigned int sdate = s.GetDate( false ); // yyyymmdd
    unsigned int stime = s.GetTime( false ); // hhmmss
    int ys = sdate/10000;
    int ms = (sdate%10000)/100;
    int ds = sdate%100;
    int hs = stime/10000;
    int Ms = (stime%10000)/100;
    int ss = stime%100;

    TTimeStamp e ( overall_end, 0 );
    unsigned int edate = e.GetDate( false ); // yyyymmdd
    unsigned int etime = e.GetTime( false ); // hhmmss
    int ye = edate/10000;
    int me = (edate%10000)/100;
    int de = edate%100;
    int he = etime/10000;
    int Me = (etime%10000)/100;
    int se = etime%100;
    YS = ys;
    MS = ms;
    DS = ds;
    overall_error = (overall_end - overall_start) / 2.0;
    overall_center = overall_start+ overall_error - seconds_1995;
    return Form("Start: %04d-%02d-%02d %02d:%02d:%02d End: %04d-%02d-%02d %02d:%02d:%02d;Hour (Central time)",ys,ms,ds,hs,Ms,ss,ye,me,de,he,Me,se);
  }

  static unsigned long overall_start,overall_end,overall_error,overall_center;
  static int YS,MS,DS;
private:
  void reset() {
    bin_value =0;
    bin_normalizer = 0;
  }
  
  const static  unsigned int seconds_1995 = 788918400; // 00:00:00 1 January 1995 UTC
  const static int NGATES = 500;
  static int counter;
  static double bin_start,bin_end,bin_center,bin_error;
  
  
  double bin_normalizer,bin_value,total_value,total_normalizer;
  int NPoints;
  
};


// Class that provide tool to modify summary plot
class SummaryPloter {
public:
  SummaryPloter() {
    plotname.push_back(new pair<string, int>("peak_cluster_pe",-1));
    plotname.push_back(new pair<string, int>("peak_cluster_mev",-1));
    plotname.push_back(new pair<string, int>("minos_deltaT_summary",-1));
    plotname.push_back(new pair<string, int>("minos_RvC_summary",-1));
    plotname.push_back(new pair<string, int>("rock_muons_summary",-1));
    plotname.push_back(new pair<string, int>("minos_matches_summary",-1));
    plotname.push_back(new pair<string, int>("minos_tracks_summary",-1));
    plotname.push_back(new pair<string, int>("time_slices_summary",-1));
    plotname.push_back(new pair<string, int>("protons_summary",-1));
    plotname.push_back(new pair<string, int>("good_minos_matches_summary",-1));
    plotname.push_back(new pair<string, int>("good_minos_tracks_summary",-1));
    plotname.push_back(new pair<string, int>("Muplus_HE_summary",-1));
    plotname.push_back(new pair<string, int>("Muplus_ME_summary",-1));
    plotname.push_back(new pair<string, int>("Muplus_LE_summary",-1));
    plotname.push_back(new pair<string, int>("Muminus_HE_summary",-1));
    plotname.push_back(new pair<string, int>("Muminus_ME_summary",-1));
    plotname.push_back(new pair<string, int>("Muminus_LE_summary",-1));	
  }
  
  void plotSum() {
    TFile * fsum = new TFile( "dump/summary_plots.root", "OLD" );
    TCanvas * c2 = new TCanvas("c2","c2");

    
    for (int i = 0; i < plotname.size(); i++) {
      sumplots.push_back((TGraphErrors*)fsum->Get(plotname[i]->first.c_str()));
      
      if (sumplots.back() ==NULL ) {
	createSummaryGraph( plotname[i]->first);
      }
      
      if (plotname[i]->second != -1 ) {
	addPoint(sumplots[i],value_cache[plotname[i]->second]);
      } else {
	std::cout << plotname[i]->first << " plot is not updated.\n";
      }
      Printer::sumPrint(sumplots[i],c2);
    }
    
    delete c2;
    
    TFile * fnew = new TFile( "dump/summary_plots.root", "RECREATE" );
    fnew->cd();
    for (int i = 0; i < sumplots.size(); i++) {
      sumplots[i]->Write();
    }
    fnew->Close();
  }

  void cacheValue(const char * name, double ave,double err) {
    pair<double,double> value(ave,err);
    
    for (int i = 0; i < plotname.size(); i++) {
      if (plotname[i]->first.compare(name)==0) {
	plotname[i]->second = value_cache.size();
	value_cache.push_back(value);
	return;
      }
    }

    std::cout <<"Failed to find summary plot with name: "<< name << ".\n";
    
  }
private:

  void createSummaryGraph( const string & name) {
    std:: cout << "Requested Summary graph not found, create a new one.\n";
    sumplots.pop_back();
    sumplots.push_back(new TGraphErrors());
    sumplots.back()->SetName(name.c_str());
  }
  
  void addPoint(TGraphErrors * sumgraph, const pair<double,double> &value) {
    int N = sumgraph->GetN();
    if ( value.first > 0 ) {
      sumgraph ->SetPoint(N, TimeDependFiller::overall_center,value.first);
      sumgraph ->SetPointError(N, TimeDependFiller::overall_error,value.second);
    }
  }

  vector<pair<double,double> > value_cache;
  vector<TGraphErrors*> sumplots;
  vector<pair<string,int> * > plotname;
  
  
};
SummaryPloter sp;

// Classes of individual grapies
// Gates Tree
class ProtonPerPulse : public GraphProcessor {
public:
  ProtonPerPulse(GateTreeDB * p):DB(p) {
  }

  void createGraph() {
    proton_per_pulse = new TGraphErrors();
    proton_per_pulse->SetName("protons_per_pulse");
  }

  void fillGraph() {
    if (Filler.fill((DB->pot)/1.0E13,1)) {
      Filler.addPoint(proton_per_pulse);
    }
  }

  void printGraph(TCanvas *c1) {
    setTitle();
    Printer::timeDependPrint(proton_per_pulse, c1);
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(proton_per_pulse,fout);
    double ave = Filler.getTotalValue()/Filler.getTotalNormalizer();
    double err = sqrt(Filler.getTotalValue())/Filler.getTotalNormalizer();
    sp.cacheValue("protons_summary",ave,err);
  }

  void cleanup() {
    delete proton_per_pulse;
    proton_per_pulse= NULL;
  }
  
private:
  void setTitle() {
    string title(TimeDependFiller::toString());
    title+=";Protons per pulse/ 10^{13}";
    proton_per_pulse->SetTitle(title.c_str());
  }
  TGraphErrors * proton_per_pulse;
  TimeDependFiller Filler;
  GateTreeDB * DB;
};

class SlicePerPOT : public GraphProcessor {
public:
  SlicePerPOT(GateTreeDB * p):DB(p) {
  }

  void createGraph() {
    slices_per_pot = new TGraphErrors();
    slices_per_pot->SetName("time_slices_per_pot");
  }

  void fillGraph() {
    if (Filler.fill(DB->n_slices,(DB->pot)/1.0E13)) {
      Filler.addPoint(slices_per_pot);
    }
  }

  void printGraph(TCanvas *c1) {
    setTitle();
    Printer::timeDependPrint(slices_per_pot, c1);
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(slices_per_pot,fout);
    double ave = Filler.getTotalValue()/Filler.getTotalNormalizer();
    double err = sqrt(Filler.getTotalValue())/Filler.getTotalNormalizer();
    sp.cacheValue("time_slices_summary",ave,err);
  }

  void cleanup() {
    delete slices_per_pot;
    slices_per_pot = NULL;
  }
  
private:
  void setTitle() {
    string title(TimeDependFiller::toString());
    title+=";Time slices / 10^{13} POT";
    slices_per_pot->SetTitle(title.c_str());
  }
  TGraphErrors * slices_per_pot;
  TimeDependFiller Filler;
  GateTreeDB * DB;
};

class RockmuonsPerPOT : public GraphProcessor {
public:
  RockmuonsPerPOT(GateTreeDB * p):DB(p) {
  }

  void createGraph() {
    graph = new TGraphErrors();
    graph->SetName("rock_muons_per_pot");
  }

  void fillGraph() {
    if (Filler.fill(DB->rock_muons,(DB->pot)/1.0E13)) {
      Filler.addPoint(graph);
    }
  }

  void printGraph(TCanvas *c1) {
    setTitle();
    Printer::timeDependPrint(graph, c1);
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(graph,fout);
    double ave = Filler.getTotalValue()/Filler.getTotalNormalizer();
    double err = sqrt(Filler.getTotalValue())/Filler.getTotalNormalizer();
    sp.cacheValue("rock_muons_summary",ave,err);
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }
  
private:
  void setTitle() {
    string title(TimeDependFiller::toString());
    title+=";Rock muon tracks / 10^{13} POT";
    graph->SetTitle(title.c_str());
  }
  TGraphErrors * graph;
  TimeDependFiller Filler;
  GateTreeDB * DB;
};

class DeadProfile : public GraphProcessor {
public:
  DeadProfile(GateTreeDB * p):DB(p) {
  }

  void createGraph(){
    graph = new TProfile( "dead_profile", ";Beam intensity (10^{12} ppp);Average dead time fraction", 30, 0.0, 60.0 );
  }

  void fillGraph(){
    graph->Fill(DB->pot/1.0E12,DB->death);
  }

  void printGraph(TCanvas * c1) {
    c1->Clear();
    graph->Draw();
    c1->Print("dump/today/dead_vs_intensity.png");
  }

  void writeRoot(TFile * fout){
    fout->cd();
    graph->Write();
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }
  
private:
  GateTreeDB * DB;
  TProfile * graph;
};

class TimeBtwGates : public GraphProcessor {
public:
  TimeBtwGates(GateTreeDB * p):DB(p) {
  }

  void createGraph() {
    graph = new TH1D( "time_btw_gates", ";Time between gates (s)", 100, 0.0, 10.0 );
  }

  void fillGraph() {
    if (DB->getI()!=1 ) graph->Fill(DB->time_btw);
  }

  void printGraph(TCanvas * c1) {
    Printer::HistPrint(graph,c1,1);
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(graph,fout);
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }
  
private:
  TH1D * graph;
  GateTreeDB * DB;
};

class MinosGateDeltaT : public GraphProcessor {
public:
  MinosGateDeltaT(GateTreeDB * p):DB(p) {
  }

  void createGraph() {
    graph = new TH1D( "minos_gate_deltaT", ";MINERvA - MINOS gate #DeltaT (seconds)", 300, -1.5, 1.5 );
  }

  void fillGraph() {
    if (DB->has_minos ) graph->Fill(DB->gate_deltaT);
  }

  void printGraph(TCanvas * c1) {
    Printer::HistPrint(graph,c1,1);
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(graph,fout);
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }
  
private:
  TH1D * graph;
  GateTreeDB * DB;
};

class MinosTracksPerPot : public GraphProcessor {
public :
  MinosTracksPerPot(GateTreeDB * p):DB(p) {
  }
  
  void createGraph() {
    graph = new TGraphErrors();
    graph->SetName("minos_tracks_per_pot");
  }

  void fillGraph() {
    if (Filler.fill(DB->minos_tracks,(DB->pot)/1.0E13)) {
      Filler.addPoint(graph);
    }
  }

  void printGraph(TCanvas *c1) {
    setTitle();
    Printer::timeDependPrint(graph, c1);
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(graph,fout);
    double ave = Filler.getTotalValue()/Filler.getTotalNormalizer();
    double err = sqrt(Filler.getTotalValue())/Filler.getTotalNormalizer();
    sp.cacheValue("minos_tracks_summary",ave,err);
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }

private:
  void setTitle() {
    string title(TimeDependFiller::toString());
    title+=";MINOS tracks / 10^{13} POT";
    graph->SetTitle(title.c_str());
  }
  
  TGraphErrors * graph;
  TimeDependFiller Filler;
  GateTreeDB * DB;
};

class MinosMatchesPerPot : public GraphProcessor {
public :
  MinosMatchesPerPot(GateTreeDB * p):DB(p) {
  }
  
  void createGraph() {
    graph = new TGraphErrors();
    graph->SetName("minos_matches_per_pot");
  }

  virtual void fillGraph() {
    if (Filler.fill(DB->minos_matches,(DB->pot)/1.0E13)) {
      Filler.addPoint(graph);
    }
  }

  void printGraph(TCanvas *c1) {
    setTitle();
    Printer::timeDependPrint(graph, c1);
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(graph,fout);
    double ave = Filler.getTotalValue()/Filler.getTotalNormalizer();
    double err = sqrt(Filler.getTotalValue())/Filler.getTotalNormalizer();
    sp.cacheValue("minos_matches_summary",ave,err);
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }

protected:
  void setTitle() {
    string title(TimeDependFiller::toString());
    title+=";MINOS-matched rock muons / 10^{13} POT";
    graph->SetTitle(title.c_str());
  }
  
  TGraphErrors * graph;
  TimeDependFiller Filler;
  GateTreeDB * DB;
};

class GoodMinosPlots: public GraphProcessor {
public:
  GoodMinosPlots(GateTreeDB * p):DB(p) {
  }

  void createGraph() {
    tracks = new TGraphErrors();
    tracks->SetName("good_minos_tracks_per_pot");
    
    matches = new TGraphErrors();
    matches->SetName("good_minos_matches_per_pot");

    total_pot = 0;
    minos_good_pot = 0;
  }

  void fillGraph() {
    double good_pot = DB->has_minos ? DB->pot/1.0E13 : 0;
    total_pot+=DB->pot/1.0E13;
    minos_good_pot+=good_pot;
    
    if (TFiller.fill(DB->minos_tracks, good_pot)) {
      TFiller.addPoint(tracks);
    }

    if (MFiller.fill(DB->minos_matches, good_pot)) {
      MFiller.addPoint(matches);
    }
    
  }

  void printGraph(TCanvas *c1) {
    minos_live_percent = 100.0 * minos_good_pot/total_pot;
    TCanvas * temp = new TCanvas("temp","temp");
    TPaveText * tpt = new TPaveText(0.2, 0.86, 0.8, 0.92);
    tpt->AddText( Form("MINOS gate match for %3.2f%% of total POT",minos_live_percent) );
    tpt->SetBorderSize( 0.0 );
    tpt->Draw();
    temp->Print("dump/today/MINOSLIVETIME.png");
    delete temp;
    
    if (tracks->GetN()) {
      setTitle();
      Printer::GoodPrint(tracks, c1,tpt);
      Printer::GoodPrint(matches,c1,tpt);
    }
    delete tpt;
  }

  void writeRoot(TFile * fout) {
    FILE * mlive = fopen( "dump/today/minos_live_percent.txt", "w" );
    fprintf( mlive, "%04d %02d %02d\n", TimeDependFiller::YS, TimeDependFiller::MS, TimeDependFiller::DS );
    fprintf( mlive, "%3.2f\n", minos_live_percent );
    fclose( mlive );
    
    Printer::writeRoot(tracks,fout);
    Printer::writeRoot(matches,fout);

    double ave , err;
    if (tracks->GetN()) {
      ave = TFiller.getTotalValue()/TFiller.getTotalNormalizer();
      err = sqrt(TFiller.getTotalValue())/TFiller.getTotalNormalizer();
      sp.cacheValue("good_minos_tracks_summary",ave, err);
      ave = MFiller.getTotalValue()/MFiller.getTotalNormalizer();
      err = sqrt(MFiller.getTotalValue())/MFiller.getTotalNormalizer();
      sp.cacheValue("good_minos_matches_summary",ave, err);
    }
  }

  void cleanup() {
    delete tracks;
    delete matches;
    tracks = NULL;
    matches = NULL;
  }

private:
  void setTitle() {
    string title(TimeDependFiller::toString());
    string Ttitle=title+";MINOS tracks / 10^{13} POT";
    tracks->SetTitle(Ttitle.c_str());
    string Mtitle=title+";MINOS-matched rock muons / 10^{13} POT";
    matches->SetTitle(Mtitle.c_str());
  }
  
  TGraphErrors * tracks;
  TGraphErrors * matches;
  TimeDependFiller TFiller,MFiller;
  GateTreeDB * DB;
  double total_pot,minos_good_pot,minos_live_percent;
};

class RockMuPlusPerPOTByE: public GraphProcessor {
public:
  RockMuPlusPerPOTByE(GateTreeDB * p):DB(p) {
  }

  void createGraph() {
    HE_mu = new TGraphErrors();
    HE_mu->SetName("high_energy_mu+_per_pot");
    ME_mu = new TGraphErrors();
    ME_mu->SetName("mid_energy_mu+_per_pot");
    LE_mu = new TGraphErrors();
    LE_mu->SetName("low_energy_mu+_per_pot");
    TMG = new TMultiGraph();
    TMG->SetName("rock_mu+_per_pot_by_energy");
  }

  void fillGraph() {
    double good_pot = DB->has_minos ? DB->pot/1.0E13 : 0;
    if (HFiller.fill(DB->mu_plus[0],good_pot)) {
      HFiller.addPoint(HE_mu);
    }
    if (MFiller.fill(DB->mu_plus[1],good_pot)) {
      MFiller.addPoint(ME_mu);
    }
    if (LFiller.fill(DB->mu_plus[2],good_pot)) {
      LFiller.addPoint(LE_mu);
    }
  }

  void printGraph(TCanvas *c1) {
    setTitle();
    
    HE_mu->SetLineColor(kRed);
    ME_mu->SetLineColor(kGreen);
    LE_mu->SetLineColor(kBlue);
    
    HE_mu->SetMarkerSize(0.5);
    ME_mu->SetMarkerSize(0.5);
    LE_mu->SetMarkerSize(0.5);

    TLegend * lgd = new TLegend( 0.35, 0.83, 0.65, 0.93 );
    lgd->AddEntry( HE_mu, "high energy mu+", "l" );
    lgd->AddEntry( ME_mu, "medium energy mu+", "l" );
    lgd->AddEntry( LE_mu, "low energy mu+", "l" );
    
    TMG->Add(LE_mu);
    TMG->Add(ME_mu);
    TMG->Add(HE_mu);
    Printer::multiGraphPrint(TMG,c1,lgd);
    delete lgd;    
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(HE_mu,fout);
    Printer::writeRoot(ME_mu,fout);
    Printer::writeRoot(LE_mu,fout);
    if (LE_mu->GetN()<10 || ME_mu->GetN()<10 || LE_mu->GetN()<10) {
      return;
    }
    TGraphErrors * graph;
    string sumname;
    for (int i=0; i < 3; i++) {
      switch (i) {
      case 0:
	graph = HE_mu;
	sumname = "Muplus_HE_summary";
	break;
      case 1:
	graph = ME_mu;
	sumname = "Muplus_ME_summary";
	break;
      case 2:
	graph = LE_mu;
	sumname = "Muplus_LE_summary";
	break;
      }
      
      graph->Fit("pol0","Q","Q");
      sp.cacheValue(sumname.c_str(),graph->GetFunction("pol0")->GetParameter(0),graph->GetFunction("pol0")->GetParError(0));
    }
  }

  void cleanup() {
    delete TMG;
    TMG= NULL;
  }
  
private:
  void setTitle() {
    string title(TimeDependFiller::toString());
    title+=";Rock muon tracks / 10^{13} POT";
    TMG->SetTitle(title.c_str());
  }
  
  TGraphErrors * HE_mu, *ME_mu, *LE_mu;
  TMultiGraph * TMG;
  TimeDependFiller HFiller,MFiller,LFiller;
  GateTreeDB * DB;
};

class RockMuMinusPerPOTByE : public GraphProcessor {
public:
   RockMuMinusPerPOTByE(GateTreeDB * p):DB(p) {
   }

  void createGraph() {
    HE_mu = new TGraphErrors();
    HE_mu->SetName("high_energy_mu-_per_pot");
    ME_mu = new TGraphErrors();
    ME_mu->SetName("mid_energy_mu-_per_pot");
    LE_mu = new TGraphErrors();
    LE_mu->SetName("low_energy_mu-_per_pot");
    TMG = new TMultiGraph();
    TMG->SetName("rock_mu-_per_pot_by_energy");
  }

  void fillGraph() {
    double good_pot = DB->has_minos ? DB->pot/1.0E13 : 0;
    if (HFiller.fill(DB->mu_minus[0],good_pot)) {
      HFiller.addPoint(HE_mu);
    }
    if (MFiller.fill(DB->mu_minus[1],good_pot)) {
      MFiller.addPoint(ME_mu);
    }
    if (LFiller.fill(DB->mu_minus[2],good_pot)) {
      LFiller.addPoint(LE_mu);
    }
  }

  void printGraph(TCanvas *c1) {
    setTitle();
    
    HE_mu->SetLineColor(kRed);
    ME_mu->SetLineColor(kGreen);
    LE_mu->SetLineColor(kBlue);
    
    HE_mu->SetMarkerSize(0.5);
    ME_mu->SetMarkerSize(0.5);
    LE_mu->SetMarkerSize(0.5);

    TLegend * lgd = new TLegend( 0.35, 0.83, 0.65, 0.93 );
    lgd->AddEntry( HE_mu, "high energy mu-", "l" );
    lgd->AddEntry( ME_mu, "medium energy mu-", "l" );
    lgd->AddEntry( LE_mu, "low energy mu-", "l" );
    
    TMG->Add(LE_mu);
    TMG->Add(ME_mu);
    TMG->Add(HE_mu);
    Printer::multiGraphPrint(TMG,c1,lgd);
    delete lgd;
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(HE_mu,fout);
    Printer::writeRoot(ME_mu,fout);
    Printer::writeRoot(LE_mu,fout);
    if (LE_mu->GetN()<10 || ME_mu->GetN()<10 || LE_mu->GetN()<10) {
      return;
    }

    TGraphErrors * graph;
    string sumname;
    for (int i=0; i < 3; i++) {
      switch (i) {
      case 0:
	graph = HE_mu;
	sumname = "Muminus_HE_summary";
	break;
      case 1:
	graph = ME_mu;
	sumname = "Muminus_ME_summary";
	break;
      case 2:
	graph = LE_mu;
	sumname = "Muminus_LE_summary";
	break;
      }
      
      graph->Fit("pol0","Q","Q");
      sp.cacheValue(sumname.c_str(),graph->GetFunction("pol0")->GetParameter(0),graph->GetFunction("pol0")->GetParError(0));
    }
  }

  void cleanup() {
    delete TMG;
    TMG= NULL;
  }
  
private:
  void setTitle() {
    string title(TimeDependFiller::toString());
    title+=";Rock muon tracks / 10^{13} POT";
    TMG->SetTitle(title.c_str());
  }
  
  TGraphErrors * HE_mu, *ME_mu, *LE_mu;
  TMultiGraph * TMG;
  TimeDependFiller HFiller,MFiller,LFiller;
  GateTreeDB * DB;
};

//Header Tree



class PlotOfDeath : public GraphProcessor{
public:
  PlotOfDeath(HeaderTreeDB * p):DB(p) {}
  
  void createGraph(){
    totalPOT = 0;
    graph = new TH2D( "plot_of_death", "Fraction of 10 #mus spill when channel is dead;Module number;Strip number", 240, -5.0, 115.0, 127, 0.5, 127.5 );
  }

  void fillGraph() {
    for( int st = 0; st < DB->n_strips; ++st ) graph->Fill( DB->module[st]+0.5*(DB->plane[st]-1), DB->strip[st], DB->deadFrac[st]*DB->total_POT );
    totalPOT+=DB->total_POT;
  }

  void printGraph(TCanvas * c1){
    c1->Clear();
    c1->SetLogy(0);
    graph->Scale(1.0 / totalPOT);
    graph->Draw("COLZ");
    c1->Print("dump/today/fraction_dead_time.png");
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(graph,fout);
  }

  void cleanup() {
    delete graph;
    graph= NULL;
  }
private:
  TH2D * graph;
  HeaderTreeDB * DB;
  double totalPOT;
  
};

//nt Tree
class MinosDeltaT : public GraphProcessor {
public:
  MinosDeltaT(NTTreeDB * p):DB(p){
  }

  void createGraph() {
    graph = new TH1D( "minos_deltaT", ";MINOS - MINERvA #DeltaT (ns)", 100, -200.0, 200.0 );
  }

  void fillGraph() {
    if( DB->ev_minosMatch == 0 || DB->ev_ntracks > 1 ) return;
    graph->Fill(DB->ev_minosMatchDeltaT);
  }

  void printGraph(TCanvas * c1) {
    Printer::HistPrint(graph,c1,1);
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(graph,fout);
    sp.cacheValue("minos_deltaT_summary",graph->GetMean(),graph->GetRMS());
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }
  
private:
  TH1D * graph;
  NTTreeDB * DB;
};

class MinosRvC : public GraphProcessor{
public:
  MinosRvC(NTTreeDB * p):DB(p) {}

  void createGraph() {
    RvC = new TH1D( "minos_RvC", ";#frac{1}{p_{range}} - #frac{1}{p_{curv}} (MeV^{-1}c)", 100, -0.0004, 0.0004 );
    RvC_byrange = new TH1D( "minos_RvC_bycurve", ";#frac{1}{p_{range}} - #frac{1}{p_{curv}} (MeV^{-1}c)", 100, -0.0004, 0.0004 );
    RvC_bycurve = new TH1D( "minos_RvC_byrange", ";#frac{1}{p_{range}} - #frac{1}{p_{curv}} (MeV^{-1}c)", 100, -0.0004, 0.0004 );
  }

  void fillGraph() {
    if( DB->ev_minosMatch == 0 || DB->ev_ntracks > 1 ) return;
    if( DB->ev_minosPcurve > 0.0 && DB->ev_minosPrange > 0.0 ) {
      double diff = 1.0/ DB->ev_minosPrange - 1.0/DB->ev_minosPcurve ;
      RvC->Fill( diff);
      if( DB->ev_minosRecoByRange ) RvC_byrange->Fill( diff);
      else RvC_bycurve->Fill( diff);
    }
  }

  void printGraph(TCanvas * c1) {
    c1->Clear();
    c1->SetLogy(0);
    RvC_byrange->SetLineColor(kRed);
    RvC_bycurve->SetLineColor(kBlue);
    RvC->Draw();
    RvC_byrange->Draw("same");
    RvC_bycurve->Draw("same");
    TLegend * rvcleg = new TLegend( 0.155, 0.6, 0.45, 0.845 );
    rvcleg->AddEntry( RvC, "All tracks", "l" );
    rvcleg->AddEntry( RvC_byrange, "By range", "l" );
    rvcleg->AddEntry( RvC_bycurve, "By curvature", "l" );
    rvcleg->Draw();
    c1->Print("dump/today/minos_prange_vs_pcurvature.png");
    delete rvcleg;
  }

  void writeRoot(TFile * fout) {
    Printer::writeRoot(RvC,fout);
    Printer::writeRoot(RvC_byrange,fout);
    Printer::writeRoot(RvC_bycurve,fout);
    sp.cacheValue("minos_RvC_summary",RvC->GetMean(),RvC->GetRMS());
  }

  void cleanup() {
    delete RvC;
    delete RvC_bycurve;
    delete RvC_byrange;
    RvC = NULL;
    RvC_bycurve= NULL;
    RvC_byrange = NULL;
  }
  
private:
  TH1D * RvC,* RvC_byrange, * RvC_bycurve;
  NTTreeDB *DB;
};

class DiffEBtwMM : public GraphProcessor{
public:
  DiffEBtwMM(NTTreeDB * p):DB(p) {
  }

   void createGraph() {
     graph = new TH1D( "Energy difference in Minerva & MINOS", "Energy diff MeV", 100, 0.0, 5000.0 );
  }
  
  void fillGraph() {
    double Minerva = DB->ev_muonE;
    double MINOS = DB->ev_minosRecoByRange ? DB->ev_minosPrange : DB->ev_minosPcurve;
    //std::cout<< "Minerva report E: "<< Minerva <<", while MINOS report P: " << MINOS << ".\n";
    graph->Fill(Minerva - MINOS);
  }

  void printGraph(TCanvas * c1) {
    Printer::HistPrint(graph,c1);
  }
  void writeRoot( TFile* fout ) {
    Printer::writeRoot(graph,fout);
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }

private:
  TH1D * graph;
  NTTreeDB * DB;
};

class ClusterPE : public GraphProcessor{
public:
  ClusterPE(NTTreeDB * p):DB(p){
    pk=-1;
    dpk=-1;
    chi2=-1;
  }
  void createGraph() {
    graph = new TH1D( "minerva_cluster_pe", ";Muon cluster PE;Fraction per 0.5 PE", 100.0, 0.0, 50.0 );
  }
  void fillGraph() {
    if (DB->ev_extraEnergy > 100.0) return;
    for( int i = 0; i < DB->n_clusters;   ++i ) {
      graph->Fill( DB->cl_pe[i] );
    } // clusters
  }

  void printGraph(TCanvas * c1) {
    if (graph->GetEntries() > 1000) {
      Fit::reNorm(graph);
      Fit::doFit(graph,pk,dpk,chi2);
      if (pk <0) pk =0, dpk =0;
      graph->GetFunction("poly5")->SetLineColor(kRed);
      graph->SetMarkerSize(0.5);
      Printer::HistPrint(graph,c1);
    }
  }
  void writeRoot( TFile* fout ) {
    Printer::writeRoot(graph,fout);
    sp.cacheValue("peak_cluster_pe",pk,dpk);
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }
  
private:
  TH1D * graph;
  NTTreeDB * DB;
  double pk,dpk,chi2;
};

class ClusterMEV : public GraphProcessor{
public:
  ClusterMEV(NTTreeDB * p):DB(p){
    pk=-1;
    dpk=-1;
    chi2=-1;
  }
  void createGraph() {
    graph = new TH1D( "minerva_cluster_mev", ";Muon cluster energy (MeV);Fraction per 0.1 MeV", 100.0, 0.0, 10.0 );
  }
  void fillGraph() {
    if( DB->ev_extraEnergy > 100.0 ) return;
    for( int i = 0; i < DB->n_clusters; ++i ) {
      graph->Fill( DB->cl_recoE[i] );
    } // clusters
  }

  void printGraph(TCanvas * c1) {
    if (graph->GetEntries() > 1000) {
      Fit::reNorm(graph);
      Fit::doFit(graph,pk,dpk,chi2);
      if (pk <0) pk =0, dpk =0;
      graph->GetFunction("poly5")->SetLineColor(kRed);
      graph->SetMarkerSize(0.5);
      Printer::HistPrint(graph,c1);
    }
  }
  void writeRoot( TFile* fout ) {
    Printer::writeRoot(graph,fout);
    sp.cacheValue("peak_cluster_mev",pk,dpk);
  }

  void cleanup() {
    delete graph;
    graph = NULL;
  }
  
private:
  TH1D * graph;
  NTTreeDB * DB;
  double pk,dpk,chi2;
};

class MuonEPlot :public GraphProcessor{
public:
  MuonEPlot(NTTreeDB * p):DB(p) {}

  void createGraph() {
    muonE = new TH1D("MINOS muon Energy", "MINOS Muon Energy(GeV)", 100, 0, High_E_cut);
    mupE = new TH1D("MINOS mu+ Energy", "MINOS Muon Energy(GeV)", 100, 0, High_E_cut);
    mumE = new TH1D("MINOS mu- Energy", "MINOS Muon Energy(GeV)", 100, 0, High_E_cut);
  }
  
  void fillGraph() {
    if( DB->ev_minosMatch == 0 || DB->ev_ntracks > 1 ) return;
    double E = DB->ev_muonE/1000;
    if (E<High_E_cut) {
      muonE->Fill(E);// Convert to GeV
      if (DB->ev_muonCharge > 0 ) {
	mupE->Fill(E);
      } else if (DB->ev_muonCharge < 0) {
	mumE->Fill(E);
      }
    }
    
  }
  void printGraph(TCanvas * c1) {
    muonE->SetLineColor( kBlack );
    mupE->SetLineColor( kRed );
    mumE->SetLineColor( kBlue );
    c1->Clear();
    c1->SetGridx(0);
    c1->SetLogy(0);
    muonE->Draw();
    mupE->Draw("same");
    mumE->Draw("same");
    TLegend *eleg = new TLegend( 0.6, 0.7, 0.75, 0.85 );
    eleg->AddEntry( muonE, "All muon", "l");
    eleg->AddEntry( mupE, "Mu+", "l");
    eleg->AddEntry( mumE, "Mu-", "l");
    eleg->Draw();
    c1->Print("dump/today/minos_rockmuon_E.png");
  }
  void writeRoot( TFile* fout ) {
    Printer::writeRoot(muonE,fout);
    Printer::writeRoot(mupE,fout);
    Printer::writeRoot(mumE,fout);
  }
  void cleanup() {
    delete muonE;
    muonE= NULL;
    delete mupE;
    mupE= NULL;
    delete mumE;
    mumE=NULL;
  }
  
private:
  TH1D *muonE, *mupE,*mumE;
  NTTreeDB * DB;
  static const int High_E_cut = 20;
};



// class for process trees.
class GateTreeProcessor : public TreeProcessor {
public:
  GateTreeProcessor(){
    DB= &my_DB;
  }

  
  void createGraphies() {
    my_DB.initChainStatus();
    graphies.push_back( new ProtonPerPulse(&my_DB));
    graphies.push_back( new SlicePerPOT(&my_DB));
    graphies.push_back( new RockmuonsPerPOT(&my_DB));
    graphies.push_back( new TimeBtwGates(&my_DB));
    graphies.push_back( new MinosGateDeltaT(&my_DB));
    graphies.push_back( new MinosTracksPerPot(&my_DB));
    graphies.push_back( new MinosMatchesPerPot(&my_DB));
    graphies.push_back( new DeadProfile(&my_DB));
    graphies.push_back( new GoodMinosPlots(&my_DB));
    graphies.push_back( new RockMuPlusPerPOTByE(&my_DB));
    graphies.push_back( new RockMuMinusPerPOTByE(&my_DB));
    
    for (int i= 0; i < graphies.size(); i++) {
      graphies[i]->createGraph();
    }
  }

  void loopOverTree() {
    cout<< "Processing Gate Tree.\n";
    while (my_DB.update()) {
      TimeDependFiller::update(my_DB.gpstime);
      // if (DB.pot/1.0E12 <1.0) continue; 
      for (int i=0; i < graphies.size(); i++) {
	graphies[i]->fillGraph();
      }
    }
  }

private:
  GateTreeDB my_DB;
};

class HeaderTreeProcessor : public TreeProcessor {
public:
  HeaderTreeProcessor() {
    DB= &my_DB;
  }

  void createGraphies(){
    my_DB.initChainStatus();
    graphies.push_back(new PlotOfDeath(&my_DB));
    for (int i= 0; i < graphies.size(); i++) {
      graphies[i]->createGraph();
    }
  }

  void loopOverTree() {
    cout<< "Processing Header Tree.\n";
    while (my_DB.update()) {
      for (int i=0; i < graphies.size(); i++) {
	graphies[i]->fillGraph();
      }
    }
  }
  
private:
  HeaderTreeDB my_DB;
};

class NTTreeProcessor : public  TreeProcessor {
public:
  NTTreeProcessor() {
    DB = &my_DB;
  }

  void createGraphies() {
    my_DB.initChainStatus();
    graphies.push_back(new MinosDeltaT(&my_DB));
    graphies.push_back(new MinosRvC(&my_DB));
    graphies.push_back(new ClusterPE(&my_DB));
    graphies.push_back(new ClusterMEV(&my_DB));
    graphies.push_back(new MuonEPlot(&my_DB));
    //graphies.push_back(new DiffEBtwMM(&my_DB));
    for (int i= 0; i < graphies.size(); i++) {
      graphies[i]->createGraph();
    }
  }
  
  void loopOverTree() {
    cout<< "Processing nt Tree.\n";
    while (my_DB.update()) {
      for (int i=0; i < graphies.size(); i++) {
	graphies[i]->fillGraph();
      }
    }
  }

private:
  NTTreeDB my_DB;

};

TFile * readPlayList(std::vector<TreeProcessor*> TP) {
  FILE * playlist = fopen( "playlist_daily.txt", "r" );
  FILE * bad_data = fopen("bad_data_list.txt", "w");
  if( playlist == NULL ) exit(0);

  // TChains for main ntuple and header

  int r0 = 0; int s0 = 0; int r1 = 0; int s1 = 0;
  bool first = true;
  while( !feof(playlist) ) {
    int run, subrun;
    char name[1000];
    if (fscanf( playlist, "%d %d %s", &run, &subrun, &name )!=3) {
      r1 = run;
      s1 = subrun;
      break;
    }
    if( first ) {
      r0 = run;
      s0 = subrun;
      first = false;
    }
    /*
    if( run == r1 && subrun == s1 ) break; // it adds the last one twice for some reason <- Because it reads an empty new line.
    r1 = run;
    s1 = subrun;
    */
    std::cout<< "Reading run: " << run<<",subrun: "<< subrun << ".\n"; 
    TFile * test_file = new TFile( name, "OLD" );
    if( test_file == NULL ) {
      fprintf( bad_data, "%d %d\n", run, subrun );
      delete test_file;
      continue;
    }
    TTree * test_tree = (TTree *)test_file->Get( "nt" );
    if( test_tree == NULL ) {
      fprintf( bad_data, "%d %d\n", run, subrun );
      delete test_tree;
      continue;
    }
    test_file->Close();
    for (int i=0; i < TP.size(); i++) {
      TP[i]->addFileToChain(name);
    }

    //delete test_file;
    //delete test_tree;    

  }
  fclose( playlist );
  fclose( bad_data );
  printf("Created chain for runs %d/%d - %d/%d\n",r0,s0,r1,s1);
  
  // Output file for plots -- file name gives run range
  return new TFile( Form("dump/today/daily_plots_r%04d_s%02d_to_r%04d_s%02d.root",r0,s0,r1,s1), "RECREATE" );
}


unsigned long TimeDependFiller::overall_start = 0xFFFFFFFFFF;
unsigned long TimeDependFiller::overall_end = 0;
unsigned long TimeDependFiller::overall_center = 0;
unsigned long TimeDependFiller::overall_error = 0;
int TimeDependFiller::counter = 0;
int TimeDependFiller::YS = 0;
int TimeDependFiller::MS = 0;
int TimeDependFiller::DS = 0;
double TimeDependFiller::bin_start = 0;
double TimeDependFiller::bin_end = 0;
double TimeDependFiller::bin_center = 0;
double TimeDependFiller::bin_error = 0;


void MakeDailyPlots_v2() {
  //Set up colors.
  gStyle->SetNumberContours(999);
  Double_t stops[7] = { 0.00, 0.05, 0.23, 0.45, 0.60, 0.85, 1.00 };
  Double_t red[7]   = { 1.00, 0.00, 0.00, 0.00, 1.00, 1.00, 0.33 };
  Double_t green[7] = { 1.00, 1.00, 0.30, 0.40, 1.00, 0.00, 0.00 };
  Double_t blue[7]  = { 1.00, 1.00, 1.00, 0.00, 0.00, 0.00, 0.00 };
  TColor::CreateGradientColorTable(7, stops, red, green, blue, 999);
  
  //Start process.
  std::vector<TreeProcessor *> TP;
  GateTreeProcessor P1;
  HeaderTreeProcessor P2;
  NTTreeProcessor P3;
  TP.push_back(&P1);
  TP.push_back(&P2);
  TP.push_back(&P3);
  TFile * fout = readPlayList(TP);
  for (int i=0; i < TP.size(); i++) {
    TP[i]->createGraphies();
    TP[i]->loopOverTree();
    TP[i]->printGraphies();
    TP[i]->writeRootFile(fout);
    TP[i]->cleanup();
  }
  fout->Close();
  sp.plotSum();
}
  
