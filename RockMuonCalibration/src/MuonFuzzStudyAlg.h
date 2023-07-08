#ifndef MUONFUZZSTUDYALG_H
#define MUONFUZZSTUDYALG_H 1

// inheritance
#include "GaudiAlg/GaudiTupleAlg.h"

// includes
#include "Rtypes.h" //for Int_t,...

//forwards
#include "Event/VectorTypeDefs.h" //includes MinervaEventFwd.h
class IGeomUtilSvc;
class IRecoObjectTimeTool;
class IMuonUtils;
class IMinervaMathTool;

namespace Minerva {
  class DeDetector;
  class StripID;
  class PlaneID;
  class IDCluster;
}

class TFile;
class TTree;

class MuonFuzzStudyAlg : public GaudiTupleAlg
{

public:

  MuonFuzzStudyAlg(std::string const &, ISvcLocator *);
  virtual StatusCode initialize();
  virtual StatusCode finalize();
  virtual ~MuonFuzzStudyAlg();

  virtual StatusCode execute();

private:

  bool makeHeaderTree();
  bool fillTruth();
  void fillMINOS( SmartRef<Minerva::Prong> prong );
  void fillTrueEnergyMap( std::map< Minerva::StripID, double > &stripTrueEnergyMap  );
  void fillClusterInfo( std::map< Minerva::StripID, double > stripTrueEnergyMap, SmartRef<Minerva::Track> pTrack );
  void fillTrackStateMap( std::map< const Minerva::PlaneID, double > &trackStateMap, SmartRef<Minerva::Track> track );

  //! the time of the current event
  ulonglong m_EventTime;

  //! ntuple file name
  std::string m_OutputFilename;
  std::string m_mcIDHitsLocation;
  std::string m_genMinInteractionLocation;

  // Minerva detector elements and tools
  const Minerva::DeDetector * m_innerDetector;
  IMuonUtils                * m_muonUtils;
  IRecoObjectTimeTool       * m_recoObjectTimeTool;
  IMinervaMathTool          * m_mathTool;

  TFile * pFile;
  TTree * pTree;
  static const int MAXCLUSTERS = 240;
  static const int MAXFUZZ = 1000;

  double m_muonSpeed;

  // nTuple variables
  // Event-level variables
  Int_t ev_run, ev_subrun, ev_gate, ev_timeslice, n_entries, n_clusters, n_hits, ev_isMC;

  // Minerva track variables
  Int_t ev_minosMatch;
  Double_t ev_trktheta, ev_trkAx, ev_trkAy, ev_extraEnergy, ev_trk_exit[3], ev_trk_exitAx, ev_trk_exitAy;

  // MINOS track variables
  Int_t ev_minosRecoByRange, ev_minosRecoByCurvature;
  Double_t ev_minosP, ev_muonCharge, ev_muonVtx[3], ev_muonP[3], ev_minosPrange, ev_minosPcurve, ev_minosVtx[3], ev_minosTrackQP;

  // Truth variables
  Int_t ev_muonTruePDG;
  Double_t ev_muonTrueVtx[3], ev_muonTrueP[3], ev_muonTrueE;

  // Cluster-level variables
  Int_t cl_subdet[MAXCLUSTERS], cl_module[MAXCLUSTERS], cl_plane[MAXCLUSTERS], cl_nstrips[MAXCLUSTERS], cl_type[MAXCLUSTERS];
  Double_t cl_tpos[MAXCLUSTERS], cl_lpos[MAXCLUSTERS], cl_pe[MAXCLUSTERS], cl_recoE[MAXCLUSTERS], cl_trueE[MAXCLUSTERS], cl_time[MAXCLUSTERS], cl_trueEall[MAXCLUSTERS];
  Double_t cl_stateAx[MAXCLUSTERS], cl_stateAy[MAXCLUSTERS], cl_cosThetaZ[MAXCLUSTERS], cl_activePathLength[MAXCLUSTERS];

  // fuzz variables
  Int_t n_fuzzclusters;
  Int_t fz_subdet[MAXFUZZ], fz_type[MAXFUZZ];
  Double_t fz_distance[MAXFUZZ], fz_energy[MAXFUZZ], fz_timediff[MAXFUZZ];
  

};

#endif // MUONFUZZSTUDYALG_H
