#ifndef ROCKMUONCALIBRATIONALG_H
#define ROCKMUONCALIBRATIONALG_H 1

// inheritance
#include "GaudiAlg/GaudiTupleAlg.h"

// includes
#include "Rtypes.h" //for Int_t,...

//forwards
#include "Event/VectorTypeDefs.h" //includes MinervaEventFwd.h
class IPlexModel;
class IGetCalAttenuation;
class IGeomUtilSvc;
class IExtraEnergyTool;
class IMuonUtils;
class IGetStripResponse;
class IClearFiberAttTool;
class IWLSBaggieAttTool;
class IPOTTool;
class IGateAnalyzabilityTool;

namespace Minerva {
  class DeDetector;
  class DeOuterDetector;
  class StripID;
  class DiscrPairID;
  class IDCluster;
}

class TFile;
class TTree;

class RockMuonCalibrationAlg : public GaudiTupleAlg
{

public:

  RockMuonCalibrationAlg(std::string const &, ISvcLocator *);
  virtual StatusCode initialize();
  virtual StatusCode finalize();
  virtual ~RockMuonCalibrationAlg();

  virtual StatusCode execute();

private:

  bool makeHeaderTree();
  bool mightHaveDeadStrips( const Minerva::IDCluster * cluster );
  void writeHitStuff( Minerva::Track * track );
  bool fillTruth();
  void fillPOT();
  void fillMINOS( SmartRef<Minerva::Prong> prong );
  void fillTrueEnergyMap( std::map< Minerva::StripID, double > &stripTrueEnergyMap  );
  void fillClusterInfo( std::map< Minerva::StripID, double > stripTrueEnergyMap, SmartRef<Minerva::Track> pTrack );
  void loopOverPlanes( SmartRef<Minerva::Track> pTrack );
  void loopOverODFrames( SmartRef<Minerva::Track> pTrack );
  void loopOverDigits( Minerva::TimeSlice * pts, SmartRef<Minerva::Track> pTrack );
  void fillTheMapOfDeath();

  //! the time of the current event
  ulonglong m_EventTime;
  //! Test Beam Detector flag for the current data
  bool m_isTestBeam;

  //! ntuple file name
  std::string m_OutputFilename;
  //! name of text file used for IOV accounting
  bool m_writeTimeFile;
  std::string m_TimeFilename;
  //! Should we allow MINOS stubs for match criteria?
  bool   m_allowMinosStub;
  std::string m_mcIDHitsLocation;
  std::string m_genMinInteractionLocation;

  // Minerva detector elements and tools
  const Minerva::DeDetector      * m_innerDetector;
  const Minerva::DeOuterDetector * m_outerDetector;
  IGetCalAttenuation     * m_getCalAttenuation; // mapper attenuation
  IMuonUtils             * m_pMuonUtils;
  IPlexModel             * m_plexModel;
  IExtraEnergyTool       * m_extraEnergy;
  IGetStripResponse      * m_getStripResponse; // used for mightBeDead function
  IWLSBaggieAttTool      * m_baggieAttTool;
  IClearFiberAttTool     * m_clearFiberAttTool;
  IPOTTool               * m_potTool;
  IGateAnalyzabilityTool * m_gateAnalyzabilityTool;

  //! Map from strip to index of strip within rock muon entry
  std::map<Minerva::StripID,int> stripToIdx;
  //! maximum hit number on each discr pair; each push comes with 16 ticks of dead time
  std::map<Minerva::DiscrPairID,unsigned int> theMapOfDeath;
  std::map<Minerva::StripID,double> totalDeadTime;

  TFile * pFile;
  TTree * pTree;
  TTree * headerTree;
  TTree * gateTree;
  static const int MAXENTRIES = 1000;
  static const int MAXCLUSTERS = 240;
  static const int HEMUONTHRESHOLD = 12000;//MeV
  static const int LEMUONTHRESHOLD = 6000;
  
  // nTuple variables
  // Gate tree
  Int_t gate_run, gate_subrun, gate_gate, gate_nslices, gate_nMinosTracks, gate_isAnalyzable;
  Int_t gate_nRocks, gate_mup_E[3],gate_mum_E[3], gate_nMatch, gate_hasMINOS;
  Double_t gate_timeToPrev, gate_nPOT, gate_gps, gate_minosGateDeltaT, gate_deadTimeFrac;

