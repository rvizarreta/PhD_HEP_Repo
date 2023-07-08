
#-- start of constituents_header ------

include ${CMTROOT}/src/Makefile.core

ifdef tag
CMTEXTRATAGS = $(tag)
else
tag       = $(CMTCONFIG)
endif

tags      = $(tag),$(CMTEXTRATAGS)

RockMuonCalibration_tag = $(tag)

#cmt_local_tagfile = $(RockMuonCalibration_tag).make
cmt_local_tagfile = $(bin)$(RockMuonCalibration_tag).make

#-include $(cmt_local_tagfile)
include $(cmt_local_tagfile)

#cmt_local_setup = $(bin)setup$$$$.make
#cmt_local_setup = $(bin)$(package)setup$$$$.make
#cmt_final_setup = $(bin)RockMuonCalibrationsetup.make
cmt_final_setup = $(bin)setup.make
#cmt_final_setup = $(bin)$(package)setup.make

#--------------------------------------------------------

#cmt_lock_setup = /tmp/lock$(cmt_lock_pid).make
#cmt_temp_tag = /tmp/tag$(cmt_lock_pid).make

#first :: $(cmt_local_tagfile)
#	@echo $(cmt_local_tagfile) ok
#ifndef QUICK
#first :: $(cmt_final_setup) ;
#else
#first :: ;
#endif

##	@bin=`$(cmtexe) show macro_value bin`

#$(cmt_local_tagfile) : $(cmt_lock_setup)
#	@echo "#CMT> Error: $@: No such file" >&2; exit 1
#$(cmt_local_tagfile) :
#	@echo "#CMT> Warning: $@: No such file" >&2; exit
#	@echo "#CMT> Info: $@: No need to rebuild file" >&2; exit

#$(cmt_final_setup) : $(cmt_local_tagfile) 
#	$(echo) "(constituents.make) Rebuilding $@"
#	@if test ! -d $(@D); then $(mkdir) -p $(@D); fi; \
#	  if test -f $(cmt_local_setup); then /bin/rm -f $(cmt_local_setup); fi; \
#	  trap '/bin/rm -f $(cmt_local_setup)' 0 1 2 15; \
#	  $(cmtexe) -tag=$(tags) show setup >>$(cmt_local_setup); \
#	  if test ! -f $@; then \
#	    mv $(cmt_local_setup) $@; \
#	  else \
#	    if /usr/bin/diff $(cmt_local_setup) $@ >/dev/null ; then \
#	      : ; \
#	    else \
#	      mv $(cmt_local_setup) $@; \
#	    fi; \
#	  fi

#	@/bin/echo $@ ok   

#config :: checkuses
#	@exit 0
#checkuses : ;

env.make ::
	printenv >env.make.tmp; $(cmtexe) check files env.make.tmp env.make

ifndef QUICK
all :: build_library_links
	$(echo) "(constituents.make) all done"
endif

javadirs ::
	@if test ! -d $(javabin) ; then $(mkdir) -p $(javabin) ; fi

srcdirs ::
	@if test ! -d $(src) ; then $(mkdir) -p $(src) ; fi

dirs :: requirements
	@if test ! -d $(bin) ; then $(mkdir) -p $(bin) ; fi
#	@if test ! -r requirements ; then echo "No requirements file" ; fi; \
#	  if test ! -d $(bin) ; then $(mkdir) -p $(bin) ; fi

requirements :
	@if test ! -r requirements ; then echo "No requirements file" ; fi

build_library_links : dirs
	$(echo) "(constituents.make) Rebuilding library links"; \
	 $(build_library_links)
#	if test ! -d $(bin) ; then $(mkdir) -p $(bin) ; fi; \
#	$(build_library_links)

makefiles : ;

.DEFAULT ::
	$(echo) "(constituents.make) $@: No rule for such target" >&2
#	@echo "#CMT> Warning: $@: Using default commands" >&2; exit

#	@if test "$@" = "$(cmt_lock_setup)"; then \
	#  /bin/rm -f $(cmt_lock_setup); \
	 # touch $(cmt_lock_setup); \
	#fi

#-- end of constituents_header ------
#-- start of group ------

all_groups :: all

all :: $(all_dependencies)  $(all_pre_constituents) $(all_constituents)  $(all_post_constituents)
	$(echo) "all ok."

#	@/bin/echo " all ok."

clean :: allclean

allclean ::  $(all_constituentsclean)
	$(echo) $(all_constituentsclean)
	$(echo) "allclean ok."

#	@echo $(all_constituentsclean)
#	@/bin/echo " allclean ok."

allclean :: makefilesclean

#-- end of group ------
#-- start of group ------

all_groups :: cmt_actions

cmt_actions :: $(cmt_actions_dependencies)  $(cmt_actions_pre_constituents) $(cmt_actions_constituents)  $(cmt_actions_post_constituents)
	$(echo) "cmt_actions ok."

#	@/bin/echo " cmt_actions ok."

clean :: allclean

cmt_actionsclean ::  $(cmt_actions_constituentsclean)
	$(echo) $(cmt_actions_constituentsclean)
	$(echo) "cmt_actionsclean ok."

#	@echo $(cmt_actions_constituentsclean)
#	@/bin/echo " cmt_actionsclean ok."

cmt_actionsclean :: makefilesclean

#-- end of group ------
#-- start of constituent ------

cmt_RockMuonCalibration_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_RockMuonCalibration_has_target_tag

#cmt_local_tagfile_RockMuonCalibration = $(RockMuonCalibration_tag)_RockMuonCalibration.make
cmt_local_tagfile_RockMuonCalibration = $(bin)$(RockMuonCalibration_tag)_RockMuonCalibration.make
cmt_local_setup_RockMuonCalibration = $(bin)setup_RockMuonCalibration$$$$.make
cmt_final_setup_RockMuonCalibration = $(bin)setup_RockMuonCalibration.make
#cmt_final_setup_RockMuonCalibration = $(bin)RockMuonCalibration_RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibration_makefile = $(bin)RockMuonCalibration.make

RockMuonCalibration_extratags = -tag_add=target_RockMuonCalibration

#$(cmt_local_tagfile_RockMuonCalibration) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_RockMuonCalibration) ::
else
$(cmt_local_tagfile_RockMuonCalibration) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_RockMuonCalibration); then /bin/rm -f $(cmt_local_tagfile_RockMuonCalibration); fi ; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibration_extratags) build tag_makefile >>$(cmt_local_tagfile_RockMuonCalibration)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_RockMuonCalibration)"; \
	  test ! -f $(cmt_local_setup_RockMuonCalibration) || \rm -f $(cmt_local_setup_RockMuonCalibration); \
	  trap '\rm -f $(cmt_local_setup_RockMuonCalibration)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibration_extratags) show setup >$(cmt_local_setup_RockMuonCalibration) && \
	  if [ -f $(cmt_final_setup_RockMuonCalibration) ] && \
	    \cmp -s $(cmt_final_setup_RockMuonCalibration) $(cmt_local_setup_RockMuonCalibration); then \
	    \rm $(cmt_local_setup_RockMuonCalibration); else \
	    \mv -f $(cmt_local_setup_RockMuonCalibration) $(cmt_final_setup_RockMuonCalibration); fi

else

#cmt_local_tagfile_RockMuonCalibration = $(RockMuonCalibration_tag).make
cmt_local_tagfile_RockMuonCalibration = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_RockMuonCalibration = $(bin)setup.make
#cmt_final_setup_RockMuonCalibration = $(bin)RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibration_makefile = $(bin)RockMuonCalibration.make

endif

ifdef STRUCTURED_OUTPUT
RockMuonCalibrationdirs :
	@if test ! -d $(bin)RockMuonCalibration; then $(mkdir) -p $(bin)RockMuonCalibration; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibration
else
RockMuonCalibrationdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# RockMuonCalibrationdirs ::
#	@if test ! -d $(bin)RockMuonCalibration; then $(mkdir) -p $(bin)RockMuonCalibration; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibration
#
#$(cmt_local_RockMuonCalibration_makefile) :: $(RockMuonCalibration_dependencies) $(cmt_local_tagfile_RockMuonCalibration) build_library_links dirs RockMuonCalibrationdirs
#else
#$(cmt_local_RockMuonCalibration_makefile) :: $(RockMuonCalibration_dependencies) $(cmt_local_tagfile_RockMuonCalibration) build_library_links dirs
#endif
#else
#$(cmt_local_RockMuonCalibration_makefile) :: $(cmt_local_tagfile_RockMuonCalibration)
#endif

makefiles : $(cmt_local_RockMuonCalibration_makefile)

ifndef QUICK
$(cmt_local_RockMuonCalibration_makefile) : $(RockMuonCalibration_dependencies) $(cmt_local_tagfile_RockMuonCalibration) build_library_links
else
$(cmt_local_RockMuonCalibration_makefile) : $(cmt_local_tagfile_RockMuonCalibration)
endif
	$(echo) "(constituents.make) Building RockMuonCalibration.make"; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibration_extratags) build constituent_makefile -out=$(cmt_local_RockMuonCalibration_makefile) RockMuonCalibration

RockMuonCalibration :: $(RockMuonCalibration_dependencies) $(cmt_local_RockMuonCalibration_makefile) dirs RockMuonCalibrationdirs
	$(echo) "(constituents.make) Starting RockMuonCalibration"
	@$(MAKE) -f $(cmt_local_RockMuonCalibration_makefile) RockMuonCalibration
	$(echo) "(constituents.make) RockMuonCalibration done"

clean :: RockMuonCalibrationclean

RockMuonCalibrationclean :: $(RockMuonCalibrationclean_dependencies) ##$(cmt_local_RockMuonCalibration_makefile)
	$(echo) "(constituents.make) Starting RockMuonCalibrationclean"
	@-if test -f $(cmt_local_RockMuonCalibration_makefile); then \
	  $(MAKE) -f $(cmt_local_RockMuonCalibration_makefile) RockMuonCalibrationclean; \
	fi
	$(echo) "(constituents.make) RockMuonCalibrationclean done"
#	@-$(MAKE) -f $(cmt_local_RockMuonCalibration_makefile) RockMuonCalibrationclean

##	  /bin/rm -f $(cmt_local_RockMuonCalibration_makefile) $(bin)RockMuonCalibration_dependencies.make

install :: RockMuonCalibrationinstall

RockMuonCalibrationinstall :: $(RockMuonCalibration_dependencies) $(cmt_local_RockMuonCalibration_makefile)
	$(echo) "(constituents.make) Starting install RockMuonCalibration"
	@-$(MAKE) -f $(cmt_local_RockMuonCalibration_makefile) install
	$(echo) "(constituents.make) install RockMuonCalibration done"

uninstall :: RockMuonCalibrationuninstall

$(foreach d,$(RockMuonCalibration_dependencies),$(eval $(d)uninstall_dependencies += RockMuonCalibrationuninstall))

RockMuonCalibrationuninstall :: $(RockMuonCalibrationuninstall_dependencies) $(cmt_local_RockMuonCalibration_makefile)
	$(echo) "(constituents.make) Starting uninstall RockMuonCalibration"
	@$(MAKE) -f $(cmt_local_RockMuonCalibration_makefile) uninstall
	$(echo) "(constituents.make) uninstall RockMuonCalibration done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ RockMuonCalibration"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ RockMuonCalibration done"
endif

#-- end of constituent ------
#-- start of constituent_lock ------

cmt_install_more_includes_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_install_more_includes_has_target_tag

#cmt_local_tagfile_install_more_includes = $(RockMuonCalibration_tag)_install_more_includes.make
cmt_local_tagfile_install_more_includes = $(bin)$(RockMuonCalibration_tag)_install_more_includes.make
cmt_local_setup_install_more_includes = $(bin)setup_install_more_includes$$$$.make
cmt_final_setup_install_more_includes = $(bin)setup_install_more_includes.make
#cmt_final_setup_install_more_includes = $(bin)RockMuonCalibration_install_more_includessetup.make
cmt_local_install_more_includes_makefile = $(bin)install_more_includes.make

install_more_includes_extratags = -tag_add=target_install_more_includes

#$(cmt_local_tagfile_install_more_includes) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_install_more_includes) ::
else
$(cmt_local_tagfile_install_more_includes) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_install_more_includes); then /bin/rm -f $(cmt_local_tagfile_install_more_includes); fi ; \
	  $(cmtexe) -tag=$(tags) $(install_more_includes_extratags) build tag_makefile >>$(cmt_local_tagfile_install_more_includes)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_install_more_includes)"; \
	  test ! -f $(cmt_local_setup_install_more_includes) || \rm -f $(cmt_local_setup_install_more_includes); \
	  trap '\rm -f $(cmt_local_setup_install_more_includes)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(install_more_includes_extratags) show setup >$(cmt_local_setup_install_more_includes) && \
	  if [ -f $(cmt_final_setup_install_more_includes) ] && \
	    \cmp -s $(cmt_final_setup_install_more_includes) $(cmt_local_setup_install_more_includes); then \
	    \rm $(cmt_local_setup_install_more_includes); else \
	    \mv -f $(cmt_local_setup_install_more_includes) $(cmt_final_setup_install_more_includes); fi

else

#cmt_local_tagfile_install_more_includes = $(RockMuonCalibration_tag).make
cmt_local_tagfile_install_more_includes = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_install_more_includes = $(bin)setup.make
#cmt_final_setup_install_more_includes = $(bin)RockMuonCalibrationsetup.make
cmt_local_install_more_includes_makefile = $(bin)install_more_includes.make

endif

ifdef STRUCTURED_OUTPUT
install_more_includesdirs :
	@if test ! -d $(bin)install_more_includes; then $(mkdir) -p $(bin)install_more_includes; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)install_more_includes
else
install_more_includesdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# install_more_includesdirs ::
#	@if test ! -d $(bin)install_more_includes; then $(mkdir) -p $(bin)install_more_includes; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)install_more_includes
#
#$(cmt_local_install_more_includes_makefile) :: $(install_more_includes_dependencies) $(cmt_local_tagfile_install_more_includes) build_library_links dirs install_more_includesdirs
#else
#$(cmt_local_install_more_includes_makefile) :: $(install_more_includes_dependencies) $(cmt_local_tagfile_install_more_includes) build_library_links dirs
#endif
#else
#$(cmt_local_install_more_includes_makefile) :: $(cmt_local_tagfile_install_more_includes)
#endif

