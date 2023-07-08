#-- start of make_header -----------------

#====================================
#  Library RockMuonCalibration
#
#   Generated Mon Jun 19 13:41:27 2023  by rvizarr
#
#====================================

include ${CMTROOT}/src/Makefile.core

ifdef tag
CMTEXTRATAGS = $(tag)
else
tag       = $(CMTCONFIG)
endif

cmt_RockMuonCalibration_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_RockMuonCalibration_has_target_tag

tags      = $(tag),$(CMTEXTRATAGS),target_RockMuonCalibration

RockMuonCalibration_tag = $(tag)

#cmt_local_tagfile_RockMuonCalibration = $(RockMuonCalibration_tag)_RockMuonCalibration.make
cmt_local_tagfile_RockMuonCalibration = $(bin)$(RockMuonCalibration_tag)_RockMuonCalibration.make

else

tags      = $(tag),$(CMTEXTRATAGS)

RockMuonCalibration_tag = $(tag)

#cmt_local_tagfile_RockMuonCalibration = $(RockMuonCalibration_tag).make
cmt_local_tagfile_RockMuonCalibration = $(bin)$(RockMuonCalibration_tag).make

endif

include $(cmt_local_tagfile_RockMuonCalibration)
#-include $(cmt_local_tagfile_RockMuonCalibration)

ifdef cmt_RockMuonCalibration_has_target_tag

cmt_final_setup_RockMuonCalibration = $(bin)setup_RockMuonCalibration.make
#cmt_final_setup_RockMuonCalibration = $(bin)RockMuonCalibration_RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibration_makefile = $(bin)RockMuonCalibration.make

else

cmt_final_setup_RockMuonCalibration = $(bin)setup.make
#cmt_final_setup_RockMuonCalibration = $(bin)RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibration_makefile = $(bin)RockMuonCalibration.make

endif

cmt_final_setup = $(bin)setup.make
#cmt_final_setup = $(bin)RockMuonCalibrationsetup.make

#RockMuonCalibration :: ;

dirs ::
	@if test ! -r requirements ; then echo "No requirements file" ; fi; \
	  if test ! -d $(bin) ; then $(mkdir) -p $(bin) ; fi

javadirs ::
	@if test ! -d $(javabin) ; then $(mkdir) -p $(javabin) ; fi

srcdirs ::
	@if test ! -d $(src) ; then $(mkdir) -p $(src) ; fi

help ::
	$(echo) 'RockMuonCalibration'

binobj = 
ifdef STRUCTURED_OUTPUT
binobj = RockMuonCalibration/
#RockMuonCalibration::
#	@if test ! -d $(bin)$(binobj) ; then $(mkdir) -p $(bin)$(binobj) ; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)$(binobj)
endif

ifdef use_requirements
$(use_requirements) : ;
endif

#-- end of make_header ------------------
#-- start of libary_header ---------------

RockMuonCalibrationlibname   = $(bin)$(library_prefix)RockMuonCalibration$(library_suffix)
RockMuonCalibrationlib       = $(RockMuonCalibrationlibname).a
RockMuonCalibrationstamp     = $(bin)RockMuonCalibration.stamp
RockMuonCalibrationshstamp   = $(bin)RockMuonCalibration.shstamp

RockMuonCalibration :: dirs  RockMuonCalibrationLIB
	$(echo) "RockMuonCalibration ok"

#-- end of libary_header ----------------
#-- start of libary ----------------------

RockMuonCalibrationLIB :: $(RockMuonCalibrationlib) $(RockMuonCalibrationshstamp)
	$(echo) "RockMuonCalibration : library ok"

$(RockMuonCalibrationlib) :: $(bin)MuonFuzzStudyAlg.o $(bin)PlexWriterAlg.o $(bin)RockMuonCalibrationAlg.o
	$(lib_echo) "static library $@"
	$(lib_silent) [ ! -f $@ ] || \rm -f $@
	$(lib_silent) $(ar) $(RockMuonCalibrationlib) $(bin)MuonFuzzStudyAlg.o $(bin)PlexWriterAlg.o $(bin)RockMuonCalibrationAlg.o
	$(lib_silent) $(ranlib) $(RockMuonCalibrationlib)
	$(lib_silent) cat /dev/null >$(RockMuonCalibrationstamp)

