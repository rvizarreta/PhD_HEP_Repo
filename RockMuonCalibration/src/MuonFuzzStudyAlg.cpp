#include "MuonFuzzStudyAlg.h"

#include "GaudiKernel/DeclareFactoryEntries.h"
#include "MinervaDet/IGeomUtilSvc.h"
#include "MinervaDet/DePlane.h"
#include "MinervaDet/DeDetector.h"
#include "DetDesc/Material.h"

#include "Event/Track.h"
#include "Event/TimeSlice.h"
#include "Event/DAQHeader.h"
#include "Event/Prong.h"
#include "Kernel/PlaneID.h"
#include "Kernel/StripID.h"
#include "Kernel/ChannelID.h"
#include "Event/GenMinInteraction.h"
#include "Event/MCHit.h"

#include "RecUtils/ProngExtraDataDefs.h"
#include "RecUtils/DigitExtraDataDefs.h"
#include "RecUtils/MCDigitExtraDataDefs.h"
#include "RecUtils/ClusterExtraDataDefs.h"

#include "RecInterfaces/IRecoObjectTimeTool.h"
#include "AnaUtils/IMuonUtils.h"
#include "MinervaUtils/IMinervaMathTool.h"
#include "TFile.h"
#include "TTree.h"


DECLARE_ALGORITHM_FACTORY(MuonFuzzStudyAlg);

//===========================================================================================
//! Constructor, initialize variables from options file
//===========================================================================================
MuonFuzzStudyAlg::MuonFuzzStudyAlg(std::string const & name, ISvcLocator * pSvcLocator)
  : GaudiTupleAlg(name, pSvcLocator)
{
  declareProperty( "OutputFilename",    m_OutputFilename     = "nt.root"      );

  declareProperty( "MuonSpeed",         m_muonSpeed          = 300.0          ); // mm / ns

  declareProperty( "MCHitsLocation",    m_mcIDHitsLocation   = "MC/ID/Hits"   );
  declareProperty( "GenMinInteractionLocation", m_genMinInteractionLocation = Minerva::GenMinInteractionLocation::Default );
}