makefiles : $(cmt_local_install_more_includes_makefile)

ifndef QUICK
$(cmt_local_install_more_includes_makefile) : $(install_more_includes_dependencies) $(cmt_local_tagfile_install_more_includes) build_library_links
else
$(cmt_local_install_more_includes_makefile) : $(cmt_local_tagfile_install_more_includes)
endif
	$(echo) "(constituents.make) Building install_more_includes.make"; \
	  $(cmtexe) -tag=$(tags) $(install_more_includes_extratags) build constituent_makefile -out=$(cmt_local_install_more_includes_makefile) install_more_includes

install_more_includes :: $(install_more_includes_dependencies) $(cmt_local_install_more_includes_makefile) dirs install_more_includesdirs
	$(echo) "(constituents.make) Creating install_more_includes${lock_suffix} and Starting install_more_includes"
	@${lock_command} install_more_includes${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} install_more_includes${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_install_more_includes_makefile) install_more_includes; \
	  retval=$$?; ${unlock_command} install_more_includes${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) install_more_includes done"

clean :: install_more_includesclean

install_more_includesclean :: $(install_more_includesclean_dependencies) ##$(cmt_local_install_more_includes_makefile)
	$(echo) "(constituents.make) Starting install_more_includesclean"
	@-if test -f $(cmt_local_install_more_includes_makefile); then \
	  $(MAKE) -f $(cmt_local_install_more_includes_makefile) install_more_includesclean; \
	fi
	$(echo) "(constituents.make) install_more_includesclean done"
#	@-$(MAKE) -f $(cmt_local_install_more_includes_makefile) install_more_includesclean

##	  /bin/rm -f $(cmt_local_install_more_includes_makefile) $(bin)install_more_includes_dependencies.make

install :: install_more_includesinstall

install_more_includesinstall :: $(install_more_includes_dependencies) $(cmt_local_install_more_includes_makefile)
	$(echo) "(constituents.make) Starting install install_more_includes"
	@-$(MAKE) -f $(cmt_local_install_more_includes_makefile) install
	$(echo) "(constituents.make) install install_more_includes done"

uninstall :: install_more_includesuninstall

$(foreach d,$(install_more_includes_dependencies),$(eval $(d)uninstall_dependencies += install_more_includesuninstall))

install_more_includesuninstall :: $(install_more_includesuninstall_dependencies) $(cmt_local_install_more_includes_makefile)
	$(echo) "(constituents.make) Starting uninstall install_more_includes"
	@$(MAKE) -f $(cmt_local_install_more_includes_makefile) uninstall
	$(echo) "(constituents.make) uninstall install_more_includes done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ install_more_includes"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ install_more_includes done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_RockMuonCalibrationRootMap_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_RockMuonCalibrationRootMap_has_target_tag

#cmt_local_tagfile_RockMuonCalibrationRootMap = $(RockMuonCalibration_tag)_RockMuonCalibrationRootMap.make
cmt_local_tagfile_RockMuonCalibrationRootMap = $(bin)$(RockMuonCalibration_tag)_RockMuonCalibrationRootMap.make
cmt_local_setup_RockMuonCalibrationRootMap = $(bin)setup_RockMuonCalibrationRootMap$$$$.make
cmt_final_setup_RockMuonCalibrationRootMap = $(bin)setup_RockMuonCalibrationRootMap.make
#cmt_final_setup_RockMuonCalibrationRootMap = $(bin)RockMuonCalibration_RockMuonCalibrationRootMapsetup.make
cmt_local_RockMuonCalibrationRootMap_makefile = $(bin)RockMuonCalibrationRootMap.make

RockMuonCalibrationRootMap_extratags = -tag_add=target_RockMuonCalibrationRootMap

#$(cmt_local_tagfile_RockMuonCalibrationRootMap) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_RockMuonCalibrationRootMap) ::
else
$(cmt_local_tagfile_RockMuonCalibrationRootMap) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_RockMuonCalibrationRootMap); then /bin/rm -f $(cmt_local_tagfile_RockMuonCalibrationRootMap); fi ; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationRootMap_extratags) build tag_makefile >>$(cmt_local_tagfile_RockMuonCalibrationRootMap)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_RockMuonCalibrationRootMap)"; \
	  test ! -f $(cmt_local_setup_RockMuonCalibrationRootMap) || \rm -f $(cmt_local_setup_RockMuonCalibrationRootMap); \
	  trap '\rm -f $(cmt_local_setup_RockMuonCalibrationRootMap)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationRootMap_extratags) show setup >$(cmt_local_setup_RockMuonCalibrationRootMap) && \
	  if [ -f $(cmt_final_setup_RockMuonCalibrationRootMap) ] && \
	    \cmp -s $(cmt_final_setup_RockMuonCalibrationRootMap) $(cmt_local_setup_RockMuonCalibrationRootMap); then \
	    \rm $(cmt_local_setup_RockMuonCalibrationRootMap); else \
	    \mv -f $(cmt_local_setup_RockMuonCalibrationRootMap) $(cmt_final_setup_RockMuonCalibrationRootMap); fi

else

#cmt_local_tagfile_RockMuonCalibrationRootMap = $(RockMuonCalibration_tag).make
cmt_local_tagfile_RockMuonCalibrationRootMap = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_RockMuonCalibrationRootMap = $(bin)setup.make
#cmt_final_setup_RockMuonCalibrationRootMap = $(bin)RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibrationRootMap_makefile = $(bin)RockMuonCalibrationRootMap.make

endif

ifdef STRUCTURED_OUTPUT
RockMuonCalibrationRootMapdirs :
	@if test ! -d $(bin)RockMuonCalibrationRootMap; then $(mkdir) -p $(bin)RockMuonCalibrationRootMap; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibrationRootMap
else
RockMuonCalibrationRootMapdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# RockMuonCalibrationRootMapdirs ::
#	@if test ! -d $(bin)RockMuonCalibrationRootMap; then $(mkdir) -p $(bin)RockMuonCalibrationRootMap; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibrationRootMap
#
#$(cmt_local_RockMuonCalibrationRootMap_makefile) :: $(RockMuonCalibrationRootMap_dependencies) $(cmt_local_tagfile_RockMuonCalibrationRootMap) build_library_links dirs RockMuonCalibrationRootMapdirs
#else
#$(cmt_local_RockMuonCalibrationRootMap_makefile) :: $(RockMuonCalibrationRootMap_dependencies) $(cmt_local_tagfile_RockMuonCalibrationRootMap) build_library_links dirs
#endif
#else
#$(cmt_local_RockMuonCalibrationRootMap_makefile) :: $(cmt_local_tagfile_RockMuonCalibrationRootMap)
#endif

makefiles : $(cmt_local_RockMuonCalibrationRootMap_makefile)

ifndef QUICK
$(cmt_local_RockMuonCalibrationRootMap_makefile) : $(RockMuonCalibrationRootMap_dependencies) $(cmt_local_tagfile_RockMuonCalibrationRootMap) build_library_links
else
$(cmt_local_RockMuonCalibrationRootMap_makefile) : $(cmt_local_tagfile_RockMuonCalibrationRootMap)
endif
	$(echo) "(constituents.make) Building RockMuonCalibrationRootMap.make"; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationRootMap_extratags) build constituent_makefile -out=$(cmt_local_RockMuonCalibrationRootMap_makefile) RockMuonCalibrationRootMap

RockMuonCalibrationRootMap :: $(RockMuonCalibrationRootMap_dependencies) $(cmt_local_RockMuonCalibrationRootMap_makefile) dirs RockMuonCalibrationRootMapdirs
	$(echo) "(constituents.make) Creating RockMuonCalibrationRootMap${lock_suffix} and Starting RockMuonCalibrationRootMap"
	@${lock_command} RockMuonCalibrationRootMap${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} RockMuonCalibrationRootMap${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_RockMuonCalibrationRootMap_makefile) RockMuonCalibrationRootMap; \
	  retval=$$?; ${unlock_command} RockMuonCalibrationRootMap${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) RockMuonCalibrationRootMap done"

clean :: RockMuonCalibrationRootMapclean

RockMuonCalibrationRootMapclean :: $(RockMuonCalibrationRootMapclean_dependencies) ##$(cmt_local_RockMuonCalibrationRootMap_makefile)
	$(echo) "(constituents.make) Starting RockMuonCalibrationRootMapclean"
	@-if test -f $(cmt_local_RockMuonCalibrationRootMap_makefile); then \
	  $(MAKE) -f $(cmt_local_RockMuonCalibrationRootMap_makefile) RockMuonCalibrationRootMapclean; \
	fi
	$(echo) "(constituents.make) RockMuonCalibrationRootMapclean done"
#	@-$(MAKE) -f $(cmt_local_RockMuonCalibrationRootMap_makefile) RockMuonCalibrationRootMapclean

##	  /bin/rm -f $(cmt_local_RockMuonCalibrationRootMap_makefile) $(bin)RockMuonCalibrationRootMap_dependencies.make

install :: RockMuonCalibrationRootMapinstall

RockMuonCalibrationRootMapinstall :: $(RockMuonCalibrationRootMap_dependencies) $(cmt_local_RockMuonCalibrationRootMap_makefile)
	$(echo) "(constituents.make) Starting install RockMuonCalibrationRootMap"
	@-$(MAKE) -f $(cmt_local_RockMuonCalibrationRootMap_makefile) install
	$(echo) "(constituents.make) install RockMuonCalibrationRootMap done"

uninstall :: RockMuonCalibrationRootMapuninstall

$(foreach d,$(RockMuonCalibrationRootMap_dependencies),$(eval $(d)uninstall_dependencies += RockMuonCalibrationRootMapuninstall))

RockMuonCalibrationRootMapuninstall :: $(RockMuonCalibrationRootMapuninstall_dependencies) $(cmt_local_RockMuonCalibrationRootMap_makefile)
	$(echo) "(constituents.make) Starting uninstall RockMuonCalibrationRootMap"
	@$(MAKE) -f $(cmt_local_RockMuonCalibrationRootMap_makefile) uninstall
	$(echo) "(constituents.make) uninstall RockMuonCalibrationRootMap done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ RockMuonCalibrationRootMap"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ RockMuonCalibrationRootMap done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_RockMuonCalibrationMergeMap_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_RockMuonCalibrationMergeMap_has_target_tag

#cmt_local_tagfile_RockMuonCalibrationMergeMap = $(RockMuonCalibration_tag)_RockMuonCalibrationMergeMap.make
cmt_local_tagfile_RockMuonCalibrationMergeMap = $(bin)$(RockMuonCalibration_tag)_RockMuonCalibrationMergeMap.make
cmt_local_setup_RockMuonCalibrationMergeMap = $(bin)setup_RockMuonCalibrationMergeMap$$$$.make
cmt_final_setup_RockMuonCalibrationMergeMap = $(bin)setup_RockMuonCalibrationMergeMap.make
#cmt_final_setup_RockMuonCalibrationMergeMap = $(bin)RockMuonCalibration_RockMuonCalibrationMergeMapsetup.make
cmt_local_RockMuonCalibrationMergeMap_makefile = $(bin)RockMuonCalibrationMergeMap.make

RockMuonCalibrationMergeMap_extratags = -tag_add=target_RockMuonCalibrationMergeMap

#$(cmt_local_tagfile_RockMuonCalibrationMergeMap) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_RockMuonCalibrationMergeMap) ::
else
$(cmt_local_tagfile_RockMuonCalibrationMergeMap) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_RockMuonCalibrationMergeMap); then /bin/rm -f $(cmt_local_tagfile_RockMuonCalibrationMergeMap); fi ; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationMergeMap_extratags) build tag_makefile >>$(cmt_local_tagfile_RockMuonCalibrationMergeMap)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_RockMuonCalibrationMergeMap)"; \
	  test ! -f $(cmt_local_setup_RockMuonCalibrationMergeMap) || \rm -f $(cmt_local_setup_RockMuonCalibrationMergeMap); \
	  trap '\rm -f $(cmt_local_setup_RockMuonCalibrationMergeMap)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationMergeMap_extratags) show setup >$(cmt_local_setup_RockMuonCalibrationMergeMap) && \
	  if [ -f $(cmt_final_setup_RockMuonCalibrationMergeMap) ] && \
	    \cmp -s $(cmt_final_setup_RockMuonCalibrationMergeMap) $(cmt_local_setup_RockMuonCalibrationMergeMap); then \
	    \rm $(cmt_local_setup_RockMuonCalibrationMergeMap); else \
	    \mv -f $(cmt_local_setup_RockMuonCalibrationMergeMap) $(cmt_final_setup_RockMuonCalibrationMergeMap); fi

else

#cmt_local_tagfile_RockMuonCalibrationMergeMap = $(RockMuonCalibration_tag).make
cmt_local_tagfile_RockMuonCalibrationMergeMap = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_RockMuonCalibrationMergeMap = $(bin)setup.make
#cmt_final_setup_RockMuonCalibrationMergeMap = $(bin)RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibrationMergeMap_makefile = $(bin)RockMuonCalibrationMergeMap.make

endif

ifdef STRUCTURED_OUTPUT
RockMuonCalibrationMergeMapdirs :
	@if test ! -d $(bin)RockMuonCalibrationMergeMap; then $(mkdir) -p $(bin)RockMuonCalibrationMergeMap; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibrationMergeMap
else
RockMuonCalibrationMergeMapdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# RockMuonCalibrationMergeMapdirs ::
#	@if test ! -d $(bin)RockMuonCalibrationMergeMap; then $(mkdir) -p $(bin)RockMuonCalibrationMergeMap; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibrationMergeMap
#
#$(cmt_local_RockMuonCalibrationMergeMap_makefile) :: $(RockMuonCalibrationMergeMap_dependencies) $(cmt_local_tagfile_RockMuonCalibrationMergeMap) build_library_links dirs RockMuonCalibrationMergeMapdirs
#else
#$(cmt_local_RockMuonCalibrationMergeMap_makefile) :: $(RockMuonCalibrationMergeMap_dependencies) $(cmt_local_tagfile_RockMuonCalibrationMergeMap) build_library_links dirs
#endif
#else
#$(cmt_local_RockMuonCalibrationMergeMap_makefile) :: $(cmt_local_tagfile_RockMuonCalibrationMergeMap)
#endif

