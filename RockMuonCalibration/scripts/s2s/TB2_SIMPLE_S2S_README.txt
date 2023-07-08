The finished S2S cal files (for the main detector) are located in,
/minerva/data/calibrations/s2s_tables/minerva
Look at the highest version number.

0. Need to make rock ntuples using,
/home/nfs/minerva/cmtuser/Minerva_v10r8p7/Tools/SystemTests/options/Testbeam2/testbeam2-rocks.opts
To turn off calibration do,
RawToDigitAlg.DoCalStrip = false;
We want to do cal to get within ~1% of right value which means multiple iterations to get there.
ToolSvc.GetCalEnergy.UseDefaults = true; // set it do use the default MEU.

1. Creating IOVs:
Just use Run1, Run2, and Run3 for testbeam. Put the IOV in s2seras.txt.

2. Edit make_s2s_script.py to have the right rock muon output file location. Run the script to get, master_s2s_script.sh. It will run, make_s2s.sh, with the right args for each IOV.
In this case the output is in,
/minerva/data/testbeam2/calmuons/CalMuon_<run>_<subrun>

3. Run master_s2s_script.sh. It will create files like, s2s_constants_<RUN>.txt where <RUN> is the first run of the IOV. It will also create root files in output/s2s_<RUN>. They are for debugging. Go do validation and run ./MakeErrorPlot if you want to know why error strips have errors.

4. Staging:
Copy s2s_constants_<RUN>.txt to /minerva/data/calibrations/s2s_tables/minerva/vX (or a testbeam 2 version of that). Then make a playlist like in /minerva/data/calibrations/s2s_tables (files are like minerva_s2s_vX_somedate.txt).
Upload using,
http://dbweb4.fnal.gov:8080/mnvcon_prd_gui/app/GUI/fileBrowser

To run comparison.
In compare directory, compare.py. Should look at difference from previous IOV and the differences should be ~0 if no hardware swap happened.

