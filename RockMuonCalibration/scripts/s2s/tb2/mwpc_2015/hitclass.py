import helper

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
        
class Hit(object):
    def __init__(self, wire, time, wc, d):
        self.pos = wire
        self.time = time
        self.wc = wc
        self.d = d
        self.timecut = False
        self.afterdeadtime = False
        self.afterpulse = False
        self.in_cluster = False
        self.tdc = helper.gettdc(wire)
        
    def is_cut(self):
        return self.timecut or self.afterpulse or self.in_cluster
    def is_cut_exclude_timecut(self):
        return self.afterpulse or self.in_cluster
    def __repr__(self):
        return "Hit(%s,%s,%s,%s,%s)" % (self.pos, self.time, self.in_cluster, self.afterpulse, self.timecut)

