#include "RockMuonCalibrationAlg.h"

#include "GaudiKernel/DeclareFactoryEntries.h"
#include "Plex/IPlexModel.h"
#include "CalTools/IGetCalAttenuation.h"
#include "CalTools/IGetStripResponse.h"
#include "CalTools/IWLSBaggieAttTool.h"
#include "CalTools/IClearFiberAttTool.h"
#include "NumiInterface/IPOTTool.h"
#include "MinervaDet/IGeomUtilSvc.h"
#include "MinervaDet/DePlane.h"
#include "MinervaDet/DeDetector.h"
#include "ODDet/DeOuterDetector.h"
#include "ODDet/DeODFrame.h"
#include "DetDesc/Material.h"
#include "GateQuality/IGateAnalyzabilityTool.h"

#include "Event/Track.h"
#include "Event/TimeSlice.h"
#include "Event/DAQHeader.h"
#include "Event/Prong.h"
#include "Kernel/PlaneID.h"
#include "Kernel/StripID.h"
#include "Kernel/DiscrPairID.h"
#include "Kernel/ChannelID.h"
#include "Kernel/FrameID.h"
#include "Event/GenMinInteraction.h"
#include "Event/MCHit.h"
#include "Event/DataQuality.h"
#include "Kernel/MinervaElectronicsParams.h" // for kClockTick

#include "RecUtils/ProngExtraDataDefs.h"
#include "RecUtils/DigitExtraDataDefs.h"
#include "RecUtils/MCDigitExtraDataDefs.h"
#include "RecUtils/ClusterExtraDataDefs.h"

#include "EnergyRecTools/IExtraEnergyTool.h"
#include "AnaUtils/IMuonUtils.h"
#include "TFile.h"
#include "TTree.h"
#include <fstream>
#include <time.h>


DECLARE_ALGORITHM_FACTORY(RockMuonCalibrationAlg);

//===========================================================================================
//! Constructor, initialize variables from options file
//===========================================================================================
RockMuonCalibrationAlg::RockMuonCalibrationAlg(std::string const & name, ISvcLocator * pSvcLocator)
  : GaudiTupleAlg(name, pSvcLocator)
{
  declareProperty( "OutputFilename",    m_OutputFilename     = "nt.root"      );
  declareProperty( "TimeFilename",      m_TimeFilename       = "time.txt"     );

  declareProperty( "WriteTimeFile",     m_writeTimeFile      = false          );
  declareProperty( "WriteHitStuff",     m_writeHitStuff      = true           );
  declareProperty( "AllowMinosStub",    m_allowMinosStub     = false          );

  declareProperty( "MCHitsLocation",    m_mcIDHitsLocation   = "MC/ID/Hits"   );
  declareProperty( "GenMinInteractionLocation", m_genMinInteractionLocation = Minerva::GenMinInteractionLocation::Default );
}

