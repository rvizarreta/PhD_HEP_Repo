source /grid/fermiapp/minerva/software_releases/v10r7p3/setup.sh
cd /minerva/app/users/minervacal/cmtuser/Minerva_v10r7p3_monitor/Top/MinervaSys/cmt
source setup.sh

cd /minerva/app/users/minervacal/cmtuser/Minerva_v10r7p3_monitor/Cal/RockMuonCalibration/scripts/monitoring
python make_AEM_plots.py