makefiles : $(cmt_local_RockMuonCalibrationMergeMap_makefile)

ifndef QUICK
$(cmt_local_RockMuonCalibrationMergeMap_makefile) : $(RockMuonCalibrationMergeMap_dependencies) $(cmt_local_tagfile_RockMuonCalibrationMergeMap) build_library_links
else
$(cmt_local_RockMuonCalibrationMergeMap_makefile) : $(cmt_local_tagfile_RockMuonCalibrationMergeMap)
endif
	$(echo) "(constituents.make) Building RockMuonCalibrationMergeMap.make"; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationMergeMap_extratags) build constituent_makefile -out=$(cmt_local_RockMuonCalibrationMergeMap_makefile) RockMuonCalibrationMergeMap

RockMuonCalibrationMergeMap :: $(RockMuonCalibrationMergeMap_dependencies) $(cmt_local_RockMuonCalibrationMergeMap_makefile) dirs RockMuonCalibrationMergeMapdirs
	$(echo) "(constituents.make) Creating RockMuonCalibrationMergeMap${lock_suffix} and Starting RockMuonCalibrationMergeMap"
	@${lock_command} RockMuonCalibrationMergeMap${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} RockMuonCalibrationMergeMap${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_RockMuonCalibrationMergeMap_makefile) RockMuonCalibrationMergeMap; \
	  retval=$$?; ${unlock_command} RockMuonCalibrationMergeMap${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) RockMuonCalibrationMergeMap done"

clean :: RockMuonCalibrationMergeMapclean

RockMuonCalibrationMergeMapclean :: $(RockMuonCalibrationMergeMapclean_dependencies) ##$(cmt_local_RockMuonCalibrationMergeMap_makefile)
	$(echo) "(constituents.make) Starting RockMuonCalibrationMergeMapclean"
	@-if test -f $(cmt_local_RockMuonCalibrationMergeMap_makefile); then \
	  $(MAKE) -f $(cmt_local_RockMuonCalibrationMergeMap_makefile) RockMuonCalibrationMergeMapclean; \
	fi
	$(echo) "(constituents.make) RockMuonCalibrationMergeMapclean done"
#	@-$(MAKE) -f $(cmt_local_RockMuonCalibrationMergeMap_makefile) RockMuonCalibrationMergeMapclean

##	  /bin/rm -f $(cmt_local_RockMuonCalibrationMergeMap_makefile) $(bin)RockMuonCalibrationMergeMap_dependencies.make

install :: RockMuonCalibrationMergeMapinstall

RockMuonCalibrationMergeMapinstall :: $(RockMuonCalibrationMergeMap_dependencies) $(cmt_local_RockMuonCalibrationMergeMap_makefile)
	$(echo) "(constituents.make) Starting install RockMuonCalibrationMergeMap"
	@-$(MAKE) -f $(cmt_local_RockMuonCalibrationMergeMap_makefile) install
	$(echo) "(constituents.make) install RockMuonCalibrationMergeMap done"

uninstall :: RockMuonCalibrationMergeMapuninstall

$(foreach d,$(RockMuonCalibrationMergeMap_dependencies),$(eval $(d)uninstall_dependencies += RockMuonCalibrationMergeMapuninstall))

RockMuonCalibrationMergeMapuninstall :: $(RockMuonCalibrationMergeMapuninstall_dependencies) $(cmt_local_RockMuonCalibrationMergeMap_makefile)
	$(echo) "(constituents.make) Starting uninstall RockMuonCalibrationMergeMap"
	@$(MAKE) -f $(cmt_local_RockMuonCalibrationMergeMap_makefile) uninstall
	$(echo) "(constituents.make) uninstall RockMuonCalibrationMergeMap done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ RockMuonCalibrationMergeMap"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ RockMuonCalibrationMergeMap done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_RockMuonCalibrationConf_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_RockMuonCalibrationConf_has_target_tag

#cmt_local_tagfile_RockMuonCalibrationConf = $(RockMuonCalibration_tag)_RockMuonCalibrationConf.make
cmt_local_tagfile_RockMuonCalibrationConf = $(bin)$(RockMuonCalibration_tag)_RockMuonCalibrationConf.make
cmt_local_setup_RockMuonCalibrationConf = $(bin)setup_RockMuonCalibrationConf$$$$.make
cmt_final_setup_RockMuonCalibrationConf = $(bin)setup_RockMuonCalibrationConf.make
#cmt_final_setup_RockMuonCalibrationConf = $(bin)RockMuonCalibration_RockMuonCalibrationConfsetup.make
cmt_local_RockMuonCalibrationConf_makefile = $(bin)RockMuonCalibrationConf.make

RockMuonCalibrationConf_extratags = -tag_add=target_RockMuonCalibrationConf

#$(cmt_local_tagfile_RockMuonCalibrationConf) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_RockMuonCalibrationConf) ::
else
$(cmt_local_tagfile_RockMuonCalibrationConf) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_RockMuonCalibrationConf); then /bin/rm -f $(cmt_local_tagfile_RockMuonCalibrationConf); fi ; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationConf_extratags) build tag_makefile >>$(cmt_local_tagfile_RockMuonCalibrationConf)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_RockMuonCalibrationConf)"; \
	  test ! -f $(cmt_local_setup_RockMuonCalibrationConf) || \rm -f $(cmt_local_setup_RockMuonCalibrationConf); \
	  trap '\rm -f $(cmt_local_setup_RockMuonCalibrationConf)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationConf_extratags) show setup >$(cmt_local_setup_RockMuonCalibrationConf) && \
	  if [ -f $(cmt_final_setup_RockMuonCalibrationConf) ] && \
	    \cmp -s $(cmt_final_setup_RockMuonCalibrationConf) $(cmt_local_setup_RockMuonCalibrationConf); then \
	    \rm $(cmt_local_setup_RockMuonCalibrationConf); else \
	    \mv -f $(cmt_local_setup_RockMuonCalibrationConf) $(cmt_final_setup_RockMuonCalibrationConf); fi

else

#cmt_local_tagfile_RockMuonCalibrationConf = $(RockMuonCalibration_tag).make
cmt_local_tagfile_RockMuonCalibrationConf = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_RockMuonCalibrationConf = $(bin)setup.make
#cmt_final_setup_RockMuonCalibrationConf = $(bin)RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibrationConf_makefile = $(bin)RockMuonCalibrationConf.make

endif

ifdef STRUCTURED_OUTPUT
RockMuonCalibrationConfdirs :
	@if test ! -d $(bin)RockMuonCalibrationConf; then $(mkdir) -p $(bin)RockMuonCalibrationConf; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibrationConf
else
RockMuonCalibrationConfdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# RockMuonCalibrationConfdirs ::
#	@if test ! -d $(bin)RockMuonCalibrationConf; then $(mkdir) -p $(bin)RockMuonCalibrationConf; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibrationConf
#
#$(cmt_local_RockMuonCalibrationConf_makefile) :: $(RockMuonCalibrationConf_dependencies) $(cmt_local_tagfile_RockMuonCalibrationConf) build_library_links dirs RockMuonCalibrationConfdirs
#else
#$(cmt_local_RockMuonCalibrationConf_makefile) :: $(RockMuonCalibrationConf_dependencies) $(cmt_local_tagfile_RockMuonCalibrationConf) build_library_links dirs
#endif
#else
#$(cmt_local_RockMuonCalibrationConf_makefile) :: $(cmt_local_tagfile_RockMuonCalibrationConf)
#endif

makefiles : $(cmt_local_RockMuonCalibrationConf_makefile)

ifndef QUICK
$(cmt_local_RockMuonCalibrationConf_makefile) : $(RockMuonCalibrationConf_dependencies) $(cmt_local_tagfile_RockMuonCalibrationConf) build_library_links
else
$(cmt_local_RockMuonCalibrationConf_makefile) : $(cmt_local_tagfile_RockMuonCalibrationConf)
endif
	$(echo) "(constituents.make) Building RockMuonCalibrationConf.make"; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationConf_extratags) build constituent_makefile -out=$(cmt_local_RockMuonCalibrationConf_makefile) RockMuonCalibrationConf

RockMuonCalibrationConf :: $(RockMuonCalibrationConf_dependencies) $(cmt_local_RockMuonCalibrationConf_makefile) dirs RockMuonCalibrationConfdirs
	$(echo) "(constituents.make) Creating RockMuonCalibrationConf${lock_suffix} and Starting RockMuonCalibrationConf"
	@${lock_command} RockMuonCalibrationConf${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} RockMuonCalibrationConf${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_RockMuonCalibrationConf_makefile) RockMuonCalibrationConf; \
	  retval=$$?; ${unlock_command} RockMuonCalibrationConf${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) RockMuonCalibrationConf done"

clean :: RockMuonCalibrationConfclean

RockMuonCalibrationConfclean :: $(RockMuonCalibrationConfclean_dependencies) ##$(cmt_local_RockMuonCalibrationConf_makefile)
	$(echo) "(constituents.make) Starting RockMuonCalibrationConfclean"
	@-if test -f $(cmt_local_RockMuonCalibrationConf_makefile); then \
	  $(MAKE) -f $(cmt_local_RockMuonCalibrationConf_makefile) RockMuonCalibrationConfclean; \
	fi
	$(echo) "(constituents.make) RockMuonCalibrationConfclean done"
#	@-$(MAKE) -f $(cmt_local_RockMuonCalibrationConf_makefile) RockMuonCalibrationConfclean

##	  /bin/rm -f $(cmt_local_RockMuonCalibrationConf_makefile) $(bin)RockMuonCalibrationConf_dependencies.make

install :: RockMuonCalibrationConfinstall

RockMuonCalibrationConfinstall :: $(RockMuonCalibrationConf_dependencies) $(cmt_local_RockMuonCalibrationConf_makefile)
	$(echo) "(constituents.make) Starting install RockMuonCalibrationConf"
	@-$(MAKE) -f $(cmt_local_RockMuonCalibrationConf_makefile) install
	$(echo) "(constituents.make) install RockMuonCalibrationConf done"

uninstall :: RockMuonCalibrationConfuninstall

$(foreach d,$(RockMuonCalibrationConf_dependencies),$(eval $(d)uninstall_dependencies += RockMuonCalibrationConfuninstall))

RockMuonCalibrationConfuninstall :: $(RockMuonCalibrationConfuninstall_dependencies) $(cmt_local_RockMuonCalibrationConf_makefile)
	$(echo) "(constituents.make) Starting uninstall RockMuonCalibrationConf"
	@$(MAKE) -f $(cmt_local_RockMuonCalibrationConf_makefile) uninstall
	$(echo) "(constituents.make) uninstall RockMuonCalibrationConf done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ RockMuonCalibrationConf"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ RockMuonCalibrationConf done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_RockMuonCalibration_python_init_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_RockMuonCalibration_python_init_has_target_tag

#cmt_local_tagfile_RockMuonCalibration_python_init = $(RockMuonCalibration_tag)_RockMuonCalibration_python_init.make
cmt_local_tagfile_RockMuonCalibration_python_init = $(bin)$(RockMuonCalibration_tag)_RockMuonCalibration_python_init.make
cmt_local_setup_RockMuonCalibration_python_init = $(bin)setup_RockMuonCalibration_python_init$$$$.make
cmt_final_setup_RockMuonCalibration_python_init = $(bin)setup_RockMuonCalibration_python_init.make
#cmt_final_setup_RockMuonCalibration_python_init = $(bin)RockMuonCalibration_RockMuonCalibration_python_initsetup.make
cmt_local_RockMuonCalibration_python_init_makefile = $(bin)RockMuonCalibration_python_init.make

RockMuonCalibration_python_init_extratags = -tag_add=target_RockMuonCalibration_python_init

#$(cmt_local_tagfile_RockMuonCalibration_python_init) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_RockMuonCalibration_python_init) ::
else
$(cmt_local_tagfile_RockMuonCalibration_python_init) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_RockMuonCalibration_python_init); then /bin/rm -f $(cmt_local_tagfile_RockMuonCalibration_python_init); fi ; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibration_python_init_extratags) build tag_makefile >>$(cmt_local_tagfile_RockMuonCalibration_python_init)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_RockMuonCalibration_python_init)"; \
	  test ! -f $(cmt_local_setup_RockMuonCalibration_python_init) || \rm -f $(cmt_local_setup_RockMuonCalibration_python_init); \
	  trap '\rm -f $(cmt_local_setup_RockMuonCalibration_python_init)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibration_python_init_extratags) show setup >$(cmt_local_setup_RockMuonCalibration_python_init) && \
	  if [ -f $(cmt_final_setup_RockMuonCalibration_python_init) ] && \
	    \cmp -s $(cmt_final_setup_RockMuonCalibration_python_init) $(cmt_local_setup_RockMuonCalibration_python_init); then \
	    \rm $(cmt_local_setup_RockMuonCalibration_python_init); else \
	    \mv -f $(cmt_local_setup_RockMuonCalibration_python_init) $(cmt_final_setup_RockMuonCalibration_python_init); fi

else

#cmt_local_tagfile_RockMuonCalibration_python_init = $(RockMuonCalibration_tag).make
cmt_local_tagfile_RockMuonCalibration_python_init = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_RockMuonCalibration_python_init = $(bin)setup.make
#cmt_final_setup_RockMuonCalibration_python_init = $(bin)RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibration_python_init_makefile = $(bin)RockMuonCalibration_python_init.make

endif

ifdef STRUCTURED_OUTPUT
RockMuonCalibration_python_initdirs :
	@if test ! -d $(bin)RockMuonCalibration_python_init; then $(mkdir) -p $(bin)RockMuonCalibration_python_init; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibration_python_init
