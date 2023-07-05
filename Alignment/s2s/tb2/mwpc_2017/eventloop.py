#
# This code loops over the mwpc dat file and saves it into a root file.
#
#
#
# Jeffrey Kleykamp
# 11/6/2015
#

import eventclass
import clusterclass
import hitclass
import helper
import calibration

import ROOT

import collections
import datetime
import os
import traceback
import array
import math
import itertools
import pprint
import logging

# Set constants
# max number of read errors before quitting
MAX_ERRORS = 10
# print status every EVENT_PRINT_RATE
EVENT_PRINT_RATE = 1000
# this takes mwpc tdc ticks and turns it into nanoseconds
# the value is based on a study. The website says 1.18 ns but it's closer to 1.177ns
MWPC_TDC_TIME_CONST  = 1.177 # ns
USE_TIMECUT = True # whether to do the afterpulsing time cut
TIMECUTNSIGMA = 1 # the number of sigma to use for the time cut
VERBOSETIMECUT = False # whether to print afterpulsing time fit parameters
DRAW_TIMEHIST = True # whether to draw the hits as function of time plot
PRINTSTATS = True # print statistics about various processes

# auto-calibration configuration.
CALIBRATE = False # whether to try to auto-calibrate or now
CALIBRATE_N_ITER = 5 # number of loops of auto-calibration
CALI_SLOPE = False # tries to make it so the mean slope of auto-calibration is 0, not working...

# configuration related to drawing plots
DrawResHists = False
DRAW_ANGLE_HISTS = False
DRAW_WIRE_RESIDUAL_PLOTS = False
DRAW_HIT_POSITION_PLOTS = False

