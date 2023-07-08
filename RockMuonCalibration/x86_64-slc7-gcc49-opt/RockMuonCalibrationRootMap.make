#-- start of make_header -----------------

#====================================
#  Document RockMuonCalibrationRootMap
#
#   Generated Mon Jun 19 13:41:52 2023  by rvizarr
#
#====================================

include ${CMTROOT}/src/Makefile.core

ifdef tag
CMTEXTRATAGS = $(tag)
else
tag       = $(CMTCONFIG)
endif

cmt_RockMuonCalibrationRootMap_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_RockMuonCalibrationRootMap_has_target_tag

tags      = $(tag),$(CMTEXTRATAGS),target_RockMuonCalibrationRootMap

RockMuonCalibration_tag = $(tag)

#cmt_local_tagfile_RockMuonCalibrationRootMap = $(RockMuonCalibration_tag)_RockMuonCalibrationRootMap.make
cmt_local_tagfile_RockMuonCalibrationRootMap = $(bin)$(RockMuonCalibration_tag)_RockMuonCalibrationRootMap.make

else

tags      = $(tag),$(CMTEXTRATAGS)

RockMuonCalibration_tag = $(tag)

#cmt_local_tagfile_RockMuonCalibrationRootMap = $(RockMuonCalibration_tag).make
cmt_local_tagfile_RockMuonCalibrationRootMap = $(bin)$(RockMuonCalibration_tag).make

endif

include $(cmt_local_tagfile_RockMuonCalibrationRootMap)
#-include $(cmt_local_tagfile_RockMuonCalibrationRootMap)

ifdef cmt_RockMuonCalibrationRootMap_has_target_tag

cmt_final_setup_RockMuonCalibrationRootMap = $(bin)setup_RockMuonCalibrationRootMap.make
#cmt_final_setup_RockMuonCalibrationRootMap = $(bin)RockMuonCalibration_RockMuonCalibrationRootMapsetup.make
cmt_local_RockMuonCalibrationRootMap_makefile = $(bin)RockMuonCalibrationRootMap.make

else

cmt_final_setup_RockMuonCalibrationRootMap = $(bin)setup.make
#cmt_final_setup_RockMuonCalibrationRootMap = $(bin)RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibrationRootMap_makefile = $(bin)RockMuonCalibrationRootMap.make

endif

cmt_final_setup = $(bin)setup.make
#cmt_final_setup = $(bin)RockMuonCalibrationsetup.make

#RockMuonCalibrationRootMap :: ;

dirs ::
	@if test ! -r requirements ; then echo "No requirements file" ; fi; \
	  if test ! -d $(bin) ; then $(mkdir) -p $(bin) ; fi

javadirs ::
	@if test ! -d $(javabin) ; then $(mkdir) -p $(javabin) ; fi

srcdirs ::
	@if test ! -d $(src) ; then $(mkdir) -p $(src) ; fi

help ::
	$(echo) 'RockMuonCalibrationRootMap'

binobj = 
ifdef STRUCTURED_OUTPUT
binobj = RockMuonCalibrationRootMap/
#RockMuonCalibrationRootMap::
#	@if test ! -d $(bin)$(binobj) ; then $(mkdir) -p $(bin)$(binobj) ; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)$(binobj)
endif

ifdef use_requirements
$(use_requirements) : ;
endif

#-- end of make_header ------------------
##
rootmapfile = RockMuonCalibration.rootmap
ROOTMAP_DIR = ../$(tag)
fulllibname = libRockMuonCalibration.$(shlibsuffix)

RockMuonCalibrationRootMap :: ${ROOTMAP_DIR}/$(rootmapfile)
	@:

${ROOTMAP_DIR}/$(rootmapfile) :: $(bin)$(fulllibname)
	@echo 'Generating rootmap file for $(fulllibname)'
	cd ../$(tag);$(genmap_cmd) -i $(fulllibname) -o ${ROOTMAP_DIR}/$(rootmapfile) $(RockMuonCalibrationRootMap_genmapflags)

install :: RockMuonCalibrationRootMapinstall
RockMuonCalibrationRootMapinstall :: RockMuonCalibrationRootMap

uninstall :: RockMuonCalibrationRootMapuninstall
RockMuonCalibrationRootMapuninstall :: RockMuonCalibrationRootMapclean

RockMuonCalibrationRootMapclean ::
	@echo 'Deleting $(rootmapfile)'
	@rm -f ${ROOTMAP_DIR}/$(rootmapfile)

#-- start of cleanup_header --------------

clean :: RockMuonCalibrationRootMapclean ;
#	@cd .

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(RockMuonCalibrationRootMap.make) $@: No rule for such target" >&2
#	@echo "#CMT> Warning: $@: No rule for such target" >&2; exit
	if echo $@ | grep '$(package)setup\.make$$' >/dev/null; then\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationRootMap.make): $@: File no longer generated" >&2; exit 0; fi
else
.DEFAULT::
	$(echo) "(RockMuonCalibrationRootMap.make) PEDANTIC: $@: No rule for such target" >&2
	if echo $@ | grep '$(package)setup\.make$$' >/dev/null; then\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationRootMap.make): $@: File no longer generated" >&2; exit 0;\
	 elif test $@ = "$(cmt_final_setup)" -o\
	 $@ = "$(cmt_final_setup_RockMuonCalibrationRootMap)" ; then\
	 found=n; for s in 1 2 3 4 5; do\
	 sleep $$s; test ! -f $@ || { found=y; break; }\
	 done; if test $$found = n; then\
	 test -z "$(cmtmsg)" ||\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationRootMap.make) PEDANTIC: $@: Seems to be missing. Ignore it for now" >&2; exit 0 ; fi;\
	 elif test `expr $@ : '.*/'` -ne 0 ; then\
	 test -z "$(cmtmsg)" ||\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationRootMap.make) PEDANTIC: $@: Seems to be a missing file. Please check" >&2; exit 2 ; \
	 else\
	 test -z "$(cmtmsg)" ||\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationRootMap.make) PEDANTIC: $@: Seems to be a fake target due to some pattern. Just ignore it" >&2 ; exit 0; fi
endif

RockMuonCalibrationRootMapclean ::
#-- end of cleanup_header ---------------