else
RockMuonCalibration_python_initdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# RockMuonCalibration_python_initdirs ::
#	@if test ! -d $(bin)RockMuonCalibration_python_init; then $(mkdir) -p $(bin)RockMuonCalibration_python_init; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibration_python_init
#
#$(cmt_local_RockMuonCalibration_python_init_makefile) :: $(RockMuonCalibration_python_init_dependencies) $(cmt_local_tagfile_RockMuonCalibration_python_init) build_library_links dirs RockMuonCalibration_python_initdirs
#else
#$(cmt_local_RockMuonCalibration_python_init_makefile) :: $(RockMuonCalibration_python_init_dependencies) $(cmt_local_tagfile_RockMuonCalibration_python_init) build_library_links dirs
#endif
#else
#$(cmt_local_RockMuonCalibration_python_init_makefile) :: $(cmt_local_tagfile_RockMuonCalibration_python_init)
#endif

makefiles : $(cmt_local_RockMuonCalibration_python_init_makefile)

ifndef QUICK
$(cmt_local_RockMuonCalibration_python_init_makefile) : $(RockMuonCalibration_python_init_dependencies) $(cmt_local_tagfile_RockMuonCalibration_python_init) build_library_links
else
$(cmt_local_RockMuonCalibration_python_init_makefile) : $(cmt_local_tagfile_RockMuonCalibration_python_init)
endif
	$(echo) "(constituents.make) Building RockMuonCalibration_python_init.make"; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibration_python_init_extratags) build constituent_makefile -out=$(cmt_local_RockMuonCalibration_python_init_makefile) RockMuonCalibration_python_init

RockMuonCalibration_python_init :: $(RockMuonCalibration_python_init_dependencies) $(cmt_local_RockMuonCalibration_python_init_makefile) dirs RockMuonCalibration_python_initdirs
	$(echo) "(constituents.make) Creating RockMuonCalibration_python_init${lock_suffix} and Starting RockMuonCalibration_python_init"
	@${lock_command} RockMuonCalibration_python_init${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} RockMuonCalibration_python_init${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_RockMuonCalibration_python_init_makefile) RockMuonCalibration_python_init; \
	  retval=$$?; ${unlock_command} RockMuonCalibration_python_init${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) RockMuonCalibration_python_init done"

clean :: RockMuonCalibration_python_initclean

RockMuonCalibration_python_initclean :: $(RockMuonCalibration_python_initclean_dependencies) ##$(cmt_local_RockMuonCalibration_python_init_makefile)
	$(echo) "(constituents.make) Starting RockMuonCalibration_python_initclean"
	@-if test -f $(cmt_local_RockMuonCalibration_python_init_makefile); then \
	  $(MAKE) -f $(cmt_local_RockMuonCalibration_python_init_makefile) RockMuonCalibration_python_initclean; \
	fi
	$(echo) "(constituents.make) RockMuonCalibration_python_initclean done"
#	@-$(MAKE) -f $(cmt_local_RockMuonCalibration_python_init_makefile) RockMuonCalibration_python_initclean

##	  /bin/rm -f $(cmt_local_RockMuonCalibration_python_init_makefile) $(bin)RockMuonCalibration_python_init_dependencies.make

install :: RockMuonCalibration_python_initinstall

RockMuonCalibration_python_initinstall :: $(RockMuonCalibration_python_init_dependencies) $(cmt_local_RockMuonCalibration_python_init_makefile)
	$(echo) "(constituents.make) Starting install RockMuonCalibration_python_init"
	@-$(MAKE) -f $(cmt_local_RockMuonCalibration_python_init_makefile) install
	$(echo) "(constituents.make) install RockMuonCalibration_python_init done"

uninstall :: RockMuonCalibration_python_inituninstall

$(foreach d,$(RockMuonCalibration_python_init_dependencies),$(eval $(d)uninstall_dependencies += RockMuonCalibration_python_inituninstall))

RockMuonCalibration_python_inituninstall :: $(RockMuonCalibration_python_inituninstall_dependencies) $(cmt_local_RockMuonCalibration_python_init_makefile)
	$(echo) "(constituents.make) Starting uninstall RockMuonCalibration_python_init"
	@$(MAKE) -f $(cmt_local_RockMuonCalibration_python_init_makefile) uninstall
	$(echo) "(constituents.make) uninstall RockMuonCalibration_python_init done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ RockMuonCalibration_python_init"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ RockMuonCalibration_python_init done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_zip_RockMuonCalibration_python_modules_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_zip_RockMuonCalibration_python_modules_has_target_tag

#cmt_local_tagfile_zip_RockMuonCalibration_python_modules = $(RockMuonCalibration_tag)_zip_RockMuonCalibration_python_modules.make
cmt_local_tagfile_zip_RockMuonCalibration_python_modules = $(bin)$(RockMuonCalibration_tag)_zip_RockMuonCalibration_python_modules.make
cmt_local_setup_zip_RockMuonCalibration_python_modules = $(bin)setup_zip_RockMuonCalibration_python_modules$$$$.make
cmt_final_setup_zip_RockMuonCalibration_python_modules = $(bin)setup_zip_RockMuonCalibration_python_modules.make
#cmt_final_setup_zip_RockMuonCalibration_python_modules = $(bin)RockMuonCalibration_zip_RockMuonCalibration_python_modulessetup.make
cmt_local_zip_RockMuonCalibration_python_modules_makefile = $(bin)zip_RockMuonCalibration_python_modules.make

zip_RockMuonCalibration_python_modules_extratags = -tag_add=target_zip_RockMuonCalibration_python_modules

#$(cmt_local_tagfile_zip_RockMuonCalibration_python_modules) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_zip_RockMuonCalibration_python_modules) ::
else
$(cmt_local_tagfile_zip_RockMuonCalibration_python_modules) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_zip_RockMuonCalibration_python_modules); then /bin/rm -f $(cmt_local_tagfile_zip_RockMuonCalibration_python_modules); fi ; \
	  $(cmtexe) -tag=$(tags) $(zip_RockMuonCalibration_python_modules_extratags) build tag_makefile >>$(cmt_local_tagfile_zip_RockMuonCalibration_python_modules)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_zip_RockMuonCalibration_python_modules)"; \
	  test ! -f $(cmt_local_setup_zip_RockMuonCalibration_python_modules) || \rm -f $(cmt_local_setup_zip_RockMuonCalibration_python_modules); \
	  trap '\rm -f $(cmt_local_setup_zip_RockMuonCalibration_python_modules)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(zip_RockMuonCalibration_python_modules_extratags) show setup >$(cmt_local_setup_zip_RockMuonCalibration_python_modules) && \
	  if [ -f $(cmt_final_setup_zip_RockMuonCalibration_python_modules) ] && \
	    \cmp -s $(cmt_final_setup_zip_RockMuonCalibration_python_modules) $(cmt_local_setup_zip_RockMuonCalibration_python_modules); then \
	    \rm $(cmt_local_setup_zip_RockMuonCalibration_python_modules); else \
	    \mv -f $(cmt_local_setup_zip_RockMuonCalibration_python_modules) $(cmt_final_setup_zip_RockMuonCalibration_python_modules); fi

else

#cmt_local_tagfile_zip_RockMuonCalibration_python_modules = $(RockMuonCalibration_tag).make
cmt_local_tagfile_zip_RockMuonCalibration_python_modules = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_zip_RockMuonCalibration_python_modules = $(bin)setup.make
#cmt_final_setup_zip_RockMuonCalibration_python_modules = $(bin)RockMuonCalibrationsetup.make
cmt_local_zip_RockMuonCalibration_python_modules_makefile = $(bin)zip_RockMuonCalibration_python_modules.make

endif

ifdef STRUCTURED_OUTPUT
zip_RockMuonCalibration_python_modulesdirs :
	@if test ! -d $(bin)zip_RockMuonCalibration_python_modules; then $(mkdir) -p $(bin)zip_RockMuonCalibration_python_modules; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)zip_RockMuonCalibration_python_modules
else
zip_RockMuonCalibration_python_modulesdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# zip_RockMuonCalibration_python_modulesdirs ::
#	@if test ! -d $(bin)zip_RockMuonCalibration_python_modules; then $(mkdir) -p $(bin)zip_RockMuonCalibration_python_modules; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)zip_RockMuonCalibration_python_modules
#
#$(cmt_local_zip_RockMuonCalibration_python_modules_makefile) :: $(zip_RockMuonCalibration_python_modules_dependencies) $(cmt_local_tagfile_zip_RockMuonCalibration_python_modules) build_library_links dirs zip_RockMuonCalibration_python_modulesdirs
#else
#$(cmt_local_zip_RockMuonCalibration_python_modules_makefile) :: $(zip_RockMuonCalibration_python_modules_dependencies) $(cmt_local_tagfile_zip_RockMuonCalibration_python_modules) build_library_links dirs
#endif
#else
#$(cmt_local_zip_RockMuonCalibration_python_modules_makefile) :: $(cmt_local_tagfile_zip_RockMuonCalibration_python_modules)
#endif

makefiles : $(cmt_local_zip_RockMuonCalibration_python_modules_makefile)

ifndef QUICK
$(cmt_local_zip_RockMuonCalibration_python_modules_makefile) : $(zip_RockMuonCalibration_python_modules_dependencies) $(cmt_local_tagfile_zip_RockMuonCalibration_python_modules) build_library_links
else
$(cmt_local_zip_RockMuonCalibration_python_modules_makefile) : $(cmt_local_tagfile_zip_RockMuonCalibration_python_modules)
endif
	$(echo) "(constituents.make) Building zip_RockMuonCalibration_python_modules.make"; \
	  $(cmtexe) -tag=$(tags) $(zip_RockMuonCalibration_python_modules_extratags) build constituent_makefile -out=$(cmt_local_zip_RockMuonCalibration_python_modules_makefile) zip_RockMuonCalibration_python_modules

zip_RockMuonCalibration_python_modules :: $(zip_RockMuonCalibration_python_modules_dependencies) $(cmt_local_zip_RockMuonCalibration_python_modules_makefile) dirs zip_RockMuonCalibration_python_modulesdirs
	$(echo) "(constituents.make) Creating zip_RockMuonCalibration_python_modules${lock_suffix} and Starting zip_RockMuonCalibration_python_modules"
	@${lock_command} zip_RockMuonCalibration_python_modules${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} zip_RockMuonCalibration_python_modules${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_zip_RockMuonCalibration_python_modules_makefile) zip_RockMuonCalibration_python_modules; \
	  retval=$$?; ${unlock_command} zip_RockMuonCalibration_python_modules${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) zip_RockMuonCalibration_python_modules done"

clean :: zip_RockMuonCalibration_python_modulesclean

zip_RockMuonCalibration_python_modulesclean :: $(zip_RockMuonCalibration_python_modulesclean_dependencies) ##$(cmt_local_zip_RockMuonCalibration_python_modules_makefile)
	$(echo) "(constituents.make) Starting zip_RockMuonCalibration_python_modulesclean"
	@-if test -f $(cmt_local_zip_RockMuonCalibration_python_modules_makefile); then \
	  $(MAKE) -f $(cmt_local_zip_RockMuonCalibration_python_modules_makefile) zip_RockMuonCalibration_python_modulesclean; \
	fi
	$(echo) "(constituents.make) zip_RockMuonCalibration_python_modulesclean done"
#	@-$(MAKE) -f $(cmt_local_zip_RockMuonCalibration_python_modules_makefile) zip_RockMuonCalibration_python_modulesclean

##	  /bin/rm -f $(cmt_local_zip_RockMuonCalibration_python_modules_makefile) $(bin)zip_RockMuonCalibration_python_modules_dependencies.make

install :: zip_RockMuonCalibration_python_modulesinstall

zip_RockMuonCalibration_python_modulesinstall :: $(zip_RockMuonCalibration_python_modules_dependencies) $(cmt_local_zip_RockMuonCalibration_python_modules_makefile)
	$(echo) "(constituents.make) Starting install zip_RockMuonCalibration_python_modules"
	@-$(MAKE) -f $(cmt_local_zip_RockMuonCalibration_python_modules_makefile) install
	$(echo) "(constituents.make) install zip_RockMuonCalibration_python_modules done"

uninstall :: zip_RockMuonCalibration_python_modulesuninstall

$(foreach d,$(zip_RockMuonCalibration_python_modules_dependencies),$(eval $(d)uninstall_dependencies += zip_RockMuonCalibration_python_modulesuninstall))

zip_RockMuonCalibration_python_modulesuninstall :: $(zip_RockMuonCalibration_python_modulesuninstall_dependencies) $(cmt_local_zip_RockMuonCalibration_python_modules_makefile)
	$(echo) "(constituents.make) Starting uninstall zip_RockMuonCalibration_python_modules"
	@$(MAKE) -f $(cmt_local_zip_RockMuonCalibration_python_modules_makefile) uninstall
	$(echo) "(constituents.make) uninstall zip_RockMuonCalibration_python_modules done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ zip_RockMuonCalibration_python_modules"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ zip_RockMuonCalibration_python_modules done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_RockMuonCalibrationConfDbMerge_has_no_target_tag = 1

#--------------------------------------------------------

ifdef cmt_RockMuonCalibrationConfDbMerge_has_target_tag

#cmt_local_tagfile_RockMuonCalibrationConfDbMerge = $(RockMuonCalibration_tag)_RockMuonCalibrationConfDbMerge.make
cmt_local_tagfile_RockMuonCalibrationConfDbMerge = $(bin)$(RockMuonCalibration_tag)_RockMuonCalibrationConfDbMerge.make
cmt_local_setup_RockMuonCalibrationConfDbMerge = $(bin)setup_RockMuonCalibrationConfDbMerge$$$$.make
cmt_final_setup_RockMuonCalibrationConfDbMerge = $(bin)setup_RockMuonCalibrationConfDbMerge.make
#cmt_final_setup_RockMuonCalibrationConfDbMerge = $(bin)RockMuonCalibration_RockMuonCalibrationConfDbMergesetup.make
cmt_local_RockMuonCalibrationConfDbMerge_makefile = $(bin)RockMuonCalibrationConfDbMerge.make

RockMuonCalibrationConfDbMerge_extratags = -tag_add=target_RockMuonCalibrationConfDbMerge