//===========================================================================================
//! Initialize routine, get tools, declare nTuple output variables
//===========================================================================================
StatusCode RockMuonCalibrationAlg::initialize()
{

  debug() << "RockMuonCalibrationAlg::initialze()" << endmsg;

  IGeomUtilSvc *geomUtilSvc;
  service("GeomUtilSvc", geomUtilSvc, true);
  m_innerDetector = geomUtilSvc->getIDDet();
  m_outerDetector = geomUtilSvc->getODDet();
  m_isTestBeam = geomUtilSvc->isTestBeam();

  if( !m_innerDetector ) {
    error() << "Could not retrieve inner detector!" << endmsg;
    return StatusCode::FAILURE;
  }

//  if( !m_isTestBeam && !m_outerDetector ) {
//    error() << "Could not retrieve outer detector!" << endmsg;
//    return StatusCode::FAILURE;
//  }

  try {
    m_getCalAttenuation = tool<IGetCalAttenuation>("GetCalAttenuation");
  } catch( GaudiException& e ) {
    error() << "Could not get GetCalAttenuation tool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_plexModel = tool<IPlexModel>("MinervaPlexModel");
  } catch( GaudiException& e ) {
    error() << "Could not get MinervaPlexModel tool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_pMuonUtils = tool<IMuonUtils>("MuonUtils");
  } catch( GaudiException& e ) {
    error() << "Could not get MuonUtils tool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_extraEnergy = tool<IExtraEnergyTool>("ExtraEnergyTool");
  } catch( GaudiException& e ) {
    error() << "Could not get ExtraEnergy tool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_getStripResponse = tool<IGetStripResponse>("GetStripResponse");
  } catch( GaudiException& e ) {
    error() << "Could not get GetStripResponse tool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_baggieAttTool = tool<IWLSBaggieAttTool>("WLSBaggieAttTool");  
  } catch( GaudiException& e ) {
    error() << "Could not get WLSBaggieAtt tool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_clearFiberAttTool = tool<IClearFiberAttTool>("ClearFiberAttTool");
  } catch( GaudiException& e ) {
    error() << "Could not get ClearFiberAttTool tool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_potTool = tool<IPOTTool>("POTTool");
  } catch( GaudiException& e ) {
    error() << "Could not get POTTool tool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_gateAnalyzabilityTool = tool<IGateAnalyzabilityTool>("GateAnalyzabilityTool");
  } catch( GaudiException& e ) {
    error() << "Could not get GateAnalyzabilityTool" << endmsg;
    return StatusCode::FAILURE;
  }

  pFile = new TFile(m_OutputFilename.c_str(), "RECREATE");
  if (pFile == 0)
  {
    fatal() << "Could not open new TFile " << m_OutputFilename.c_str() << endmsg;
    return StatusCode::FAILURE;
  }

  // "main" TTree -- fills once per passing rock muon, can be 0-several times per gate
  pTree = new TTree("nt","nt");
  if( pTree == 0 ) {
    fatal() << "Could not book main TTree" << endmsg;
    return StatusCode::FAILURE;
  }

  // Event accounting
  pTree->Branch("ev_run", &ev_run, "ev_run/I", 32768);
  pTree->Branch("ev_subrun", &ev_subrun, "ev_subrun/I", 32768);
  pTree->Branch("ev_gate", &ev_gate, "ev_gate/I", 32768);
  pTree->Branch("ev_isMC", &ev_isMC, "ev_isMC/I", 32768);
  pTree->Branch("ev_ntracks", &ev_ntracks, "ev_ntracks/I", 32768);
  pTree->Branch("ev_gps_time", &m_EventTime, "ev_gps_time/l", 32768 ); // The lowercase "l" specifies ULong64_t

  // Minerva track variables -- filled once per event, every event
  pTree->Branch("ev_timeslice", &ev_timeslice, "ev_timeslice/I", 32768);
  pTree->Branch("ev_trktheta", &ev_trktheta, "ev_trktheta/D", 65536);
  pTree->Branch("ev_trkAx", &ev_trkAx, "ev_trkAx/D", 65536);
  pTree->Branch("ev_trkAy", &ev_trkAy, "ev_trkAy/D", 65536);
  pTree->Branch("ev_trk_exit", &ev_trk_exit, "ev_trk_exit[3]/D", 65536);
  pTree->Branch("ev_trk", &ev_trk, "ev_trk[3]/D", 65536);
  pTree->Branch("ev_trk_exitAx", &ev_trk_exitAx, "ev_trk_exitAx/D", 65536);
  pTree->Branch("ev_trk_exitAy", &ev_trk_exitAy, "ev_trk_exitAy/D", 65536);  
  pTree->Branch("ev_muonEnterFront", &ev_muonEnterFront, "ev_muonEnterFront/I", 32768);
  pTree->Branch("ev_muonEnterSide", &ev_muonEnterSide, "ev_muonEnterSide/I", 32768);
  pTree->Branch("ev_muonExitBack", &ev_muonExitBack, "ev_muonExitBack/I", 32768);
  pTree->Branch("ev_muonExitSide", &ev_muonExitSide, "ev_muonExitSide/I", 32768);
  pTree->Branch("ev_extraEnergy", &ev_extraEnergy, "ev_extraEnergy/D", 65536);
  pTree->Branch("ev_minosMatch", &ev_minosMatch, "ev_minosMatch/I", 32768);
  pTree->Branch("ev_MEU", &ev_MEU, "ev_MEU/D", 65536);
  pTree->Branch("ev_LY", &ev_LY, "ev_LY/D", 65536);

  // MINOS track variables -- filled once per event, only if ev_minosMatch is true (bogus otherwise)
  pTree->Branch("ev_minosTrackQuality", &ev_minosTrackQuality, "ev_minosTrackQuality/I", 32768);
  pTree->Branch("ev_minosTrackChi2", &ev_minosTrackChi2, "ev_minosTrackChi2/D", 65536);
  pTree->Branch("ev_minosTrackNDF", &ev_minosTrackNDF, "ev_minosTrackNDF/D", 65536);
  pTree->Branch("ev_minosTrackPassFit", &ev_minosTrackPassFit, "ev_minosTrackPassFit/D", 65536);
  pTree->Branch("ev_minosRecoByRange", &ev_minosRecoByRange, "ev_minosRecoByRange/I", 32768);
  pTree->Branch("ev_minosRecoByCurvature", &ev_minosRecoByCurvature, "ev_minosRecoByCurvature/I", 32768);
  pTree->Branch("ev_minosP", &ev_minosP, "ev_minosP/D", 65536);
  pTree->Branch("ev_minosPrange", &ev_minosPrange, "ev_minosPrange/D", 65536);
  pTree->Branch("ev_minosPcurve", &ev_minosPcurve, "ev_minosPcurve/D", 65536);
  pTree->Branch("ev_muonCharge", &ev_muonCharge, "ev_muonCharge/D", 65536);
  pTree->Branch("ev_minosVtx", &ev_minosVtx, "ev_minosVtx[3]/D", 65536);
  pTree->Branch("ev_muonVtx", &ev_muonVtx, "ev_muonVtx[3]/D", 65536); // minerva vertex
  pTree->Branch("ev_muonP", &ev_muonP, "ev_muonP[3]/D", 65536);
  pTree->Branch("ev_muonE", &ev_muonE, "ev_muonE/D", 65536);
  pTree->Branch("ev_minosMatchDeltaT", &ev_minosMatchDeltaT, "ev_minosMatchDeltaT/D", 65536);
  pTree->Branch("ev_minosTrackQP", &ev_minosTrackQP, "ev_minosTrackQP/D", 65536); // for data-driven rock muon MC
  pTree->Branch("ev_minosTrackSigmaQP", &ev_minosTrackSigmaQP, "ev_minosTrackSigmaQP/D", 65536);

  // Truth variables -- filled once per event, every MC event (bogus for data)
  pTree->Branch("ev_muonTruePDG", &ev_muonTruePDG, "ev_muonTruePDG/I", 32768);
  pTree->Branch("ev_muonTrueVtx", &ev_muonTrueVtx, "ev_muonTrueVtx[3]/D", 65536);
  pTree->Branch("ev_muonTrueP", &ev_muonTrueP, "ev_muonTrueP[3]/D", 65536);
  pTree->Branch("ev_muonTrueE", &ev_muonTrueE, "ev_muonTrueE/D", 65536);

  // Strip variables -- filled for path != 0 OR mev != 0
  pTree->Branch("n_entries", &n_entries, "n_entries/I", 32768);
  pTree->Branch("st_module", st_module, "st_module[n_entries]/I", 32768);
  pTree->Branch("st_plane", st_plane, "st_plane[n_entries]/I", 32768);
  pTree->Branch("st_strip", st_strip, "st_strip[n_entries]/I", 32768);
  pTree->Branch("st_rack", st_rack, "st_rack[n_entries]/I", 32768);
  pTree->Branch("st_view", st_view, "st_view[n_entries]/I", 32768);
  pTree->Branch("st_mev", st_mev, "st_mev[n_entries]/D", 65536);
  pTree->Branch("st_path", st_path, "st_path[n_entries]/D", 65536);
  pTree->Branch("st_base", st_base, "st_base[n_entries]/D", 65536);
  pTree->Branch("st_lpos", st_lpos, "st_lpos[n_entries]/D", 65536);
  pTree->Branch("st_crate", st_crate, "st_crate[n_entries]/I", 32768);
  pTree->Branch("st_croc", st_croc, "st_croc[n_entries]/I", 32768);
  pTree->Branch("st_chain", st_chain, "st_chain[n_entries]/I", 32768);
  pTree->Branch("st_board", st_board, "st_board[n_entries]/I", 32768);
  pTree->Branch("st_pixel", st_pixel, "st_pixel[n_entries]/I", 32768);
  pTree->Branch("st_pe", st_pe, "st_pe[n_entries]/D", 65536);
  pTree->Branch("st_q", st_q, "st_q[n_entries]/D", 65536);
  pTree->Branch("st_s2s", st_s2s, "st_s2s[n_entries]/D", 65536);

  // Cluster variables -- filled for all clusters
  pTree->Branch("n_clusters", &n_clusters, "n_clusters/I", 32768);
  pTree->Branch("cl_subdet", cl_subdet, "cl_subdet[n_clusters]/I", 32768);
  pTree->Branch("cl_module", cl_module, "cl_module[n_clusters]/I", 32768);
  pTree->Branch("cl_plane", cl_plane, "cl_plane[n_clusters]/I", 32768);
  pTree->Branch("cl_tpos", cl_tpos, "cl_tpos[n_clusters]/D", 65536);
  pTree->Branch("cl_lpos", cl_lpos, "cl_lpos[n_clusters]/D", 65536);
  pTree->Branch("cl_pe", cl_pe, "cl_pe[n_clusters]/D", 65536);
  pTree->Branch("cl_q", cl_q, "cl_q[n_clusters]/D", 65536);
  pTree->Branch("cl_recoE", cl_recoE, "cl_recoE[n_clusters]/D", 65536);
  pTree->Branch("cl_trueE", cl_trueE, "cl_trueE[n_clusters]/D", 65536);
  pTree->Branch("cl_stateAx", cl_stateAx, "cl_stateAx[n_clusters]/D", 65536);
  pTree->Branch("cl_stateAy", cl_stateAy, "cl_stateAy[n_clusters]/D", 65536);
  pTree->Branch("cl_cosThetaZ", cl_cosThetaZ, "cl_cosThetaZ[n_clusters]/D", 65536);
  pTree->Branch("cl_time", cl_time, "cl_time[n_clusters]/D", 65536);
  pTree->Branch("cl_nstrips", cl_nstrips, "cl_nstrips[n_clusters]/I", 32768);
  pTree->Branch("cl_type", cl_type, "cl_type[n_clusters]/I", 32768);
  pTree->Branch("cl_mightBeDead", cl_mightBeDead, "cl_mightBeDead[n_clusters]/I", 32768);
  pTree->Branch("cl_activePathLength", cl_activePathLength, "cl_activePathLength[n_clusters]/D", 65536);

  // Hit variables -- filled for pe != 0
  pTree->Branch( "n_hits", &n_hits, "n_hits/I", 32768 );
  pTree->Branch( "hit_crate", hit_crate, "hit_crate[n_hits]/I", 32768 );
  pTree->Branch( "hit_croc",  hit_croc,  "hit_croc[n_hits]/I",  32768 );
  pTree->Branch( "hit_chain", hit_chain, "hit_chain[n_hits]/I", 32768 );
  pTree->Branch( "hit_board", hit_board, "hit_board[n_hits]/I", 32768 );
  pTree->Branch( "hit_pixel", hit_pixel, "hit_pixel[n_hits]/I", 32768 );
  pTree->Branch( "hit_pe",  hit_pe,  "hit_pe[n_hits]/D",  65536); // pe
  pTree->Branch( "hit_rt",  hit_rt,  "hit_rt[n_hits]/D",  65536); // raw time
  pTree->Branch( "hit_ct",  hit_ct,  "hit_ct[n_hits]/D",  65536); // calibrated time
  pTree->Branch( "hit_tof", hit_tof, "hit_tof[n_hits]/D", 65536); // time of flight from muon start to this hit
  pTree->Branch( "hit_dtc", hit_dtc, "hit_dtc[n_hits]/D", 65536); // distance to connector
  pTree->Branch( "hit_dtm", hit_dtm, "hit_dtm[n_hits]/D", 65536); // distance to mirror
  pTree->Branch( "hit_shl", hit_shl, "hit_shl[n_hits]/D", 65536); // 
  pTree->Branch( "hit_bfl", hit_bfl, "hit_bfl[n_hits]/D", 65536); // baggie fiber length
  pTree->Branch( "hit_cfl", hit_cfl, "hit_cfl[n_hits]/D", 65536); // clear fiber length

  // Gate tree -- fills once per gate, every gate
  gateTree = new TTree("gates", "gates");
  if( gateTree == 0 ) {
    fatal() << "Could not book gate TTree" << endmsg;
    return StatusCode::FAILURE;
  }

  gateTree->Branch( "gate_run", &gate_run, "gate_run/I", 32768 );
  gateTree->Branch( "gate_subrun", &gate_subrun, "gate_subrun/I", 32768 );
  gateTree->Branch( "gate_gate", &gate_gate, "gate_gate/I", 32768 );
  gateTree->Branch( "gate_nslices", &gate_nslices, "gate_nslices/I", 32768 );
  gateTree->Branch( "gate_gps", &gate_gps, "gate_gps/D", 65536 ); // in seconds
  gateTree->Branch( "gate_timeToPrev", &gate_timeToPrev, "gate_timeToPrev/D", 65536 ); // in s
  gateTree->Branch( "gate_nMinosTracks", &gate_nMinosTracks, "gate_nMinosTracks/I", 32768 );
  gateTree->Branch( "gate_nRocks", &gate_nRocks, "gate_nRocks/I", 32768 );
  gateTree->Branch( "gate_nMatch", &gate_nMatch, "gate_nMatch/I", 32768 );
  gateTree->Branch( "gate_nPOT", &gate_nPOT, "gate_nPOT/D", 65536 );
  gateTree->Branch( "gate_isAnalyzable", &gate_isAnalyzable, "gate_isAnalyzable/I", 32768 );
  gateTree->Branch( "gate_hasMINOS", &gate_hasMINOS, "gate_hasMINOS/I", 32768 );
  gateTree->Branch( "gate_minosGateDeltaT", &gate_minosGateDeltaT, "gate_minosGateDeltaT/D", 65536 );
  gateTree->Branch( "gate_deadTimeFrac", &gate_deadTimeFrac, "gate_deadTimeFrac/D", 65536 );
  gateTree->Branch( "gate_mup_E", &gate_mup_E, "Gate_mup_E[3]/I",32768);
  gateTree->Branch( "gate_mum_E", &gate_mum_E, "Gate_mum_E[3]/I",32768);

  // For header
  bFirstEvent = true;
  total_POT = 0.0;
  total_nMinosTracks = 0;
  begin_time = -1;
  end_time = -1;
  n_gates = 0;

  return GaudiTupleAlg::initialize();
}

