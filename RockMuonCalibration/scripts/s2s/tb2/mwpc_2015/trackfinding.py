from __future__ import division

import helper

import ROOT
ROOT.gROOT.SetBatch(True)

import math
import itertools
import array

# the min gof for a line
MIN_GOF = 1

class Point(object):
    def __init__(self, x=0, y=0, dx=0, dy=0, is_used=False, cluster=None):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        assert dy != 0
        self.is_used = is_used
        self.n_points = 1 # TODO consider making poisson dist
        self.res = 0
        self.respererr = 0
        self.cluster = cluster
        self.tracknum = -1
        cluster.point = self
        
    def __repr__(self):
        out = "Point(x=%s, y=%s, dx=%s, dy=%s, is_used=%s)" % (self.x, self.y, self.dx, self.dy, self.is_used)
        return out
        
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
        
    def setused(self, used=True):
        self.is_used = used
        
    def round_point(self):
        self.y = round(self.y)
        # TODO change rounding based on n-points
        
class Module(object):
    def __init__(self, i, points=None):
        if points == None:
            points = []
        self.points = points
        self.module_number = i
    def __repr__(self):
        return "Module(number=%s, npoints=%s, id=%s)" % (self.module_number, len(self.points), id(self))
        
    def add(self, point):
        self.points.append(point)
        
    # testing code, don't use for main track finding
    def round_points(self):
        for p in self.points:
            p.round_point()
        
    # testing code, don't use for main track finding
    def combine_points(self, threshold=1):
        done = False
        points = set(self.points)
        while not done:
            done = True
            for p1, p2 in itertools.combinations(points, 2):
                if abs(p1.y - p2.y) < threshold:
                    x = p1.x
                    y = (p1.y + p2.y) * 0.5
                    dy = math.sqrt(p1.dy**2 + p2.dy**2 + threshold**2)
                    dx = math.sqrt(p1.dx**2 + p2.dx**2)
                    newpoint = Point(x=x, y=y, dx=dx, dy=dy)
                    # remove old point and add new
                    points.remove(p1)
                    points.remove(p2)
                    points.add(newpoint)
                    # found a match, now restart search
                    done = False
                    break
        self.points = list(points)
        
class Line(object):
    def __init__(self, m=0, b=0, dm=0, db=0, chi2=0, points=None, n=None):
        if points == None:
            points = []
        if n == None: n = len(points)
        self.m    = m
        self.b    = b
        self.dm   = dm
        self.db   = db
        self.chi2 = chi2
        self.points = points
        self.n    = n
        self.direction = 0
        self.missingmodule = None
        
        # make res not using point but only if there are enough points
        if len(self.points) > 2:
            allpoints = set(self.points)
            for point in self.points:
                # note that in this context x is position of module in beam direction
                # and y is position up and down, or left and right on the module
                
                # make line with point removed
                line = makelinefrompoints(list(allpoints - set([point])))
                
                point.res = point.y - line.getpoint(point.x)
                point.respererr = point.res / point.dy
        
    def get_goodness_of_fit(self):
        dof = self.getdof()
        return self.chi2 / dof if dof != 0 else float("inf")
        
    def getdof(self):
        return self.n - 2
    
    def setused(self, used=True):
        for point in self.points:
            point.setused()
            
    def getpoint(self, x):
        return self.m * x + self.b
        
    def __repr__(self):
        return "Line(m=%s, b=%s, chi2=%s, n=%s, dm=%s, db=%s)" % (self.m, self.b, self.chi2, self.n, self.dm, self.db)
        