  // for header tree death toll 
  Int_t n_strips;
  Double_t fractionOfDeath[30000];
  Int_t module[30000], plane[30000], strip[30000];

  // Event-level variables
  Int_t ev_run, ev_subrun, ev_gate, ev_timeslice, n_entries, n_clusters, n_hits, ev_isMC, ev_ntracks;
  Double_t ev_MEU, ev_LY;

  // Minerva track variables
  Int_t ev_minosMatch, ev_muonEnterFront, ev_muonEnterSide, ev_muonExitBack, ev_muonExitSide;
  Double_t ev_trktheta, ev_trkAx, ev_trkAy, ev_extraEnergy, ev_trk_exit[3], ev_trk_exitAx, ev_trk_exitAy, ev_trk[3];

  // MINOS track variables
  Int_t ev_minosRecoByRange, ev_minosRecoByCurvature, ev_minosTrackQuality;
  Double_t ev_minosP, ev_muonCharge, ev_muonVtx[3], ev_muonP[3], ev_muonE, ev_minosPrange, ev_minosPcurve, ev_minosMatchDeltaT, ev_minosTrackChi2, ev_minosTrackNDF, ev_minosVtx[3], ev_minosTrackQP, ev_minosTrackSigmaQP, ev_minosTrackPassFit;

  // Truth variables
  Int_t ev_muonTruePDG;
  Double_t ev_muonTrueVtx[3], ev_muonTrueP[3], ev_muonTrueE;

  // Strip-level variables -- filled for hits OR path length
  Int_t st_module[MAXENTRIES], st_plane[MAXENTRIES], st_strip[MAXENTRIES], st_rack[MAXENTRIES], st_view[MAXENTRIES];
  Double_t st_mev[MAXENTRIES], st_path[MAXENTRIES], st_base[MAXENTRIES], st_lpos[MAXENTRIES];
  Int_t st_crate[MAXENTRIES], st_croc[MAXENTRIES], st_chain[MAXENTRIES], st_board[MAXENTRIES], st_pixel[MAXENTRIES];
  Double_t st_pe[MAXENTRIES], st_q[MAXENTRIES], st_s2s[MAXENTRIES];

  // Cluster-level variables
  Int_t cl_subdet[MAXCLUSTERS], cl_module[MAXCLUSTERS], cl_plane[MAXCLUSTERS], cl_nstrips[MAXCLUSTERS], cl_type[MAXCLUSTERS], cl_mightBeDead[MAXCLUSTERS];
  Double_t cl_tpos[MAXCLUSTERS], cl_lpos[MAXCLUSTERS], cl_pe[MAXCLUSTERS], cl_recoE[MAXCLUSTERS], cl_trueE[MAXCLUSTERS], cl_time[MAXCLUSTERS], cl_q[MAXCLUSTERS];
  Double_t cl_stateAx[MAXCLUSTERS], cl_stateAy[MAXCLUSTERS], cl_cosThetaZ[MAXCLUSTERS], cl_activePathLength[MAXCLUSTERS];

  // Hit-level variables -- filled for hits only
  Int_t hit_crate[MAXENTRIES], hit_croc[MAXENTRIES], hit_chain[MAXENTRIES], hit_board[MAXENTRIES], hit_pixel[MAXENTRIES];
  Double_t hit_pe[MAXENTRIES], hit_rt[MAXENTRIES], hit_ct[MAXENTRIES], hit_tof[MAXENTRIES], hit_dtc[MAXENTRIES], hit_dtm[MAXENTRIES], hit_shl[MAXENTRIES], hit_bfl[MAXENTRIES], hit_cfl[MAXENTRIES];

  //! Flag for first event, used for IOV accounting
  bool bFirstEvent;
  //! Time at start of subrun
  ulonglong begin_time;
  //! Time at end of subrun
  ulonglong end_time;

  //! Do you want to save timing calibration variables to the ntuple?
  bool m_writeHitStuff;

  //! count POT for subrun
  double total_POT;
  unsigned int total_nMinosTracks;
  unsigned int n_gates;

};

#endif // ROCKMUONCALIBRATIONALG_H
