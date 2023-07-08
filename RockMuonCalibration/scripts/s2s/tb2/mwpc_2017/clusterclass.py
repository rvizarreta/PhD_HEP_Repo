
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

class Cluster(object):
    def __init__(self, hit_pos, hit_time, key):
        self.wires = [hit_pos]
        self.hit_times = [hit_time]
        self.key = key # == (wire chamber number, direction)
        self.angle_offset = 0
        self.angle_offset_err = 0
        self.calc_hit_params()
        self.point = None
        self.islate = False
        
    def calc_hit_params(self):
        self.hit_pos = sum(self.wires) / float(len(self.wires))
        self.hit_pos += self.getoffset()
        self.hit_time = min(self.hit_times)
        
    def getoffset(self):
        if calibration.USEOFFSETS:
            out = calibration.getoffset(self.key)
            return out
        else: return 0
        
    def get_wire_range(self, offset = 0):
        return min(self.wires) - offset, max(self.wires) + offset
        
    def __repr__(self):
        return "Cluster(%s, %s)" % (self.hit_pos, self.hit_time)
        
    def get_hit_pos(self, useangle=True):
        # should return as wire number
        if useangle:
            return self.hit_pos + self.angle_offset
        else:
            return self.hit_pos
            
    def get_local_hit_pos(self):
        return sum(self.wires) / float(len(self.wires))
        
    def is_part_of_cluster(self, hit):
        wire_pos = hit.pos
        time = hit.time
        if time - self.hit_time > calibration.TIMEERROR: return False
        min_wire, max_wire = self.get_wire_range(calibration.CONNECTED_HIT_RANGE)
        if not min_wire <= wire_pos <= max_wire: return False
        return True
        
    def get_hit_time(self):
        return self.hit_time
        
    def add(self, wire_pos, time):
        min_, max_ = self.get_wire_range(1.2)
        if not min_ <= wire_pos <= max_:
            print wire_pos, "not in range (%s, %s)" % (min_, max_)
            assert False
        self.wires.append(wire_pos)
        self.hit_times.append(time)
        self.calc_hit_params()
        
    def is_hit_afterpulsing(self, wire_pos, hit_pos):
        min_wire, max_wire = self.get_wire_range(calibration.AFTERPULSE_RANGE)
        if not (min_wire <= wire_pos <= max_wire): return False
        return True
        
    def get_hit_err(self, useangle=True):
        if len(self.wires) == 0: raise Exception("No wire info!")
        # gets std dev
        err2 = 1 / 12.0 # error is dist/sqrt(12), so error**2 = 1mm**2/12
        angleoffseterr = self.angle_offset_err if (calibration.USEOFFSETS and useangle) else 0
        return math.sqrt(err2 + sum([(h - self.hit_pos)**2 for h in self.wires]) / len(self.wires) + angleoffseterr**2)
        
    def get_hit_pos_info(self, useangle=True):
        return self.get_hit_pos(useangle), self.get_hit_err(useangle)
            
        
    def get_nwires(self):
        return len(self.wires)
        
    def apply_angle_offsets(self, wcnum, direction, opp_pos, opp_err):
        key = (wcnum, direction)
        b, berr, m, merr, no_angle_info_err = calibration.angleoffsets[key]
        if opp_pos is None:
            # stats["apply_angle_offsets: no opp hit pos"] += 1
            self.angle_offset = 0
            self.angle_offset_err = no_angle_info_err
            return
        x = opp_pos
        m *= -1
        b *= -1
        self.angle_offset = (m*x+b)/2.0
        temp = opp_pos**2 * merr**2 + m**2 * opp_err + berr**2
        self.angle_offset_err = math.sqrt(temp)
        # stats["apply_angle_offsets: finished getting pos"] += 1
