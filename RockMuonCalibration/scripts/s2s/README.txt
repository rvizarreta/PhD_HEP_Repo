Strip-to-strip calibration for experts
Chris Marshall
17 July 2014

This document is intended to provide instructions on how to generate strip-to-strip constants to be loaded into the database using the scripts in this area, $ROCKMUONCALIBRATIONROOT/scripts/s2s.

Step 0: Processing

RockMuonCalibrationAlg ntuples are needed. To generate these files, run the "muon" stage in ProductionScripts.  The options file template is $SYSTEMTESTSROOT/options/CalibProcessing/RockMuonReconstruction.opts. There are three important things to consider:
  1. What S2S constants do you want to use for the processing? To turn off applying the calibration, set the option:
     RawToDigitAlg.DoCalStrip = false;
     To get the desired ~1% level calibration, multiple iterations are required if your starting point is no S2S constants. If you are generating ntuples for data which has never been calibrated, a good option is to use the latest S2S table, which is the default if you leave DoCalStrip = true and do nothing.  The table that is used can be found in /minerva/data/calibrations/s2s_tables/minerva.  Look for the highest version number, and the highest run numer in that directory.
  2. Do you want to kill error strips? For physics data, all strips that are assigned error codes by S2S are zeroed, and hits on these strips are given no energy and marked as discarded. For calibration purposes, you probably don't want to do that. Each new S2S interval of validity (IOV) should give all the channels a fresh start and an opportunity to prove themselves.
  3. What MEU value do you want? The MEU factor increases with time to compensate for the decreasing light level. For calibrating, you most likely want to just use a fixed MEU. The actual value of the constant is irrelevant (this is the relative energy calibration after all), so use the default MEU:
     ToolSvc.GetCalEnergy.UseDefaults = true;

Once you have configured the options file template to your liking, submit the jobs:
  python SubmitDataRuns --first_run <first> --last_run <last> --args "--muon --outdir /full/path/to/output/directory --usecat"
You may also wish to add --high_prio to the string of args. The jobs typically take about an hour.

Step 1: Creating IOVs

The first rule of creating IOVs is to break on hardware swaps whenever possible. In ECL, you can search for PMT swap and FEB swap forms to get a list of run numbers right after hardware swaps. About 300,000 rock muons are required to do the calibration. Some IOVs may be much longer than that if there are no hardware changes in the detector for a long time. It is also a good idea to break on changes to the beam configuration. This is not always possible, and not as important as hardware swaps. Special runs are often very short and do not provide enough rock muons to do the calibration, so you may have an IOV which contains special runs and regular runs, which is fine. But hardware swaps are very important because we expect the strip response to be different.

Once you have determined the IOVs, add the start and end run/subrun to s2seras.txt. This file is read in by a script later.

Step 2: Make the "master" script

The file make_s2s_script.py is used to generate a bash script which in turn will do the calibration for you. Edit it to add the correct ntuple location (the --outdir argument of Step 0) and software version that was used in Step 0. Once you've done this, simply call make_s2s_script.py and you will get a script master_s2s_script.sh out. Look at it and make sure it has all of the IOVs that you want. It will have two lines for each IOV, one that makes the output area, and the other that calls make_s2s.sh with some arguments pertaining to the IOV. It will have this for every IOV in s2seras.txt, but you might not want to generate constants for all of them every time.

Step 3: Make the constants

If you are just checking out the area fresh, you first need to compile some macros by just typing make.

Source the script master_s2s_script.sh. This should be done in a screen, as it will take a couple hours per IOV. That means if you are generating constans for many IOVs it can take a really long time. The output of this script is a file s2s_constants_<RUN>.txt for each IOV, where <RUN> is the starting run number of the IOV. It will also output a bunch of root files text files to output/s2s_<RUN>. Those can be used for debugging. Also, if you want to study why the error strips were classified as such, you can go to the validation area and do ./MakeErrorPlots which will produce a pdf with one page devoted to each error strip.

Step 4: Stage the constants for the DB

Log in as minervacal, and copy the constants files s2s_constants_<RUN>.txt to /minerva/data/calibrations/s2s_tables/minerva/vX, where X is the version number of the calibration. This has nothing to do with any other version, and is just used for organization within the s2s_tables area. The next thing you have to do is make a playlist. Look at one of the existing ones in /minerva/data/calibrations/s2s_tables (files are like minerva_s2s_vX_somedate.txt) and it should be pretty obvious what you need to do. Then copy the playlit file to your local computer, and stage it to the production database on the web:
http://dbweb4.fnal.gov:8080/mnvcon_prd_gui/app/GUI/fileBrowser
Click "Upload new playlist of data files" and select your playlist file. This does not actually load the database, only stages the constants to be loaded. Click "Show all files ready to be uploaded" and make sure that all your files are there. Then contact the database guru (Chris Marshall as of July 2014) who will load the constants to the DB. 

Step 5: Party.

Details of Step 3:

In Step 3, you executed a script that did 8 things sequentially in order to make the s2s table. Here we discuss what all those things do.  Basically we just go through the script make_s2s.sh and explain each step.