#------------------------------------------------------------------
#  Future improvement? to empty the object files after
#  storing in the library
#
##	  for f in $?; do \
##	    rm $${f}; touch $${f}; \
##	  done
#------------------------------------------------------------------

#
# We add one level of dependency upon the true shared library 
# (rather than simply upon the stamp file)
# this is for cases where the shared library has not been built
# while the stamp was created (error??) 
#

$(RockMuonCalibrationlibname).$(shlibsuffix) :: $(RockMuonCalibrationlib) requirements $(use_requirements) $(RockMuonCalibrationstamps)
	$(lib_echo) "shared library $@"
	$(lib_silent) if test "$(makecmd)"; then QUIET=; else QUIET=1; fi; QUIET=$${QUIET} bin=$(bin) $(make_shlib) "$(tags)" RockMuonCalibration $(RockMuonCalibration_shlibflags)

$(RockMuonCalibrationshstamp) :: $(RockMuonCalibrationlibname).$(shlibsuffix)
	$(lib_silent) if test -f $(RockMuonCalibrationlibname).$(shlibsuffix) ; then cat /dev/null >$(RockMuonCalibrationshstamp) ; fi

RockMuonCalibrationclean ::
	$(cleanup_echo) objects RockMuonCalibration
	$(cleanup_silent) /bin/rm -f $(bin)MuonFuzzStudyAlg.o $(bin)PlexWriterAlg.o $(bin)RockMuonCalibrationAlg.o
	$(cleanup_silent) /bin/rm -f $(patsubst %.o,%.d,$(bin)MuonFuzzStudyAlg.o $(bin)PlexWriterAlg.o $(bin)RockMuonCalibrationAlg.o) $(patsubst %.o,%.dep,$(bin)MuonFuzzStudyAlg.o $(bin)PlexWriterAlg.o $(bin)RockMuonCalibrationAlg.o) $(patsubst %.o,%.d.stamp,$(bin)MuonFuzzStudyAlg.o $(bin)PlexWriterAlg.o $(bin)RockMuonCalibrationAlg.o)
	$(cleanup_silent) cd $(bin); /bin/rm -rf RockMuonCalibration_deps RockMuonCalibration_dependencies.make

#-----------------------------------------------------------------
#
#  New section for automatic installation
#
#-----------------------------------------------------------------

install_dir = ${CMTINSTALLAREA}/$(tag)/lib
RockMuonCalibrationinstallname = $(library_prefix)RockMuonCalibration$(library_suffix).$(shlibsuffix)

RockMuonCalibration :: RockMuonCalibrationinstall

install :: RockMuonCalibrationinstall

RockMuonCalibrationinstall :: $(install_dir)/$(RockMuonCalibrationinstallname)
ifdef CMTINSTALLAREA
	$(echo) "installation done"
endif

$(install_dir)/$(RockMuonCalibrationinstallname) :: $(bin)$(RockMuonCalibrationinstallname)
ifdef CMTINSTALLAREA
	$(install_silent) $(cmt_install_action) \
	    -source "`(cd $(bin); pwd)`" \
	    -name "$(RockMuonCalibrationinstallname)" \
	    -out "$(install_dir)" \
	    -cmd "$(cmt_installarea_command)" \
	    -cmtpath "$($(package)_cmtpath)"
endif

##RockMuonCalibrationclean :: RockMuonCalibrationuninstall

uninstall :: RockMuonCalibrationuninstall

RockMuonCalibrationuninstall ::
ifdef CMTINSTALLAREA
	$(cleanup_silent) $(cmt_uninstall_action) \
	    -source "`(cd $(bin); pwd)`" \
	    -name "$(RockMuonCalibrationinstallname)" \
	    -out "$(install_dir)" \
	    -cmtpath "$($(package)_cmtpath)"