#$(cmt_local_tagfile_RockMuonCalibrationConfDbMerge) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_RockMuonCalibrationConfDbMerge) ::
else
$(cmt_local_tagfile_RockMuonCalibrationConfDbMerge) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_RockMuonCalibrationConfDbMerge); then /bin/rm -f $(cmt_local_tagfile_RockMuonCalibrationConfDbMerge); fi ; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationConfDbMerge_extratags) build tag_makefile >>$(cmt_local_tagfile_RockMuonCalibrationConfDbMerge)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_RockMuonCalibrationConfDbMerge)"; \
	  test ! -f $(cmt_local_setup_RockMuonCalibrationConfDbMerge) || \rm -f $(cmt_local_setup_RockMuonCalibrationConfDbMerge); \
	  trap '\rm -f $(cmt_local_setup_RockMuonCalibrationConfDbMerge)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationConfDbMerge_extratags) show setup >$(cmt_local_setup_RockMuonCalibrationConfDbMerge) && \
	  if [ -f $(cmt_final_setup_RockMuonCalibrationConfDbMerge) ] && \
	    \cmp -s $(cmt_final_setup_RockMuonCalibrationConfDbMerge) $(cmt_local_setup_RockMuonCalibrationConfDbMerge); then \
	    \rm $(cmt_local_setup_RockMuonCalibrationConfDbMerge); else \
	    \mv -f $(cmt_local_setup_RockMuonCalibrationConfDbMerge) $(cmt_final_setup_RockMuonCalibrationConfDbMerge); fi

else

#cmt_local_tagfile_RockMuonCalibrationConfDbMerge = $(RockMuonCalibration_tag).make
cmt_local_tagfile_RockMuonCalibrationConfDbMerge = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_RockMuonCalibrationConfDbMerge = $(bin)setup.make
#cmt_final_setup_RockMuonCalibrationConfDbMerge = $(bin)RockMuonCalibrationsetup.make
cmt_local_RockMuonCalibrationConfDbMerge_makefile = $(bin)RockMuonCalibrationConfDbMerge.make

endif

ifdef STRUCTURED_OUTPUT
RockMuonCalibrationConfDbMergedirs :
	@if test ! -d $(bin)RockMuonCalibrationConfDbMerge; then $(mkdir) -p $(bin)RockMuonCalibrationConfDbMerge; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibrationConfDbMerge
else
RockMuonCalibrationConfDbMergedirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# RockMuonCalibrationConfDbMergedirs ::
#	@if test ! -d $(bin)RockMuonCalibrationConfDbMerge; then $(mkdir) -p $(bin)RockMuonCalibrationConfDbMerge; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)RockMuonCalibrationConfDbMerge
#
#$(cmt_local_RockMuonCalibrationConfDbMerge_makefile) :: $(RockMuonCalibrationConfDbMerge_dependencies) $(cmt_local_tagfile_RockMuonCalibrationConfDbMerge) build_library_links dirs RockMuonCalibrationConfDbMergedirs
#else
#$(cmt_local_RockMuonCalibrationConfDbMerge_makefile) :: $(RockMuonCalibrationConfDbMerge_dependencies) $(cmt_local_tagfile_RockMuonCalibrationConfDbMerge) build_library_links dirs
#endif
#else
#$(cmt_local_RockMuonCalibrationConfDbMerge_makefile) :: $(cmt_local_tagfile_RockMuonCalibrationConfDbMerge)
#endif

makefiles : $(cmt_local_RockMuonCalibrationConfDbMerge_makefile)

ifndef QUICK
$(cmt_local_RockMuonCalibrationConfDbMerge_makefile) : $(RockMuonCalibrationConfDbMerge_dependencies) $(cmt_local_tagfile_RockMuonCalibrationConfDbMerge) build_library_links
else
$(cmt_local_RockMuonCalibrationConfDbMerge_makefile) : $(cmt_local_tagfile_RockMuonCalibrationConfDbMerge)
endif
	$(echo) "(constituents.make) Building RockMuonCalibrationConfDbMerge.make"; \
	  $(cmtexe) -tag=$(tags) $(RockMuonCalibrationConfDbMerge_extratags) build constituent_makefile -out=$(cmt_local_RockMuonCalibrationConfDbMerge_makefile) RockMuonCalibrationConfDbMerge

RockMuonCalibrationConfDbMerge :: $(RockMuonCalibrationConfDbMerge_dependencies) $(cmt_local_RockMuonCalibrationConfDbMerge_makefile) dirs RockMuonCalibrationConfDbMergedirs
	$(echo) "(constituents.make) Creating RockMuonCalibrationConfDbMerge${lock_suffix} and Starting RockMuonCalibrationConfDbMerge"
	@${lock_command} RockMuonCalibrationConfDbMerge${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} RockMuonCalibrationConfDbMerge${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_RockMuonCalibrationConfDbMerge_makefile) RockMuonCalibrationConfDbMerge; \
	  retval=$$?; ${unlock_command} RockMuonCalibrationConfDbMerge${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) RockMuonCalibrationConfDbMerge done"

clean :: RockMuonCalibrationConfDbMergeclean

RockMuonCalibrationConfDbMergeclean :: $(RockMuonCalibrationConfDbMergeclean_dependencies) ##$(cmt_local_RockMuonCalibrationConfDbMerge_makefile)
	$(echo) "(constituents.make) Starting RockMuonCalibrationConfDbMergeclean"
	@-if test -f $(cmt_local_RockMuonCalibrationConfDbMerge_makefile); then \
	  $(MAKE) -f $(cmt_local_RockMuonCalibrationConfDbMerge_makefile) RockMuonCalibrationConfDbMergeclean; \
	fi
	$(echo) "(constituents.make) RockMuonCalibrationConfDbMergeclean done"
#	@-$(MAKE) -f $(cmt_local_RockMuonCalibrationConfDbMerge_makefile) RockMuonCalibrationConfDbMergeclean

##	  /bin/rm -f $(cmt_local_RockMuonCalibrationConfDbMerge_makefile) $(bin)RockMuonCalibrationConfDbMerge_dependencies.make

install :: RockMuonCalibrationConfDbMergeinstall

RockMuonCalibrationConfDbMergeinstall :: $(RockMuonCalibrationConfDbMerge_dependencies) $(cmt_local_RockMuonCalibrationConfDbMerge_makefile)
	$(echo) "(constituents.make) Starting install RockMuonCalibrationConfDbMerge"
	@-$(MAKE) -f $(cmt_local_RockMuonCalibrationConfDbMerge_makefile) install
	$(echo) "(constituents.make) install RockMuonCalibrationConfDbMerge done"

uninstall :: RockMuonCalibrationConfDbMergeuninstall

$(foreach d,$(RockMuonCalibrationConfDbMerge_dependencies),$(eval $(d)uninstall_dependencies += RockMuonCalibrationConfDbMergeuninstall))

RockMuonCalibrationConfDbMergeuninstall :: $(RockMuonCalibrationConfDbMergeuninstall_dependencies) $(cmt_local_RockMuonCalibrationConfDbMerge_makefile)
	$(echo) "(constituents.make) Starting uninstall RockMuonCalibrationConfDbMerge"
	@$(MAKE) -f $(cmt_local_RockMuonCalibrationConfDbMerge_makefile) uninstall
	$(echo) "(constituents.make) uninstall RockMuonCalibrationConfDbMerge done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ RockMuonCalibrationConfDbMerge"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ RockMuonCalibrationConfDbMerge done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_make_has_target_tag = 1

#--------------------------------------------------------

ifdef cmt_make_has_target_tag

#cmt_local_tagfile_make = $(RockMuonCalibration_tag)_make.make
cmt_local_tagfile_make = $(bin)$(RockMuonCalibration_tag)_make.make
cmt_local_setup_make = $(bin)setup_make$$$$.make
cmt_final_setup_make = $(bin)setup_make.make
#cmt_final_setup_make = $(bin)RockMuonCalibration_makesetup.make
cmt_local_make_makefile = $(bin)make.make

make_extratags = -tag_add=target_make

#$(cmt_local_tagfile_make) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_make) ::
else
$(cmt_local_tagfile_make) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_make); then /bin/rm -f $(cmt_local_tagfile_make); fi ; \
	  $(cmtexe) -tag=$(tags) $(make_extratags) build tag_makefile >>$(cmt_local_tagfile_make)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_make)"; \
	  test ! -f $(cmt_local_setup_make) || \rm -f $(cmt_local_setup_make); \
	  trap '\rm -f $(cmt_local_setup_make)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(make_extratags) show setup >$(cmt_local_setup_make) && \
	  if [ -f $(cmt_final_setup_make) ] && \
	    \cmp -s $(cmt_final_setup_make) $(cmt_local_setup_make); then \
	    \rm $(cmt_local_setup_make); else \
	    \mv -f $(cmt_local_setup_make) $(cmt_final_setup_make); fi

else

#cmt_local_tagfile_make = $(RockMuonCalibration_tag).make
cmt_local_tagfile_make = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_make = $(bin)setup.make
#cmt_final_setup_make = $(bin)RockMuonCalibrationsetup.make
cmt_local_make_makefile = $(bin)make.make

endif

ifdef STRUCTURED_OUTPUT
makedirs :
	@if test ! -d $(bin)make; then $(mkdir) -p $(bin)make; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)make
else
makedirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# makedirs ::
#	@if test ! -d $(bin)make; then $(mkdir) -p $(bin)make; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)make
#
#$(cmt_local_make_makefile) :: $(make_dependencies) $(cmt_local_tagfile_make) build_library_links dirs makedirs
#else
#$(cmt_local_make_makefile) :: $(make_dependencies) $(cmt_local_tagfile_make) build_library_links dirs
#endif
#else
#$(cmt_local_make_makefile) :: $(cmt_local_tagfile_make)
#endif

makefiles : $(cmt_local_make_makefile)

ifndef QUICK
$(cmt_local_make_makefile) : $(make_dependencies) $(cmt_local_tagfile_make) build_library_links
else
$(cmt_local_make_makefile) : $(cmt_local_tagfile_make)
endif
	$(echo) "(constituents.make) Building make.make"; \
	  $(cmtexe) -tag=$(tags) $(make_extratags) build constituent_makefile -out=$(cmt_local_make_makefile) make

make :: $(make_dependencies) $(cmt_local_make_makefile) dirs makedirs
	$(echo) "(constituents.make) Creating make${lock_suffix} and Starting make"
	@${lock_command} make${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} make${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_make_makefile) make; \
	  retval=$$?; ${unlock_command} make${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) make done"

clean :: makeclean

makeclean :: $(makeclean_dependencies) ##$(cmt_local_make_makefile)
	$(echo) "(constituents.make) Starting makeclean"
	@-if test -f $(cmt_local_make_makefile); then \
	  $(MAKE) -f $(cmt_local_make_makefile) makeclean; \
	fi
	$(echo) "(constituents.make) makeclean done"
#	@-$(MAKE) -f $(cmt_local_make_makefile) makeclean

##	  /bin/rm -f $(cmt_local_make_makefile) $(bin)make_dependencies.make

install :: makeinstall

makeinstall :: $(make_dependencies) $(cmt_local_make_makefile)
	$(echo) "(constituents.make) Starting install make"
	@-$(MAKE) -f $(cmt_local_make_makefile) install
	$(echo) "(constituents.make) install make done"

uninstall :: makeuninstall

$(foreach d,$(make_dependencies),$(eval $(d)uninstall_dependencies += makeuninstall))

makeuninstall :: $(makeuninstall_dependencies) $(cmt_local_make_makefile)
	$(echo) "(constituents.make) Starting uninstall make"
	@$(MAKE) -f $(cmt_local_make_makefile) uninstall
	$(echo) "(constituents.make) uninstall make done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ make"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ make done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_CompilePython_has_target_tag = 1

#--------------------------------------------------------

ifdef cmt_CompilePython_has_target_tag

#cmt_local_tagfile_CompilePython = $(RockMuonCalibration_tag)_CompilePython.make
cmt_local_tagfile_CompilePython = $(bin)$(RockMuonCalibration_tag)_CompilePython.make
cmt_local_setup_CompilePython = $(bin)setup_CompilePython$$$$.make
cmt_final_setup_CompilePython = $(bin)setup_CompilePython.make
#cmt_final_setup_CompilePython = $(bin)RockMuonCalibration_CompilePythonsetup.make
cmt_local_CompilePython_makefile = $(bin)CompilePython.make

CompilePython_extratags = -tag_add=target_CompilePython

#$(cmt_local_tagfile_CompilePython) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_CompilePython) ::
else
$(cmt_local_tagfile_CompilePython) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_CompilePython); then /bin/rm -f $(cmt_local_tagfile_CompilePython); fi ; \
	  $(cmtexe) -tag=$(tags) $(CompilePython_extratags) build tag_makefile >>$(cmt_local_tagfile_CompilePython)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_CompilePython)"; \
	  test ! -f $(cmt_local_setup_CompilePython) || \rm -f $(cmt_local_setup_CompilePython); \
	  trap '\rm -f $(cmt_local_setup_CompilePython)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(CompilePython_extratags) show setup >$(cmt_local_setup_CompilePython) && \
	  if [ -f $(cmt_final_setup_CompilePython) ] && \
	    \cmp -s $(cmt_final_setup_CompilePython) $(cmt_local_setup_CompilePython); then \
	    \rm $(cmt_local_setup_CompilePython); else \
	    \mv -f $(cmt_local_setup_CompilePython) $(cmt_final_setup_CompilePython); fi

else

#cmt_local_tagfile_CompilePython = $(RockMuonCalibration_tag).make
cmt_local_tagfile_CompilePython = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_CompilePython = $(bin)setup.make
#cmt_final_setup_CompilePython = $(bin)RockMuonCalibrationsetup.make
cmt_local_CompilePython_makefile = $(bin)CompilePython.make

endif

ifdef STRUCTURED_OUTPUT
CompilePythondirs :
	@if test ! -d $(bin)CompilePython; then $(mkdir) -p $(bin)CompilePython; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)CompilePython
else
CompilePythondirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# CompilePythondirs ::
#	@if test ! -d $(bin)CompilePython; then $(mkdir) -p $(bin)CompilePython; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)CompilePython
#
#$(cmt_local_CompilePython_makefile) :: $(CompilePython_dependencies) $(cmt_local_tagfile_CompilePython) build_library_links dirs CompilePythondirs
#else
#$(cmt_local_CompilePython_makefile) :: $(CompilePython_dependencies) $(cmt_local_tagfile_CompilePython) build_library_links dirs
#endif
#else
#$(cmt_local_CompilePython_makefile) :: $(cmt_local_tagfile_CompilePython)
#endif