//===========================================================================================
//! Finalize
//===========================================================================================
StatusCode RockMuonCalibrationAlg::finalize()
{

  if ( m_writeTimeFile )
  {
    time_t bt = (time_t)((double)begin_time/1E6);
    time_t et = (time_t)((double)end_time/1E6);
    char elapsed[10];
    sprintf(elapsed, "%4.2f", (double)(end_time - begin_time)/(1E6*60));
    ofstream fout;
    fout.open(m_TimeFilename.c_str());
    fout << "# begin   " << begin_time << " " << ctime( &bt );
    fout << "# end     " << end_time << " " << ctime( &et );
    fout << "# elapsed " << elapsed << " min" << std::endl;
    fout.close();
  }

  const char *oldPath = gDirectory->GetPath(); //remember where root's pwd was
  if( !pFile->cd() ) 
    error() << "Could not change current directory to the output file" << endmsg;
  else
  {
    if( !makeHeaderTree() )
      error() << "Creation of \"header\" TTree failed." << endmsg;
    // gate tree too
    gateTree->Write();
    pTree->Write();

    gDirectory->cd( oldPath ); //reset root's pwd
    pFile->Close();
  }

  return GaudiTupleAlg::finalize();
}

//===========================================================================================
//! Destructor
//===========================================================================================
RockMuonCalibrationAlg::~RockMuonCalibrationAlg()
{
}

//===========================================================================================
//! Main algorithm execution, where the magic happens
//===========================================================================================
StatusCode RockMuonCalibrationAlg::execute() 
{

  debug() << "RockMuonCalibrationAlg::execute()" << endmsg;

  // Get event information from DAQ Header; event time is used later for attenuation
  Minerva::DAQHeader const * pDAQHeader = get<Minerva::DAQHeader> (Minerva::DAQHeaderLocation::Default);
  const bool isMC = pDAQHeader->isMCTrigger();
  ev_isMC = isMC;

  gate_nMinosTracks = 0;
  if( exist<Minerva::MinosRecoTracks>(Minerva::MinosRecoTrackLocation::Default) ) {
    Minerva::MinosRecoTracks * minosTracks = get<Minerva::MinosRecoTracks>(Minerva::MinosRecoTrackLocation::Default);
    gate_nMinosTracks = minosTracks->size();
    total_nMinosTracks += gate_nMinosTracks;
  }

  debug() << "Got MINOS tracks and there are " << gate_nMinosTracks << endmsg;

  gate_isAnalyzable = m_gateAnalyzabilityTool->gateIsAnalyzable();
  gate_hasMINOS = m_gateAnalyzabilityTool->MinosDataExists();

  debug() << "Analyzable? " << gate_isAnalyzable << " MINOS gate match? " << gate_hasMINOS << endmsg;

  if( exist<Minerva::DataQuality>( Minerva::DataQualityLocation::Default ) ){
    const Minerva::DataQuality * dataQual = get<Minerva::DataQuality>( Minerva::DataQualityLocation::Default );
    if( gate_hasMINOS ) gate_minosGateDeltaT = dataQual->MinervaMinosTimeDiff();
    else gate_minosGateDeltaT = -9999.0;
  } else {
    error() << "Could not get DataQuality object but let's not crash" << endmsg;
    gate_minosGateDeltaT = -9999.0;
  }

  debug() << "MINOS gate match deltaT = " << gate_minosGateDeltaT << endmsg;

  fillPOT();

  // Count number of rock muons, MINOS-matches for gate
  gate_nRocks = 0;
  gate_nMatch = 0;
  
  for (Int_t i = 0; i < 3; i++) {
    gate_mum_E[i]=0;
    gate_mup_E[i]=0;
  }
  
  if( isMC ) {
    bool truth_worked = fillTruth(); // The code for MC assumes there is 1 GenMinInteraction per gate
    if( !truth_worked ) return StatusCode::SUCCESS;
  }

  ev_run = pDAQHeader->runNumber();
  ev_subrun = pDAQHeader->subRunNumber();
  ev_gate = pDAQHeader->gateNumber();

  gate_run = ev_run;
  gate_subrun = ev_subrun;
  gate_gate = ev_gate;

  gate_timeToPrev = -9999.0;
  double old_time = -9999.0;
  if( !bFirstEvent ) {
    old_time = m_EventTime; // for last gate
  }

  m_EventTime = pDAQHeader->gpsTime();
  gate_gps = m_EventTime / 1.0E6; // convert to seconds

  if( !bFirstEvent ) {
    gate_timeToPrev = (m_EventTime - old_time)/1.0E6; // in seconds
  } else {
    begin_time = m_EventTime;
    bFirstEvent = false;
  }
  end_time = m_EventTime;

  Minerva::TimeSlices * ptsvec = get<Minerva::TimeSlices>( Minerva::TimeSliceLocation::Default );
  Minerva::TimeSlices::const_iterator its;

  gate_nslices = ptsvec->size();

  for( its = ptsvec->begin(); its != ptsvec->end(); ++its ) {
    Minerva::TimeSlice * pts = *its;

    ev_timeslice = pts->sliceNumber();
    if( ev_timeslice == 0 ) continue;

    SmartRefVector<Minerva::Prong> prongVec = pts->select<Minerva::Prong>("All","All");
    ev_ntracks = prongVec.size();
    for( SmartRefVector<Minerva::Prong>::iterator itProng = prongVec.begin(); itProng != prongVec.end(); ++itProng ) {

      SmartRef<Minerva::Prong> prong = *itProng;
      // Prong must have one track
      if( prong->minervaTracks().size() != 1 ) continue;
      SmartRef<Minerva::Track> pTrack = prong->minervaTracks()[0];

      fillMINOS( prong );

      stripToIdx.clear();

      // Use MuonUtils rock muon tool to select rock muons if you are not test beam
      IMuonUtils::RockMuEntryData entry;
      IMuonUtils::RockMuExitData exit;
      ev_muonEnterFront = 0;
      ev_muonExitBack = 0;
      ev_muonEnterSide = 0;
      ev_muonExitSide = 0;
      if ( !m_isTestBeam ) {
        bool rockmu = m_pMuonUtils->isRockMuon( pTrack, entry, exit );
        // Require that muon enter and exit
        if( !rockmu || entry == IMuonUtils::CONTAINED || exit == IMuonUtils::NO_EXIT ) continue;

        // Now we know it enters front or side and exits back or side
        if( entry == IMuonUtils::ENTER_FRONT ) ev_muonEnterFront = 1;
        else ev_muonEnterSide = 1;

        if( exit == IMuonUtils::EXIT_BACK ) ev_muonExitBack = 1;
        else ev_muonExitSide = 1;
      }

      gate_nRocks++;
      
      if( ev_minosMatch == 1 ) {
	gate_nMatch++;
	Int_t* pointer = (ev_muonCharge>0) ? gate_mup_E : gate_mum_E ;
	if (ev_muonE > HEMUONTHRESHOLD) {
	  pointer[0]++;
	} else if (ev_muonE>LEMUONTHRESHOLD){
	  pointer[1]++;
	} else {
	  pointer[2]++;
	}
      }
      
      // Save extra energy to impose cut which gets rid of rock muon + crazy shower slices
      ev_extraEnergy = m_extraEnergy->getExtraIDEnergy( pTrack );

      std::map< Minerva::StripID, double > stripTrueEnergyMap;
      fillTrueEnergyMap( stripTrueEnergyMap );

      fillClusterInfo( stripTrueEnergyMap, pTrack );

      debug() << "Found an acceptable rock muon in run " << ev_run << "/" << ev_subrun << " gate " << ev_gate << " slice " << ev_timeslice << " there are " << ev_ntracks << " tracks" << endmsg;

      ev_trktheta = pTrack->theta();
      ev_trkAx = pTrack->firstState().ax();
      ev_trkAy = pTrack->firstState().ay();
      ev_trk[0] = pTrack->firstState().x();
      ev_trk[1] = pTrack->firstState().y();
      ev_trk[2] = pTrack->firstState().z();
      ev_trk_exit[0] = pTrack->lastState().x();
      ev_trk_exit[1] = pTrack->lastState().y();
      ev_trk_exit[2] = pTrack->lastState().z();
      ev_trk_exitAx = pTrack->lastState().ax();
      ev_trk_exitAy = pTrack->lastState().ay();

      // Fill path length information
      loopOverPlanes( pTrack );

      // Fill energy information
      loopOverDigits( pts, pTrack );

      // Only use front-to-rear rock muons for timing calibration
      if( m_writeHitStuff ) 
        writeHitStuff(pTrack);

      debug() << "Wrote " << n_entries << " entries for this rock muon" << endmsg;

      pTree->Fill();
    } // loop over tracks

  } // loop over time slices

  fillTheMapOfDeath();
  ++n_gates;

  // Fill gate tree every time
  gateTree->Fill();

  return StatusCode::SUCCESS;
}

