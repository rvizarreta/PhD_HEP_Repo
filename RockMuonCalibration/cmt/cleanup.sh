if test "${CMTROOT}" = ""; then
  CMTROOT=/cvmfs/minerva.opensciencegrid.org/minerva/software_releases/lcgcmake/lcg_61a_forSL7/external/cmt/v1r20p20090520/x86_64-slc7-gcc49-opt/CMT/v1r20p20090520; export CMTROOT
fi
. ${CMTROOT}/mgr/setup.sh
tempfile=`${CMTROOT}/mgr/cmt -quiet build temporary_name`
if test ! $? = 0 ; then tempfile=/tmp/cmt.$$; fi
${CMTROOT}/mgr/cmt cleanup -sh -pack=RockMuonCalibration -version=${MINERVA_RELEASE} -path=/minerva/app/users/rvizarr/cmtuser/Minerva_v22r1p1_2x2/Cal $* >${tempfile}; . ${tempfile}
/bin/rm -f ${tempfile}

