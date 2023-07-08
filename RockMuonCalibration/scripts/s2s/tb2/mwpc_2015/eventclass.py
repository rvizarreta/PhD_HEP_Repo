
import hitclass
import clusterclass
import helper
import calibration
import trackfinding

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

INSERTFAKEHITSFORTESTING = False # TODO find better home
idkindex = 0
  
def function_to_use_for_additional(x):
    if x.in_cluster: return False
    if x.afterpulse: return False
    if not x.afterdeadtime: return False
    return True
    
def function_to_use_for_primary_clusters(x):
    if x.in_cluster: return False
    if x.afterpulse: return False
    if x.timecut: return False
    return True
    
    
stats = collections.defaultdict(int)

def printstats():
    print "Stats:"
    pprint.pprint(sorted(stats.items()))
    
def resetstats():
    stats.clear()

class Event(object):
    def insertExtraHits(self, hitsbysystem):
        import random
        N = 1
        prob = 1
        hit_range = (0, 128) #(32, 32*3)
        hit_time_range = (150, 200)
        for key, hitslist in hitsbysystem.items():
            if key[1] == 1: continue # skip y direction since we fill both
            wc, d = key
            d2 = (d + 1) % 2
            hitslist2 = hitsbysystem[(wc, d2)]
            
            for i in range(N):
                if random.random() > prob: continue
                hit_time = random.randint(*hit_time_range)
                # wc d1
                hit_pos = random.randint(*hit_range)
                h = hitclass.Hit(hit_pos, hit_time, wc, d)
                hitslist.append(h)
                h = hitclass.Hit(hit_pos, hit_time + 50, wc, d)
                hitslist.append(h)
                # wc d2
                hit_pos2 = random.randint(*hit_range)
                h = hitclass.Hit(hit_pos2, hit_time, wc, d2)
                hitslist2.append(h)
                h = hitclass.Hit(hit_pos2+5, hit_time + 50, wc, d2)
                hitslist2.append(h)
        
        
    def makehits(self, timecutinfo):
        hitsbysystem = collections.defaultdict(list)
        for i, hit_pos in enumerate(self.wire):
            # make a hit object
            hit_time = self.hit_time[i]
            wc, d = self.wire_chamber[i], self.direction[i]
            h = hitclass.Hit(hit_pos, hit_time, wc, d)
            
            # create dict keys for plotting and getting the time cut
            key = (wc, d)
            # we add every hit but we filter based on the is_cut function
            hitsbysystem[key].append(h)
            stats["makehits: time cut, keep hit"] += 1
            
            
        if INSERTFAKEHITSFORTESTING:
            self.insertExtraHits(hitsbysystem)
        
        # apply a time cut
        for key, hitslist in hitsbysystem.items():
            wc, d = key
            tdc = h.tdc
            tkey = (wc, d, tdc)
            
            # get time cut info
            mintime, maxtime = timecutinfo[tkey]
            for h in hitslist:
                hit_pos = h.pos
                hit_time = h.time
                # plot hit positions for different time cuts in 1d
                helper.drawhitpos(hit_time, key, hit_pos)
                # check if this hit is cut by wires
                if  hit_time > maxtime or hit_time < mintime:
                    # this is afterpulse according to the timecutinfo
                    stats["makehits: time cut, throw away afterpulse (tdc time cut)"] += 1
                    h.timecut = True
                    if hit_time >= maxtime + calibration.DEADTIME:
                        h.afterdeadtime = True
            
            
        
        
        global idkindex
        #idkindex = 0
        for key, hits_list in hitsbysystem.items():
            # loop while there are still hits that aren't cut
            # they are cut if they are afterpulsing, timecut or part of a cluster already
            clusters = []
            while len(list(itertools.ifilter(function_to_use_for_primary_clusters, hits_list))) > 0:
                c = self.construct_clusters(hits_list)
                clusters.append(c)
            # finally save the clusters
            self.clusters[key] = clusters
            
            
            additional_clusters = []
            while len(list(itertools.ifilter(function_to_use_for_additional, hits_list))) > 0:
                #l = list(itertools.imap(is_not_cutv2, hits_list))
                #length = l.count(True)
                #print key
                #print length, len(hits_list)
                #print clusters
                #print list(zip(l, hits_list))
                #if length > 0:
                #    stats["additional_clusters: more than one hit"] += 1
                c = self.construct_clusters(hits_list, False)
                add = True
                # TODO cleanup code
                for cluster in clusters:
                    dist = abs(c.get_local_hit_pos() - cluster.get_local_hit_pos())
                    if dist < calibration.AFTERPULSE_RANGE:
                        add = False
                        break # don't add this cluster since it's afterpulsing
                if add:
                    stats["additional_clusters: add"] += 1
                    additional_clusters.append(c)
                else:
                    stats["additional_clusters: don't add"] += 1
                #print additional_clusters
            #if idkindex > 20: exit()
            idkindex += 1
            # finally save the clusters
            stats[("additional_clusters", len(additional_clusters))] += 1
            self.clusters_during_tdc_timecut[key] = additional_clusters
        
            
           
        if calibration.angleoffsets is not None:
            for key, clusters in self.clusters.items():
                opp = (key[0], (key[1]+1)%2)
                opphitpos = None
                opphiterr = None
                if len(clusters) == 1:
                    stats["Angle offset: clusters: one"] += 1
                    try:
                        oppclusters = self.clusters[opp]
                        if len(oppclusters) == 1:
                            opphit = oppclusters[0]
                            stats["Angle offset: opp clusters: one"] += 1
                            opphitpos, opphiterr = opphit.get_hit_pos_info(False)
                        else: 
                            if len(oppclusters) == 0:
                                stats["Angle offset: opp clusters: None"] += 1
                            else: stats["Angle offset: opp clusters: too many"] += 1
                            
                    except KeyError:
                        stats["Angle offset: opp clusters: No opp key"] += 1
                        pass
                else: 
                    if len(clusters) == 0:
                        stats["Angle offset: clusters: None"] += 1
                    else: stats["Angle offset: clusters: too many"] += 1
                if opphitpos is None: stats["Angle offset: hit pos None"] += 1
                else: stats["Angle offset: hit pos exists"] += 1
                # note: it will only have a non-None hit pos if both 
                # x and y have only a single cluster
                for c in clusters:
                    c.apply_angle_offsets(key[0], key[1], opphitpos, opphiterr)
                
        helper.drawstuff(self)
        self.maketracks()
            
    def getpairs(self, x, y):
        key = lambda h: h.get_hit_time()
        lx = sorted(x, key=key)
        ly = sorted(y, key=key)
        out = []
        
        if len(lx) == 0: stats["getpairs: No x hits"] += 1
        if len(ly) == 0: stats["getpairs: No y hits"] += 1
        if len(lx) > 1: stats["getpairs: More than 1 x hit"] += 1
        if len(ly) > 1: stats["getpairs: More than 1 y hit"] += 1
        if len(ly) == len(lx): stats["getpairs: x and y have different lengths"] += 1
        else: stats["getpairs: x and y have same lengths"] += 1
        #return list(itertools.product(lx, ly))
        for i, a in enumerate(lx):
            if i >= len(ly):
                break
            out.append((a,ly[i]))
        return out
            
    def construct_clusters(self, hits_list, exclude_tdc_timecut_hits=True):
        if exclude_tdc_timecut_hits:
            keep_hit = function_to_use_for_primary_clusters
        else: 
            keep_hit = function_to_use_for_additional
        hits_list = list(itertools.ifilter(keep_hit, hits_list))
        # sort by time
        hits_list.sort(key=lambda x: x.time) 
        
        # get earliest hit
        earliest_hit = hits_list[0]
        key = (earliest_hit.wc, earliest_hit.d)
        primary_cluster = clusterclass.Cluster(earliest_hit.pos, earliest_hit.time, key)
        earliest_hit.in_cluster = True
        hits = [primary_cluster]
        
        # isolate the rest of the hits
        other_hits = hits_list[1:]
        # sort other hits based on dist from primary hit
        primary_cluster_pos = primary_cluster.get_local_hit_pos()
        other_hits.sort(key=lambda x: abs(x.pos - primary_cluster_pos))
        # 'extra hits' are hits that aren't part of primary hit
        for o in other_hits:
            # add any wires that are part of hit
            if primary_cluster.is_part_of_cluster(o):
                stats["makehits: extra hits, add to hit"] += 1
                primary_cluster.add(o.pos, o.time)
                o.in_cluster = True
            else: 
                stats["makehits: extra hits, add to extra hits"] += 1
            
        # find if extra hits are afterpulsing
        #cut_exclude_timecut = lambda x: x.is_cut_exclude_timecut()
        extra_hits = list(itertools.ifilter(lambda x: not x.in_cluster, hits_list))
        for e in extra_hits:
            if primary_cluster.is_hit_afterpulsing(e.pos, e.time):
                # Mark hit as afterpulsing
                e.afterpulse = True
                stats["makehits: afterpulse search, found afterpulsing"] += 1
            else: 
                # hit is second hit
                #self.has_clean_track = False
                stats["makehits: afterpulse search, a second hit"] += 1
                stats[("makehits: afterpulse search, a second hit in", key)] += 1
                #if DrawHitPosPlots:
                #    dist = abs(e.pos - primary_cluster.get_local_hit_pos())
                #    plots["secondhitdist"][key].Fill(dist)
        return primary_cluster
            
    def __init__(self):
        self.number_of_hits = 0
        self.module = []
        self.channel = []
        self.hit_time = []
        self.wire_chamber = []
        self.zpos = []
        self.wire = []
        self.direction = []
        self.spill_num = -999
        self.global_event_num = -999
        self.spill_event_num = -999
        self.ttime = datetime.datetime.min
        self.etime1 = 0
        self.etime2 = 0
        self.clusters = dict()
        self.clusters_during_tdc_timecut = dict()
        self.resx = [-999]*4
        self.resy = [-999]*4
        self.has_clean_track = True
        self.tracks = []
        self.latetracks = []
        self.trackx = None
        self.tracky = None
        
    def __str__(self):
        out = ["Event:"]
        for a in dir(self):
            try:
                out.append("%s: %s" % (a, self.__dict__[a]))
                out[-1] = out[-1][0:min(len(out[-1]), 20)]
            except: pass
        return ", ".join(out)
                
    def maketracks(self):
        self.tracks = trackfinding.maketracksfromclusters(self.clusters)
        # check if there is exactly 1 track in x and y
        self.has_clean_track = True if len(self.tracks) == 2 and self.tracks[0].direction != self.tracks[1].direction else False
        if self.has_clean_track:
            for track in self.tracks:
                if track.direction == 0:
                    self.trackx = track
                else:
                    self.tracky = track
        self.latetracks = trackfinding.maketracksfromclusters(self.clusters_during_tdc_timecut)
        self.has_clean_track = self.has_clean_track and len(self.latetracks) == 0
        # TODO add 2 cluster track info. Also change cluster track number to -2
        