//===========================================================================================
//! Header tree contains information about the entire subrun
//===========================================================================================
bool RockMuonCalibrationAlg::makeHeaderTree()
{

  headerTree = new TTree( "header", "header" );
  if( headerTree == 0 )
  {
    error() << "Could not instantiate TTree \"header\"" << endmsg;
    return false;
  }

  headerTree->Branch( "begin_gps_time", &begin_time, "begin_gps_time/l", 32768 ); // The lowercase "l" specifies ULong64_t
  headerTree->Branch( "end_gps_time",   &end_time,   "end_gps_time/l",   32768 ); // The lowercase "l" specifies ULong64_t
  headerTree->Branch( "total_POT",      &total_POT,  "total_POT/D",      65536 );
  headerTree->Branch( "total_nMinosTracks", &total_nMinosTracks, "total_nMinosTracks/I", 32768);
  headerTree->Branch( "isTestBeam",     &m_isTestBeam, "isTestBeam/I", 32768);

  headerTree->Branch( "n_strips", &n_strips, "n_strips/I", 32768 );
  headerTree->Branch( "module", module, "module[n_strips]/I", 32768 );
  headerTree->Branch( "plane", plane, "plane[n_strips]/I", 32768 );
  headerTree->Branch( "strip", strip, "strip[n_strips]/I", 32768 );
  headerTree->Branch( "fractionOfDeath", fractionOfDeath, "fractionOfDeath[n_strips]/D", 65536 );

  n_strips = 0;
  std::vector<const Minerva::DePlane*> planes = m_innerDetector->getDePlanes();
  for( std::vector<const Minerva::DePlane*>::iterator itPlane = planes.begin(); itPlane != planes.end(); ++itPlane ) {
    const Minerva::DePlane * pPlane = *itPlane;
    // Loop over strips in current plane, check if track intersects strip
    for( Minerva::DePlane::StripCItr itStrip = pPlane->stripBegin(); itStrip != pPlane->stripEnd(); ++itStrip ) {
      Minerva::StripID sid = itStrip->first;

      module[n_strips] = sid.module();
      plane[n_strips] = sid.plane();
      strip[n_strips] = sid.strip();

      if( totalDeadTime.find(sid) == totalDeadTime.end() ) fractionOfDeath[n_strips] = 0.0; // this seems very unlikely
      else fractionOfDeath[n_strips] = totalDeadTime[sid] / (10000.0*n_gates); // total spill time for the subrun

      ++n_strips;
    }
  }

  std::map<std::string, double> potMap = m_potTool->getPOTSummary();
  total_POT = potMap["POT_Total"];

  headerTree->Fill();
  headerTree->Write();

  return true;

}

//===========================================================================================
//! If strips adjacent to those on the cluster are dead, there may be missing energy
//===========================================================================================
bool RockMuonCalibrationAlg::mightHaveDeadStrips( const Minerva::IDCluster * cluster )
{

  unsigned int high_strip = ( m_isTestBeam ? 63 : 127 );

  unsigned int first_strip = high_strip;
  unsigned int last_strip = 1;
  const SmartRefVector<Minerva::IDDigit> digits = cluster->digits();
  if( !digits.size() ) return false; // no digits = no dead strips
  Minerva::StripID fid = digits.front()->stripid();
  Minerva::PlaneID pid( fid.detector(), fid.subdet(), fid.module(), fid.plane() );
  for( SmartRefVector<Minerva::IDDigit>::const_iterator itDig = digits.begin(); itDig != digits.end(); ++itDig ) {
    if( (*itDig)->strip() < first_strip ) first_strip = (*itDig)->strip();
    if( (*itDig)->strip() > last_strip ) last_strip = (*itDig)->strip();
  }

  // Look one strip to each side of the cluster  
  if( first_strip > 1 ) --first_strip;
  if( last_strip < high_strip ) ++last_strip;

  for( unsigned int str = first_strip; str <= last_strip; ++str ) {
    Minerva::StripID sid(pid, str);
    if( m_getStripResponse->isDead(sid,m_EventTime) ) return true; // if one is dead then stop
  }
  return false; // if we haven't returned yet

}