endif

#-- end of libary -----------------------
#-- start of dependency ------------------
ifneq ($(MAKECMDGOALS),RockMuonCalibrationclean)
ifneq ($(MAKECMDGOALS),uninstall)

#$(bin)RockMuonCalibration_dependencies.make :: dirs

ifndef QUICK
$(bin)RockMuonCalibration_dependencies.make : $(src)MuonFuzzStudyAlg.cpp $(src)PlexWriterAlg.cpp $(src)RockMuonCalibrationAlg.cpp $(use_requirements) $(cmt_final_setup_RockMuonCalibration)
	$(echo) "(RockMuonCalibration.make) Rebuilding $@"; \
	  $(build_dependencies) RockMuonCalibration -all_sources -out=$@ $(src)MuonFuzzStudyAlg.cpp $(src)PlexWriterAlg.cpp $(src)RockMuonCalibrationAlg.cpp
endif

#$(RockMuonCalibration_dependencies)

-include $(bin)RockMuonCalibration_dependencies.make

endif
endif
#-- end of dependency -------------------
#-- start of cpp_library -----------------

ifneq ($(MAKECMDGOALS),RockMuonCalibrationclean)
ifneq ($(MAKECMDGOALS),uninstall)
-include $(bin)$(binobj)MuonFuzzStudyAlg.d
endif
endif


$(bin)$(binobj)MuonFuzzStudyAlg.o $(bin)$(binobj)MuonFuzzStudyAlg.d : $(src)MuonFuzzStudyAlg.cpp  $(use_requirements) $(cmt_final_setup_RockMuonCalibration)
	$(cpp_echo) $(src)MuonFuzzStudyAlg.cpp
	@mkdir -p $(@D)
	$(cpp_silent) $(cppcomp) $(use_pp_cppflags) $(RockMuonCalibration_pp_cppflags) $(app_RockMuonCalibration_pp_cppflags) $(MuonFuzzStudyAlg_pp_cppflags) $(use_cppflags) $(RockMuonCalibration_cppflags) $(lib_RockMuonCalibration_cppflags) $(app_RockMuonCalibration_cppflags) $(MuonFuzzStudyAlg_cppflags) $(MuonFuzzStudyAlg_cpp_cppflags)  -MP -MMD -MT $(bin)$(binobj)MuonFuzzStudyAlg.o -MT $(bin)$(binobj)MuonFuzzStudyAlg.d -MF $(bin)$(binobj)MuonFuzzStudyAlg.d -o $(bin)$(binobj)MuonFuzzStudyAlg.o $(src)MuonFuzzStudyAlg.cpp


#-- end of cpp_library ------------------
#-- start of cpp_library -----------------

ifneq ($(MAKECMDGOALS),RockMuonCalibrationclean)
ifneq ($(MAKECMDGOALS),uninstall)
-include $(bin)$(binobj)PlexWriterAlg.d
endif
endif


$(bin)$(binobj)PlexWriterAlg.o $(bin)$(binobj)PlexWriterAlg.d : $(src)PlexWriterAlg.cpp  $(use_requirements) $(cmt_final_setup_RockMuonCalibration)
	$(cpp_echo) $(src)PlexWriterAlg.cpp
	@mkdir -p $(@D)
	$(cpp_silent) $(cppcomp) $(use_pp_cppflags) $(RockMuonCalibration_pp_cppflags) $(app_RockMuonCalibration_pp_cppflags) $(PlexWriterAlg_pp_cppflags) $(use_cppflags) $(RockMuonCalibration_cppflags) $(lib_RockMuonCalibration_cppflags) $(app_RockMuonCalibration_cppflags) $(PlexWriterAlg_cppflags) $(PlexWriterAlg_cpp_cppflags)  -MP -MMD -MT $(bin)$(binobj)PlexWriterAlg.o -MT $(bin)$(binobj)PlexWriterAlg.d -MF $(bin)$(binobj)PlexWriterAlg.d -o $(bin)$(binobj)PlexWriterAlg.o $(src)PlexWriterAlg.cpp


