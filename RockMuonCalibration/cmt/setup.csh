# echo "Setting RockMuonCalibration ${MINERVA_RELEASE} in /minerva/app/users/rvizarr/cmtuser/Minerva_v22r1p1_2x2/Cal"

if ( $?CMTROOT == 0 ) then
  setenv CMTROOT /cvmfs/minerva.opensciencegrid.org/minerva/software_releases/lcgcmake/lcg_61a_forSL7/external/cmt/v1r20p20090520/x86_64-slc7-gcc49-opt/CMT/v1r20p20090520
endif
source ${CMTROOT}/mgr/setup.csh

set tempfile=`${CMTROOT}/mgr/cmt -quiet build temporary_name`
if $status != 0 then
  set tempfile=/tmp/cmt.$$
endif
${CMTROOT}/mgr/cmt setup -csh -pack=RockMuonCalibration -version=${MINERVA_RELEASE} -path=/minerva/app/users/rvizarr/cmtuser/Minerva_v22r1p1_2x2/Cal  -no_cleanup $* >${tempfile}; source ${tempfile}
/bin/rm -f ${tempfile}