//===========================================================================================
//! Hit variables are used for timing calibration
//===========================================================================================
void RockMuonCalibrationAlg::writeHitStuff( Minerva::Track * track )
{


  bool isForward = true;

  if ( m_isTestBeam ) {

    Minerva::DAQHeader* daqHeader = get<Minerva::DAQHeader>( Minerva::DAQHeaderLocation::Default );
    if ( !daqHeader ) throw MinervaException("DAQHeader not in data!");
    if ( daqHeader->triggerType() == Minerva::DAQHeader::Cosmic && track->firstState().ax() < 0 ) {
      isForward = false;
    }
  }

  // the assumption here is that the track's nodes are z-sorted upstream to downstream
  Gaudi::XYZPoint ref_p = track->firstState().position();
  double tof = 0.0;

  n_hits = 0;

  Minerva::Track::NodeContainer::const_iterator itNode = track->nodes().begin();
  for (; itNode != track->nodes().end() && n_hits < MAXENTRIES; ++itNode ) {

    Gaudi::XYZPoint p = (*itNode)->position();
    Gaudi::XYZVector v = p - ref_p;
    if( isForward ) tof += v.R() / MinervaUnits::c_light;
    else tof -= v.R() / MinervaUnits::c_light;
    ref_p = p; // save for next node

    if( !(*itNode)->hasCluster() ) {
      counter( "ClusterlessNodes" )++;
      continue;
    }

    SmartRefVector<Minerva::IDDigit> idDigits = (*itNode)->idcluster()->digits();
    SmartRefVector<Minerva::IDDigit>::iterator idDigit;
    for ( idDigit = idDigits.begin(); idDigit != idDigits.end() && n_hits < MAXENTRIES; idDigit++) {

      if ( !(*idDigit)->discrFired() ) continue;

      Minerva::StripID   sid = (*idDigit)->stripid();
      Minerva::ChannelID cid = m_plexModel->getChannelID( sid );

      const Minerva::DePlane* dePlane = m_innerDetector->getDePlane(sid);
      if (!dePlane) continue;

      double digit_pe = (*idDigit)->pe();

      hit_crate[n_hits] = cid.crate();
      hit_croc[n_hits]  = cid.croc();
      hit_chain[n_hits] = cid.chain();
      hit_board[n_hits] = cid.board();
      hit_pixel[n_hits] = cid.pixel();

      hit_pe[n_hits]  = digit_pe;
      hit_rt[n_hits]  = (*idDigit)->rawTime();
      hit_ct[n_hits]  = (*idDigit)->calTime();
      hit_tof[n_hits] = tof;
      hit_dtc[n_hits] = dePlane->distanceToConnector( p, sid );
      hit_dtm[n_hits] = dePlane->distanceToMirror( p, sid );
      hit_shl[n_hits] = dePlane->getStripHalfLength( sid );
      hit_bfl[n_hits] = m_baggieAttTool->getWLSFiberLength( sid );
      hit_cfl[n_hits] = m_clearFiberAttTool->getClearFiberLength( sid );

      n_hits++;

      if( n_hits == MAXENTRIES ) break;

    } // idDigit
  } // itNode

  if( n_hits == MAXENTRIES ) {
    warning() << "entries overflow" << endmsg;
    ++counter( "OVERFLOW" );
  }

}

//===========================================================================================
//! Truth stuff for MEU tuning
//===========================================================================================
bool RockMuonCalibrationAlg::fillTruth()
{

  ev_muonTruePDG = 0;
  ev_muonTrueVtx[0] = -9999.0; ev_muonTrueVtx[1] = -9999.0; ev_muonTrueVtx[2] = -9999.0;
  ev_muonTrueP[0] = -9999.0; ev_muonTrueP[1] = -9999.0; ev_muonTrueP[2] = -9999.0;
  ev_muonTrueE = -9999.0;

  Minerva::GenMinInteractions* interactions = get<Minerva::GenMinInteractions>( m_genMinInteractionLocation );
  if( interactions->size() != 1 ){
    error() << "Found " << interactions->size() << " GenMinInteractions in the gate.  One GenMinInteraction per gate required" << endmsg;
    return false;
  }
  Minerva::GenMinInteraction* interaction = *interactions->begin();
  if ( interaction->nParticlesFS() != 1 ) {
    error() << "Found " << interaction->nParticlesFS() << " final state particles in the gate.  One final state per gate required" << endmsg;
    return false;
  }
  ev_muonTruePDG = interaction->fSpdg().front();
  ev_muonTrueP[0] = interaction->fsParticlesPx().front();
  ev_muonTrueP[1] = interaction->fsParticlesPy().front();
  ev_muonTrueP[2] = interaction->fsParticlesPz().front();
  ev_muonTrueE = interaction->fsParticlesE().front();
  ev_muonTrueVtx[0] = interaction->Vtx().X();
  ev_muonTrueVtx[1] = interaction->Vtx().Y();
  ev_muonTrueVtx[2] = interaction->Vtx().Z();

  return true;
}

//===========================================================================================
//! Truth stuff for MEU tuning
//===========================================================================================
void RockMuonCalibrationAlg::fillPOT()
{

  // Get POT map before adding current gate
  std::map<std::string, double> potMap = m_potTool->getPOTSummary();
  double old_POT = potMap["POT_Total"];

  m_potTool->addPOT("Total");

  potMap = m_potTool->getPOTSummary();
  double new_POT = potMap["POT_Total"];

  // Subtract old from new to get this gate's POT
  gate_nPOT = new_POT - old_POT;
}


//===========================================================================================
//! MINOS information
//===========================================================================================
void RockMuonCalibrationAlg::fillMINOS( SmartRef<Minerva::Prong> prong )
{

  // initialize event variables
  ev_minosMatch = 0;
  ev_minosP = -1.0;
  ev_minosPrange = -1.0;
  ev_minosPcurve = -1.0;
  ev_muonCharge = 0;
  ev_muonVtx[0] = -9999.0; ev_muonVtx[1] = -9999.0; ev_muonVtx[2] = -9999.0;
  ev_minosVtx[0] = -9999.0; ev_minosVtx[1] = -9999.0; ev_minosVtx[2] = -9999.0;
  ev_muonP[0] = -9999.0; ev_muonP[1] = -9999.0; ev_muonP[2] = -9999.0;
  ev_muonE = -9999.0;
  ev_minosMatchDeltaT = -9999.0;
  ev_minosTrackChi2 = -1.0;
  ev_minosTrackNDF = -1.0;
  ev_minosTrackQuality = -1;
  ev_minosTrackPassFit = -1;
  ev_minosRecoByRange = -1;
  ev_minosRecoByCurvature = -1;
  ev_minosTrackQP = -9999.0;
  ev_minosTrackSigmaQP = -9999.0;

  if( m_isTestBeam ) return;

  Minerva::Track * track = prong->minervaTracks()[0];

  // MinosOK must be set and not 0
  int minosOK = 1;
  if( ! prong->getIntData(ProngExtraDataDefs::MinosOK(), minosOK) ) return;
  if( minosOK == 0 ) return;

  if( !m_pMuonUtils->isRockMuon( track ) ) return;

  SmartRef<Minerva::Particle> muon;
  if( !m_pMuonUtils->findMuonParticle(prong, muon) ) return;

  if( ! (muon->methodSignature() == "MuonEnergyRec") ) return;

  if( !m_allowMinosStub && prong->MinosStub() ) return;

  if( !prong->hasDoubleData(ProngExtraDataDefs::MinosMomentum()) ) return;

  // MinosMomentum is common to tracks and stubs
  ev_minosP = prong->getDoubleData(ProngExtraDataDefs::MinosMomentum());
  ev_minosMatch = 1;

  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackPRange()) )
    ev_minosPrange = prong->getDoubleData( ProngExtraDataDefs::MinosTrackPRange() );
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackPCurvature()) )
    ev_minosPcurve = prong->getDoubleData( ProngExtraDataDefs::MinosTrackPCurvature() );

  // fill deltaT
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosMatchTimeMinos()) &&
      prong->hasDoubleData(ProngExtraDataDefs::MinosMatchTimeMinerva()) )
    ev_minosMatchDeltaT = prong->getDoubleData( ProngExtraDataDefs::MinosMatchTimeMinos() ) -
                          prong->getDoubleData( ProngExtraDataDefs::MinosMatchTimeMinerva() );

  // fill MINOS vertex
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackVtxX()) )
    ev_minosVtx[0] = prong->getDoubleData( ProngExtraDataDefs::MinosTrackVtxX() );
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackVtxY()) )
    ev_minosVtx[1] = prong->getDoubleData( ProngExtraDataDefs::MinosTrackVtxY() );
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackVtxZ()) )
    ev_minosVtx[2] = prong->getDoubleData( ProngExtraDataDefs::MinosTrackVtxZ() );

  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackChi2()) )
    ev_minosTrackChi2 = prong->getDoubleData( ProngExtraDataDefs::MinosTrackChi2() );
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackNDF()) )
    ev_minosTrackNDF = prong->getDoubleData( ProngExtraDataDefs::MinosTrackNDF() );

  // 0 = unknown, 1 = gold, 2 = silver, 3 = bronze
  if( prong->hasIntData(ProngExtraDataDefs::MinosTrackQuality()) )
    ev_minosTrackQuality = prong->getIntData( ProngExtraDataDefs::MinosTrackQuality() );
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackFitPass()) )
    ev_minosTrackPassFit = prong->getDoubleData( ProngExtraDataDefs::MinosTrackFitPass() );

  if( prong->hasIntData(ProngExtraDataDefs::MinosRecoByRange()) )
    ev_minosRecoByRange = prong->getIntData( ProngExtraDataDefs::MinosRecoByRange() );
  if( prong->hasIntData(ProngExtraDataDefs::MinosRecoByCurvature()) )
    ev_minosRecoByCurvature = prong->getIntData( ProngExtraDataDefs::MinosRecoByCurvature() );

  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackQP()) )
    ev_minosTrackQP = prong->getDoubleData( ProngExtraDataDefs::MinosTrackQP() );
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackSigmaQP()) )
    ev_minosTrackSigmaQP = prong->getDoubleData( ProngExtraDataDefs::MinosTrackSigmaQP() );

  int charge = 0;
  m_pMuonUtils->muonCharge( prong, charge );

  ev_muonCharge = charge;
  const Gaudi::XYZTVector position = muon->startPos();
  ev_muonVtx[0] = position.X();
  ev_muonVtx[1] = position.Y();
  ev_muonVtx[2] = position.Z();

  const Gaudi::XYZTVector momentum = muon->momentumVec();
  ev_muonP[0] = momentum.Px();
  ev_muonP[1] = momentum.Py();
  ev_muonP[2] = momentum.Pz();
  ev_muonE = momentum.E();

}

