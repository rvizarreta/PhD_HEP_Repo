#include "PlexWriterAlg.h"

#include "GaudiKernel/DeclareFactoryEntries.h"
#include "Plex/IPlexModel.h"
#include "CalTools/IGetCalAttenuation.h"
#include "CalTools/IWLSBaggieAttTool.h"
#include "CalTools/IClearFiberAttTool.h"
#include "MinervaDet/IGeomUtilSvc.h"
#include "MinervaDet/DeDetector.h"
#include "MinervaDet/DeSubdet.h"
#include "MinervaDet/DeModule.h"
#include "MinervaDet/DePlane.h"

#include "Kernel/ChannelID.h"
#include "Event/DAQHeader.h"

#include "TFile.h"
#include "TTree.h"


DECLARE_ALGORITHM_FACTORY( PlexWriterAlg );

/*
 * Constr, initliaze, execute, finalize, destr
 */

PlexWriterAlg::PlexWriterAlg(std::string const & name, ISvcLocator * pSvcLocator)
  : GaudiTupleAlg(name, pSvcLocator)
{
  declareProperty("RunNumber", m_RunNumber = 2168);
}

StatusCode PlexWriterAlg::initialize()
{

  IGeomUtilSvc *geomUtilSvc;
  service("GeomUtilSvc", geomUtilSvc, true);
  m_isTestBeam = geomUtilSvc->isTestBeam();

  if( m_isTestBeam ) m_pDetector = getDet<Minerva::DeDetector>("/dd/Structure/Minerva/Detector/MTest");
  else m_pDetector = getDet<Minerva::DeDetector>("/dd/Structure/Minerva/Detector/InnerDetector");

  if( !m_pDetector ) {
    error() << "Could not retrieve inner detector!" << endmsg;
    return StatusCode::FAILURE;
  }
  
  try {
    m_plexModel = tool<IPlexModel>("MinervaPlexModel");
  } catch( GaudiException& e ) {
    error() << "Could not get MinervaPlexModel tool" << endmsg;
    return StatusCode::FAILURE;
  }

  pFile = new TFile("plex.root", "RECREATE");
  if (pFile == 0)
  {
    fatal() << "Could not open plex.root for writing" << endmsg;
    return StatusCode::FAILURE;
  }
  pTree = new TTree("plex", "plex");
  if (pTree == 0)
  {
    fatal() << "Could not book TTree" << endmsg;
    return StatusCode::FAILURE;
  }
  pTree->Branch("id", &m_id, "id/I", 32768);
  pTree->Branch("strip", &m_strip, "strip/I", 32768);
  pTree->Branch("plane", &m_plane, "plane/I", 32768);
  pTree->Branch("module", &m_module, "module/I", 32768);
  pTree->Branch("subdet", &m_subdet, "subdet/I", 32768);
  pTree->Branch("link", &m_link, "link/I", 32768);
  pTree->Branch("crate", &m_crate, "crate/I", 32768);
  pTree->Branch("croc", &m_croc, "croc/I", 32768);
  pTree->Branch("chain", &m_chain, "chain/I", 32768);
  pTree->Branch("board", &m_board, "board/I", 32768);
  pTree->Branch("conn", &m_conn, "conn/I", 32768);
  pTree->Branch("pixel", &m_pixel, "pixel/I", 32768);
  pTree->Branch("view", &m_view, "view/I", 32768);
  pTree->Branch("points_up", &m_points_up, "points_up/I", 32768);
  pTree->Branch("z", &m_z, "z/D", 65536);
  pTree->Branch("L", &m_L, "L/D", 65536);
  pTree->Branch("tpos", &m_tpos, "tpos/D", 65536);
  
  return GaudiTupleAlg::initialize();
}

StatusCode PlexWriterAlg::execute()
{
  info() << "Begin..." << endreq;
  CreatePlexTuple();
  return StatusCode::SUCCESS;
}

StatusCode PlexWriterAlg::finalize()
{
  return GaudiTupleAlg::finalize();
}

PlexWriterAlg::~PlexWriterAlg()
{
}

/*
 * CreatePlexTuple
 * writes a convenient ntuple to the output stream
 */

StatusCode PlexWriterAlg::CreatePlexTuple()
{

  // --- Set the run number for the Plex tool ---

  put(new Minerva::DAQHeader, Minerva::DAQHeaderLocation::Default);
  Minerva::DAQHeader * pDAQHeader = getOrCreate<Minerva::DAQHeader,Minerva::DAQHeader> (Minerva::DAQHeaderLocation::Default);
  pDAQHeader->setRunNumber(m_RunNumber);

  // --- Loop over all strips ---

  Minerva::DeDetector::DeSubdetCItr itSubdet;  Minerva::DeSubdet const * pSubdet;
  Minerva::DeSubdet  ::DeModuleCItr itModule;  Minerva::DeModule const * pModule;
  Minerva::DeModule  ::DePlaneCItr  itPlane;   Minerva::DePlane  const * pPlane;
  Minerva::DePlane   ::StripCItr    itStrip;   Minerva::StripID stripid;

  info() << "begin" << endreq;

  for (itSubdet = m_pDetector->subdetBegin(); itSubdet != m_pDetector->subdetEnd(); ++itSubdet)
  {
    pSubdet = *itSubdet;
    for (itModule = pSubdet->moduleBegin(); itModule != pSubdet->moduleEnd(); ++itModule)
    {
      pModule = *itModule;
      int module = (pModule->getModuleID()).module();
      info() << "module " << module << endreq;
      for (itPlane = pModule->planeBegin(); itPlane != pModule->planeEnd(); ++itPlane)
      {
        pPlane = *itPlane;
        int iView;
        Minerva::DePlane::View_t view_t = pPlane->getView();
        if (view_t == Minerva::DePlane::X) iView = 1;
        else if (view_t == Minerva::DePlane::U) iView = 2;
        else if (view_t == Minerva::DePlane::V) iView = 3;
        else iView = 0;
        for (itStrip = pPlane->stripBegin(); itStrip != pPlane->stripEnd(); ++itStrip)
        {
          stripid = itStrip->first;
          if( !(m_plexModel->isInstrumented(stripid)) ) continue;
          m_id =       stripid.id();
          m_strip =    stripid.strip();
          m_plane =    stripid.plane();
          m_module =   stripid.module();
          m_subdet =   stripid.subdet();

          Minerva::ChannelID channelid = m_plexModel->getChannelID(stripid);
          m_link =     channelid.link();
          m_crate =    channelid.crate();
          m_croc =     channelid.croc();
          m_chain =    channelid.chain();
          m_board =    channelid.board();
          m_conn =     m_plexModel->getPmtConnector(channelid);
          m_pixel =    channelid.pixel();

          m_view =     iView;
          if (m_isTestBeam)
            m_points_up = pPlane->doesStripPointUpstream(stripid);
          else
            m_points_up = -1;
          m_z =        pPlane->getZCenter();
          m_L =        2.*pPlane->getStripHalfLength(stripid);
          m_tpos =     pPlane->getTPos(stripid);

          pTree->Fill();
          pTree->AutoSave("SaveSelf");
        }
        
      }
      
    }
    
  } // --- end of the loop over all strips ---

  info() << "end" << endreq;

  return StatusCode::SUCCESS;
} 