def findlines(modules, mingoodness=None):
    if mingoodness == None: mingoodness = MIN_GOF
    already_tried = dict()
    lines = []
    # make every sequence of modules, min length is 3
    length = len(modules)
    possiblemodules = set(map(lambda x: x.module_number, modules))
    while length >= 3:
        # get the sequences of modules that are length 'length'
        usedmodules = list(itertools.combinations(modules, length))
        potential_lines = []
        #print "length", length
        #pprint.pprint(usedmodules)
        for combination in usedmodules:
            # loop over all points
            #pprint.pprint(combination)
            #exit()
            for points in itertools.product(*map(lambda x: x.points, combination)):
                # sanity checks
                assert len(points) == length
                
                if any(map(lambda x: x.is_used, points)):
                    # skip, one of the points is already used in a line 
                    #print "Skipping", 
                    #pprint.pprint(points)
                    continue 
                #pprint.pprint(points)
                    
                map_of_ids = tuple(map(id, tuple(points)))
                
                # make lines using the points
                try:
                    line = already_tried[map_of_ids]
                except KeyError:
                    line = makelinefrompoints(points)
                if line is None: 
                    # skip, fit didn't work
                    continue 
                    
                gof = line.get_goodness_of_fit()
                # check if line is good
                if gof <= mingoodness:
                    # add line to list of potential lines
                    usedmodulesset = set(map(lambda x: x.module_number, combination))
                    missingmodules = list(possiblemodules.difference(usedmodulesset))
                    if len(missingmodules) == 0:
                        missingmodule = None
                    else:
                        missingmodule = missingmodules[0] if len(missingmodules) == 1 else -1*len(missingmodules)
                    line.missingmodule = missingmodule
                    temp = (gof, line)
                    potential_lines.append(temp)
        # check if we found lines
        if len(potential_lines) == 0:
            # we found no lines, try again with len - 1
            length -= 1
            continue 
        # now that we've made all lines of this length
        # find the best line (the one with minimum gof)
        potential_lines.sort()
        best_gof, best_line = potential_lines[0]
        # set all the points to 'is_used' status, so they won't be used again
        best_line.setused()
        lines.append(best_line)
    return lines
        
            
def makelinefrompoints(points, use_errors_for_track = True, fit_opts = "NQFS"):
    # fit_opts: Q = quiet mode, N=do not draw, F=use minuit, M=find better fit, S=return result
    # more info: https://root.cern.ch/root/html/TGraph.html#TGraph:Fit
    # sanity check
    assert len(points) >= 2
    if use_errors_for_track:
        assert all(map(lambda p: p.dy != 0, points))
        
    a = lambda x: array.array("d", x)
    # convert x arrays and graph
    xarr = a(map(lambda x: x.x,  points))
    xerr = a(map(lambda x: x.dx, points))
    yarr = a(map(lambda x: x.y,  points))
    yerr = a(map(lambda x: x.dy, points))
    graph = ROOT.TGraphErrors(len(xarr), xarr, yarr, xerr, yerr) if use_errors_for_track else ROOT.TGraph(len(xarr), xarr, yarr)
    result = graph.Fit("pol1", fit_opts)
    if int(result) != 0: return None
    return Line(b = result.Value(0), db = result.ParError(0), 
                m = result.Value(1), dm = result.ParError(1),
                chi2 = result.Chi2(), points=points)
                

def maketracksfromclusters(clustersbymodule, mingoodness=None):
    n = 4
    modulesx = [Module(i+1) for i in range(n)]
    modulesy = [Module(i+1) for i in range(n)]
    # cluster.key = wc(1-4), direction (0,1)
    for key, clusters in clustersbymodule.items():
        for cluster in clusters:
            wc = key[0]
            module = wc - 1
            direction = key[1]
            if direction == 0:
                modules = modulesx
            else: modules = modulesy
            x, xerr = cluster.get_hit_pos_info()
            z, zerr = helper.getzpos(wc, direction)
            p = Point(z, x, zerr, xerr, cluster=cluster)
            modules[module].add(p)
    tracksx = findlines(modulesx)
    tracksy = findlines(modulesy)
    # make 2 point tracks here, send back in separate object 
    # since every combo of two points in diff modules will make track
    for track in tracksy:
        track.direction = 1
    tracks = []
    tracks.extend(tracksx)
    tracks.extend(tracksy)
    for i, track in enumerate(tracks):
        for point in track.points:
            point.tracknum = i
    
    # TODO assign track numbers to each point
    return tracks