//===========================================================================================
//! True energy info
//===========================================================================================
void RockMuonCalibrationAlg::fillTrueEnergyMap( std::map< Minerva::StripID, double > &stripTrueEnergyMap )
{
  // The following assumes there is 1 GenMinInteraction per gate
  // If there is to be more than one GenMinInteraction per gate, then updates need to be made to
  // match GenMinInteraction to TimeSlices and MCHits to GenMinInteractions

  // Find the Geant energy deposited in each strip.
  // IMPORTANT: For the MEU tuning, do not retrieve MCHits from IDDigits/MCIDDigits since they only contain MCHits that produced 1 or more photoelectrons at the photocathode.
  // @todo Should get MCHits from a GenMinInteraction
  Minerva::MCHits* idMCHits = getOrCreate<Minerva::MCHits,Minerva::MCHits>( evtSvc(), m_mcIDHitsLocation );
  for( Minerva::MCHits::const_iterator itHit = idMCHits->begin(); itHit != idMCHits->end(); ++itHit ) {

    Minerva::MCHit* hit = *itHit;
    if ( hit->energy() <= 0.0 ) continue; // historical: energy of x-talk hits set to default negative value

    Gaudi::XYZPoint hitCenter( ( hit->StartX() + hit->StopX() ) / 2.0, ( hit->StartY() + hit->StopY() ) / 2.0, ( hit->StartZ() + hit->StopZ() ) / 2.0  );
    if( !m_innerDetector->isInside( hitCenter ) ) continue;
    StripID stripid = m_innerDetector->getStripID( hitCenter );
    if ( !stripid ) continue;

    if ( stripTrueEnergyMap.find( stripid ) == stripTrueEnergyMap.end() ) stripTrueEnergyMap[ stripid ] = 0.0;
    stripTrueEnergyMap[ stripid ] += hit->energy();

  }
}


//===========================================================================================
//! Cluster information
//===========================================================================================
void RockMuonCalibrationAlg::fillClusterInfo( std::map< Minerva::StripID, double > stripTrueEnergyMap, SmartRef<Minerva::Track> pTrack )
{
  // MEU and LY factors used for this event
  ev_LY = 0.0;
  ev_MEU = 0.0;

  // Fill cluster information
  const std::vector<Minerva::Node*>& nodes = pTrack->nodes();
  n_clusters = 0;
  for( std::vector<Minerva::Node*>::const_iterator itNode = nodes.begin(); itNode != nodes.end(); ++itNode ) {

    if ( !(*itNode)->hasCluster() ) continue;
    const Minerva::IDCluster* idcluster = (*itNode)->idcluster();

    cl_subdet[n_clusters]    = idcluster->subdet();
    cl_module[n_clusters]    = idcluster->planeid().module();
    cl_plane[n_clusters]     = idcluster->planeid().plane();
    cl_tpos[n_clusters]      = idcluster->position();
    cl_lpos[n_clusters]      = idcluster->lpos();
    cl_pe[n_clusters]        = idcluster->pe();
    cl_recoE[n_clusters]     = idcluster->energy();
    cl_time[n_clusters]      = idcluster->time();
    cl_nstrips[n_clusters]   = idcluster->iddigs();
    cl_type[n_clusters]      = idcluster->type();
    cl_stateAx[n_clusters]   = (*itNode)->state().ax();
    cl_stateAy[n_clusters]   = (*itNode)->state().ay();
    cl_cosThetaZ[n_clusters] = 1.0 / sqrt( 1.0 + pow( (*itNode)->state().ax(), 2 ) + pow( (*itNode)->state().ay(), 2 ) );
    cl_mightBeDead[n_clusters] = mightHaveDeadStrips(idcluster);

    cl_q[n_clusters] = 0.0;
    SmartRefVector<Minerva::IDDigit> digits = idcluster->digits();
    for ( SmartRefVector<Minerva::IDDigit>::iterator d = digits.begin(); d != digits.end(); ++d ) {
      cl_q[n_clusters] += (*d)->q();
    }

    // Get the total active path length in the cluster's plane
    double activePathLength = 0.0;

    Gaudi::XYZPoint nodePos = (*itNode)->trackPoint();
    Gaudi::XYZVector nodeVec = (*itNode)->trackVec().Unit();
    const Minerva::DePlane* dePlane = m_innerDetector->getDePlane( (*itNode)->idcluster()->planeid() );
    dePlane->RayToLocal( nodePos, nodeVec );

    const ILVolume* lvol = dePlane->geometry()->lvolume();
    ILVolume::Intersections intersections;
    lvol->intersectLine( nodePos, nodeVec, intersections, 0.0 );
    std::vector<ILVolume::Intersection>::iterator itIntersect;
    for( itIntersect = intersections.begin(); itIntersect != intersections.end(); ++itIntersect ) {
      const Material* material = itIntersect->second;
      if ( material->name() == "PlasticScint" )
      {
        ILVolume::Interval interval = itIntersect->first;
        activePathLength += interval.second - interval.first;
      }
    }

    cl_activePathLength[n_clusters] = activePathLength;

    if( ev_isMC ) {
      double trueClusterEnergy = 0.0;
      SmartRefVector<Minerva::IDDigit> clusterDigits = idcluster->digits();
      SmartRefVector<Minerva::IDDigit>::iterator itClusterDigit;
      for ( itClusterDigit = clusterDigits.begin(); itClusterDigit != clusterDigits.end(); ++itClusterDigit ) {
        if ( stripTrueEnergyMap.find( (*itClusterDigit)->stripid() ) == stripTrueEnergyMap.end() ) continue;
        trueClusterEnergy += stripTrueEnergyMap[ (*itClusterDigit)->stripid() ];
        if( (*itClusterDigit)->hasDoubleData(MCDigitExtraDataDefs::AppliedLightYieldFactor()) ) {
          double lyfact = (*itClusterDigit)->getDoubleData( MCDigitExtraDataDefs::AppliedLightYieldFactor() );
          if( ev_LY == 0.0 ) ev_LY = lyfact;
          else if( ev_LY != lyfact ) warning() << "LY change! Was " << ev_LY << " now " << lyfact << endmsg;
        } else {
          warning() << "MCDigit does not have light yield factor extra data!" << endmsg;
        }
      }
      cl_trueE[n_clusters] = trueClusterEnergy;
    }
    else cl_trueE[n_clusters] = -9999.0;

    ++n_clusters;
    if( n_clusters == MAXCLUSTERS ) { // I don't know how this can happen, but just in case
      warning() << "Encountered more than " << n_clusters << " clusters in this track" << endmsg;
      counter("TooManyClusters")++;
      break; 
    }
  }
}