makefiles : $(cmt_local_CompilePython_makefile)

ifndef QUICK
$(cmt_local_CompilePython_makefile) : $(CompilePython_dependencies) $(cmt_local_tagfile_CompilePython) build_library_links
else
$(cmt_local_CompilePython_makefile) : $(cmt_local_tagfile_CompilePython)
endif
	$(echo) "(constituents.make) Building CompilePython.make"; \
	  $(cmtexe) -tag=$(tags) $(CompilePython_extratags) build constituent_makefile -out=$(cmt_local_CompilePython_makefile) CompilePython

CompilePython :: $(CompilePython_dependencies) $(cmt_local_CompilePython_makefile) dirs CompilePythondirs
	$(echo) "(constituents.make) Creating CompilePython${lock_suffix} and Starting CompilePython"
	@${lock_command} CompilePython${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} CompilePython${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_CompilePython_makefile) CompilePython; \
	  retval=$$?; ${unlock_command} CompilePython${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) CompilePython done"

clean :: CompilePythonclean

CompilePythonclean :: $(CompilePythonclean_dependencies) ##$(cmt_local_CompilePython_makefile)
	$(echo) "(constituents.make) Starting CompilePythonclean"
	@-if test -f $(cmt_local_CompilePython_makefile); then \
	  $(MAKE) -f $(cmt_local_CompilePython_makefile) CompilePythonclean; \
	fi
	$(echo) "(constituents.make) CompilePythonclean done"
#	@-$(MAKE) -f $(cmt_local_CompilePython_makefile) CompilePythonclean

##	  /bin/rm -f $(cmt_local_CompilePython_makefile) $(bin)CompilePython_dependencies.make

install :: CompilePythoninstall

CompilePythoninstall :: $(CompilePython_dependencies) $(cmt_local_CompilePython_makefile)
	$(echo) "(constituents.make) Starting install CompilePython"
	@-$(MAKE) -f $(cmt_local_CompilePython_makefile) install
	$(echo) "(constituents.make) install CompilePython done"

uninstall :: CompilePythonuninstall

$(foreach d,$(CompilePython_dependencies),$(eval $(d)uninstall_dependencies += CompilePythonuninstall))

CompilePythonuninstall :: $(CompilePythonuninstall_dependencies) $(cmt_local_CompilePython_makefile)
	$(echo) "(constituents.make) Starting uninstall CompilePython"
	@$(MAKE) -f $(cmt_local_CompilePython_makefile) uninstall
	$(echo) "(constituents.make) uninstall CompilePython done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ CompilePython"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ CompilePython done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_qmtest_run_has_target_tag = 1

#--------------------------------------------------------

ifdef cmt_qmtest_run_has_target_tag

#cmt_local_tagfile_qmtest_run = $(RockMuonCalibration_tag)_qmtest_run.make
cmt_local_tagfile_qmtest_run = $(bin)$(RockMuonCalibration_tag)_qmtest_run.make
cmt_local_setup_qmtest_run = $(bin)setup_qmtest_run$$$$.make
cmt_final_setup_qmtest_run = $(bin)setup_qmtest_run.make
#cmt_final_setup_qmtest_run = $(bin)RockMuonCalibration_qmtest_runsetup.make
cmt_local_qmtest_run_makefile = $(bin)qmtest_run.make

qmtest_run_extratags = -tag_add=target_qmtest_run

#$(cmt_local_tagfile_qmtest_run) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_qmtest_run) ::
else
$(cmt_local_tagfile_qmtest_run) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_qmtest_run); then /bin/rm -f $(cmt_local_tagfile_qmtest_run); fi ; \
	  $(cmtexe) -tag=$(tags) $(qmtest_run_extratags) build tag_makefile >>$(cmt_local_tagfile_qmtest_run)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_qmtest_run)"; \
	  test ! -f $(cmt_local_setup_qmtest_run) || \rm -f $(cmt_local_setup_qmtest_run); \
	  trap '\rm -f $(cmt_local_setup_qmtest_run)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(qmtest_run_extratags) show setup >$(cmt_local_setup_qmtest_run) && \
	  if [ -f $(cmt_final_setup_qmtest_run) ] && \
	    \cmp -s $(cmt_final_setup_qmtest_run) $(cmt_local_setup_qmtest_run); then \
	    \rm $(cmt_local_setup_qmtest_run); else \
	    \mv -f $(cmt_local_setup_qmtest_run) $(cmt_final_setup_qmtest_run); fi

else

#cmt_local_tagfile_qmtest_run = $(RockMuonCalibration_tag).make
cmt_local_tagfile_qmtest_run = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_qmtest_run = $(bin)setup.make
#cmt_final_setup_qmtest_run = $(bin)RockMuonCalibrationsetup.make
cmt_local_qmtest_run_makefile = $(bin)qmtest_run.make

endif

ifdef STRUCTURED_OUTPUT
qmtest_rundirs :
	@if test ! -d $(bin)qmtest_run; then $(mkdir) -p $(bin)qmtest_run; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)qmtest_run
else
qmtest_rundirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# qmtest_rundirs ::
#	@if test ! -d $(bin)qmtest_run; then $(mkdir) -p $(bin)qmtest_run; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)qmtest_run
#
#$(cmt_local_qmtest_run_makefile) :: $(qmtest_run_dependencies) $(cmt_local_tagfile_qmtest_run) build_library_links dirs qmtest_rundirs
#else
#$(cmt_local_qmtest_run_makefile) :: $(qmtest_run_dependencies) $(cmt_local_tagfile_qmtest_run) build_library_links dirs
#endif
#else
#$(cmt_local_qmtest_run_makefile) :: $(cmt_local_tagfile_qmtest_run)
#endif

makefiles : $(cmt_local_qmtest_run_makefile)

ifndef QUICK
$(cmt_local_qmtest_run_makefile) : $(qmtest_run_dependencies) $(cmt_local_tagfile_qmtest_run) build_library_links
else
$(cmt_local_qmtest_run_makefile) : $(cmt_local_tagfile_qmtest_run)
endif
	$(echo) "(constituents.make) Building qmtest_run.make"; \
	  $(cmtexe) -tag=$(tags) $(qmtest_run_extratags) build constituent_makefile -out=$(cmt_local_qmtest_run_makefile) qmtest_run

qmtest_run :: $(qmtest_run_dependencies) $(cmt_local_qmtest_run_makefile) dirs qmtest_rundirs
	$(echo) "(constituents.make) Creating qmtest_run${lock_suffix} and Starting qmtest_run"
	@${lock_command} qmtest_run${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} qmtest_run${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_qmtest_run_makefile) qmtest_run; \
	  retval=$$?; ${unlock_command} qmtest_run${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) qmtest_run done"

clean :: qmtest_runclean

qmtest_runclean :: $(qmtest_runclean_dependencies) ##$(cmt_local_qmtest_run_makefile)
	$(echo) "(constituents.make) Starting qmtest_runclean"
	@-if test -f $(cmt_local_qmtest_run_makefile); then \
	  $(MAKE) -f $(cmt_local_qmtest_run_makefile) qmtest_runclean; \
	fi
	$(echo) "(constituents.make) qmtest_runclean done"
#	@-$(MAKE) -f $(cmt_local_qmtest_run_makefile) qmtest_runclean

##	  /bin/rm -f $(cmt_local_qmtest_run_makefile) $(bin)qmtest_run_dependencies.make

install :: qmtest_runinstall

qmtest_runinstall :: $(qmtest_run_dependencies) $(cmt_local_qmtest_run_makefile)
	$(echo) "(constituents.make) Starting install qmtest_run"
	@-$(MAKE) -f $(cmt_local_qmtest_run_makefile) install
	$(echo) "(constituents.make) install qmtest_run done"

uninstall :: qmtest_rununinstall

$(foreach d,$(qmtest_run_dependencies),$(eval $(d)uninstall_dependencies += qmtest_rununinstall))

qmtest_rununinstall :: $(qmtest_rununinstall_dependencies) $(cmt_local_qmtest_run_makefile)
	$(echo) "(constituents.make) Starting uninstall qmtest_run"
	@$(MAKE) -f $(cmt_local_qmtest_run_makefile) uninstall
	$(echo) "(constituents.make) uninstall qmtest_run done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ qmtest_run"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ qmtest_run done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_qmtest_summarize_has_target_tag = 1

#--------------------------------------------------------

ifdef cmt_qmtest_summarize_has_target_tag

#cmt_local_tagfile_qmtest_summarize = $(RockMuonCalibration_tag)_qmtest_summarize.make
cmt_local_tagfile_qmtest_summarize = $(bin)$(RockMuonCalibration_tag)_qmtest_summarize.make
cmt_local_setup_qmtest_summarize = $(bin)setup_qmtest_summarize$$$$.make
cmt_final_setup_qmtest_summarize = $(bin)setup_qmtest_summarize.make
#cmt_final_setup_qmtest_summarize = $(bin)RockMuonCalibration_qmtest_summarizesetup.make
cmt_local_qmtest_summarize_makefile = $(bin)qmtest_summarize.make

qmtest_summarize_extratags = -tag_add=target_qmtest_summarize

#$(cmt_local_tagfile_qmtest_summarize) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_qmtest_summarize) ::
else
$(cmt_local_tagfile_qmtest_summarize) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_qmtest_summarize); then /bin/rm -f $(cmt_local_tagfile_qmtest_summarize); fi ; \
	  $(cmtexe) -tag=$(tags) $(qmtest_summarize_extratags) build tag_makefile >>$(cmt_local_tagfile_qmtest_summarize)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_qmtest_summarize)"; \
	  test ! -f $(cmt_local_setup_qmtest_summarize) || \rm -f $(cmt_local_setup_qmtest_summarize); \
	  trap '\rm -f $(cmt_local_setup_qmtest_summarize)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(qmtest_summarize_extratags) show setup >$(cmt_local_setup_qmtest_summarize) && \
	  if [ -f $(cmt_final_setup_qmtest_summarize) ] && \
	    \cmp -s $(cmt_final_setup_qmtest_summarize) $(cmt_local_setup_qmtest_summarize); then \
	    \rm $(cmt_local_setup_qmtest_summarize); else \
	    \mv -f $(cmt_local_setup_qmtest_summarize) $(cmt_final_setup_qmtest_summarize); fi

else

#cmt_local_tagfile_qmtest_summarize = $(RockMuonCalibration_tag).make
cmt_local_tagfile_qmtest_summarize = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_qmtest_summarize = $(bin)setup.make
#cmt_final_setup_qmtest_summarize = $(bin)RockMuonCalibrationsetup.make
cmt_local_qmtest_summarize_makefile = $(bin)qmtest_summarize.make

endif

ifdef STRUCTURED_OUTPUT
qmtest_summarizedirs :
	@if test ! -d $(bin)qmtest_summarize; then $(mkdir) -p $(bin)qmtest_summarize; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)qmtest_summarize
else
qmtest_summarizedirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# qmtest_summarizedirs ::
#	@if test ! -d $(bin)qmtest_summarize; then $(mkdir) -p $(bin)qmtest_summarize; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)qmtest_summarize
#
#$(cmt_local_qmtest_summarize_makefile) :: $(qmtest_summarize_dependencies) $(cmt_local_tagfile_qmtest_summarize) build_library_links dirs qmtest_summarizedirs
#else
#$(cmt_local_qmtest_summarize_makefile) :: $(qmtest_summarize_dependencies) $(cmt_local_tagfile_qmtest_summarize) build_library_links dirs
#endif
#else
#$(cmt_local_qmtest_summarize_makefile) :: $(cmt_local_tagfile_qmtest_summarize)
#endif

makefiles : $(cmt_local_qmtest_summarize_makefile)

ifndef QUICK
$(cmt_local_qmtest_summarize_makefile) : $(qmtest_summarize_dependencies) $(cmt_local_tagfile_qmtest_summarize) build_library_links
else
$(cmt_local_qmtest_summarize_makefile) : $(cmt_local_tagfile_qmtest_summarize)
endif
	$(echo) "(constituents.make) Building qmtest_summarize.make"; \
	  $(cmtexe) -tag=$(tags) $(qmtest_summarize_extratags) build constituent_makefile -out=$(cmt_local_qmtest_summarize_makefile) qmtest_summarize

qmtest_summarize :: $(qmtest_summarize_dependencies) $(cmt_local_qmtest_summarize_makefile) dirs qmtest_summarizedirs
	$(echo) "(constituents.make) Creating qmtest_summarize${lock_suffix} and Starting qmtest_summarize"
	@${lock_command} qmtest_summarize${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} qmtest_summarize${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_qmtest_summarize_makefile) qmtest_summarize; \
	  retval=$$?; ${unlock_command} qmtest_summarize${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) qmtest_summarize done"

clean :: qmtest_summarizeclean

qmtest_summarizeclean :: $(qmtest_summarizeclean_dependencies) ##$(cmt_local_qmtest_summarize_makefile)
	$(echo) "(constituents.make) Starting qmtest_summarizeclean"
	@-if test -f $(cmt_local_qmtest_summarize_makefile); then \
	  $(MAKE) -f $(cmt_local_qmtest_summarize_makefile) qmtest_summarizeclean; \
	fi
	$(echo) "(constituents.make) qmtest_summarizeclean done"
#	@-$(MAKE) -f $(cmt_local_qmtest_summarize_makefile) qmtest_summarizeclean

##	  /bin/rm -f $(cmt_local_qmtest_summarize_makefile) $(bin)qmtest_summarize_dependencies.make

install :: qmtest_summarizeinstall

qmtest_summarizeinstall :: $(qmtest_summarize_dependencies) $(cmt_local_qmtest_summarize_makefile)
	$(echo) "(constituents.make) Starting install qmtest_summarize"
	@-$(MAKE) -f $(cmt_local_qmtest_summarize_makefile) install
	$(echo) "(constituents.make) install qmtest_summarize done"

uninstall :: qmtest_summarizeuninstall

$(foreach d,$(qmtest_summarize_dependencies),$(eval $(d)uninstall_dependencies += qmtest_summarizeuninstall))