if __name__ == "__main__":
    import pprint
    import random
    
    def makeline(xarray=range(4), m=5, b=4, var=0):
        #  (-10/13, 2/13) or to three decimal points, (-0.769, 0.154) 
        # r = 0.784, theta=atan( 0.154/0.769)=0.197
        out = []
        assert var != 0
        for x in xarray:
            y = m * x + b + random.gauss(0, var)
            p = Point(x, y, dy=var)
            out.append(p)
        return out
        
    def getbox(points):
        xmin, xmax = float("inf"), float("-inf")
        ymin, ymax = float("inf"), float("-inf")
        for p in points:
            xmin = min(p.x, xmin)
            xmax = max(p.x, xmax)
            ymin = min(p.y, ymin)
            ymax = max(p.y, ymax)
        return xmin, xmax*1.1, ymin, ymax*1.1
        
    def makelines(lines, xmin, xmax, linecolor=1):
        out = []
        for l in lines:
            m1, b1 = l.m, l.b
            f1 = ROOT.TF1("f%s" % id(l), "%s*x+%s" % (m1, b1), xmin, xmax)
            f1.SetLineColor(linecolor)
            out.append(f1)
        return out
        
    def matchlines(truelines, lines, threshold=1, measurepoints=(0, 13339.6)):
        matched_lines = [] # pairs of true and matched line
        unmatched_lines = [] # lines that exist in true but not algorithmically.
        extra_lines = set(lines) # lines that don't exist in true
        for t in truelines:
            matched = False
            t1 = t.getpoint(measurepoints[0])
            t2 = t.getpoint(measurepoints[1])
            for l in lines:
                y1 = l.getpoint(measurepoints[0])
                y2 = l.getpoint(measurepoints[1])
                if abs(y1 - t1) < threshold and abs(y2 - t2) < threshold:
                    result = dict()
                    result["res1"] = (y1 - t1)
                    result["res2"] = (y2 - t2)
                    result["resmean"] = 0.5 * (abs(y1 - t1) + abs(y2 - t2))
                    result["trueline"] = t
                    result["line"] = l
                    matched_lines.append( result )
                    if l in extra_lines:
                        extra_lines.remove(l)
                    matched = True
            if not matched:
                unmatched_lines.append(t)
        return matched_lines, list(unmatched_lines), extra_lines
                
                
        
    #def test(nlines=1, var=0.1, point_removal_rate=(0.111, 0.229, 0.462, 0.298), noise=0.000148, draw=True):
    def test(nlines=1, var=math.sqrt(1/12.0), point_removal_rate=(0.0, 0.0,0.0,0.0), noise=0.00148, draw=True):
        # note: point_removal_rate == 1-eff
        # data driven eff and noise. See 9/15 notes.
        xarray = [0, 2761.3, 5602.7, 13339.6]
        #xarray = [x / 4 for x in range(4)]
        m = 2
        b = 64
        n = len(xarray)
        points = []
        given_points = []
        truelines = []
        modules = [Module(i+1) for i in range(n)]
        #random.seed(6467546)
        for i in range(n):
            x = xarray[i]
            for j in range(int(128)):
                if random.random() < noise:
                    y = j
                    p = Point(x, y, dy=var)
                    points.append(p)
                    modules[i].points.append(p)
        for i in range(nlines):
            # these are based on real mwpc distribution from 1517 / 10
            #mi = random.gauss(0, 8.4e-4)
            mi = random.gauss(0,0.001)
            bi = -999
            while True:
                bi = random.gauss(55, 30)
                if 15 <= bi <= 115:
                    break
            truelines.append(Line(m=mi, b=bi))
            line = makeline(xarray=xarray, m=mi, b=bi, var=var)
            points.extend(line)
            filtered_line = []
            for i in range(n):
                if random.random() > point_removal_rate[i]:
                    modules[i].points.append(line[i])
                    filtered_line.append(line[i])
        
        # make a hist of the lines
        xmin, xmax, ymin, ymax = getbox(points)
        if draw:
            hist1 = ROOT.TH2D("hist1", "hist1;x;y", 100, xmin, xmax, 100, ymin, ymax)
        for module in modules:
            module.round_points()
            module.combine_points()
            if draw:
                for p in module.points:
                        hist1.Fill(p.x, p.y)
        
            
        # find the lines
        alllines = findlines(modules)
        
        
        matchedlines, unmatchedlines, extra_lines = matchlines(truelines, alllines)
        n_matchedlines = len(matchedlines)
        n_unmatchedlines = len(unmatchedlines)
        n_extra_lines = len(extra_lines)
        
        if draw:
            # make a canvas for drawing and split it in two
            c = ROOT.TCanvas("c", "c", 1500, 800)
            c.Divide(2,2)
            # draw the line
            c.cd(1)
            hist1.DrawCopy("colz")
            c.cd(2)
            hist1.DrawCopy("colz")
            truelinesfordrawing = makelines(truelines, xmin, xmax)
            for l in truelinesfordrawing:
                l.Draw("same")
            c.cd(3)
            hist1.DrawCopy("colz")
            linesfordrawing = makelines(alllines, xmin, xmax)
            for l in linesfordrawing:
                l.Draw("same")
            c.cd(4)
            hist1.DrawCopy("colz")
            print "Red = true line not found"
            print "Green = found unreal extra line"
            linesfordrawing2 = makelines(unmatchedlines, xmin, xmax, 2)
            linesfordrawing2.extend(makelines(extra_lines, xmin, xmax, 3))
            for l in linesfordrawing2:
                l.Draw("same")
            c.Print("test.png")
        return (matchedlines, unmatchedlines, extra_lines)
    def onerun():
        
        r = test()
        print "unmatchedlines", r[1]
        print "extralines", r[2]
        if len(r[0]) > 0:
            print "res mean", sum(map(lambda x: x["resmean"], r[0])) / len(r[0])
            
    
    # from https://stackoverflow.com/questions/3679694/a-weighted-version-of-random-choice
    def weighted_choice(choices):
        total = sum(w for c, w in choices)
        r = random.uniform(0, total)
        upto = 0
        for c, w in choices:

          if upto + w >= r:
             return c
          upto += w
        assert False, "Shouldn't get here"
       
    def my_weighted_choice(weights):
        s = sum(weights)
        r = random.uniform(0, s)
        upto = 0
        for i, w in enumerate(weights):
            if upto + w >= r:
                return i
            upto += w
        assert False, "Shouldn't happen"


            
    def characterize(n=1000):
        dx = -0.5
        nchi2 = 20
        maxchi2 = 1
        hn_unmatched = ROOT.TH1D("hn_unmatched", "hn_unmatched;ratio: lines not found", 5, 0+dx, 5+dx)
        hn_extra = ROOT.TH1D("hn_extra", "hn_extra;ratio: extra unreal lines", 5, 0+dx, 5+dx) 
        hresidual1 = ROOT.TH1D("hresidual1", "hresidual1;residual", 50, -1, 1)
        hresidual2 = ROOT.TH1D("hresidual2", "hresidual2;residual", 50, -1, 1)
        hchi2 = ROOT.TH1D("hchi", "hchi2;chi2", nchi2, 0, maxchi2)
        hchi2perpoints = ROOT.TH2D("hchi2perpoints", "hchi2perpoints;n points in line;chi2", 5, 0+dx, 5+dx, nchi2, 0, maxchi2)
        hminchi2perlinesfound = ROOT.TH2D("hminchi2perlinesfound", "hminchi2perlinesfound;n lines found;chi2", 5, 0+dx, 5+dx, nchi2, 0, maxchi2)
        h1linecorrect = ROOT.TH1D("h1linecorrect", "h1linecorrect;0:nlines==guess=1, 1:nlines>1, guess!=1, 2:nlines==1, guess!=1, 3:nlines>1, guess==1;ratio", 4, -0.5, 3.5)
        guess1correct = 0
        guessmorecorrect = 0
        guessmore1line = 0
        guess1moreline = 0
        line1 = 0
        linemore = 0
        
        #trandom = ROOT.TRandom()
        nlines_weights = (0, 100, 5, 1)
        for i in range(n):
            #nlines = trandom.Poisson(1)
            nlines = my_weighted_choice(nlines_weights)
            #print i, nlines
            #if i > 100: exit()
            if nlines == 1:
                line1 += 1
            elif nlines > 1:
                linemore += 1
            else: continue # skip 0 lines
            matchedlines, unmatchedlines, extra_lines = test(draw=False, nlines=nlines)
            if len(matchedlines) + len(extra_lines) != 1:
                if nlines == 1:
                    guessmore1line += 1
                else: guessmorecorrect += 1
            else:  # guess 1 line
                if nlines == 1:
                    guess1correct += 1
                else:
                    guess1moreline += 1
            hn_unmatched.Fill(len(unmatchedlines))
            hn_extra.Fill(len(extra_lines))
            nlines = len(matchedlines) + len(extra_lines)
            if nlines > 0:
                minchi2 = min(itertools.chain(map(lambda x: x.chi2, extra_lines), map(lambda x: x["line"].chi2, matchedlines)))
                hminchi2perlinesfound.Fill(float(nlines), float(minchi2))
            for p in matchedlines:
                hresidual1.Fill(p["res1"])
                hresidual2.Fill(p["res2"])
                npoints = len(p["line"].points)
                chi2 = p["line"].chi2
                hchi2perpoints.Fill(float(npoints), float(chi2))
                hchi2.Fill(float(chi2))
                
        total = line1 + linemore
        if line1 == 0: line1 = 1
        if linemore == 0: linemore = 1
        print "Prob of being right =", (guess1correct + guessmorecorrect) / total 
        print "Prob of being wrong =", (guessmore1line + guess1moreline) / total 
        guess1correct /= line1
        guessmorecorrect /= linemore
        guessmore1line /= line1
        guess1moreline /= linemore
        h1linecorrect.Fill(0, guess1correct)
        h1linecorrect.Fill(1, guessmorecorrect)
        h1linecorrect.Fill(2, guessmore1line)
        h1linecorrect.Fill(3, guess1moreline)
        print "guess1correct", guess1correct
        print "guessmorecorrect", guessmorecorrect
        print "guessmore1line", guessmore1line
        print "guess1moreline", guess1moreline
        
        hn_unmatched.Sumw2()
        hn_unmatched.Scale(1/hn_unmatched.Integral())
        hn_extra.Sumw2()
        hn_extra.Scale(1/hn_extra.Integral())
        hresidual1.Scale(1/hresidual1.Integral())
        hresidual2.Scale(1/hresidual2.Integral())
        drawopts = "E1"
        drawopts2 = ""
        opts2d = "colz"
        c = ROOT.TCanvas("c", "c", 1500, 800)
        c.Divide(3,2)
        c.cd(1)
        hn_unmatched.Draw(drawopts)
        c.cd(2)
        hn_extra.Draw(drawopts)
        c.cd(3)
        #hresidual1.Draw(drawopts2)
        hchi2.Draw(drawopts)
        c.cd(4)
        #hresidual2.Draw(drawopts2)
        hchi2perpoints.Draw(opts2d)
        c.cd(5)
        hminchi2perlinesfound.Draw(opts2d)
        c.cd(6)
        h1linecorrect.Draw("")
        c.Print("test.png")
    characterize()
    #test(nlines=4)
    
    