//===========================================================================================
//! Path length information by looping over planes and strips
//===========================================================================================
void RockMuonCalibrationAlg::loopOverPlanes( SmartRef<Minerva::Track> pTrack )
{
  // Loop over planes, require that plane is within z-extent of track.
  // Loop over strips in each plane and check for path length from track
  float upos = pTrack->upstreamNode()->module() + 0.5*(pTrack->upstreamNode()->plane() - 1);
  float dpos = pTrack->downstreamNode()->module() + 0.5*(pTrack->downstreamNode()->plane() - 1);

  std::vector<const Minerva::DePlane*> planes = m_innerDetector->getDePlanes();
  std::vector<const Minerva::DeODFrame*> frames = m_outerDetector->getDeODFrames();
  n_entries = 0; // index of the entry within this rock muon
  for( std::vector<const Minerva::DePlane*>::iterator itPlane = planes.begin(); itPlane != planes.end(); ++itPlane ) {
    const Minerva::DePlane * pPlane = *itPlane;
    Minerva::PlaneID pid = pPlane->getPlaneID();

    if( upos > pid.module()+0.5*(pid.plane()-1) || dpos < pid.module()+0.5*(pid.plane()-1) ) continue;

    // Get track position and direction from nearest state to current plane
    double zCenter = pPlane->getZCenter();
    Gaudi::XYZPoint x = pTrack->nearestState( zCenter ).position();
    Gaudi::XYZVector u = pTrack->nearestState( zCenter ).slopes().Unit();
    pPlane->RayToLocal(x, u);

    plot(zCenter-(pTrack->nearestState( zCenter ).z()),"nearest_state",-50.0,50.0,100);

    // Loop over strips in current plane, check if track intersects strip
    for( Minerva::DePlane::StripCItr itStrip = pPlane->stripBegin(); itStrip != pPlane->stripEnd(); ++itStrip ) {
      Minerva::StripID sid = itStrip->first;
      IPVolume const * pPV = itStrip->second;

      ISolid const * pSolid = pPV->lvolume()->solid();

      ISolid::Ticks ticks;
      Gaudi::XYZPoint xL = pPV->toLocal(x);
      Gaudi::XYZVector uL = pPV->toLocal(x+u) - xL;

      int i = pSolid->intersectionTicks(xL, uL, ticks);
      if( i == 2 ) {
        // Fill path length and base position, the point along the strip triangle base where the track crosses
        st_path[n_entries] = fabs(ticks[1] - ticks[0]);
        double entry_x = (x + ticks[0] * u).x();
        double exit_x = (x + ticks[1] * u).x();
        double base_x = -9999.0;
        if( m_isTestBeam ) { // Test beam strips point in funny directions due to plane flips
          if( !pPlane->doesStripPointUpstream(sid) ) base_x = entry_x; 
          else base_x = exit_x;
        } else {
          if( sid.strip() % 2 == 0 ) base_x = entry_x;
          else base_x = exit_x;
        }
        double tpos = pPlane->getTPos( sid );
        st_base[n_entries] = base_x - tpos;
        st_mev[n_entries] = 0.0; // This will be updated later if there is a digit on this strip
        st_s2s[n_entries] = -1.0; // Applied s2s constant will be update if there is a digit
        st_module[n_entries] = sid.module();
        st_plane[n_entries] = sid.plane();
        st_strip[n_entries] = sid.strip();
        stripToIdx[sid] = n_entries;

        debug() << "Entry " << n_entries << ": " << sid.module() << "/" << sid.plane() << "/" << sid.strip() << " has path " << st_path[n_entries] << endmsg;

        // Save rack number, which is useful for plex debugging
        Minerva::ChannelID chid = m_plexModel->getChannelID( sid );
        int module_set_number = m_plexModel->getMSNumber( chid );
        st_rack[n_entries] = module_set_number;
        st_crate[n_entries] = chid.crate();
        st_croc[n_entries] = chid.croc();
        st_chain[n_entries] = chid.chain();
        st_board[n_entries] = chid.board();
        st_pixel[n_entries] = chid.pixel();

        Minerva::DePlane::View_t view_t = pPlane->getView();
        if (view_t == Minerva::DePlane::X) st_view[n_entries] = 1;
        else if (view_t == Minerva::DePlane::U) st_view[n_entries] = 2;
        else if (view_t == Minerva::DePlane::V) st_view[n_entries] = 3;
        else st_view[n_entries] = 0;

         ++n_entries;
      } // if i == 2
    } // loop over strips
  } // loop over planes for path information
}


//===========================================================================================
//! Path length information by looping over outer detector elements
//! In progress: currently does nothing
//===========================================================================================
void RockMuonCalibrationAlg::loopOverODFrames( SmartRef<Minerva::Track> pTrack )
{

  // IN PROGRESS: OD calibration
  debug() << "OD calibration does not currently work" << pTrack << endmsg;
/*

  // Loop over bars for OD path information
  for( std::vector<const Minerva::DeODFrame*>::iterator itFrame = frames.begin(); itFrame != frames.end(); ++itFrame ) {
    const Minerva::DeODFrame * frame = *itFrame;
    Minerva::FrameID fid = frame->getFrameID();

    // Only look if you are upstream of a side-entering track or downstream of a side-exiting track
    if( ! ((ev_muonEnterSide && fid.frame() < upos) || (ev_muonExitSide && fid.frame() > dpos - 1.0)) ) continue;

    // Get position and slope of nearest state to frame z center -- the upstream or downstream edge
    double zCenter = frame->getZCenter();
    Gaudi::XYZPoint x = pTrack->nearestState( zCenter ).position();
    Gaudi::XYZVector u = pTrack->nearestState( zCenter ).slopes().Unit();

    // Project to frame Z center -- not necessary for strips because the nearest state is in that plane
    double zdiff = zCenter - x.z();
    double yy = x.y() + u.y()*zdiff;
    double xx = x.x() + u.x()*zdiff;
    x.SetXYZ( xx, yy, zCenter );

    frame->RayToLocal(x, u); // does alignment corrections if there are any

    // now get the bars
    for( Minerva::DeODFrame::ODBarCItr itBar = frame->barBegin(); itBar != frame->barEnd(); ++itBar ) {
      Minerva::BarID bid = itBar->first;
      IPVolume const * pPV = itBar->second;
      ISolid const * pSolid = pPV->lvolume()->solid();

      ISolid::Ticks ticks;
      Gaudi::XYZPoint xL = pPV->toLocal(x);
      Gaudi::XYZVector uL = pPV->toLocal(x+u) - xL;

      Gaudi::XYZPoint bp = frame->getBarPos(bid);

      double dist = (bp - x).R();

      char out[1000];
      sprintf( out, "%3d/%d/%d/%d, x = (%7.1f, %7.1f, %2.1f) bar = (%7.1f, %7.1f, %6.1f) R = %2.1f",
          bid.frame(), bid.tower(), bid.story(), bid.bar(), 
          xL.x(), xL.y(), xL.z(), bp.x(), bp.y(), bp.z(), dist );

      info() << out << endmsg;

      int i = pSolid->intersectionTicks(xL, uL, ticks);
      if (i == 2) {
        info() << "The track went though a bar! Frame " << bid.frame() << " Tower " << bid.tower() << " Story " << bid.story() << " Bar " << bid.bar() << endmsg;
      } // if i == 2
      else if( i != 0 ) warning() << "!!!!!!!!!!!!!!!!!! i = " << i << endmsg;
    } // loop over bars
  } // OD frames
*/
}

