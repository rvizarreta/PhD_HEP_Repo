//==================================================================================================
// PrintConstants.C
// input: summary.root
// output: s2s_constants_new.txt, Specials.txt
// Reads in summary ntuple, computes average dEdX for good strips, and computes s2s constant
// Outputs s2s constants file, to which a time header is added before it goes in the database
//==================================================================================================

void PrintConstants()
{

  int id, strip, plane, module, subdet, N;
  int good, badshift, dead, badrms, badzero, lowE;
  double dedx, error, rmsTot, dedxTot, shift, rms, zeroFrac;

  srand( time(NULL) );

  TFile * fin = new TFile("summary.root", "READ");
  if( !fin ) {
    printf("No summary.root!\n");
    exit(0);
  }
  FILE * fp;
  FILE * fp2;

  fp = fopen("s2s_constants_new.txt", "w");
  fp2 = fopen("error_strips.txt", "w");

  TTree * nts = (TTree *) fin->Get("nts");
    
  nts->SetBranchAddress("id", &id);
  nts->SetBranchAddress("strip", &strip);
  nts->SetBranchAddress("plane", &plane);
  nts->SetBranchAddress("module", &module);
  nts->SetBranchAddress("subdet", &subdet);
  nts->SetBranchAddress("good", &good);
  nts->SetBranchAddress("badshift", &badshift);
  nts->SetBranchAddress("dead", &dead);
  nts->SetBranchAddress("badrms", &badrms);
  nts->SetBranchAddress("badzero", &badzero);
  nts->SetBranchAddress("dedx.meanTrunc", &dedx);
  nts->SetBranchAddress("dedx.errorTot", &error);
  nts->SetBranchAddress("dedx.nTot", &N);
  nts->SetBranchAddress("shift", &shift);
  nts->SetBranchAddress("rms", &rms);
  nts->SetBranchAddress("zero_fraction", &zeroFrac);
    
  int ROWS = nts->GetEntries();
    
  // Find the center of the dE/dX distribution to determine error strip cutoff
  double sum = 0.0;
  double sumsq = 0.0;
  int nsum = 0;
  for( int i = 0; i < ROWS; ++i ) {
    nts->GetEntry(i);
    if (!good) continue; // Already flagged as an error
    sum += dedx;
    sumsq += dedx*dedx;
    ++nsum;
  }
  double center = sum / nsum;
  double sigma = sqrt(sumsq/nsum - center*center);
  double lower = 0.15 * center;
  printf("center = %f MeV/cm (no MEU calibration applied)\n", center);
  printf("sigma  = %f MeV/cm (no MEU calibration applied)\n", sigma);
  printf("Lower Bound = %f MeV/cm\n", lower);

  // Set error flag for low-energy strips and determine minimum occupancy
  int minocc = 1000000;
  for( int i = 0; i < ROWS; ++i ) {
    nts->GetEntry(i);
    if (!good) continue;
    if (strip != 1 && strip != 127 && N < minocc) minocc = N;
  }

  fprintf(fp, "# min occ %d hits\n", minocc);
  fprintf(fp, "# detector subdet module plane strip s2s ds2s entries error\n");

  // Now determine the average inverse energy
  double avgConst = 0.0;
  int nGood = 0;
  for( int i = 0; i < ROWS; ++i ) {
    nts->GetEntry(i);
    if( !good ) continue;
    avgConst += (1.0 / dedx);
    ++nGood;
  }
  avgConst /= nGood;
  // avgConst is now the average 1 / dedx

  int nbadshift = 0;
  int ndead = 0;
  int nlow = 0;
  int nbadrms = 0;
  int nbadzero = 0;
  int nerror = 0;

  vector<string> allvec;

  int nrand = 0;

  double actual_average = 0.0;

  for( int i = 0; i < ROWS; ++i ) {
    nts->GetEntry(i);

    double x, dx;
    if( dedx > 0.0 ) {
      x = (1.0/dedx) / avgConst;
      dx = ( error/(dedx*dedx) ) / avgConst;
    } else {
      x = 0.0;
      dx = 0.0;
    }
    int errorlabel=0;
    if (!good) {
      if (dead)         { errorlabel+=10000; ++ndead; }
      if (badshift)     { errorlabel+=1000; ++nbadshift; }
      if (badrms)       { errorlabel+=100; ++nbadrms; }
      if (badzero)      { errorlabel+=10; ++nbadzero; }
      if (dedx < lower) { errorlabel+=1; ++nlow; }

      ++nerror;

      int hash;
      hash = 10000*module + 1000*plane + strip;

      char info[200];
      sprintf(info, "%07d module=%d plane=%d strip=%d error=%05d dedx=%3.2f rms=%3.2f shift=%3.2f zero=%d \n", hash, module, plane, strip, errorlabel, dedx, rms, shift, (int)floor(100*zeroFrac));

      allvec.push_back(info);

    } else if( rand() % 2000 == 7 && nrand < 10 ) { // put ~10 examples at the end of the list
      char goodinfo[200];
      sprintf( goodinfo, "%07d module=%d plane=%d strip=%d error=%05d dedx=%3.2f rms=%3.2f shift=%3.2f zero=%d \n", 9999990+nrand, module, plane, strip, errorlabel, dedx, rms, shift, (int)floor(100*zeroFrac));

      allvec.push_back(goodinfo);

      ++nrand;
    }

    // Error strips will have computed s2s constant put in DB, GetStripResponse deals with it
    fprintf(fp, "1 %d %d %d %d %f %f %d %05d \n", subdet, module, plane, strip, x, dx, N, errorlabel);

    if( good ) actual_average += x/nGood;

  }

  printf("%d strips have a Zero Mean\n", ndead);
  printf("%d strips have a Bad Shift error\n", nbadshift);
  printf("%d strips have a High RMS error\n", nbadrms);
  printf("%d strips have a Mean Below Lower Bound error\n", nlow);
  printf("%d strips have a High zero fraction error\n", nbadzero);
  printf("%d strips have an Error Flag of any kind\n", nerror);
  printf("Average s2s constant for %d good channels is %6.5f\n", nGood, actual_average);

  //------------------------------------------------------------------------------------------------
  // Sort error strips
  //------------------------------------------------------------------------------------------------
  vector<string> sorted;
  while( allvec.size() ) {
    int smallest = 99999999;
    int idx = -1;
    for( int i = 0; i < allvec.size(); i++ ) {
      string hashstr = allvec[i].substr(0,7);
      int hash = atoi(hashstr.c_str());
      if( hash < smallest ) { smallest = hash; idx = i; }
    }
    sorted.push_back( allvec[idx] );
    allvec.erase( allvec.begin() + idx );
  }

  for( int i = 0; i < sorted.size(); i++ ) {
    string hashstr = sorted[i].substr(0,7);
    string infoout = sorted[i].substr(8);
    fprintf(fp2, "%s", infoout.c_str());
  
    int hash = atoi(hashstr.c_str());

    if( hash >= 9999990 ) continue;

    int module, plane, strip;
    if( hash > 0 ) {
      strip = hash%1000;
      plane = (hash/1000)%10;
      module = hash/10000;
    } else {
      module = (hash/10000)-1;
      plane = (hash-module*10000)/1000;
      strip = (hash-module*10000)%1000;
    }
  }

  fclose(fp);
  fclose(fp2);

}

