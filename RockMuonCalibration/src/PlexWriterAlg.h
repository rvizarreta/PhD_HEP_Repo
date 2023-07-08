#ifndef PLEXWRITERALG_H
#define PLEXWRITERALG_H 1

// inheritance
#include "GaudiAlg/GaudiTupleAlg.h"

// includes
#include "Rtypes.h" //for Int_t,...

// forwards
class IPlexModel;

namespace Minerva {
  class DeDetector;
}

class TFile;
class TTree;

class PlexWriterAlg : public GaudiTupleAlg
{

public:

  PlexWriterAlg(std::string const &, ISvcLocator *);
  virtual StatusCode initialize();
  virtual StatusCode execute();
  virtual StatusCode finalize();
  virtual ~PlexWriterAlg();

private:

  unsigned int m_RunNumber;
  int m_isTestBeam;

  // --- Minerva detector elements and tools ---
  // --- initialized at initialize() ---
  Minerva::DeDetector * m_pDetector;
  IPlexModel * m_plexModel;

  // --- CreatePlexTuple ---
  StatusCode CreatePlexTuple();
  // --- writes a convenient ntuple to the output stream ---

  TFile * pFile;
  TTree * pTree;
  
  Int_t m_id, m_strip, m_plane, m_module, m_subdet;
  Int_t m_link, m_crate, m_croc, m_chain, m_board, m_conn, m_pixel;
  Int_t m_view, m_points_up;
  Double_t m_z, m_L, m_tpos;
};

#endif // PLEXWRITERALG_H