//===========================================================================================
//! FILL THE MAP OF DEATH
//===========================================================================================
void RockMuonCalibrationAlg::fillTheMapOfDeath()
{
  theMapOfDeath.clear();
  
  Minerva::IDDigits* digits = get<Minerva::IDDigits>( Minerva::IDDigitLocation::Default );
  for( Minerva::IDDigits::iterator itDig = digits->begin(); itDig != digits->end(); ++itDig ) {
    if( (*itDig)->rawTime() > 10000.0 ) continue; // only count for the actual beam spill
    Minerva::ChannelID cid( (*itDig)->key() );
    Minerva::DiscrPairID pairID = m_plexModel->getDiscrPair( cid );
    if( theMapOfDeath.find(pairID) == theMapOfDeath.end() ) theMapOfDeath[pairID] = cid.hit(); // first hit on this pair in gate
    else {
      unsigned int maxHit = theMapOfDeath[pairID];
      if( cid.hit() > maxHit ) theMapOfDeath[pairID] = cid.hit();
    }
  }

  // now figure out the total dead time in each strip
  gate_deadTimeFrac = 0.0;
  int num_strips = 0;
  std::vector<const Minerva::DePlane*> planes = m_innerDetector->getDePlanes();
  for( std::vector<const Minerva::DePlane*>::iterator itPlane = planes.begin(); itPlane != planes.end(); ++itPlane ) {
    const Minerva::DePlane * pPlane = *itPlane;
    // Loop over strips in current plane, check if track intersects strip
    for( Minerva::DePlane::StripCItr itStrip = pPlane->stripBegin(); itStrip != pPlane->stripEnd(); ++itStrip ) {
      Minerva::StripID sid = itStrip->first;
      Minerva::DiscrPairID pairID = m_plexModel->getDiscrPair( sid );
      ++num_strips;

      double dead_time_so_far = 0.0;
      if( totalDeadTime.find(sid) != totalDeadTime.end() ) dead_time_so_far = totalDeadTime[sid];

      // how much to add?
      if( theMapOfDeath.find(pairID) != theMapOfDeath.end() ) { // there was dead time on this strip for this gate, add it
        double thisGateDeadTime = ((1+theMapOfDeath[pairID]) * 16.0 * Minerva::kClockTick);
        totalDeadTime[sid] = dead_time_so_far + thisGateDeadTime;
        gate_deadTimeFrac += thisGateDeadTime;
      }
    }
  }
  debug() << "Total dead time " << gate_deadTimeFrac << endmsg;
  gate_deadTimeFrac /= (10000.0*num_strips); // maximum possible dead time would be every strip is dead the whole 10 microseconds

}

//===========================================================================================
//! Write every digit in the slice
//===========================================================================================
void RockMuonCalibrationAlg::loopOverDigits( Minerva::TimeSlice * pts, SmartRef<Minerva::Track> pTrack )
{
  // Fill the nTuple entry for each digit in the slice regardless of whether there was path length.
  // For plex debugging, it is necessary to know where the energy ended up
  const SmartRefVector<Minerva::IDDigit> & digVec = pts->select<Minerva::IDDigit>("Used:Unused","All");
  for( SmartRefVector<Minerva::IDDigit>::const_iterator itDig = digVec.begin(); itDig != digVec.end(); ++itDig ) {
    Minerva::IDDigit const * pDigit = *itDig;
    Minerva::StripID sid = pDigit->stripid();

    Minerva::ChannelID cid = m_plexModel->getChannelID( sid );

    if( pDigit->hasDoubleData(DigitExtraDataDefs::AppliedMEUConstant()) ) {
      double meufact = pDigit->getDoubleData( DigitExtraDataDefs::AppliedMEUConstant() );
      if( ev_MEU == 0.0 ) ev_MEU = meufact;
      else if( meufact != ev_MEU ) warning() << "MEU factor change! Was " << ev_MEU << " now " << meufact << endmsg;
    } else {
      warning() << "Digit doesn't have MEU factor extra data!" << endmsg;
    }

    Minerva::PlaneID pid( sid.detector(), sid.subdet(), sid.module(), sid.plane() );
    const Minerva::DePlane * pPlane = m_innerDetector->getDePlane( pid );

    // Correct for attenuation to track point--AttenuationAlg corrects cluster energies but not digit energies.
    // This step matters a lot for digits that are part of the track node, and there it should always be right.
    // If there is no node in the plane, skip the attenuation--this will happen when there are plex errors, and
    // we don't need the energy information to be as precise
    double zCenter = pPlane->getZCenter();
    Minerva::Node * pNode = pTrack->nearestNode( zCenter );

    double lpos = -9999.0;

    double att_track = 1.0;
    if( pNode->module() != (int)sid.module() || pNode->plane() != (int)sid.plane() ) {
      debug() << "No node at module " << sid.module() << " plane " << sid.plane() << "! Digits will be attenuated to strip center only!" << endmsg;
    } else {
      double halfstrip  = pPlane->getStripHalfLength( sid );
      double dconnector = pPlane->distanceToConnector( pNode->trackPoint(), sid );
      double distance   = halfstrip - dconnector;

      lpos = pPlane->getLPos(pNode->trackPoint());

      verbose() << "   strip half length : " << halfstrip << " mm" << endmsg;
      verbose() << "   distance to readout end : " << dconnector << " mm" << endmsg;
      verbose() << "   attenuation distance : " << distance << " mm" << endmsg;

      StatusCode sc;
      m_getCalAttenuation->calibrate_from_center(sid, m_EventTime, distance, att_track);
      if (sc.isFailure()) {
        warning() << "attenuation status is failure" << endmsg;
        ++counter("ATTFAIL");
      }
    }

    // Check the map to see if there is already an entry for this strip (i.e. it has path length)
    if( stripToIdx.find( sid ) != stripToIdx.end() ) {
      int update_entry = stripToIdx[sid];
      st_mev[update_entry] = pDigit->normEnergy() * att_track;
      st_lpos[update_entry] = lpos;
      if( pDigit->hasDoubleData(DigitExtraDataDefs::AppliedS2SConstant()) ) {
        st_s2s[update_entry] = pDigit->getDoubleData(DigitExtraDataDefs::AppliedS2SConstant());
      }

      st_q[update_entry] = pDigit->q();
      st_pe[update_entry] = pDigit->pe();

      debug() << "Matched entry " << update_entry << ": " << sid.module() << "/" << sid.plane() << "/" << sid.strip() << " energy = " << st_mev[update_entry] << " path = " << st_path[update_entry] << endmsg;

    } else {
      st_crate[n_entries] = cid.crate();
      st_croc[n_entries] = cid.croc();
      st_chain[n_entries] = cid.chain();
      st_board[n_entries] = cid.board();
      st_pixel[n_entries] = cid.pixel();

      st_q[n_entries] = pDigit->q();
      st_pe[n_entries] = pDigit->pe();

      // If there was no path length, there is not yet an entry for this strip
      st_mev[n_entries] = pDigit->normEnergy() * att_track;
      if( pDigit->hasDoubleData(DigitExtraDataDefs::AppliedS2SConstant()) ) {
        st_s2s[n_entries] = pDigit->getDoubleData(DigitExtraDataDefs::AppliedS2SConstant());
      }
      st_path[n_entries] = 0.0;
      st_base[n_entries] = -99.0; // base goes from -17 to +17 so fill an absurd value if there is no reconstructed track
      st_module[n_entries] = sid.module();
      st_plane[n_entries] = sid.plane();
      st_strip[n_entries] = sid.strip();
      st_lpos[n_entries] = lpos;

      Minerva::ChannelID chid = m_plexModel->getChannelID( sid );
      int module_set_number = m_plexModel->getMSNumber( chid );
      st_rack[n_entries] = module_set_number;

      Minerva::DePlane::View_t view_t = pPlane->getView();
      if (view_t == Minerva::DePlane::X) st_view[n_entries] = 1;
      else if (view_t == Minerva::DePlane::U) st_view[n_entries] = 2;
      else if (view_t == Minerva::DePlane::V) st_view[n_entries] = 3;
      else st_view[n_entries] = 0;

      debug() << "New entry " << n_entries << ": " << sid.module() << "/" << sid.plane() << "/" << sid.strip() << " energy = " << st_mev[n_entries] << " path = 0.0" << endmsg;

      ++n_entries;
      if( n_entries == MAXENTRIES ) break;

    }
  } // loop over digits in time slice

  // Quit if you reach the size limit for each entry to avoid a segfault
  if( n_entries == MAXENTRIES ) {
    debug() << "Encountered event with more than " << n_entries << " entries, probably not a rock muon." << endmsg;
    ++counter("OverMaxEntries");
  }
}

