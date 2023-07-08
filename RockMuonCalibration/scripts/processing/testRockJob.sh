output=/pnfs/minerva/scratch/users/minervacal/RockMuonTest
#ROCKMUONCALIBRATIONROOT=/cvmfs/minerva.opensciencegrid.org/minerva/Minerva_RockMuon/Minerva_v10r9p1_monitoring/Cal/RockMuonCalibration
playlistdir=/minerva/app/users/minervacal/cmtuser/Minerva_v10r9p1_monitoring/Cal/RockMuonCalibration
if [[ -d $output ]]; then
  echo Please remove output directory.
  return 1
fi
python ${PRODUCTIONSCRIPTSROOT}/data_scripts/SubmitDataRuns.py \
  --playlist ${playlistdir}/scripts/processing/test_playlist.txt \
  --arg "--rockmumonitoring --raw_digits --use_role_calibration --nightly_subgroup --usecat --outdir ${output} --dst --calib_stage monitoring"