//===========================================================================================
//! Initialize routine, get tools, declare nTuple output variables
//===========================================================================================
StatusCode MuonFuzzStudyAlg::initialize()
{

  debug() << "MuonFuzzStudyAlg::initialze()" << endmsg;

  IGeomUtilSvc *geomUtilSvc;
  service("GeomUtilSvc", geomUtilSvc, true);
  m_innerDetector = geomUtilSvc->getIDDet();

  if( !m_innerDetector ) {
    error() << "Could not retrieve inner detector!" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_muonUtils = tool<IMuonUtils>("MuonUtils");
  } catch( GaudiException& e ) {
    error() << "Could not get MuonUtils tool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_recoObjectTimeTool = tool<IRecoObjectTimeTool>("RecoObjectTimeTool");
  } catch( GaudiException& e ) {
    error() << "Could not get RecoObjectTimeTool" << endmsg;
    return StatusCode::FAILURE;
  }

  try {
    m_mathTool = tool<IMinervaMathTool>("MinervaMathTool");
  } catch( GaudiException& e ) {
    error() << "Could not get MinervaMathTool" << endmsg;
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
  pTree->Branch("ev_gps_time", &m_EventTime, "ev_gps_time/l", 32768 ); // The lowercase "l" specifies ULong64_t

  // Minerva track variables -- filled once per event, every event
  pTree->Branch("ev_timeslice", &ev_timeslice, "ev_timeslice/I", 32768);
  pTree->Branch("ev_trktheta", &ev_trktheta, "ev_trktheta/D", 65536);
  pTree->Branch("ev_trkAx", &ev_trkAx, "ev_trkAx/D", 65536);
  pTree->Branch("ev_trkAy", &ev_trkAy, "ev_trkAy/D", 65536);
  pTree->Branch("ev_trk_exit", &ev_trk_exit, "ev_trk_exit[3]/D", 65536);
  pTree->Branch("ev_trk_exitAx", &ev_trk_exitAx, "ev_trk_exitAx/D", 65536);
  pTree->Branch("ev_trk_exitAy", &ev_trk_exitAy, "ev_trk_exitAy/D", 65536);  
  pTree->Branch("ev_extraEnergy", &ev_extraEnergy, "ev_extraEnergy/D", 65536);

  // MINOS track variables -- filled once per event, only if ev_minosMatch is true (bogus otherwise)
  pTree->Branch("ev_minosMatch",&ev_minosMatch, "ev_minosMatch/I", 32768);
  pTree->Branch("ev_minosRecoByRange", &ev_minosRecoByRange, "ev_minosRecoByRange/I", 32768);
  pTree->Branch("ev_minosRecoByCurvature", &ev_minosRecoByCurvature, "ev_minosRecoByCurvature/I", 32768);
  pTree->Branch("ev_minosP", &ev_minosP, "ev_minosP/D", 65536);
  pTree->Branch("ev_minosPrange", &ev_minosPrange, "ev_minosPrange/D", 65536);
  pTree->Branch("ev_minosPcurve", &ev_minosPcurve, "ev_minosPcurve/D", 65536);
  pTree->Branch("ev_muonCharge", &ev_muonCharge, "ev_muonCharge/D", 65536);
  pTree->Branch("ev_minosVtx", &ev_minosVtx, "ev_minosVtx[3]/D", 65536);
  pTree->Branch("ev_muonVtx", &ev_muonVtx, "ev_muonVtx[3]/D", 65536); // minerva vertex
  pTree->Branch("ev_muonP", &ev_muonP, "ev_muonP[3]/D", 65536);
  pTree->Branch("ev_minosTrackQP", &ev_minosTrackQP, "ev_minosTrackQP/D", 65536); // for data-driven rock muon MC

  // Truth variables -- filled once per event, every MC event (bogus for data)
  pTree->Branch("ev_muonTruePDG", &ev_muonTruePDG, "ev_muonTruePDG/I", 32768);
  pTree->Branch("ev_muonTrueVtx", &ev_muonTrueVtx, "ev_muonTrueVtx[3]/D", 65536);
  pTree->Branch("ev_muonTrueP", &ev_muonTrueP, "ev_muonTrueP[3]/D", 65536);
  pTree->Branch("ev_muonTrueE", &ev_muonTrueE, "ev_muonTrueE/D", 65536);

  // Cluster variables -- filled for all clusters
  pTree->Branch("n_clusters", &n_clusters, "n_clusters/I", 32768);
  pTree->Branch("cl_subdet", cl_subdet, "cl_subdet[n_clusters]/I", 32768);
  pTree->Branch("cl_module", cl_module, "cl_module[n_clusters]/I", 32768);
  pTree->Branch("cl_plane", cl_plane, "cl_plane[n_clusters]/I", 32768);
  pTree->Branch("cl_tpos", cl_tpos, "cl_tpos[n_clusters]/D", 65536);
  pTree->Branch("cl_lpos", cl_lpos, "cl_lpos[n_clusters]/D", 65536);
  pTree->Branch("cl_pe", cl_pe, "cl_pe[n_clusters]/D", 65536);
  pTree->Branch("cl_recoE", cl_recoE, "cl_recoE[n_clusters]/D", 65536);
  pTree->Branch("cl_trueE", cl_trueE, "cl_trueE[n_clusters]/D", 65536);
  pTree->Branch("cl_trueEall", cl_trueEall, "cl_trueEall[n_clusters]/D", 65536);
  pTree->Branch("cl_stateAx", cl_stateAx, "cl_stateAx[n_clusters]/D", 65536);
  pTree->Branch("cl_stateAy", cl_stateAy, "cl_stateAy[n_clusters]/D", 65536);
  pTree->Branch("cl_cosThetaZ", cl_cosThetaZ, "cl_cosThetaZ[n_clusters]/D", 65536);
  pTree->Branch("cl_time", cl_time, "cl_time[n_clusters]/D", 65536);
  pTree->Branch("cl_nstrips", cl_nstrips, "cl_nstrips[n_clusters]/I", 32768);
  pTree->Branch("cl_type", cl_type, "cl_type[n_clusters]/I", 32768);
  pTree->Branch("cl_activePathLength", cl_activePathLength, "cl_activePathLength[n_clusters]/D", 65536);

  // Muon fuzz variables -- filled for fuzz digits only
  pTree->Branch("n_fuzzclusters", &n_fuzzclusters, "n_fuzzclusters/I", 32768);
  pTree->Branch("fz_subdet", fz_subdet, "fz_subdet[n_fuzzclusters]/I", 32768);
  pTree->Branch("fz_type", fz_type, "fz_type[n_fuzzclusters]/I", 32768);
  pTree->Branch("fz_distance", fz_distance, "fz_distance[n_fuzzclusters]/D", 65536);
  pTree->Branch("fz_energy", fz_energy, "fz_energy[n_fuzzclusters]/D", 65536);
  pTree->Branch("fz_timediff", fz_timediff, "fz_timediff[n_fuzzclusters]/D", 65536);

  return GaudiTupleAlg::initialize();
}

//===========================================================================================
//! Finalize
//===========================================================================================
StatusCode MuonFuzzStudyAlg::finalize()
{
  const char *oldPath = gDirectory->GetPath(); //remember where root's pwd was
  if( !pFile->cd() )
    error() << "Could not change current directory to the output file" << endmsg;
  else
  {
    pTree->Write();

    gDirectory->cd( oldPath ); //reset root's pwd
    pFile->Close();
  }

  return GaudiTupleAlg::finalize();
}

//===========================================================================================
//! Destructor
//===========================================================================================
MuonFuzzStudyAlg::~MuonFuzzStudyAlg()
{
}

//===========================================================================================
//! Main algorithm execution, where the magic happens
//===========================================================================================
StatusCode MuonFuzzStudyAlg::execute() 
{

  debug() << "MuonFuzzStudyAlg::execute()" << endmsg;

  // Get event information from DAQ Header, and figure out if this is MC
  Minerva::DAQHeader const * pDAQHeader = get<Minerva::DAQHeader> (Minerva::DAQHeaderLocation::Default);
  const bool isMC = pDAQHeader->isMCTrigger();
  ev_isMC = isMC;

  if( isMC ) {
    bool truth_worked = fillTruth(); // The code for MC assumes there is 1 GenMinInteraction per gate
    if( !truth_worked ) return StatusCode::SUCCESS; // if it's MC but no truth, something has gone wrong
  }

  // event accounting
  ev_run = pDAQHeader->runNumber();
  ev_subrun = pDAQHeader->subRunNumber();
  ev_gate = pDAQHeader->gateNumber();

  m_EventTime = pDAQHeader->gpsTime();

  // Get time slices from the TES
  Minerva::TimeSlices * ptsvec = get<Minerva::TimeSlices>( Minerva::TimeSliceLocation::Default );
  Minerva::TimeSlices::const_iterator its;

  for( its = ptsvec->begin(); its != ptsvec->end(); ++its ) {
    Minerva::TimeSlice * pts = *its;

    ev_timeslice = pts->sliceNumber();
    if( ev_timeslice == 0 ) continue; // time slice 0 is diffuse garbage

    SmartRefVector<Minerva::Prong> prongVec = pts->select<Minerva::Prong>("All","All");
    if( prongVec.size() != 1 ) continue; // require exactly one track

    SmartRef<Minerva::Prong> prong = prongVec[0];
    if( prong->minervaTracks().size() != 1 ) continue; // prong must have one track if it's a rock muon
    SmartRef<Minerva::Track> pTrack = prong->minervaTracks()[0];

    double track_vertex_time = m_recoObjectTimeTool->trackVertexTime( pTrack );

    // make a map of PlaneID to tansverse coordinate of the track
    std::map<const Minerva::PlaneID,double> trackStateMap;
    fillTrackStateMap( trackStateMap, pTrack );

    // Use MuonUtils rock muon tool to select rock muons if you are not test beam
    IMuonUtils::RockMuEntryData entry;
    IMuonUtils::RockMuExitData exit;

    bool rockmu = m_muonUtils->isRockMuon( pTrack, entry, exit );
    // Require that muon enter front and exit back -- side-entering "rock muons" are usually from OD interactions
    if( !rockmu ) continue;
    if( entry != IMuonUtils::ENTER_FRONT ) continue;
    if( exit != IMuonUtils::EXIT_BACK ) continue;

    // fill MINOS-match information
    fillMINOS( prong );

    // Save extra energy to impose cut which gets rid of rock muon + crazy shower slices
    ev_extraEnergy = 0.0; // we'll add this up as we go through the fuzz

    n_fuzzclusters = 0;
    SmartRefVector<Minerva::IDCluster> fuzzClusters = pts->select<Minerva::IDCluster>("Unused","All"); // vector of ALL non-muon clusters
    for( SmartRefVector<Minerva::IDCluster>::iterator itC = fuzzClusters.begin(); itC != fuzzClusters.end(); ++itC ) {
      ev_extraEnergy += (*itC)->energy(); // all extra energy of all distances

      double mu_tpos = trackStateMap[(*itC)->planeid()];
      fz_distance[n_fuzzclusters] = abs(mu_tpos - (*itC)->position());
      fz_energy[n_fuzzclusters] = (*itC)->energy();
      fz_type[n_fuzzclusters] = (*itC)->type();
      fz_subdet[n_fuzzclusters] = (*itC)->subdet();

      double zdiff = (*itC)->z() - pTrack->firstState().z();
      double mu_time = track_vertex_time + zdiff / m_muonSpeed; // TOF-corrected time of muon track in this z position
      debug() << "Vtx time " << track_vertex_time << " correction " << zdiff / m_muonSpeed << " cluster time " << (*itC)->time() << " muon time " << mu_time << endmsg;
      fz_timediff[n_fuzzclusters] = (*itC)->time() - mu_time;
      n_fuzzclusters++;
    }

    std::map< Minerva::StripID, double > stripTrueEnergyMap;
    fillTrueEnergyMap( stripTrueEnergyMap );

    fillClusterInfo( stripTrueEnergyMap, pTrack );

    // track information
    ev_trktheta = pTrack->theta();
    ev_trkAx = pTrack->firstState().ax();
    ev_trkAy = pTrack->firstState().ay();
    ev_trk_exit[0] = pTrack->lastState().x();
    ev_trk_exit[1] = pTrack->lastState().y();
    ev_trk_exit[2] = pTrack->lastState().z();
    ev_trk_exitAx = pTrack->lastState().ax();
    ev_trk_exitAy = pTrack->lastState().ay();


    pTree->Fill(); // fill the tree

  } // loop over time slices

  return StatusCode::SUCCESS;
}

void MuonFuzzStudyAlg::fillTrackStateMap( std::map< const Minerva::PlaneID, double > &trackStateMap, SmartRef<Minerva::Track> track )
{

  trackStateMap.clear(); // not necessary but a habit of mine

  const std::vector<Minerva::Node*> nodes = track->nodes();
  for( std::vector<Minerva::Node*>::const_iterator itNode = nodes.begin(); itNode != nodes.end(); ++itNode ) {
    Gaudi::XYZPoint pos = (*itNode)->position(); // 3d position, xyz
    const Minerva::PlaneID pid = (*itNode)->planeid();
    double tpos = -9999.0;
    if     ( (*itNode)->view() == Minerva::Node::X ) tpos = pos.x();
    else if( (*itNode)->view() == Minerva::Node::U ) tpos = m_mathTool->calcUfromXY( pos.x(), pos.y() );
    else if( (*itNode)->view() == Minerva::Node::V ) tpos = m_mathTool->calcVfromXY( pos.x(), pos.y() );
    else warning() << "Unknown view!" << endmsg;
    
    trackStateMap[pid] = tpos;
  }

}


//===========================================================================================
//! Truth stuff
//===========================================================================================
bool MuonFuzzStudyAlg::fillTruth()
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
//! MINOS information
//===========================================================================================
void MuonFuzzStudyAlg::fillMINOS( SmartRef<Minerva::Prong> prong )
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
  ev_minosRecoByRange = -1;
  ev_minosRecoByCurvature = -1;
  ev_minosTrackQP = -9999.0;

  // MinosOK must be set and not 0
  int minosOK = 1;
  if( ! prong->getIntData(ProngExtraDataDefs::MinosOK(), minosOK) ) return;
  if( minosOK == 0 ) return;

  SmartRef<Minerva::Particle> muon;
  if( !m_muonUtils->findMuonParticle(prong, muon) ) return;

  if( ! (muon->methodSignature() == "MuonEnergyRec") ) return;

  if( prong->MinosStub() ) return; // require an actual track rather than a "stub"

  if( !prong->hasDoubleData(ProngExtraDataDefs::MinosMomentum()) ) return; // require that the momentum be measured

  // MinosMomentum is common to tracks and stubs
  ev_minosP = prong->getDoubleData(ProngExtraDataDefs::MinosMomentum());
  ev_minosMatch = 1;

  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackPRange()) )
    ev_minosPrange = prong->getDoubleData( ProngExtraDataDefs::MinosTrackPRange() );
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackPCurvature()) )
    ev_minosPcurve = prong->getDoubleData( ProngExtraDataDefs::MinosTrackPCurvature() );


  // fill MINOS vertex
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackVtxX()) )
    ev_minosVtx[0] = prong->getDoubleData( ProngExtraDataDefs::MinosTrackVtxX() );
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackVtxY()) )
    ev_minosVtx[1] = prong->getDoubleData( ProngExtraDataDefs::MinosTrackVtxY() );
  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackVtxZ()) )
    ev_minosVtx[2] = prong->getDoubleData( ProngExtraDataDefs::MinosTrackVtxZ() );

  if( prong->hasIntData(ProngExtraDataDefs::MinosRecoByRange()) )
    ev_minosRecoByRange = prong->getIntData( ProngExtraDataDefs::MinosRecoByRange() );
  if( prong->hasIntData(ProngExtraDataDefs::MinosRecoByCurvature()) )
    ev_minosRecoByCurvature = prong->getIntData( ProngExtraDataDefs::MinosRecoByCurvature() );

  if( prong->hasDoubleData(ProngExtraDataDefs::MinosTrackQP()) )
    ev_minosTrackQP = prong->getDoubleData( ProngExtraDataDefs::MinosTrackQP() );

  int charge = 0;
  m_muonUtils->muonCharge( prong, charge );

  ev_muonCharge = charge;
  const Gaudi::XYZTVector position = muon->startPos();
  ev_muonVtx[0] = position.X();
  ev_muonVtx[1] = position.Y();
  ev_muonVtx[2] = position.Z();

  const Gaudi::XYZTVector momentum = muon->momentumVec();
  ev_muonP[0] = momentum.Px();
  ev_muonP[1] = momentum.Py();
  ev_muonP[2] = momentum.Pz();

}

