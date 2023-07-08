#-- start of make_header -----------------

#====================================
#  Document RockMuonCalibrationMergeMap
#
#   Generated Mon Jun 19 13:41:53 2023  by rvizarr
#
#====================================

include ${CMTROOT}/src/Makefile.core

ifdef tag
CMTEXTRATAGS = $(tag)
else
tag       = $(CMTCONFIG)
endif

cmt_RockMuonCalibrationMergeMap_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_RockMuonCalibrationMergeMap_has_target_tag

tags      = $(tag),$(CMTEXTRATAGS),target_RockMuonCalibrationMergeMap

RockMuonCalibration_tag = $(tag)

#cmt_local_tagfile_RockMuonCalibrationMergeMap = $(RockMuonCalibration_tag)_RockMuonCalibrationMergeMap.make
cmt_local_tagfile_RockMuonCalibrationMergeMap = $(bin)$(RockMuonCalibration_tag)_RockMuonCalibrationMergeMap.make

else

tags      = $(tag),$(CMTEXTRATAGS)

RockMuonCalibration_tag = $(tag)

#cmt_local_tagfile_RockMuonCalibrationMergeMap = $(RockMuonCalibration_tag).make
cmt_local_tagfile_RockMuonCalibrationMergeMap = $(bin)$(RockMuonCalibration_tag).make

endif

include $(cmt_local_tagfile_RockMuonCalibrationMergeMap)
#-include $(cmt_local_tagfile_RockMuonCalibrationMergeMap)

ifdef cmt_RockMuonCalibrationMergeMap_has_target_tag

cmt_final_setup_RockMuonCalibrationMergeMap = $(bin)setup_RockMuonCalibrationMergeMap.make
#cmt_final_setup_RockMuonCalibrationMergeMap = $(bin)RockMuonCalibration_RockMuonCalibrationMergeMapsetup.make
cmt_local_RockMuonCalibrationMergeMap_makefile = $(bin)RockMuonCalibrationMergeMap.make

else

cmt_final_setup_RockMuonCalibrationMergeMap = $(bin)setup.make
#cmt_final_setup_RockMuonCalibrationMergeMap = $(bin)RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibrationMergeMap_makefile = $(bin)RockMuonCalibrationMergeMap.make

endif

cmt_final_setup = $(bin)setup.make
#cmt_final_setup = $(bin)RockMuonCalibrationsetup.make

#RockMuonCalibrationMergeMap :: ;

dirs ::
	@if test ! -r requirements ; then echo "No requirements file" ; fi; \
	  if test ! -d $(bin) ; then $(mkdir) -p $(bin) ; fi

javadirs ::
	@if test ! -d $(javabin) ; then $(mkdir) -p $(javabin) ; fi

srcdirs ::
	@if test ! -d $(src) ; then $(mkdir) -p $(src) ; fi

help ::
	$(echo) 'RockMuonCalibrationMergeMap'

binobj = 
ifdef STRUCTURED_OUTPUT
binobj = RockMuonCalibrationMergeMap/
#RockMuonCalibrationMergeMap::
#	@if test ! -d $(bin)$(binobj) ; then $(mkdir) -p $(bin)$(binobj) ; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)$(binobj)
endif

ifdef use_requirements
$(use_requirements) : ;
endif

#-- end of make_header ------------------
# File: cmt/fragments/merge_rootmap_header
# Author: Sebastien Binet (binet@cern.ch)

# Makefile fragment to merge a <library>.rootmap file into a single
# <project>.rootmap file in the (lib) install area
# If no InstallArea is present the fragment is dummy


.PHONY: RockMuonCalibrationMergeMap RockMuonCalibrationMergeMapclean

# default is already '#'
#genmap_comment_char := "'#'"

rootMapRef    := ../$(tag)/RockMuonCalibration.rootmap

ifdef CMTINSTALLAREA
rootMapDir    := ${CMTINSTALLAREA}/$(tag)/lib
mergedRootMap := $(rootMapDir)/$(project).rootmap
stampRootMap  := $(rootMapRef).stamp
else
rootMapDir    := ../$(tag)
mergedRootMap := 
stampRootMap  :=
endif

RockMuonCalibrationMergeMap :: $(stampRootMap) $(mergedRootMap)
	@:

.NOTPARALLEL : $(stampRootMap) $(mergedRootMap)

$(stampRootMap) $(mergedRootMap) :: $(rootMapRef)
	@echo "Running merge_rootmap  RockMuonCalibrationMergeMap" 
	$(merge_rootmap_cmd) --do-merge \
         --input-file $(rootMapRef) --merged-file $(mergedRootMap)

RockMuonCalibrationMergeMapclean ::
	$(cleanup_silent) $(merge_rootmap_cmd) --un-merge \
         --input-file $(rootMapRef) --merged-file $(mergedRootMap) ;
	$(cleanup_silent) $(remove_command) $(stampRootMap)
libRockMuonCalibration_so_dependencies = ../x86_64-slc7-gcc49-opt/libRockMuonCalibration.so
#-- start of cleanup_header --------------

clean :: RockMuonCalibrationMergeMapclean ;
#	@cd .

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(RockMuonCalibrationMergeMap.make) $@: No rule for such target" >&2
#	@echo "#CMT> Warning: $@: No rule for such target" >&2; exit
	if echo $@ | grep '$(package)setup\.make$$' >/dev/null; then\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationMergeMap.make): $@: File no longer generated" >&2; exit 0; fi
else
.DEFAULT::
	$(echo) "(RockMuonCalibrationMergeMap.make) PEDANTIC: $@: No rule for such target" >&2
	if echo $@ | grep '$(package)setup\.make$$' >/dev/null; then\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationMergeMap.make): $@: File no longer generated" >&2; exit 0;\
	 elif test $@ = "$(cmt_final_setup)" -o\
	 $@ = "$(cmt_final_setup_RockMuonCalibrationMergeMap)" ; then\
	 found=n; for s in 1 2 3 4 5; do\
	 sleep $$s; test ! -f $@ || { found=y; break; }\
	 done; if test $$found = n; then\
	 test -z "$(cmtmsg)" ||\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationMergeMap.make) PEDANTIC: $@: Seems to be missing. Ignore it for now" >&2; exit 0 ; fi;\
	 elif test `expr $@ : '.*/'` -ne 0 ; then\
	 test -z "$(cmtmsg)" ||\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationMergeMap.make) PEDANTIC: $@: Seems to be a missing file. Please check" >&2; exit 2 ; \
	 else\
	 test -z "$(cmtmsg)" ||\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibrationMergeMap.make) PEDANTIC: $@: Seems to be a fake target due to some pattern. Just ignore it" >&2 ; exit 0; fi
endif

RockMuonCalibrationMergeMapclean ::
#-- end of cleanup_header ---------------