qmtest_summarizeuninstall :: $(qmtest_summarizeuninstall_dependencies) $(cmt_local_qmtest_summarize_makefile)
	$(echo) "(constituents.make) Starting uninstall qmtest_summarize"
	@$(MAKE) -f $(cmt_local_qmtest_summarize_makefile) uninstall
	$(echo) "(constituents.make) uninstall qmtest_summarize done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ qmtest_summarize"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ qmtest_summarize done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_TestPackage_has_target_tag = 1

#--------------------------------------------------------

ifdef cmt_TestPackage_has_target_tag

#cmt_local_tagfile_TestPackage = $(RockMuonCalibration_tag)_TestPackage.make
cmt_local_tagfile_TestPackage = $(bin)$(RockMuonCalibration_tag)_TestPackage.make
cmt_local_setup_TestPackage = $(bin)setup_TestPackage$$$$.make
cmt_final_setup_TestPackage = $(bin)setup_TestPackage.make
#cmt_final_setup_TestPackage = $(bin)RockMuonCalibration_TestPackagesetup.make
cmt_local_TestPackage_makefile = $(bin)TestPackage.make

TestPackage_extratags = -tag_add=target_TestPackage

#$(cmt_local_tagfile_TestPackage) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_TestPackage) ::
else
$(cmt_local_tagfile_TestPackage) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_TestPackage); then /bin/rm -f $(cmt_local_tagfile_TestPackage); fi ; \
	  $(cmtexe) -tag=$(tags) $(TestPackage_extratags) build tag_makefile >>$(cmt_local_tagfile_TestPackage)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_TestPackage)"; \
	  test ! -f $(cmt_local_setup_TestPackage) || \rm -f $(cmt_local_setup_TestPackage); \
	  trap '\rm -f $(cmt_local_setup_TestPackage)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(TestPackage_extratags) show setup >$(cmt_local_setup_TestPackage) && \
	  if [ -f $(cmt_final_setup_TestPackage) ] && \
	    \cmp -s $(cmt_final_setup_TestPackage) $(cmt_local_setup_TestPackage); then \
	    \rm $(cmt_local_setup_TestPackage); else \
	    \mv -f $(cmt_local_setup_TestPackage) $(cmt_final_setup_TestPackage); fi

else

#cmt_local_tagfile_TestPackage = $(RockMuonCalibration_tag).make
cmt_local_tagfile_TestPackage = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_TestPackage = $(bin)setup.make
#cmt_final_setup_TestPackage = $(bin)RockMuonCalibrationsetup.make
cmt_local_TestPackage_makefile = $(bin)TestPackage.make

endif

ifdef STRUCTURED_OUTPUT
TestPackagedirs :
	@if test ! -d $(bin)TestPackage; then $(mkdir) -p $(bin)TestPackage; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)TestPackage
else
TestPackagedirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# TestPackagedirs ::
#	@if test ! -d $(bin)TestPackage; then $(mkdir) -p $(bin)TestPackage; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)TestPackage
#
#$(cmt_local_TestPackage_makefile) :: $(TestPackage_dependencies) $(cmt_local_tagfile_TestPackage) build_library_links dirs TestPackagedirs
#else
#$(cmt_local_TestPackage_makefile) :: $(TestPackage_dependencies) $(cmt_local_tagfile_TestPackage) build_library_links dirs
#endif
#else
#$(cmt_local_TestPackage_makefile) :: $(cmt_local_tagfile_TestPackage)
#endif

makefiles : $(cmt_local_TestPackage_makefile)

ifndef QUICK
$(cmt_local_TestPackage_makefile) : $(TestPackage_dependencies) $(cmt_local_tagfile_TestPackage) build_library_links
else
$(cmt_local_TestPackage_makefile) : $(cmt_local_tagfile_TestPackage)
endif
	$(echo) "(constituents.make) Building TestPackage.make"; \
	  $(cmtexe) -tag=$(tags) $(TestPackage_extratags) build constituent_makefile -out=$(cmt_local_TestPackage_makefile) TestPackage

TestPackage :: $(TestPackage_dependencies) $(cmt_local_TestPackage_makefile) dirs TestPackagedirs
	$(echo) "(constituents.make) Creating TestPackage${lock_suffix} and Starting TestPackage"
	@${lock_command} TestPackage${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} TestPackage${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_TestPackage_makefile) TestPackage; \
	  retval=$$?; ${unlock_command} TestPackage${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) TestPackage done"

clean :: TestPackageclean

TestPackageclean :: $(TestPackageclean_dependencies) ##$(cmt_local_TestPackage_makefile)
	$(echo) "(constituents.make) Starting TestPackageclean"
	@-if test -f $(cmt_local_TestPackage_makefile); then \
	  $(MAKE) -f $(cmt_local_TestPackage_makefile) TestPackageclean; \
	fi
	$(echo) "(constituents.make) TestPackageclean done"
#	@-$(MAKE) -f $(cmt_local_TestPackage_makefile) TestPackageclean

##	  /bin/rm -f $(cmt_local_TestPackage_makefile) $(bin)TestPackage_dependencies.make

install :: TestPackageinstall

TestPackageinstall :: $(TestPackage_dependencies) $(cmt_local_TestPackage_makefile)
	$(echo) "(constituents.make) Starting install TestPackage"
	@-$(MAKE) -f $(cmt_local_TestPackage_makefile) install
	$(echo) "(constituents.make) install TestPackage done"

uninstall :: TestPackageuninstall

$(foreach d,$(TestPackage_dependencies),$(eval $(d)uninstall_dependencies += TestPackageuninstall))

TestPackageuninstall :: $(TestPackageuninstall_dependencies) $(cmt_local_TestPackage_makefile)
	$(echo) "(constituents.make) Starting uninstall TestPackage"
	@$(MAKE) -f $(cmt_local_TestPackage_makefile) uninstall
	$(echo) "(constituents.make) uninstall TestPackage done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ TestPackage"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ TestPackage done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_TestProject_has_target_tag = 1

#--------------------------------------------------------

ifdef cmt_TestProject_has_target_tag

#cmt_local_tagfile_TestProject = $(RockMuonCalibration_tag)_TestProject.make
cmt_local_tagfile_TestProject = $(bin)$(RockMuonCalibration_tag)_TestProject.make
cmt_local_setup_TestProject = $(bin)setup_TestProject$$$$.make
cmt_final_setup_TestProject = $(bin)setup_TestProject.make
#cmt_final_setup_TestProject = $(bin)RockMuonCalibration_TestProjectsetup.make
cmt_local_TestProject_makefile = $(bin)TestProject.make

TestProject_extratags = -tag_add=target_TestProject

#$(cmt_local_tagfile_TestProject) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_TestProject) ::
else
$(cmt_local_tagfile_TestProject) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_TestProject); then /bin/rm -f $(cmt_local_tagfile_TestProject); fi ; \
	  $(cmtexe) -tag=$(tags) $(TestProject_extratags) build tag_makefile >>$(cmt_local_tagfile_TestProject)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_TestProject)"; \
	  test ! -f $(cmt_local_setup_TestProject) || \rm -f $(cmt_local_setup_TestProject); \
	  trap '\rm -f $(cmt_local_setup_TestProject)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(TestProject_extratags) show setup >$(cmt_local_setup_TestProject) && \
	  if [ -f $(cmt_final_setup_TestProject) ] && \
	    \cmp -s $(cmt_final_setup_TestProject) $(cmt_local_setup_TestProject); then \
	    \rm $(cmt_local_setup_TestProject); else \
	    \mv -f $(cmt_local_setup_TestProject) $(cmt_final_setup_TestProject); fi

else

#cmt_local_tagfile_TestProject = $(RockMuonCalibration_tag).make
cmt_local_tagfile_TestProject = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_TestProject = $(bin)setup.make
#cmt_final_setup_TestProject = $(bin)RockMuonCalibrationsetup.make
cmt_local_TestProject_makefile = $(bin)TestProject.make

endif

ifdef STRUCTURED_OUTPUT
TestProjectdirs :
	@if test ! -d $(bin)TestProject; then $(mkdir) -p $(bin)TestProject; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)TestProject
else
TestProjectdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# TestProjectdirs ::
#	@if test ! -d $(bin)TestProject; then $(mkdir) -p $(bin)TestProject; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)TestProject
#
#$(cmt_local_TestProject_makefile) :: $(TestProject_dependencies) $(cmt_local_tagfile_TestProject) build_library_links dirs TestProjectdirs
#else
#$(cmt_local_TestProject_makefile) :: $(TestProject_dependencies) $(cmt_local_tagfile_TestProject) build_library_links dirs
#endif
#else
#$(cmt_local_TestProject_makefile) :: $(cmt_local_tagfile_TestProject)
#endif

makefiles : $(cmt_local_TestProject_makefile)

ifndef QUICK
$(cmt_local_TestProject_makefile) : $(TestProject_dependencies) $(cmt_local_tagfile_TestProject) build_library_links
else
$(cmt_local_TestProject_makefile) : $(cmt_local_tagfile_TestProject)
endif
	$(echo) "(constituents.make) Building TestProject.make"; \
	  $(cmtexe) -tag=$(tags) $(TestProject_extratags) build constituent_makefile -out=$(cmt_local_TestProject_makefile) TestProject

TestProject :: $(TestProject_dependencies) $(cmt_local_TestProject_makefile) dirs TestProjectdirs
	$(echo) "(constituents.make) Creating TestProject${lock_suffix} and Starting TestProject"
	@${lock_command} TestProject${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} TestProject${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_TestProject_makefile) TestProject; \
	  retval=$$?; ${unlock_command} TestProject${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) TestProject done"

clean :: TestProjectclean

TestProjectclean :: $(TestProjectclean_dependencies) ##$(cmt_local_TestProject_makefile)
	$(echo) "(constituents.make) Starting TestProjectclean"
	@-if test -f $(cmt_local_TestProject_makefile); then \
	  $(MAKE) -f $(cmt_local_TestProject_makefile) TestProjectclean; \
	fi
	$(echo) "(constituents.make) TestProjectclean done"
#	@-$(MAKE) -f $(cmt_local_TestProject_makefile) TestProjectclean

##	  /bin/rm -f $(cmt_local_TestProject_makefile) $(bin)TestProject_dependencies.make

install :: TestProjectinstall

TestProjectinstall :: $(TestProject_dependencies) $(cmt_local_TestProject_makefile)
	$(echo) "(constituents.make) Starting install TestProject"
	@-$(MAKE) -f $(cmt_local_TestProject_makefile) install
	$(echo) "(constituents.make) install TestProject done"

uninstall :: TestProjectuninstall

$(foreach d,$(TestProject_dependencies),$(eval $(d)uninstall_dependencies += TestProjectuninstall))

TestProjectuninstall :: $(TestProjectuninstall_dependencies) $(cmt_local_TestProject_makefile)
	$(echo) "(constituents.make) Starting uninstall TestProject"
	@$(MAKE) -f $(cmt_local_TestProject_makefile) uninstall
	$(echo) "(constituents.make) uninstall TestProject done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ TestProject"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ TestProject done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_new_rootsys_has_target_tag = 1

#--------------------------------------------------------

ifdef cmt_new_rootsys_has_target_tag

#cmt_local_tagfile_new_rootsys = $(RockMuonCalibration_tag)_new_rootsys.make
cmt_local_tagfile_new_rootsys = $(bin)$(RockMuonCalibration_tag)_new_rootsys.make
cmt_local_setup_new_rootsys = $(bin)setup_new_rootsys$$$$.make
cmt_final_setup_new_rootsys = $(bin)setup_new_rootsys.make
#cmt_final_setup_new_rootsys = $(bin)RockMuonCalibration_new_rootsyssetup.make
cmt_local_new_rootsys_makefile = $(bin)new_rootsys.make

new_rootsys_extratags = -tag_add=target_new_rootsys

#$(cmt_local_tagfile_new_rootsys) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_new_rootsys) ::
else
$(cmt_local_tagfile_new_rootsys) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_new_rootsys); then /bin/rm -f $(cmt_local_tagfile_new_rootsys); fi ; \
	  $(cmtexe) -tag=$(tags) $(new_rootsys_extratags) build tag_makefile >>$(cmt_local_tagfile_new_rootsys)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_new_rootsys)"; \
	  test ! -f $(cmt_local_setup_new_rootsys) || \rm -f $(cmt_local_setup_new_rootsys); \
	  trap '\rm -f $(cmt_local_setup_new_rootsys)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(new_rootsys_extratags) show setup >$(cmt_local_setup_new_rootsys) && \
	  if [ -f $(cmt_final_setup_new_rootsys) ] && \
	    \cmp -s $(cmt_final_setup_new_rootsys) $(cmt_local_setup_new_rootsys); then \
	    \rm $(cmt_local_setup_new_rootsys); else \
	    \mv -f $(cmt_local_setup_new_rootsys) $(cmt_final_setup_new_rootsys); fi

else

#cmt_local_tagfile_new_rootsys = $(RockMuonCalibration_tag).make
cmt_local_tagfile_new_rootsys = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_new_rootsys = $(bin)setup.make
#cmt_final_setup_new_rootsys = $(bin)RockMuonCalibrationsetup.make
cmt_local_new_rootsys_makefile = $(bin)new_rootsys.make

endif

ifdef STRUCTURED_OUTPUT
new_rootsysdirs :
	@if test ! -d $(bin)new_rootsys; then $(mkdir) -p $(bin)new_rootsys; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)new_rootsys
else
new_rootsysdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# new_rootsysdirs ::
#	@if test ! -d $(bin)new_rootsys; then $(mkdir) -p $(bin)new_rootsys; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)new_rootsys
#
#$(cmt_local_new_rootsys_makefile) :: $(new_rootsys_dependencies) $(cmt_local_tagfile_new_rootsys) build_library_links dirs new_rootsysdirs
#else
#$(cmt_local_new_rootsys_makefile) :: $(new_rootsys_dependencies) $(cmt_local_tagfile_new_rootsys) build_library_links dirs
#endif
#else
#$(cmt_local_new_rootsys_makefile) :: $(cmt_local_tagfile_new_rootsys)
#endif

makefiles : $(cmt_local_new_rootsys_makefile)

