#!/bin/sh
#
# maks_s2s.sh
#
# Reads ntuples and creates s2s_constants.txt
#
# Arguments: data_processing_path version run1 subrun1 run2 subrun2
#
cd $ROCKMUONCALIBRATIONROOT/scripts/s2s

python make_playlist.py $*

if [ ! -f playlist.txt ]
then
  echo 'Could not make playlist!'
#  exit 1
fi

echo '******************************'
echo '***** Creating plex map ******'
echo '******************************'

RUN=`head -n 1 playlist.txt | cut -d ' ' -f 1`

cd $ROCKMUONCALIBRATIONROOT/options

cp PlexWriter.opts PlexWriterRun$RUN.opts
echo "PlexWriterAlg.RunNumber = $RUN;" >> PlexWriterRun$RUN.opts
if [ $RUN -le 1999 ]
then
  # Old geometry?
  #echo "DetectorDataSvc.DetDbLocation = \"$MINERVA_GEOMETRY/Frozen.xml\";" >> PlexWriterRun$RUN.opts
  # New geometry
  echo "DetectorDataSvc.DetDbLocation = \"$MINERVA_GEOMETRY/MINERVA2x2.xml\";" >> PlexWriterRun$RUN.opts
fi

OUTDIR=$ROCKMUONCALIBRATIONROOT/scripts/s2s/output/s2s_$RUN

Gaudi.exe PlexWriterRun$RUN.opts

if [ ! -f plex.root ]
then
  echo 'Could not make plex map!'
  #exit 1
fi

mv plex.root $ROCKMUONCALIBRATIONROOT/scripts/s2s

echo '*****************************'
echo '***** Reading Ntuples *******'
echo '*****************************'

cd $ROCKMUONCALIBRATIONROOT/scripts/s2s

./ReadNT

if [ ! -f ReadNT.root ]
then
  echo 'Could not read ntuples!'
#  exit 1
fi

# NOT INTERESTED FOR ALIGNMENT PURPOSES

echo '**********************************'
echo '***** Creating summary tuple *****'
echo '**********************************'

root -l -q -b MakeSummaryTuple.C

if [ ! -f summary.root ]
then
  echo 'Could not make summary tuple!'
#  exit 1
fi

echo '*********************************'
echo '***** Creating constants ********'
echo '*********************************'

root -l -q -b PrintConstants.C

if [ ! -f s2s_constants_new.txt ]
then
  echo 'Could not make s2s constants!'
#  exit 1
fi

./DoFitCorrection

if [ ! -f fit_corrections.txt ]
then
  echo 'Could not make fit correction file!'
#  exit 1
fi

# For Eroica calibrations: DB was used for first iteration, so grab the constants from the staging area
if [ $RUN -le 1999 ]
then
  if [ $RUN -le 999 ]
  then
  cp /minerva/data/calibrations/s2s_tables/minerva/v5/s2s_constants_gen2_prime_0$RUN.txt s2s_constants_old.txt
  else
  cp /minerva/data/calibrations/s2s_tables/minerva/v5/s2s_constants_gen2_prime_$RUN.txt s2s_constants_old.txt
  fi
else
  cp /minerva/data/calibrations/s2s_tables/minerva/v5/s2s_constants_$RUN.txt s2s_constants_old.txt
fi

# assumes s2s_constats_old.txt is the file that has the constants that were applied during processing

python IterateS2SConstants.py

if [ ! -f s2s_constants.txt ]
then
  echo 'Iteration combination step has failed!'
#  exit 1
fi

python MakeTimeHeader.py

cat time_header2.txt s2s_constants.txt > s2s_constants_$RUN.txt
#rm s2s_constants.txt
#mv time_header2.txt $OUTDIR/time_header.txt
#rm time_header.txt
#mv ReadNT.root $OUTDIR
#mv error_strips.txt $OUTDIR
#mv s2s_constants_new.txt $OUTDIR
#mv s2s_constants_old.txt $OUTDIR
#mv plex.root $OUTDIR
#mv summary.root $OUTDIR
#mv playlist.txt $OUTDIR
#mv FitCorrection.root $OUTDIR
#mv fit_corrections.txt $OUTDIR

echo '****************************'
echo '********* Done! ************'
echo '****************************'

# go back to the main area to start the next one
cd $ROCKMUONCALIBRATIONROOT/scripts/s2s