class EventLoop(object):
    def __init__(self, ttree_filename, dat_filename, file_mode="RECREATE", tree_name="mwpc", nmax=None):
        """Make the event loop which opens the file, reads it, 
        reconstructs and saves a root files.
        ttree_filename 
        """
        # the ttree filename
        self.ttree_filename = ttree_filename
        # the file mode, usually recreate
        self.file_mode = file_mode
        # the ttree name, usually mwpc
        self.tree_name = tree_name
        # the filename where the data is saved
        self.dat_filename = dat_filename
        # This saves the information on the current event
        self.info = collections.defaultdict(int)
        # This saves the list-based information on the current event
        self.info_list = collections.defaultdict(list)
        # saves the time of the current event that is being processed
        self.ttime = datetime.datetime.min
        # basically tracks whether the event contained at least one hit
        self.found_channel = False
        # saves all the afterpulsing time plots, which is used to make a cut
        self.timeplots = dict()
        # keeps track of the number of reading errors found
        self.num_errors = 0
        # saves the maximum number of events to save. Like if you only want to saved the first 100.
        self.nmax = nmax
        
        # holds each event
        self.events = []
        # create all the events
        self.loop()
        #self.close()
        
    def loop(self):
        """Opens the dat file, loops through each line and saves the information
        """
        # resets the stats that keeps track
        eventclass.resetstats()   
        # set the event number to -1 as a start     
        self.info["global_event"] = -1
        # create the plots needed for afterpulsing cut
        self.maketimeplots()
        # open the dat file
        with open(self.dat_filename) as f:
            # loop through each line of the dat file
            for i, line in enumerate(f):
                # process the current line
                self.inner_loop(line)
            # finally process the final event, bc we only process events when
            # reaching the next event. But there's no event to process
            self.process_event() 
        # now get the time cut for afterpulsing, makes clusters/tracks
        # and create other plots
        self.afterread()
        # finally, save the events to the root file
        self.finalizeloop()
        logging.info("complete")
        # now it optionally prints statistics, like how many events have tracks
        if PRINTSTATS:
            eventclass.printstats()
        
        
    def afterread(self):
        """Makes the afterpulsing time cut, makes clusters, and tracks.
        Also makes and saves plots.
        """
        logging.info("Making hits")
        # Gets the afterpulsing time cut locations
        timecutinfo = self.gettimecutinfo() # dict of time cut by wc and direction
        # loop n numbers, where n is the number of calibration steps.
        for j in range(CALIBRATE_N_ITER if CALIBRATE or CALI_SLOPE else 1):
            # creates plots
            helper.createplots(DRAW_HIT_POSITION_PLOTS, DRAW_WIRE_RESIDUAL_PLOTS, DRAW_ANGLE_HISTS)
            # cuts down the number of events if needed
            if self.nmax is not None:
                del self.events[self.nmax:]
            # loops over each event in order to make clusters and tracks
            for i, event in enumerate(self.events):
                # prints progress
                if i % EVENT_PRINT_RATE == 0: logging.info("Hit #%s" % i)
                # makes hits while cutting out afterpulsing
                event.makehits(timecutinfo)
                # saves statistics
                eventclass.stats["afterread: process event"] += 1
            # saves the plots if needed
            helper.saveplots(DRAW_HIT_POSITION_PLOTS, DRAW_WIRE_RESIDUAL_PLOTS, DRAW_ANGLE_HISTS)
            # optionally calibrates
            self.calibrate(j)
            # prints the afterpulse cutoff times
            logging.info("Afterpulse cutoff times:")
            pprint.pprint(sorted(timecutinfo.items(), key=lambda x: x[0]))
                
    def calibrate(self, j):
        """Makes residual plots and optionally calibrate
        The calibration is based on the mean residual.
        The loop in 'afterread' loops CALIBRATE_N_ITER times in order to make
        tracks and clusters based on the current calibration
        """
        logging.info("Residuals coming up for iter %s:" % j)
        # loop over each module and direction
        for n, key in enumerate(itertools.product(range(1, 5), range(2))):
            # get the mean and rms for that residual plot
            mean, rms = helper.plots["residual"][key].GetMean(), helper.plots["residual"][key].GetRMS()
            # delete the residual plot
            helper.plots["residual"][key].Delete()
            # print out the mean residual values. Should be ~0.
            logging.info("(wc,d)=%s: mean=%s, rms=%s" % (key, mean, rms))
            # if calibrating then update the offsets
            if not CALIBRATE:
                continue
            hitoffsets[key] += mean
            
        # tries to calibrate the average slope to be zero
        if CALI_SLOPE:
            # gets the mean slope in x and y
            mx, my = self.get_mean_slopes()
            print "Means slopes:", mx, my
            # loops over each module and direction
            for n, key in enumerate(itertools.product(range(1, 5), range(2))):
                # gets the position in z (ie the beam direction)
                zpos, zerr = helper.getzpos(*key)
                # gets the slope associated with this direction
                m = mx if key[1] == 0 else my
                # calculates the mean offset based on the mean slope
                offset = zpos * m
                # applies that offset to the calibration
                hitoffsets[key] += offset
            
        # finally, print the current offsets after calibration
        pprint.pprint(calibration.hitoffsets)
        
    def get_mean_slopes(self):
        """ Gets the mean slope in each direction in order 
        to calbrate out the slope 
        """
        length = len(self.events)
        # if the length is zero, then return a default value
        if length == 0: return (0,0)
        x = lambda n: n.mx
        y = lambda n: n.my
        # mean is sum(m) / length
        return (self.getsum(x)/length, self.getsum(x)/length)
    
    def getsum(self, func):
        """A helper function for get_mean_slopes""" 
        it = map(func, itertools.ifilter(lambda x: x.has_clean_track, self.events))
        return math.fsum(it)
        
        
    def maketimeplots(self):
        """Makes the plots needed to calculate the afterpulse time cuts"""
        # loops over each module, direction, and tdc
        for key in itertools.product(range(1, 5), range(2), range(2)):
            # make a name for the hist
            name = "time%s%s%s" % key
            r = 500
            # make the hist
            t = ROOT.TH1D(name, name, 300, 0, r)
            # saves the hist for use
            self.timeplots[key] = t
            
    def gettimecutinfo(self):
        """Gets the afterpulse time cut in a dict of module, direction, tdc"""
        # returns a default value if we aren't using the cut
        if not USE_TIMECUT:
            x = lambda : (0, 1000)
            return collections.defaultdict(x)
            
        # allow us to use old methods
        method = 0
        if method == 0:
            # Method 0 summary:
            # Make a TSpectrum
            # Use the TSpectrum to find the first peak
            # Fit a gaussian to the first peak
            # The time cut is then gaussian mean + n sigma
        
            # use TSpectrum to get time range of first peak
            t = ROOT.TSpectrum()
            # make a canvas to draw
            c = ROOT.TCanvas("c", "c", 1500, 1600)
            # there are 4 modules, 2 directions, and 2 tdc's each, so 4x4
            c.Divide(4,4)
            
            # make sure it plots a title
            ROOT.gStyle.SetOptTitle(1)
            # make a gaussian function to plot
            fGaussian = ROOT.TF1("fGaussian","gaus",0,500);
            # set the gaussian's line color
            fGaussian.SetLineColor(2);
            # make the return dict
            out = dict()
            # loop over each module, direction and tdc
            for n, key in enumerate(itertools.product(range(1, 5), range(2), range(2))):
                # change the canvas
                c.cd(n+1)
                # set the plot's title
                self.timeplots[key].SetTitle("wc%s,d%s,tdc%s;time (ns); counts" % key)
                # draw the plots on the canvas
                self.timeplots[key].Draw()
                # find the peaks using the tspectrum
                t.Search(self.timeplots[key],2,"goff",0.25)
                #print t.GetNPeaks(), "peaks"
                # this marks the "early peak" which is the beam peak
                early_peak = float("inf")
                # loop over each peak and find the earliest one
                for i in range(t.GetNPeaks()):
                    #print t.GetPositionX()[i],
                    #print t.GetPositionY()[i]
                    
                    # check if this peak is earlier than
                    # the current earliest peak
                    early_peak = min(early_peak, t.GetPositionX()[i])
                # find the bin corresponding to the early peak
                maxbin = self.timeplots[key].FindBin( early_peak )
                # find the mean of the gaussian, just use bin center
                mean = self.timeplots[key].GetBinCenter(maxbin)
                # find the amplitude fo the gaussian
                ampl = self.timeplots[key].GetBinContent(maxbin)
                # set the gaussian's parameters, use a sigma of 4.5
                fGaussian.SetParameters(ampl,mean,4.5)
                # fit from 0 to earliest peak mean + 8 ns.
                # we don't want to include the afterpulsing peak in the fit
                fGaussian.SetRange(0,mean+8.0)
                # create the fit options
                opts = "R" if VERBOSETIMECUT else "0+QR"
                # do the actual fit
                self.timeplots[key].Fit(fGaussian,opts)
                # get the fit values
                mean = fGaussian.GetParameter(1);
                sigma = fGaussian.GetParameter(2);
                # print out the fit values
                print "mean, sigma:", mean, sigma
                # the time cut is mean + 1 sigma. 
                x = mean + TIMECUTNSIGMA * sigma 
                # set the cut value in
                out[key] = (0, x)
            # update the canvas because we can
            c.Update()
            
            # optionally we can average the time cuts between tdc 1 and 2
            if calibration.COMBINETIMECUTS:
                # make the dict to replace the current one
                new = dict()
                # loop over module and direction
                for a, b in itertools.product(range(1, 5), range(2)):
                    # make numbers for saving
                    newstart, newend = 0, 0
                    keys = []
                    # loop over tdc
                    for tdc in range(2):
                        # make a key of module, direction, tdc
                        key = (a, b, tdc)
                        # get the old start and end values
                        start, end = out[key]
                        # add current values to rolling average
                        newstart += start
                        newend += end
                        # save the key
                        keys.append(key)
                    # compute the average for start and end
                    newstart /= float(len(keys))
                    newend /= float(len(keys))
                    # loop over each key and save the average
                    for key in keys:
                        new[key] = (newstart, newend)
                # replace the dictionary
                out = new
                
            
            # optionally draw the time histogram
            if DRAW_TIMEHIST: 
                c.Print("plotHitTimesTSpec.png")
            # print the time cut values
            pprint.pprint(out)
            # and return
            return out
        # end if method == 0
            
            
        if method == 1:
            # Method 1 summary
            # Try fitting 2 guassians.
            # Earliest guassian is beam peak
            # Second guassian is afterpulsing peak
            # Warning: Don't use
            # Fitting 2 guassians is unstable so you might get nonsense values
            out = dict()
            if DRAW_TIMEHIST:
                logging.info("Drawing time hists")
                can = ROOT.TCanvas("c", "c", 1500, 800)
                can.Divide(4,2)
                #ROOT.gStyle.SetOptStat(000001111)
            for n, key in enumerate(itertools.product(range(1, 5), range(2))):
                if DRAW_TIMEHIST:
                    n += 1
                    can.cd(n)
                    self.timeplots[key].Draw()
                # general info
                # https://root.cern.ch/root/html/tutorials/fit/multifit.C.html
                # https://www.linkedin.com/groups/Is-there-standardized-formula-where-2041711.S.80694621
                # https://root.cern.ch/root/html/TF1.html
                # gaus is [0]*exp(-0.5*((x-[1])/[2])**2)
                
                # special case where the plots are effectively empty 
                # ie when the dat files are empty
                if self.timeplots[key].GetEntries() == 0:
                    x = lambda : (0, 1000)
                    return collections.defaultdict(x)
                
                # first fit a single gaussian
                fitopts = "SQ" if DRAW_TIMEHIST else "SQN" 
                r = self.timeplots[key].Fit("gaus", fitopts)
                # create double gaussian
                func = ROOT.TF1("func","gaus(0)+gaus(3)", 0, 200) #85,125)
                # create initial conditions for double gaussian
                par = array.array("d", [r.Value(0), r.Value(1)-r.Value(2), r.Value(2)/4.0, r.Value(0), r.Value(1)+r.Value(2), r.Value(2)/2.0])
                func.SetParameters(par)
                r = self.timeplots[key].Fit(func, fitopts)
                # a1, m1, sigma1 is 0,1,2
                # a2, m2, sigma2 is 3,4,5
                a1 = r.Value(0)
                m1 = r.Value(1)
                s1 = r.Value(2)
                a2 = r.Value(3)
                m2 = r.Value(4)
                s2 = r.Value(5)
                
                x = m1 + 8
                out[key] = (0, x)
            if DRAW_TIMEHIST:
                logging.info("Cutoff times:", sorted(out.items(), key=lambda x: x[0]))
                can.Update()
                can.Print("HitTimes.png")
                if not batch: raw_input()
            return out
        # end if method == 1
        
        # old code?
        """
        b = m2*s1 - m1*s2
        twoa = (s2**2 - s1**2) # == a * 2
        #c = 0.5*(s2**2)*(m1**2) - (s1**2)*(s2**2)*math.log(abs(a1/a2))-0.5*(s1**2)*(m2**2)
        c = s2**2*(0.5*m1**2 - s1**2*math.log(a1)) - s1**2*(0.5*m2**2-s2**2*math.log(a2))
        print "b, 2a, c =", b, twoa, c
        print "math.log(abs(a1/a2))", math.log(abs(a1/a2))
        print "0.5*(s2**2)*(m1**2)", 0.5*(s2**2)*(m1**2)
        print "0.5*(s1**2)*(m2**2)", 0.5*(s1**2)*(m2**2)
        x = -b / twoa + math.sqrt(b**2-2*twoa*c) / (twoa) if b**2-2*twoa*c >= 0 else 10000
        print x
        """
        
    def finalizeloop(self):
        """Saves a root file with the events"""
        self.open_()
        self.save_()
        self.close()
        
    def open_(self):
        """Opens the root file and makes a ttree"""
        logging.info("Opening %s in %s mode" % (self.ttree_filename, self.file_mode))
        self.tfile = ROOT.TFile(self.ttree_filename, self.file_mode)
        self.ttree = ROOT.TTree(self.tree_name,'Wire chamber tree')
        
    def close(self):
        """Closes the root file after writing the ttree"""
        logging.info("Writing file")
        self.write()
        logging.info("Closing file")
        self.tfile.Close()  
         
    def write(self):
        """Writes the ttree to the tfile"""
        logging.info("Writing")
        self.tfile.Write(self.tree_name, ROOT.TObject.kOverwrite)
        #self.tfile.Write(self.tree2_name, ROOT.TObject.kOverwrite)
                
    def inner_loop(self, line):
        """Processes a single line from the dat file
        For more info see,
        https://cdcvs.fnal.gov/redmine/projects/ftbfwirechamberdaq/wiki/Processed_hit_data_description
        """
        # try processing a line, might have exception if line is incomplete
        try:
            # This marks the new event
            if line.startswith("EVENT"):
                # process the previous event and reset for this event
                self.process_event()
                temp = line.split()
                self.info["global_event"] = int(temp[1])
                self.info["spill_event"] = int(temp[2])
            elif line.startswith("SPILL"):
                self.process_event()
                self.info["spill"] = int(line.split()[1])
            elif line.startswith("TTIME"):
                temp = line.split(None,1)[1].strip()
                try:
                    self.ttime = datetime.datetime.strptime(temp, "%d/%m/%y %H:%M:%S") 
                    # if before or after daylight savings time... TODO currently not taking into account time diff so events in 6 hr area might be wrong
                    hours_delta = 6 if self.ttime < datetime.datetime(2015, 3, 8, 2) else 5
                    self.ttime += datetime.timedelta(hours=hours_delta)
                except ValueError as e:
                    # the earliest files (ie my muon file) had a
                    # time bug, so pick a default time
                    # based on the creation time
                    self.ttime = datetime.datetime.utcfromtimestamp(os.path.getctime(self.dat_filename))
            elif line.startswith("Module"):
                self.info["module"] = int(line.split()[1])
            elif line.startswith("Channel"):
                self.found_channel = True
                temp = line.split()
                self.info["channel"] = int(temp[1])
                self.info["channel_time"] = int(temp[2]) # Time Bits 1.18 ns steps
                # store hit count info
                info = (self.info["module"], self.info["channel"], self.info["channel_time"])
                self.info_list["module_info"].append(info)
            elif line.startswith("ETIME"):
                temp = line.split()
                self.info["etime1"] = int(temp[1])
                self.info["etime2"] = int(temp[2])
        except Exception as e:
            # Print info on the exception
            logging.debug("'%s' had an %s exception while processing. It's probably nothing", line, e)
            logging.debug(traceback.format_exc())
            # keep track of the number of exceptions
            self.num_errors += 1
            if self.num_errors > MAX_ERRORS:
                logging.error("Reached max number of errors")
                raise
            else: pass # say a line was incomplete at the end
            
            
            
    def process_event(self):
        """Processes the info on the current event into an Event object
        and adds it to the list.
        """
        # skip the first write when everything is still -999
        # also skip events that happen after the spill line but before processing the next
        if  self.info["global_event"] < 0: return
        event = eventclass.Event()
        # finalize event
        if self.info["global_event"]%EVENT_PRINT_RATE==0:
            logging.info("Event: %s" % self.info["global_event"])
        
        index = 0
        event.number_of_hits = len(self.info_list["module_info"])
        # write channels
        for m, ch, h in self.info_list["module_info"]:
            event.module.append(m)
            event.channel.append(ch)
            event.hit_time.append(h)
            # calculate the wire chamber number
            wire_chamber = (m - 1) / 4 + 1
            event.wire_chamber.append(wire_chamber)
            # calculate the wire
            wire = 64 + ch if m % 2 == 0 else ch 
            event.wire.append(wire)
            # calculate whether it's an x or y plane, 0 means x, 1 means y
            direction = 0 if ((m - 1) / 2) % 2 == 0 else 1
            zpos, zerr = helper.getzpos(wire_chamber, direction)
            event.zpos.append(zpos)
            # fill the time plot for the TSpectrum
            tdc = helper.gettdc(wire)
            key = (wire_chamber, direction, tdc)
            self.timeplots[key].Fill(h)
            event.direction.append(direction)
            # finally up the index
            index += 1
                                    
        # write event info
        # SPILL      <spill number>
        event.spill_num = self.info["spill"]
        # EVENT      <total triggers in run>  <triggers in this spill>
        event.global_event_num = self.info["global_event"]
        event.spill_event_num = self.info["spill_event"]
            
        # write time info
        # from: TTIME      <dd/mm/yy hh:mm:ss>
        event.ttime = self.ttime
        event.etime1 = self.info["etime1"]
        event.etime2 = self.info["etime2"]
        # from: ETIME      <controller time stamp>  <TDC event time stamp>
        self.events.append(event)
        if self.info["global_event"]%EVENT_PRINT_RATE==0 and False:
            logging.debug(event)
        
        # reset
        del self.info_list["module_info"][:]
        self.info["global_event"] = -999
        
    def save_(self):
        """Save all the events into a ttree
        """
        logging.info("Saving %s events" % len(self.events))
        # make all the branches
        length = 2048
        
        # branches which depend on number of hits in the wires
        numhits = array.array("i",[0])
        bnumhits = self.ttree.Branch("mwpc_number_of_hits", numhits, "mwpc_number_of_hits/I")
        module = array.array("i",[0]*length)
        bmodule = self.ttree.Branch("mwpc_module", module, "mwpc_module[mwpc_number_of_hits]/I")
        channel = array.array("i",[0]*length)
        bchannel = self.ttree.Branch("mwpc_channel", channel, "mwpc_channel[mwpc_number_of_hits]/I")
        hit_time = array.array("i",[0]*length)
        bhit_time = self.ttree.Branch("mwpc_hit_time", hit_time, "mwpc_hit_time[mwpc_number_of_hits]/I")
        wire_chamber = array.array("i",[0]*length)
        bwire_chamber = self.ttree.Branch("mwpc_wire_chamber", wire_chamber, "mwpc_wire_chamber[mwpc_number_of_hits]/I")
        zpos = array.array("d",[0]*length)
        bzpos = self.ttree.Branch("mwpc_zpos", zpos, "mwpc_zpos[mwpc_number_of_hits]/D")
        wire = array.array("i",[0]*length)
        bwire = self.ttree.Branch("mwpc_wire", wire, "mwpc_wire[mwpc_number_of_hits]/I")
        direction = array.array("i",[0]*length)
        bdirection = self.ttree.Branch("mwpc_direction", direction, "mwpc_direction[mwpc_number_of_hits]/I")
        
        # clusters 
        mwpc_number_of_clusters = array.array("i",[0])
        bmwpc_number_of_clusters = self.ttree.Branch("mwpc_number_of_clusters", mwpc_number_of_clusters, "mwpc_number_of_clusters/I")
        mwpc_cluster_wc = array.array("i",[0]*length)
        bmwpc_cluster_wc = self.ttree.Branch("mwpc_cluster_wc", mwpc_cluster_wc, "mwpc_cluster_wc[mwpc_number_of_clusters]/I")
        mwpc_cluster_direction = array.array("i",[0]*length)
        bmwpc_cluster_direction = self.ttree.Branch("mwpc_cluster_direction", mwpc_cluster_direction, "mwpc_cluster_direction[mwpc_number_of_clusters]/I")
        mwpc_cluster_position = array.array("d",[0]*length)
        bmwpc_cluster_position = self.ttree.Branch("mwpc_cluster_position", mwpc_cluster_position, "mwpc_cluster_position[mwpc_number_of_clusters]/D")
        mwpc_cluster_position_err = array.array("d",[0]*length)
        bmwpc_cluster_position_err = self.ttree.Branch("mwpc_cluster_position_err", mwpc_cluster_position_err, "mwpc_cluster_position_err[mwpc_number_of_clusters]/D")
        mwpc_cluster_zpos = array.array("d",[0]*length)
        bmwpc_cluster_zpos = self.ttree.Branch("mwpc_cluster_zpos", mwpc_cluster_zpos, "mwpc_cluster_zpos[mwpc_number_of_clusters]/D")
        mwpc_cluster_zpos_err = array.array("d",[0]*length)
        bmwpc_cluster_zpos_err = self.ttree.Branch("mwpc_cluster_zpos_err", mwpc_cluster_zpos_err, "mwpc_cluster_zpos_err[mwpc_number_of_clusters]/D")
        mwpc_cluster_res = array.array("d",[0]*length)
        bmwpc_cluster_res = self.ttree.Branch("mwpc_cluster_res", mwpc_cluster_res, "mwpc_cluster_res[mwpc_number_of_clusters]/D")
        mwpc_cluster_respererr = array.array("d",[0]*length)
        bmwpc_cluster_respererr = self.ttree.Branch("mwpc_cluster_respererr", mwpc_cluster_respererr, "mwpc_cluster_respererr[mwpc_number_of_clusters]/D")
        # store hit time
        mwpc_cluster_time = array.array("d",[0]*length)
        bmwpc_cluster_time = self.ttree.Branch("mwpc_cluster_time", mwpc_cluster_time, "mwpc_cluster_time[mwpc_number_of_clusters]/D")
        # store the number of wires
        mwpc_cluster_nwire = array.array("i",[0]*length)
        bmwpc_cluster_nwire = self.ttree.Branch("mwpc_cluster_nwire", mwpc_cluster_nwire, "mwpc_cluster_nwire[mwpc_number_of_clusters]/I")
        mwpc_cluster_tracknum = array.array("i",[0]*length)
        bmwpc_cluster_tracknum = self.ttree.Branch("mwpc_cluster_tracknum", mwpc_cluster_tracknum, "mwpc_cluster_tracknum[mwpc_number_of_clusters]/I")
        mwpc_cluster_islate = array.array("i",[0]*length)
        bmwpc_cluster_islate = self.ttree.Branch("mwpc_cluster_islate", mwpc_cluster_islate, "mwpc_cluster_islate[mwpc_number_of_clusters]/I")
        
        
        # n clusters
        mwpc_bymodule_nclusters_x = array.array("d",[0]*4)
        bmwpc_bymodule_nclusters_x = self.ttree.Branch("mwpc_bymodule_nclusters_x", mwpc_bymodule_nclusters_x, "mwpc_bymodule_nclusters_x[4]/D")
        mwpc_bymodule_nclusters_y = array.array("d",[0]*4)
        bmwpc_bymodule_nclusters_y = self.ttree.Branch("mwpc_bymodule_nclusters_y", mwpc_bymodule_nclusters_y, "mwpc_bymodule_nclusters_y[4]/D")
        # n late clusters
        mwpc_bymodule_nlateclusters_x = array.array("d",[0]*4)
        bmwpc_bymodule_nlateclusters_x = self.ttree.Branch("mwpc_bymodule_nlateclusters_x", mwpc_bymodule_nlateclusters_x, "mwpc_bymodule_nlateclusters_x[4]/D")
        mwpc_bymodule_nlateclusters_y = array.array("d",[0]*4)
        bmwpc_bymodule_nlateclusters_y = self.ttree.Branch("mwpc_bymodule_nlateclusters_y", mwpc_bymodule_nlateclusters_y, "mwpc_bymodule_nlateclusters_y[4]/D")
        
        # tracks
        mwpc_track_isclean = array.array("i", [0])
        bmwpc_track_isclean = self.ttree.Branch("mwpc_track_isclean", mwpc_track_isclean, "mwpc_track_isclean/I")
        mwpc_track_ntracks = array.array("i", [0])
        bmwpc_track_ntracks = self.ttree.Branch("mwpc_track_ntracks", mwpc_track_ntracks, "mwpc_track_ntracks/I")
        mwpc_track_ntracks_x = array.array("i", [0])
        bmwpc_track_ntracks_x = self.ttree.Branch("mwpc_track_ntracks_x", mwpc_track_ntracks_x, "mwpc_track_ntracks_x/I")
        mwpc_track_ntracks_y = array.array("i", [0])
        bmwpc_track_ntracks_y = self.ttree.Branch("mwpc_track_ntracks_y", mwpc_track_ntracks_y, "mwpc_track_ntracks_y/I")
        # info
        mwpc_track_b = array.array("d", [0]*length)
        bmwpc_track_b = self.ttree.Branch("mwpc_track_b", mwpc_track_b, "mwpc_track_b[mwpc_track_ntracks]/D")
        mwpc_track_berr = array.array("d", [0]*length)
        bmwpc_track_berr = self.ttree.Branch("mwpc_track_berr", mwpc_track_berr, "mwpc_track_berr[mwpc_track_ntracks]/D")
        mwpc_track_m = array.array("d", [0]*length)
        bmwpc_track_m = self.ttree.Branch("mwpc_track_m", mwpc_track_m, "mwpc_track_m[mwpc_track_ntracks]/D")
        mwpc_track_merr = array.array("d", [0]*length)
        bmwpc_track_merr = self.ttree.Branch("mwpc_track_merr", mwpc_track_merr, "mwpc_track_mxerr[mwpc_track_ntracks]/D")
        mwpc_track_nclusters = array.array("i", [0]*length)
        bmwpc_track_nclusters = self.ttree.Branch("mwpc_track_nclusters", mwpc_track_nclusters, "mwpc_track_nclusters[mwpc_track_ntracks]/I")
        mwpc_track_direction = array.array("i", [0]*length)
        bmwpc_track_direction = self.ttree.Branch("mwpc_track_direction", mwpc_track_direction, "mwpc_track_direction[mwpc_track_ntracks]/I")
        mwpc_track_islate = array.array("i", [0]*length)
        bmwpc_track_islate = self.ttree.Branch("mwpc_track_islate", mwpc_track_islate, "mwpc_track_islate[mwpc_track_ntracks]/I")
        mwpc_track_missingmodule = array.array("i", [0]*length)
        bmwpc_track_missingmodule = self.ttree.Branch("mwpc_track_missingmodule", mwpc_track_missingmodule, "mwpc_track_missingmodule[mwpc_track_ntracks]/I")
        mwpc_track_chi2 = array.array("d", [0]*length)
        bmwpc_track_chi2 = self.ttree.Branch("mwpc_track_chi2", mwpc_track_chi2, "mwpc_track_chi2[mwpc_track_ntracks]/D")
        
        num_posi = len(calibration.instrument_positions)
        # x proj positions
        proj_xa = array.array("d", [-999]*num_posi)
        bproj_xa = self.ttree.Branch("mwpc_track_proj_x", proj_xa, "mwpc_track_proj_x[%s]/D" % num_posi)
        proj_xerra = array.array("d", [-999]*num_posi)
        bproj_xerra = self.ttree.Branch("mwpc_track_proj_xerr", proj_xerra, "mwpc_track_proj_xerr[%s]/D" % num_posi)
        # y proj positions
        proj_ya = array.array("d", [-999]*num_posi)
        bproj_ya = self.ttree.Branch("mwpc_track_proj_y", proj_ya, "mwpc_track_proj_y[%s]/D" % num_posi)
        proj_yerra = array.array("d", [-999]*num_posi)
        bproj_yerra = self.ttree.Branch("mwpc_track_proj_yerr", proj_yerra, "mwpc_track_proj_yerr[%s]/D" % num_posi)
        # z proj positions
        proj_za = array.array("d", [-999]*num_posi)
        bproj_za = self.ttree.Branch("mwpc_track_proj_z", proj_za, "mwpc_track_proj_z[%s]/D" % num_posi)
        proj_zerra = array.array("d", [-999]*num_posi)
        bproj_zerra = self.ttree.Branch("mwpc_track_proj_zerr", proj_zerra, "mwpc_track_proj_zerr[%s]/D" % num_posi)
        
        # event-based branches
        global_event = array.array("i",[0])
        bglobal_event = self.ttree.Branch("mwpc_global_event_num", global_event, "mwpc_global_event_num/I")
        spill_event = array.array("i",[0])
        bspill_event = self.ttree.Branch("mwpc_spill_event_num", spill_event, "mwpc_spill_event_num/I")
        spill_num = array.array("i",[0])
        bspill_num = self.ttree.Branch("mwpc_spill_num", spill_num, "mwpc_spill_num/I")
        
        # time
        event_time = array.array("d",[0])
        bevent_time = self.ttree.Branch("mwpc_event_time", event_time, "mwpc_event_time/D") 
        time_after_spill = array.array("d",[0])
        btime_after_spill = self.ttree.Branch("mwpc_time_after_spill", time_after_spill, "mwpc_time_after_spill/D")
        
        # loop over events
        for event in self.events:
            # fill wire based stuff
            numhits[0] = event.number_of_hits
            for i in range(event.number_of_hits):
                module[i] = event.module[i]
                channel[i] = event.channel[i]
                hit_time[i] = event.hit_time[i]
                wire_chamber[i] = event.wire_chamber[i]
                zpos[i] = event.zpos[i]
                wire[i] = event.wire[i]
                direction[i] = event.direction[i]
                
            # fill event-based numbers
            global_event[0] = event.global_event_num
            spill_event[0] = event.spill_event_num
            spill_num[0] = event.spill_num
            
            epoch = datetime.datetime.utcfromtimestamp(0)
            td = event.ttime - epoch
            # The TDC time stamp is the number of 9.4 ns clock ticks since 
            # begin spill. Assuming a five second spill, this word has at most 
            # 29 significant bits but is cast as a 32 bit quantity. The 
            # Controller time stamp is the lower order 12 bits of the number 
            # of 1.18ns ticks that have elapsed between begin spill until the 
            # receipt of this trigger. Bits 8..0 of the TDC time stamp are 
            # compared to bits 11..3 of the controller time stamp as a check 
            # of synchronization between the TDC and controller counters. The 
            # concatenation of the 32 bit TDC time stamp with the lower order 
            # three bits of the controller time stamp forms a 35 bit word which 
            # represents the time of arrival of the trigger with respect to 
            # spill begin in 1.18ns steps. The 10 bit TDC time word is a 
            # measure of the time elapsed from the trigger time stamp to the
            # hit arrival in 1.18ns steps. 
            # etime 1 = word 7 = Event Time Stamp sent by the controller
            # etime 2 = word 8/9 = TDC Event Time Stamp Upper Bits (31..16), TDC Event Time Stamp Lower Bits (15..0)
            # (2**3 * etime2 + etime1) * 1.18 * 10**-9 = event time after trigger in seconds
            extratime = ((2**3 * (event.etime2 % 2**32)) + event.etime1 % (2**3-1)) * MWPC_TDC_TIME_CONST * 10**-9
            #print bin(event.etime2), bin(event.etime1), bin(2**3 * event.etime2), bin(int(event.etime1 & (2**3-1))), bin(int(extratime)), extratime
            #print event.etime2*8, event.etime1 % (2**3-1), extratime
            event_time[0] = (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / (10**6) + extratime
            time_after_spill[0] = extratime
            
            '''try: #TODO temp
                assert lasttime > event_time[0]
            except AssertionError:
                print lasttime, event_time[0]
                raise
            lasttime = event_time[0]'''
            
            
            
            
            # store the cluster info
            for key in itertools.product(range(1,5), range(2)):
                wc = key[0]
                try:
                    if key[1] == 1: mwpc_bymodule_nclusters_y[wc-1] = len(event.clusters[key])
                    else: mwpc_bymodule_nclusters_x[wc-1] = len(event.clusters[key])
                except KeyError: pass
                try:
                    if key[1] == 1: mwpc_bymodule_nlateclusters_y[wc-1] = len(event.clusters_during_tdc_timecut[key])
                    else: mwpc_bymodule_nlateclusters_x[wc-1] = len(event.clusters_during_tdc_timecut[key])
                except KeyError: pass
            # store the clusters
            clusters = list(itertools.chain(itertools.chain(*event.clusters.values()), itertools.chain(*event.clusters_during_tdc_timecut.values())))
            mwpc_number_of_clusters[0] = len(clusters)
            for i, cluster in enumerate(clusters):
                pos, poserr = cluster.get_hit_pos_info()
                nwires = cluster.get_nwires()
                res, respererr = cluster.point.res, cluster.point.respererr
                time = cluster.get_hit_time()
                wc, d = cluster.key
                # fill branches
                mwpc_cluster_wc[i] = wc
                mwpc_cluster_direction[i] = d
                mwpc_cluster_position[i] = pos
                mwpc_cluster_position_err[i] = poserr
                mwpc_cluster_zpos[i] = cluster.point.x # x for track finding is the same as z pos
                mwpc_cluster_zpos_err[i] = cluster.point.dx
                mwpc_cluster_time[i] = time
                mwpc_cluster_nwire[i] = nwires
                mwpc_cluster_tracknum[i] = cluster.point.tracknum
                mwpc_cluster_islate[i] = 1 if cluster.islate else 0
                
                mwpc_cluster_res[i] = cluster.point.res
                mwpc_cluster_respererr[i] = cluster.point.respererr
                assert cluster.point.tracknum >= -1
                assert nwires >= 0 and nwires <= 128
                    
            # save track info
            mwpc_track_isclean[0] = 1 if event.has_clean_track else 0
            mwpc_track_ntracks[0] = len(event.tracks) + len(event.latetracks)
            ntracks_x = 0
            ntracks_y = 0
            for i, track in enumerate(itertools.chain(event.tracks, event.latetracks)):
                mwpc_track_b[i] = track.b
                mwpc_track_berr[i] = track.db
                mwpc_track_m[i] = track.m
                mwpc_track_merr[i] = track.dm
                mwpc_track_nclusters[i] = track.n
                mwpc_track_direction[i] = track.direction
                mwpc_track_islate[i] = 0 if i < len(event.tracks) else 1
                mwpc_track_missingmodule[i] = track.missingmodule if track.missingmodule is not None else -1
                mwpc_track_chi2[i] = track.chi2
                if i < len(event.tracks): # not late track
                    if track.direction == 0:
                        ntracks_x += 1
                    else: ntracks_y += 1
            mwpc_track_ntracks_x[0] = ntracks_x
            mwpc_track_ntracks_y[0] = ntracks_y
            if event.has_clean_track:
                # get projected track position for various points in beamline
                bx_, bxerr_, mx_, mxerr_ = event.trackx.b, event.trackx.db, event.trackx.m, event.trackx.dm
                by_, byerr_, my_, myerr_ = event.tracky.b, event.tracky.db, event.tracky.m, event.tracky.dm
                for i, zinfo in enumerate(calibration.instrument_positions):
                    z, zerr = zinfo
                    # get the projections
                    x, xerr = helper.project_track(bx_, bxerr_, mx_, mxerr_, z, zerr)
                    y, yerr = helper.project_track(by_, byerr_, my_, myerr_, z, zerr)
                    # save the values
                    proj_xa[i] = x
                    proj_xerra[i] = xerr
                    proj_ya[i] = y
                    proj_yerra[i] = yerr
                    proj_za[i] = z
                    proj_zerra[i] = zerr
            else:
                for i, zinfo in enumerate(calibration.instrument_positions):
                    # reset the values
                    proj_xa[i] = -999
                    proj_xerra[i] = -999
                    proj_ya[i] = -999
                    proj_yerra[i] = -999
                    proj_za[i] = -999
                    proj_zerra[i] = -999
                
            
                
            
            # finally fill the event
            self.ttree.Fill()
        logging.info("Done saving %s events" % len(self.events))
