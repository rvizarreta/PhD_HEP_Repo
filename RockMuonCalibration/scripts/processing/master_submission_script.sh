#!/bin/bash

#export KEYTAB=/var/adm/krb5/`/usr/krb5/bin/kcron -f`
#export KEYUSER=`/usr/krb5/bin/klist -k ${KEYTAB} | grep FNAL.GOV | cut -c 5- | cut -f 1 -d /` | head -n 1
#export KEYUSER="marshalc"
#/usr/krb5/bin/kinit -5 -A  -kt ${KEYTAB} ${KEYUSER}/cron/`hostname`@FNAL.GOV

release=v21r1p1

#. /grid/fermiapp/minerva/software_releases/v10r9p1/setup.sh
. /cvmfs/minerva.opensciencegrid.org/minerva/software_releases/${release}/setup.sh
# export IFDH_VERSION=v2_0_8

# setup jobsub_client to use for the submission
# setup jobsub_client -z /grid/fermiapp/products/common/db
  
cd /minerva/app/users/${USER}/cmtuser/Minerva_${release}_monitoring/Tools/ProductionScripts
. cmt/setup.sh
#. /minerva/app/users/minervacal/cmtuser/Minerva_v10r9p1_monitoring/Tools/ProductionScripts/cmt/setup.sh
#. /minerva/app/users/minervacal/cmtuser/Minerva_v10r9p1_monitoring/Cal/RockMuonCalibration/cmt/setup.sh
cd ${ROCKMUONCALIBRATIONROOT}
. cmt/setup.sh

#export MINERVA_SUBMIT_HOST="gpsn01.fnal.gov"

#special user grid proxy
export X509_USER_PROXY=/opt/minervacal/minervacal.Calibration.proxy
export GROUP=minerva

cd ${ROCKMUONCALIBRATIONROOT}/scripts/processing

python submitGridJobs.py

