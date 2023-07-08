from __future__ import division

import ROOT
ROOT.gROOT.SetBatch(True)

import math


class Point(object):
    def __init__(self, x=0, y=0, dx=0, dy=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        
    def __repr__(self):
        out = "Point(x=%s, y=%s, dx=%s, dy=%s)" % (self.x, self.y, self.dx. self.dy)
        return out
        
    def length(self):
        return math.sqrt(self.x**2 + self.y**2)
        
class HoughPoint(object):
    def __init__(self, value=0, theta=0, r=0, dt=0, dr=0):
        self.value = value
        self.theta = theta
        self.r = r
        self.dt = dt
        self.dr = dr
        
    def __repr__(self):
        #out = "HoughPoint(value=%s, theta=%s, r=%s, dt=%s, dr=%s)" % (self.value, self.theta, self.r, self.dt, self.dr)
        out = "HoughPoint(value={0}, theta={1}, r={2}, dt={3}, dr={4})".format(self.value, self.theta, self.r, self.dt, self.dr)
        return out
        
    def asline(self):
        r, t = self.r, self.theta
        m, b = 0, 0
        if r != 0: 
            b = r * (math.sin(t) + math.cos(t)**2 / math.sin(t))
            m = math.tan(t) - b / (r * math.cos(t))
        return Line(m, b)
        
class Line(object):
    def __init__(self, m=0, b=0):
        self.m = m
        self.b = b
    def __repr__(self):
        return "Line(m=%s, b=%s)" % (self.m, self.b)
        
    def ashough(self):
        theta = math.atan2(-1, self.m)
        radius = self.b / (math.sin(theta) - self.m * math.cos(theta))
        return HoughPoint(theta=theta, r=radius)
    
        

def houghtransform(list_of_points, min_theta=-math.pi/1.5, max_theta=math.pi/1.5, ntheta=200, min_r=None, max_r=None, nr=600):
    if max_r == None: 
        max_r = max(map(lambda p: p.length(), list_of_points))
        max_r *= 1.1
    if min_r == None: min_r = -max_r
    # sanity checks
    assert min_theta < max_theta
    assert ntheta > 0
    assert min_r < max_r
    assert nr > 0
    # calculate the change in theta per step
    dt = (max_theta - min_theta) / ntheta
    assert dt > 0
    # set the number of subsamples to take per dt step and per dr step
    # the number of loops per theta step is n_steps_per_pixel**2
    n_steps_per_pixel = 10
    # make the histogram to save the data
    unique_id = id(list_of_points)
    unique_name = "houghtransform" + str(unique_id)
    unique_title = unique_name + ";theta (radians);POCA dist"
    hist = ROOT.TH2D(unique_name, unique_title, ntheta, min_theta, max_theta, nr, min_r, max_r)
    # loop over each point
    for point in list_of_points:
        theta = min_theta
        x = point.x
        y = point.y
        dx = point.dx
        dy = point.dy
        while theta <= max_theta:
            # calc the transform
            r = x * math.cos(theta) + y * math.sin(theta)
            # calc the error
            temp = dx**2 * math.cos(theta)**2 + dy**2 * math.sin(theta)**2 + dt**2 * (math.cos(theta) + math.sin(theta))**2
            dr = math.sqrt(temp)
            # loop over each possible r
            n_sigma = 3
            range_ = dr * n_sigma
            current_dr = -range_
            ddr = dr / n_steps_per_pixel
            while current_dr <= range_:
                # make weight guassian
                wgt = math.exp((current_dr)**2 / dr**2)
                # enter that point in the histogram
                hist.Fill(theta, r + current_dr, wgt)
                # step dr
                current_dr += ddr
            # step theta
            theta += dt / n_steps_per_pixel
            
    #hist.Smooth()
    # scale to between 0 and 1
    max_ = hist.GetMaximum()
    hist.Scale(1/max_)
    
    info = dict()
    info["rrange"] = max_r - min_r
    info["thetarange"] = max_theta - min_theta
            
    return hist, info
    
def findpeaks(hist, threshold=0.8):
    xaxis = hist.GetXaxis()
    yaxis = hist.GetYaxis()
    out = []
    for xbin in range(1, hist.GetNbinsX()+1):
        for ybin in range(1, hist.GetNbinsY()+1):
            value = hist.GetBinContent(xbin, ybin)
            if value >= threshold:
                # get theta and the radius (x&y resp.)
                x = xaxis.GetBinCenter(xbin)
                dx = xaxis.GetBinUpEdge(xbin) - x
                y = yaxis.GetBinCenter(ybin)
                dy = yaxis.GetBinUpEdge(ybin) - y
                p = HoughPoint(value, x, y, dx, dy)
                out.append(p)
    out = sorted(out, key=lambda x: x.value, reverse=True)
    return out
    
def filter_peaks(peaks, threshold=0.5):
    # find all peaks that are different by X% from higher value peaks
    goodpeaks = []
    # loop over all peaks
    for p in peaks:
        peakbad = False
        for peak in goodpeaks:
            # check if variation is not within 10% of a good peak
            if abs(p.r - peak.r) / abs(peak.r) < threshold and abs(p.theta - peak.theta) / abs(peak.theta) < threshold:
                # add the value to the good peak
                peak.value += p.value 
                peakbad = True
                break
        # check if peak is good
        if not peakbad:
            # add peak to good peaks
            goodpeaks.append(p)
    goodpeaks = sorted(goodpeaks, key=lambda x: x.value, reverse=True)
    return goodpeaks
    
def filter_lines(lines, threshold=0.5):
    goodlines = []
    for l in lines:
        linebad = False
        for line in goodlines:
            # check if variation is not within 10% of a good peak
            fails = 0
            if abs(line.b - l.b) / abs(line.b) < threshold:
                fails += 1
            if abs(line.m - l.m) / abs(line.m) < threshold:
                fails += 1
            if fails == 2:
                linebad = True
                break
        # check if peak is good
        if not linebad:
            # add peak to good peaks
            goodlines.append(l)
            
    return goodlines
    
def filter_lines2(lines, max_slope):
    return filter(lambda x: abs(x.m) < max_slope, lines)
    
def getlines(p):
    return map(lambda x: x.asline(), p)
    
def movepoints(points, dx, dy, xcompression=0.01, ycompression=0.1):
    for p in points:
        p.x += dx
        p.x *= xcompression
        p.y += dy
        p.y *= ycompression
    return points
    
def movelinesback(lines, dx, dy, xcompression=0.01, ycompression=0.1):
    for l in lines:
        l.b -= dy
        #l.m /= xcompression
        #l.m *= ycompression
        l.m *= xcompression
        l.m /= ycompression
    return lines

if __name__ == "__main__":
    import pprint
    import random
    
    def makeline(xarray=range(4), m=5, b=4, var=0, dy=None):
        #  (-10/13, 2/13) or to three decimal points, (-0.769, 0.154) 
        # r = 0.784, theta=atan( 0.154/0.769)=0.197
        out = []
        for x in xarray:
            y = m * x + b + random.gauss(0, var)
            p = Point(x, y, dy=var if dy is None else dy)
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
        
    def makelines(lines, xmin, xmax):
        out = []
        for l in lines:
            m1, b1 = l.m, l.b
            f1 = ROOT.TF1("f%s" % id(l), "%s*x+%s" % (m1, b1), xmin, xmax)
            out.append(f1)
        return out
        
    def test():
        m = 2
        b = 64
        n = 20
        var = 0.01
        mvar = 0
        bvar = 50
        nlines = 3
        dy = 1
        points = []
        #xarray = [0, 2761.3, 5602.7, 13339.6]
        xarray = [5 * x / n for x in range(n)]
        truelines = []
        random.seed(6467546)
        for i in range(nlines):
            #mi, bi = m, b
            #mi, bi = m, b + random.uniform(-64, 64)
            #mi, bi = m + random.uniform(-5, 5), b
            mi, bi = m + random.uniform(-mvar, mvar), b + random.uniform(-bvar, bvar)
            # these are based on real mwpc distribution from 1517 / 10
            #mi = random.gauss(0, 8.4e-4)
            '''mi = random.gauss(0,0.001)
            bi = -999
            while True:
                bi = random.gauss(55, 30)
                if 15 <= bi <= 115:
                    break'''
            print "final mb", mi, bi
            truelines.append(Line(m=mi, b=bi))
            points.extend(makeline(xarray=xarray, m=mi, b=bi, var=var, dy=dy))
            
        # transform the points so that the origin is no longer along the path
        '''dx = 0#4000
        dy = 0 #64
        xcompress=1# 0.01
        ycompress=1
        movepoints(points, dx, dy, xcompress, ycompress)'''
        
        # make a hist of the lines
        xmin, xmax, ymin, ymax = getbox(points)
        hist1 = ROOT.TH2D("hist1", "hist1;x;y", 100, xmin, xmax, 100, ymin, ymax)
        for p in points:
            hist1.Fill(p.x, p.y)
        
            
        # take the hough transform
        #hough = houghtransform(points, min_theta=-math.atan(0.1)+math.pi/2, max_theta=math.atan(0.1)+math.pi/2)
        hough, houghinfo = houghtransform(points) #, min_theta=-math.atan(0.1)+math.pi/2, max_theta=math.atan(0.1)+math.pi/2)
        threshold = 0.5
        peak_filter_threshold = 0.2
        line_filter_threshold = 0.5
        max_slope = m + mvar
        allpeaks = p = findpeaks(hough,threshold=threshold)
        print "n peaks:", len(p)
        p = filter_peaks(p, peak_filter_threshold)
        print "n peaks after filter:", len(p)
        alllines = lines = getlines(p)
        print "n lines:", len(lines)
        lines = filter_lines(lines, line_filter_threshold)
        print "n lines after filter1:", len(lines)
        #lines = filter_lines2(lines, max_slope)
        #print "n lines after filter2:", len(lines)
        
        print "all peaks:"
        pprint.pprint(allpeaks)
        print "filtered peaks:"
        pprint.pprint(p)
        print "all lines:"
        pprint.pprint(alllines)
        print "filtered lines:"
        pprint.pprint(lines)
        
        # make a canvas for drawing and split it in two
        c = ROOT.TCanvas("c", "c", 1500, 800)
        c.Divide(2,2)
        # draw the line
        c.cd(1)
        hist1.DrawCopy("colz")
        # draw the hough transform
        c.cd(2)
        hough.DrawCopy("colz")
        c.cd(3)
        # draw the hough graph with tresholding
        hough.GetZaxis().SetRangeUser(threshold,1)
        hough.Draw("colz")
        print "True hough points"
        allellipses = []
        for l in truelines:
            h = l.ashough()
            print h
            n = 100
            e = ROOT.TEllipse(h.theta, h.r, houghinfo['thetarange'] / n, houghinfo['rrange'] / n)
            e.SetLineStyle(0)
            e.SetFillColor(1)
            allellipses.append(e)
            #e.Draw("same")
        c.cd(4)
        hist1.Draw("colz")
        # transform lines back
        #movelinesback(lines, dx, dy, xcompress, ycompress)
        lines = makelines(lines, xmin, xmax)
        for l in lines:
            l.Draw("same")
        c.Print("test.png")
    test()
    
    
    
