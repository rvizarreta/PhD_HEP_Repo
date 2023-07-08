void MakeWeeklyPlots()
{

  // Get current playlist of runs -- quit if no playlist exists
  FILE * playlist = fopen( "playlist_weekly.txt", "r" );
  if( playlist == NULL ) exit(0);

  // TChains for main ntuple and header
  TChain * nt = new TChain( "nt", "nt" );
  TChain * header = new TChain( "header", "header" );

  // Loop over playlist of files and add them to the TChains
  int r0 = 0; int s0 = 0; int r1 = 0; int s1 = 0;
  bool first = true;
  while( !feof(playlist) ) {
    int run, subrun;
    char name[1000];
    fscanf( playlist, "%d %d %s", &run, &subrun, &name );
    if( first ) {
      r0 = run;
      s0 = subrun;
      first = false;
    }
    if( run == r1 && subrun == s1 ) break; // it adds the last one twice for some reason
    r1 = run;
    s1 = subrun;
    TFile * test_file = new TFile( name, "OLD" );
    if( test_file == NULL ) {
      fprintf( bad_data, "%d %d\n", run, subrun );
      delete test_file;
      continue;
    }
    TTree * test_tree = (TTree*)test_file->Get( "nt" );
    if( test_tree == NULL ) {
      delete test_tree;
      continue;
    }

    nt->Add( name );
    header->Add( name );

  }
  fclose( playlist );
  printf("Created chain for runs %d/%d - %d/%d\n",r0,s0,r1,s1);

  // Output file for plots -- file name gives run range
  TFile * fout = new TFile( Form("dump/thisweek/weekly_plots_r%04d_s%02d_to_r%04d_s%02d.root",r0,s0,r1,s1,r0,s0,r1,s1), "RECREATE" );

  // Histograms
  TH1 * chanEnergy[120][2][127];
  TH2 * tm_energy2d = new TH2D("tm_energy2d", "Truncated mean energy / path;Module;Strip", 240, -5, 115, 127, 1, 128);
  TH1 * tm_energy1d = new TH1D("tm_energy1d", ";Truncated mean energy / path (MeV/cm);Fraction per 0.01 MeV", 100, 1.0, 2.0 );
  TH2 * n_entries_str = new TH2D("n_entries_str", ";Module;Strip", 240, -5, 115, 127, 1, 128 );
  TProfile2D * alignment_shifts = new TProfile2D("alignment_shifts", "Alignment shift;Module;Strip", 240, -5, 115, 127, 1, 128);
  TProfile * energy_vs_path = new TProfile("energy_vs_path", "Energy vs Path; cm; MeV", 90, 0.2, 2);
  TH2 * zero_fraction = new TH2D("zero_fraction", "Fraction of tracks with zero energy;Module;Strip", 240, -5, 115, 127, 1, 128);

  TH2 * electronics[2][8];
  TProfile2D * e_avgPE[2][8];
  for( int crate = 0; crate < 2; ++crate ) {
    for( int croc = 0; croc < 8; ++croc ) {
      electronics[crate][croc] = new TH2D( Form("nh_crate%d_croc%d",crate,croc+1), Form("N Hits Crate %d Croc %d;Board;Chain",crate,croc+1), 80, 1.0, 11.0, 32, 0.0, 4.0 );
      e_avgPE[crate][croc] = new TProfile2D( Form("pe_crate%d_croc%d",crate,croc+1), Form("Avg. PE Crate %d Croc %d;Board;Chain",crate,croc+1), 80, 1.0, 11.0, 32, 0.0, 4.0 );
    }
  }
  for( int i = -5; i < 115; i++ ) {
    for( int j = 1; j <= 2; j++ ) {
      for( int k = 1; k <= 127; k++ ) {
        int modidx = i+5;
        int plidx = j-1;
        int stridx = k-1;
        chanEnergy[modidx][plidx][stridx] = new TH1D(Form("mod%03d_pl%01d_str%03d",i,j,k),Form("mod%03d_pl%01d_str%03d;Energy (pseudo-MeV)",i,j,k),20000,0.0,20.0);
      }
    }
  }

  double pot = getPOT( header );  

  int NN = nt->GetEntries();

  int n_entries;
  int strip[1000], plane[1000], module[1000];
  double path[1000], base[1000], E[1000];

  int n_hits;
  int hit_crate[1000], hit_croc[1000], hit_chain[1000], hit_board[1000], hit_pixel[1000];
  double hit_pe[1000];

  nt->SetBranchAddress("n_entries", &n_entries);
  nt->SetBranchAddress("st_strip", strip);
  nt->SetBranchAddress("st_plane", plane);
  nt->SetBranchAddress("st_module", module);
  nt->SetBranchAddress("st_path", path);
  nt->SetBranchAddress("st_base", base);
  nt->SetBranchAddress("st_mev", E);
  nt->SetBranchAddress("n_hits", &n_hits);
  nt->SetBranchAddress("hit_crate", hit_crate);
  nt->SetBranchAddress("hit_croc", hit_croc);
  nt->SetBranchAddress("hit_chain", hit_chain);
  nt->SetBranchAddress("hit_board", hit_board);
  nt->SetBranchAddress("hit_pixel", hit_pixel);
  nt->SetBranchAddress("hit_pe", hit_pe);

  for( int ii = 0; ii < NN; ++ii ) {
    nt->GetEntry(ii);
    if( ii % 10000 == 0 ) printf("Processing track %d of %d...\n", ii, NN);

    for( int i = 0; i < n_entries; ++i ){

      double path_cm = 0.1 * path[i];
      if( path_cm < 0.2 ) continue;

      // Fill alignment histograms with normal incidence correction factor C
      double C = (17-fabs(base[i]))/path[i];
      alignment_shifts->Fill(module[i] + 0.5 * (plane[i] - 1), strip[i], base[i], E[i]*C);

      // Energy vs. path for sanity check
      energy_vs_path->Fill(path_cm, E[i]);

      // Determine index to chanEnergy for this channel
      int modidx = module[i]+5;
      int plidx = plane[i]-1;
      int stridx = strip[i]-1;

      // Fill truncated mean histogram for non-zero energy
      if( E[i] != 0.0 ) chanEnergy[modidx][plidx][stridx]->Fill(E[i]/path_cm);
      else zero_fraction->Fill(module[i] + 0.5 * (plane[i] - 1), strip[i]);

      n_entries_str->Fill( module[i] + 0.5 * (plane[i]-1), strip[i] );

    } // entries

    // Hit loop for electronics space stuff
    for( int h = 0; h < n_hits; ++h ) {

      int column = hit_pixel[h] % 8;
      int row = hit_pixel[h] / 8;

      double xx = hit_board[h] + column/8.0;
      double yy = hit_chain[h] + row/8.0;

      electronics[hit_crate[h]][hit_croc[h]-1]->Fill( xx, yy );
      e_avgPE[hit_crate[h]][hit_croc[h]-1]->Fill( xx, yy, hit_pe[h] );
    } // hits
  } // rock muons

  //------------------------------------------------------------------------------------------------
  // Iterate over energy histogram for each channel to find truncated mean
  //------------------------------------------------------------------------------------------------
  double TM[120][2][127] = {{{0.0}}}
  printf("Determining truncated mean with %d iterations...\n",n_iterations);
  for( int it = 0; it < 6; it++ ) {
    for( int mod = 0; mod < 120; mod++ ) {
      for( int pl = 0; pl <= 1; pl++ ) {
        for( int str = 0; str < 127; str++ ) {
          double upper = 1.5 * TM[mod][pl][str];
          double lower = 0.5 * TM[mod][pl][str];
          if( it == 0 ) upper = 20.0;
          if( chanEnergy[mod][pl][str]->GetEntries() > 0 ) {
            chanEnergy[mod][pl][str]->GetXaxis()->SetRangeUser(lower,upper); // refine range
            TM[mod][pl][str] = chanEnergy[mod][pl][str]->GetMean(); // new mean for next iteration
          } else TM[mod][pl][str] = 0.0; // kills this channel forever and ever
        } // strip
      } // plane
    } // module
  } // iteration

  // Fill histograms
  for( int mod = -5; mod <= 114; mod++ ) {
    if( mod % 10 == 0 ) printf("Filling summary histograms for module %d...\n", mod);
    for( int pl = 1; pl <= 2; pl++ ) {
      for( int str = 1; str <= 127; str++ ) {
        int modidx = mod+5; int plidx = pl-1; int stridx = str-1;

        int bin = tm_energy2d->FindBin( mod+0.5*(pl-1), str );

        double mean = chanEnergy[modidx][plidx][stridx]->GetMean();
        tm_energy2d->SetBinContent( bin, mean );
        chanEnergy[modidx][plidx][stridx]->GetXaxis()->SetRangeUser( 0.0, 20.0 );
        double stdev = chanEnergy[modidx][plidx][stridx]->GetRMS();
        tm_energy2d->SetBinError( bin, stdev );
        tm_energy1d->Fill( mean );


        double nzero = zero_fraction->GetBinContent( bin );
        int nEnt = n_entries_str->GetBinContent( bin ); // includes zero entries
        if( nEnt > 0 ) zero_fraction->SetBinContent( bin, nzero/nEnt );
        else zero_fraction->SetBinContent( bin, 0.0 ); // This is for strips that are actually passive targets

        delete chanEnergy[modidx][plidx][stridx];
      }
    }
  }

  // Set some display stuff
  alignment_shifts->SetMinimum(-5.0);
  alignment_shifts->SetMaximum( 5.0);
  energy_vs_path->SetMarkerSize(0.5);
  tm_energy2d->SetMaximum(2.5);
  double max_hits = 0.0;
  for( int crate = 0; crate < 2; ++crate ) {
    for( int croc = 0; croc < 8; ++croc ) {
      if( electronics[crate][croc]->GetMaximum() > max_hits ) max_hits = electronics[crate][croc]->GetMaximum();
    }
  }
  for( int crate = 0; crate < 2; ++crate ) {
    for( int croc = 0; croc < 8; ++croc ) {
      electronics[crate][croc]->SetMaximum(max_hits); // all same scale
      electronics[crate][croc]->SetMinimum(0.0); // all same scale
      e_avgPE[crate][croc]->SetMaximum(15.0);
      e_avgPE[crate][croc]->SetMinimum(0.0);
    }
  }

  // Write the histograms
  fout->cd();
  tm_energy2d->Write();
  tm_energy1d->Write();
  n_entries_str->Write();
  alignment_shifts->Write();
  energy_vs_path->Write();
  zero_fraction->Write();
  for( int crate = 0; crate < 2; ++crate ) {
    for( int croc = 0; croc < 8; ++croc ) {
      electronics[crate][croc]->Write();
      e_avgPE[crate][croc]->Write();
    }
  }

  // plot dump
  TCanvas * c1 = new TCanvas("c1","c1");
  tm_energy2d->Draw("colz");
  c1->Print(Form("dump/thisweek/truncated_mean_energy_2D.png",r0,s0,r1,s1));
  tm_energy1d->Draw();
  c1->Print(Form("dump/thisweek/truncated_mean_energy_1D.png",r0,s0,r1,s1));
  n_entries_str->Draw("colz");
  c1->Print(Form("dump/thisweek/n_entries_per_strip.png",r0,s0,r1,s1));
  alignment_shifts->Draw("colz");
  c1->Print(Form("dump/thisweek/alignment_shifts.png",r0,s0,r1,s1));
  energy_vs_path->Draw();
  c1->Print(Form("dump/thisweek/energy_vs_path.png",r0,s0,r1,s1));
  zero_fraction->Draw("colz");
  c1->Print(Form("dump/thisweek/zero_fraction.png",r0,s0,r1,s1));
  delete c1;

  TCanvas * c2 = new TCanvas("c2","c2",800,400);
  c2->Divide(4,2);
  for( int crate = 0; crate < 2; ++crate ) {
    for( int croc = 0; croc < 8; ++croc ) {
      c2->cd(croc+1);
      electronics[crate][croc]->Draw("colz");
    }
    c2->Print(Form("dump/thisweek/n_hits_crate%d.png",crate));
  }

  for( int crate = 0; crate < 2; ++crate ) {
    for( int croc = 0; croc < 8; ++croc ) {
      c2->cd(croc+1);
      e_avgPE[crate][croc]->Draw("colz");
    }
    c2->Print(Form("dump/thisweek/avg_pe_crate%d.png",crate));
  }
}

// getPOT returns the number of POT (in units of e13) for a header chain
double getPOT( TChain * header )
{

  int n_subruns = header->GetEntries();
  double total_POT;
  header->SetBranchAddress( "total_POT", &total_POT );

  double n_pot = 0.0;
  for( int sr = 0; sr < n_subruns; ++sr ) {
    header->GetEntry(sr);
    n_pot += total_POT/1.0E13;
  }

  return n_pot;

}