1. make_playlist.py

This script takes as arguments the ntuple location, the software version used to generate the ntuples (which need not be the same as the version used to run the script), and the start and end runs of the IOV. It produces a file playlist.txt which is just a list of subruns and the file path to each ntuple. It is read in by ReadNT and DoFitCorrection to get the ntuples.

2. PlexWriter

PlexWriter.cpp is a file that runs a simple Gaudi job to produce a small ntuple that contains an entry for each channel. The purpose of the Gaudi job is to access the plex to figure out which strips exist. Some physical addresses (module / plane / strip) which seem legit don't actually exist (for example module 9 is a passive target, which has no connected channels). The ntuple is used by MakeSummaryTuple as a convenient way to loop through channels. The actual plex information in the ntuple is not used, and there are certainly better ways to do this.

3. ReadNT

This script loops over the entries in the RockMuonCalibrationAlg ntuples (an entry is a rock muon) and produces a set of histograms which are used to generate the constants and determine whether each strip is OK or bad. The most important output is a 2D histogram of the detector, where each bin contains the interative truncated mean dEdX for a channel, and its uncertainty. The ntuples are obtained from the playlist.txt file. Within ReadNT.cxx, a 1D histogram of the energy for each channel is maintained (26,000 histograms). The truncated mean is determined iteratively, by considering only the range of (0.5x, 1.5x) where x is the truncated mean from the previous iteration. Another important histogram in this script is the zero fraction. This is defined as the fraction of the time when a given strip has at least 2 mm of reconstructed path length but no digit. You expect this to happen a few percent of the time due to Poisson fluctuations to 0 photoelectrons. Dead channels typically have higher zero fractions, and many are near 100%. The output of ReadNT is a ROOT file ReadNT.root containing the histograms.

4. MakeSummaryTuple

This script loops through channels and makes a smaller ntuple file with one entry per channel (~26,000 entries, instead of >300,000 rock muons). The entries are stuff like the truncated mean energy, the zero fraction, the RMS of the energy distribution, etc. and are used to determine the s2s constants and identify error channels. Error classifcation is done here and stored in the output ntuple, summary.root. This script takes about 5 seconds to run, so it is not compiled and just runs with CINT.

5. PrintConstants

This script looks at the entries in the summary.root ntuple from MakeSummaryTuple and determines the s2s constants. Its main output is the actual s2s constant table, a text file. The constants are determined by first looping through the channels to determine the average (1/dEdX) of the good channels. The constant for each channel is (1/dEdX) for the channel divided by the mean. By definition, the average s2s constant is 1.0. This script also outputs a list of error strips and some information about them which can be read in by MakeErrorPlots. Like MakeSummaryTuple, this takes 5 seconds to run so it isn't compiled.

6. DoFitCorrection

Ideally, we would use the fitted peak dEdX rather than the truncated mean. The peak is basically independent of the muon energy, while the truncated mean could have some small dependence on it. For most channels, the iterative truncated mean computed in ReadNT is about 4% higher than the fitted peak in DoFitCorrection. Deviations from this are due to differences in the shape of the energy distribution. These differences are due primarily to differences in scintillator (including aging) and different passive absorbers. These two effects are uniform throughout a plane (with the exception of the side ECAL), and we don't have enough statistics to reliably fit each channel, so the happy medium is using the truncated mean for the channel-to-channel calibration, then correcting each plane using an actual fit. The fit function is a 5th-order polynomial, which works really well in the peak region (not so well in the tail, but we don't fit the tail). The output of this script is a text file with each plane and its correction. The corrections are normalized to 1.0, and are typically small, differing from unity by a few percent at most.

7. IterateS2SConstants

S2S is iterative because the S2S constants affect the node positions, which in turn affect the track fit. The track fit affects the calculation of S2S because the path length is used. So the calibration is typically done in two iterations.  On the second iteration, the constants that you get out of PrintConstants are relative to the constants that were used to generate the ntuples. So the actual calibration constant for each channel is the product of the first version and the second, and also the plane-to-plane correction from the fit. There is an additional normalization step to ensure that the average s2s constant is 1.0, because even though each of the three are normalized to 1, the products need not be (though typically they are good to hundredths of a percent).

8. MakeTimeHeader

The RockMuonCalibrationAlg ntuples have an additional tree called "header" which just contains the start and end times for the file. ReadNT prints out a simple text file with two numbers, the start and end times for the whole IOV, in microseconds. The database has a standard header format which is human readable, and C++ has a very shitty time module, so only the microseconds are determined by ReadNT, and the human readable version is done here in python. This time_header.txt file is catted onto the final s2s constants file so the database can handle the time stamp correctly.

Comparison:

In the compare directory there is a script compare.py. The purpose of this script is to make plots of the s2s constants and the ratio of the s2s constants to the constant for the same channel of 1) the previous IOV or 2) the previous version of s2s. For channels that did not have hardware swaps, the s2s constants should change negligibly. The ratio should be within a couple percent of unity. The options are just booleans at the top of the file where you specify what comparisons you want to make, and where the files are.
