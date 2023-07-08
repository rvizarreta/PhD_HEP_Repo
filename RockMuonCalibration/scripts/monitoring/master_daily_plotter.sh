#!/bin/bash

# Destroy any residual permissions to allow for quicker diagnosis of authentication problems
kdestroy

# set up special kerberos principal to copy stuff to /web/sites
PRINCIPAL=minerva-online/minerva/minerva-om.fnal.gov@FNAL.GOV

KEYTAB=/opt/minervacal/krb-s.keytab

export KRB5CCNAME=FILE:/tmp/krb5cc_minervacal_nusoftweb

KINIT=/usr/krb5/bin/kinit

${KINIT} -5 -A  -k -t ${KEYTAB} ${PRINCIPAL}

. /grid/fermiapp/minerva/software_releases/v10r9p1/setup.sh
cd /minerva/app/users/minervacal/cmtuser/Minerva_v10r9p1_monitoring/Top/MinervaSys/cmt
. /minerva/app/users/minervacal/cmtuser/Minerva_v10r9p1_monitoring/Top/MinervaSys/cmt/setup.sh
cd /minerva/app/users/minervacal/cmtuser/Minerva_v10r9p1_monitoring/Cal/RockMuonCalibration/cmt
. /minerva/app/users/minervacal/cmtuser/Minerva_v10r9p1_monitoring/Cal/RockMuonCalibration/cmt/setup.sh

cd /minerva/app/users/minervacal/cmtuser/Minerva_v10r9p1_monitoring/Cal/RockMuonCalibration/scripts/monitoring

python make_plots.py