#-- end of cpp_library ------------------
#-- start of cpp_library -----------------

ifneq ($(MAKECMDGOALS),RockMuonCalibrationclean)
ifneq ($(MAKECMDGOALS),uninstall)
-include $(bin)$(binobj)RockMuonCalibrationAlg.d
endif
endif


$(bin)$(binobj)RockMuonCalibrationAlg.o $(bin)$(binobj)RockMuonCalibrationAlg.d : $(src)RockMuonCalibrationAlg.cpp  $(use_requirements) $(cmt_final_setup_RockMuonCalibration)
	$(cpp_echo) $(src)RockMuonCalibrationAlg.cpp
	@mkdir -p $(@D)
	$(cpp_silent) $(cppcomp) $(use_pp_cppflags) $(RockMuonCalibration_pp_cppflags) $(app_RockMuonCalibration_pp_cppflags) $(RockMuonCalibrationAlg_pp_cppflags) $(use_cppflags) $(RockMuonCalibration_cppflags) $(lib_RockMuonCalibration_cppflags) $(app_RockMuonCalibration_cppflags) $(RockMuonCalibrationAlg_cppflags) $(RockMuonCalibrationAlg_cpp_cppflags)  -MP -MMD -MT $(bin)$(binobj)RockMuonCalibrationAlg.o -MT $(bin)$(binobj)RockMuonCalibrationAlg.d -MF $(bin)$(binobj)RockMuonCalibrationAlg.d -o $(bin)$(binobj)RockMuonCalibrationAlg.o $(src)RockMuonCalibrationAlg.cpp


#-- end of cpp_library ------------------
#-- start of cleanup_header --------------

clean :: RockMuonCalibrationclean ;
#	@cd .

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(RockMuonCalibration.make) $@: No rule for such target" >&2
#	@echo "#CMT> Warning: $@: No rule for such target" >&2; exit
	if echo $@ | grep '$(package)setup\.make$$' >/dev/null; then\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibration.make): $@: File no longer generated" >&2; exit 0; fi
else
.DEFAULT::
	$(echo) "(RockMuonCalibration.make) PEDANTIC: $@: No rule for such target" >&2
	if echo $@ | grep '$(package)setup\.make$$' >/dev/null; then\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibration.make): $@: File no longer generated" >&2; exit 0;\
	 elif test $@ = "$(cmt_final_setup)" -o\
	 $@ = "$(cmt_final_setup_RockMuonCalibration)" ; then\
	 found=n; for s in 1 2 3 4 5; do\
	 sleep $$s; test ! -f $@ || { found=y; break; }\
	 done; if test $$found = n; then\
	 test -z "$(cmtmsg)" ||\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibration.make) PEDANTIC: $@: Seems to be missing. Ignore it for now" >&2; exit 0 ; fi;\
	 elif test `expr $@ : '.*/'` -ne 0 ; then\
	 test -z "$(cmtmsg)" ||\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibration.make) PEDANTIC: $@: Seems to be a missing file. Please check" >&2; exit 2 ; \
	 else\
	 test -z "$(cmtmsg)" ||\
	 echo "$(CMTMSGPREFIX)" "(RockMuonCalibration.make) PEDANTIC: $@: Seems to be a fake target due to some pattern. Just ignore it" >&2 ; exit 0; fi
endif

RockMuonCalibrationclean ::
#-- end of cleanup_header ---------------
#-- start of cleanup_library -------------
	$(cleanup_echo) library RockMuonCalibration
	-$(cleanup_silent) cd $(bin); /bin/rm -f $(library_prefix)RockMuonCalibration$(library_suffix).a $(library_prefix)RockMuonCalibration$(library_suffix).s? RockMuonCalibration.stamp RockMuonCalibration.shstamp
#-- end of cleanup_library ---------------