//===========================================================================================
//! True energy info
//===========================================================================================
void MuonFuzzStudyAlg::fillTrueEnergyMap( std::map< Minerva::StripID, double > &stripTrueEnergyMap )
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
    Minerva::StripID stripid = m_innerDetector->getStripID( hitCenter );
    if ( !stripid ) continue;

    if ( stripTrueEnergyMap.find( stripid ) == stripTrueEnergyMap.end() ) stripTrueEnergyMap[ stripid ] = 0.0;
    stripTrueEnergyMap[ stripid ] += hit->energy();

  }
}


//===========================================================================================
//! Cluster information
//===========================================================================================
void MuonFuzzStudyAlg::fillClusterInfo( std::map< Minerva::StripID, double > stripTrueEnergyMap, SmartRef<Minerva::Track> pTrack )
{

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
      // first fill only the true energy in the strips that make up the cluster
      double trueClusterEnergy = 0.0;
      SmartRefVector<Minerva::IDDigit> clusterDigits = idcluster->digits();
      SmartRefVector<Minerva::IDDigit>::iterator itClusterDigit;
      for ( itClusterDigit = clusterDigits.begin(); itClusterDigit != clusterDigits.end(); ++itClusterDigit ) {
        if ( stripTrueEnergyMap.find( (*itClusterDigit)->stripid() ) == stripTrueEnergyMap.end() ) continue;
        trueClusterEnergy += stripTrueEnergyMap[ (*itClusterDigit)->stripid() ];
      }
      cl_trueE[n_clusters] = trueClusterEnergy;
    }
    else cl_trueE[n_clusters] = -9999.0;

    if( ev_isMC ) {
      // now all the true energy in the plane, regardless of whether it is from the cluster or not
      double totalTrueEnergy = 0.0;
      Minerva::PlaneID planeid = idcluster->planeid();
      for( unsigned int strip = 1; strip <= 127; ++strip ) {
        Minerva::StripID stripid( planeid, strip );
        if ( stripTrueEnergyMap.find( stripid ) == stripTrueEnergyMap.end() ) continue;
        totalTrueEnergy += stripTrueEnergyMap[ stripid ];
      }
      cl_trueEall[n_clusters] = totalTrueEnergy;
    }
    else cl_trueEall[n_clusters] = -9999.0;

    ++n_clusters;
    if( n_clusters == MAXCLUSTERS ) { // I don't know how this can happen, but just in case
      warning() << "Encountered more than " << n_clusters << " clusters in this track" << endmsg;
      counter("TooManyClusters")++;
      break; 
    }
  }
}