ifndef QUICK
$(cmt_local_new_rootsys_makefile) : $(new_rootsys_dependencies) $(cmt_local_tagfile_new_rootsys) build_library_links
else
$(cmt_local_new_rootsys_makefile) : $(cmt_local_tagfile_new_rootsys)
endif
	$(echo) "(constituents.make) Building new_rootsys.make"; \
	  $(cmtexe) -tag=$(tags) $(new_rootsys_extratags) build constituent_makefile -out=$(cmt_local_new_rootsys_makefile) new_rootsys

new_rootsys :: $(new_rootsys_dependencies) $(cmt_local_new_rootsys_makefile) dirs new_rootsysdirs
	$(echo) "(constituents.make) Creating new_rootsys${lock_suffix} and Starting new_rootsys"
	@${lock_command} new_rootsys${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} new_rootsys${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_new_rootsys_makefile) new_rootsys; \
	  retval=$$?; ${unlock_command} new_rootsys${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) new_rootsys done"

clean :: new_rootsysclean

new_rootsysclean :: $(new_rootsysclean_dependencies) ##$(cmt_local_new_rootsys_makefile)
	$(echo) "(constituents.make) Starting new_rootsysclean"
	@-if test -f $(cmt_local_new_rootsys_makefile); then \
	  $(MAKE) -f $(cmt_local_new_rootsys_makefile) new_rootsysclean; \
	fi
	$(echo) "(constituents.make) new_rootsysclean done"
#	@-$(MAKE) -f $(cmt_local_new_rootsys_makefile) new_rootsysclean

##	  /bin/rm -f $(cmt_local_new_rootsys_makefile) $(bin)new_rootsys_dependencies.make

install :: new_rootsysinstall

new_rootsysinstall :: $(new_rootsys_dependencies) $(cmt_local_new_rootsys_makefile)
	$(echo) "(constituents.make) Starting install new_rootsys"
	@-$(MAKE) -f $(cmt_local_new_rootsys_makefile) install
	$(echo) "(constituents.make) install new_rootsys done"

uninstall :: new_rootsysuninstall

$(foreach d,$(new_rootsys_dependencies),$(eval $(d)uninstall_dependencies += new_rootsysuninstall))

new_rootsysuninstall :: $(new_rootsysuninstall_dependencies) $(cmt_local_new_rootsys_makefile)
	$(echo) "(constituents.make) Starting uninstall new_rootsys"
	@$(MAKE) -f $(cmt_local_new_rootsys_makefile) uninstall
	$(echo) "(constituents.make) uninstall new_rootsys done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ new_rootsys"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ new_rootsys done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_dowork_has_target_tag = 1

#--------------------------------------------------------

ifdef cmt_dowork_has_target_tag

#cmt_local_tagfile_dowork = $(RockMuonCalibration_tag)_dowork.make
cmt_local_tagfile_dowork = $(bin)$(RockMuonCalibration_tag)_dowork.make
cmt_local_setup_dowork = $(bin)setup_dowork$$$$.make
cmt_final_setup_dowork = $(bin)setup_dowork.make
#cmt_final_setup_dowork = $(bin)RockMuonCalibration_doworksetup.make
cmt_local_dowork_makefile = $(bin)dowork.make

dowork_extratags = -tag_add=target_dowork

#$(cmt_local_tagfile_dowork) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_dowork) ::
else
$(cmt_local_tagfile_dowork) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_dowork); then /bin/rm -f $(cmt_local_tagfile_dowork); fi ; \
	  $(cmtexe) -tag=$(tags) $(dowork_extratags) build tag_makefile >>$(cmt_local_tagfile_dowork)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_dowork)"; \
	  test ! -f $(cmt_local_setup_dowork) || \rm -f $(cmt_local_setup_dowork); \
	  trap '\rm -f $(cmt_local_setup_dowork)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(dowork_extratags) show setup >$(cmt_local_setup_dowork) && \
	  if [ -f $(cmt_final_setup_dowork) ] && \
	    \cmp -s $(cmt_final_setup_dowork) $(cmt_local_setup_dowork); then \
	    \rm $(cmt_local_setup_dowork); else \
	    \mv -f $(cmt_local_setup_dowork) $(cmt_final_setup_dowork); fi

else

#cmt_local_tagfile_dowork = $(RockMuonCalibration_tag).make
cmt_local_tagfile_dowork = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_dowork = $(bin)setup.make
#cmt_final_setup_dowork = $(bin)RockMuonCalibrationsetup.make
cmt_local_dowork_makefile = $(bin)dowork.make

endif

ifdef STRUCTURED_OUTPUT
doworkdirs :
	@if test ! -d $(bin)dowork; then $(mkdir) -p $(bin)dowork; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)dowork
else
doworkdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# doworkdirs ::
#	@if test ! -d $(bin)dowork; then $(mkdir) -p $(bin)dowork; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)dowork
#
#$(cmt_local_dowork_makefile) :: $(dowork_dependencies) $(cmt_local_tagfile_dowork) build_library_links dirs doworkdirs
#else
#$(cmt_local_dowork_makefile) :: $(dowork_dependencies) $(cmt_local_tagfile_dowork) build_library_links dirs
#endif
#else
#$(cmt_local_dowork_makefile) :: $(cmt_local_tagfile_dowork)
#endif

makefiles : $(cmt_local_dowork_makefile)

ifndef QUICK
$(cmt_local_dowork_makefile) : $(dowork_dependencies) $(cmt_local_tagfile_dowork) build_library_links
else
$(cmt_local_dowork_makefile) : $(cmt_local_tagfile_dowork)
endif
	$(echo) "(constituents.make) Building dowork.make"; \
	  $(cmtexe) -tag=$(tags) $(dowork_extratags) build constituent_makefile -out=$(cmt_local_dowork_makefile) dowork

dowork :: $(dowork_dependencies) $(cmt_local_dowork_makefile) dirs doworkdirs
	$(echo) "(constituents.make) Creating dowork${lock_suffix} and Starting dowork"
	@${lock_command} dowork${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} dowork${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_dowork_makefile) dowork; \
	  retval=$$?; ${unlock_command} dowork${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) dowork done"

clean :: doworkclean

doworkclean :: $(doworkclean_dependencies) ##$(cmt_local_dowork_makefile)
	$(echo) "(constituents.make) Starting doworkclean"
	@-if test -f $(cmt_local_dowork_makefile); then \
	  $(MAKE) -f $(cmt_local_dowork_makefile) doworkclean; \
	fi
	$(echo) "(constituents.make) doworkclean done"
#	@-$(MAKE) -f $(cmt_local_dowork_makefile) doworkclean

##	  /bin/rm -f $(cmt_local_dowork_makefile) $(bin)dowork_dependencies.make

install :: doworkinstall

doworkinstall :: $(dowork_dependencies) $(cmt_local_dowork_makefile)
	$(echo) "(constituents.make) Starting install dowork"
	@-$(MAKE) -f $(cmt_local_dowork_makefile) install
	$(echo) "(constituents.make) install dowork done"

uninstall :: doworkuninstall

$(foreach d,$(dowork_dependencies),$(eval $(d)uninstall_dependencies += doworkuninstall))

doworkuninstall :: $(doworkuninstall_dependencies) $(cmt_local_dowork_makefile)
	$(echo) "(constituents.make) Starting uninstall dowork"
	@$(MAKE) -f $(cmt_local_dowork_makefile) uninstall
	$(echo) "(constituents.make) uninstall dowork done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ dowork"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ dowork done"
endif

#-- end of constituent_lock ------
#-- start of constituent_lock ------

cmt_symlinks_has_target_tag = 1

#--------------------------------------------------------

ifdef cmt_symlinks_has_target_tag

#cmt_local_tagfile_symlinks = $(RockMuonCalibration_tag)_symlinks.make
cmt_local_tagfile_symlinks = $(bin)$(RockMuonCalibration_tag)_symlinks.make
cmt_local_setup_symlinks = $(bin)setup_symlinks$$$$.make
cmt_final_setup_symlinks = $(bin)setup_symlinks.make
#cmt_final_setup_symlinks = $(bin)RockMuonCalibration_symlinkssetup.make
cmt_local_symlinks_makefile = $(bin)symlinks.make

symlinks_extratags = -tag_add=target_symlinks

#$(cmt_local_tagfile_symlinks) : $(cmt_lock_setup)
ifndef QUICK
$(cmt_local_tagfile_symlinks) ::
else
$(cmt_local_tagfile_symlinks) :
endif
	$(echo) "(constituents.make) Rebuilding $@"; \
	  if test -f $(cmt_local_tagfile_symlinks); then /bin/rm -f $(cmt_local_tagfile_symlinks); fi ; \
	  $(cmtexe) -tag=$(tags) $(symlinks_extratags) build tag_makefile >>$(cmt_local_tagfile_symlinks)
	$(echo) "(constituents.make) Rebuilding $(cmt_final_setup_symlinks)"; \
	  test ! -f $(cmt_local_setup_symlinks) || \rm -f $(cmt_local_setup_symlinks); \
	  trap '\rm -f $(cmt_local_setup_symlinks)' 0 1 2 15; \
	  $(cmtexe) -tag=$(tags) $(symlinks_extratags) show setup >$(cmt_local_setup_symlinks) && \
	  if [ -f $(cmt_final_setup_symlinks) ] && \
	    \cmp -s $(cmt_final_setup_symlinks) $(cmt_local_setup_symlinks); then \
	    \rm $(cmt_local_setup_symlinks); else \
	    \mv -f $(cmt_local_setup_symlinks) $(cmt_final_setup_symlinks); fi

else

#cmt_local_tagfile_symlinks = $(RockMuonCalibration_tag).make
cmt_local_tagfile_symlinks = $(bin)$(RockMuonCalibration_tag).make
cmt_final_setup_symlinks = $(bin)setup.make
#cmt_final_setup_symlinks = $(bin)RockMuonCalibrationsetup.make
cmt_local_symlinks_makefile = $(bin)symlinks.make

endif

ifdef STRUCTURED_OUTPUT
symlinksdirs :
	@if test ! -d $(bin)symlinks; then $(mkdir) -p $(bin)symlinks; fi
	$(echo) "STRUCTURED_OUTPUT="$(bin)symlinks
else
symlinksdirs : ;
endif

#ifndef QUICK
#ifdef STRUCTURED_OUTPUT
# symlinksdirs ::
#	@if test ! -d $(bin)symlinks; then $(mkdir) -p $(bin)symlinks; fi
#	$(echo) "STRUCTURED_OUTPUT="$(bin)symlinks
#
#$(cmt_local_symlinks_makefile) :: $(symlinks_dependencies) $(cmt_local_tagfile_symlinks) build_library_links dirs symlinksdirs
#else
#$(cmt_local_symlinks_makefile) :: $(symlinks_dependencies) $(cmt_local_tagfile_symlinks) build_library_links dirs
#endif
#else
#$(cmt_local_symlinks_makefile) :: $(cmt_local_tagfile_symlinks)
#endif

makefiles : $(cmt_local_symlinks_makefile)

ifndef QUICK
$(cmt_local_symlinks_makefile) : $(symlinks_dependencies) $(cmt_local_tagfile_symlinks) build_library_links
else
$(cmt_local_symlinks_makefile) : $(cmt_local_tagfile_symlinks)
endif
	$(echo) "(constituents.make) Building symlinks.make"; \
	  $(cmtexe) -tag=$(tags) $(symlinks_extratags) build constituent_makefile -out=$(cmt_local_symlinks_makefile) symlinks

symlinks :: $(symlinks_dependencies) $(cmt_local_symlinks_makefile) dirs symlinksdirs
	$(echo) "(constituents.make) Creating symlinks${lock_suffix} and Starting symlinks"
	@${lock_command} symlinks${lock_suffix} || exit $$?; \
	  retval=$$?; \
	  trap '${unlock_command} symlinks${lock_suffix}; exit $${retval}' 1 2 15; \
	  $(MAKE) -f $(cmt_local_symlinks_makefile) symlinks; \
	  retval=$$?; ${unlock_command} symlinks${lock_suffix}; exit $${retval}
	$(echo) "(constituents.make) symlinks done"

clean :: symlinksclean

symlinksclean :: $(symlinksclean_dependencies) ##$(cmt_local_symlinks_makefile)
	$(echo) "(constituents.make) Starting symlinksclean"
	@-if test -f $(cmt_local_symlinks_makefile); then \
	  $(MAKE) -f $(cmt_local_symlinks_makefile) symlinksclean; \
	fi
	$(echo) "(constituents.make) symlinksclean done"
#	@-$(MAKE) -f $(cmt_local_symlinks_makefile) symlinksclean

##	  /bin/rm -f $(cmt_local_symlinks_makefile) $(bin)symlinks_dependencies.make

install :: symlinksinstall

symlinksinstall :: $(symlinks_dependencies) $(cmt_local_symlinks_makefile)
	$(echo) "(constituents.make) Starting install symlinks"
	@-$(MAKE) -f $(cmt_local_symlinks_makefile) install
	$(echo) "(constituents.make) install symlinks done"

uninstall :: symlinksuninstall

$(foreach d,$(symlinks_dependencies),$(eval $(d)uninstall_dependencies += symlinksuninstall))

symlinksuninstall :: $(symlinksuninstall_dependencies) $(cmt_local_symlinks_makefile)
	$(echo) "(constituents.make) Starting uninstall symlinks"
	@$(MAKE) -f $(cmt_local_symlinks_makefile) uninstall
	$(echo) "(constituents.make) uninstall symlinks done"

ifndef PEDANTIC
.DEFAULT::
	$(echo) "(constituents.make) Starting $@ symlinks"
	$(echo) Using default action for $@
	$(echo) "(constituents.make) $@ symlinks done"
endif

#-- end of constituent_lock ------
#-- start of constituents_trailer ------

clean :: remove_library_links

remove_library_links ::
	$(echo) "(constituents.make) Removing library links"; \
	  $(remove_library_links)

makefilesclean ::

###	@/bin/rm -f checkuses

###	/bin/rm -f *.make*

clean :: makefilesclean

binclean :: clean
	$(echo) "(constituents.make) Removing binary directory $(bin)"
	@if test ! "$(bin)" = "./"; then \
	  /bin/rm -rf $(bin); \
	fi

#-- end of constituents_trailer ------
