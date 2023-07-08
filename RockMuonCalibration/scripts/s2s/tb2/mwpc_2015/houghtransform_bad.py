from __future__ import division
import itertools
import math
import array

import ROOT
ROOT.gROOT.SetBatch(True)

class Point(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    def __repr__(self):
        out = "Point(x=%s, y=%s)" % (repr(self.x), repr(self.y))
        return out
        
def getpoca(p1, p2):
    dx = p1.x - p2.x
    dy = p1.y - p2.y
    if dx == 0 or dy == 0: 
        print p1, p2, dx, dy, "dx == 0 or dy == 0"
        return None
    # calculate the slope created by the two points
    m = dx / dy
    if m == 0 or m**2 - 1 == 0: 
        print p1, p2, dx, dy, m, "m == 0 or m**2 - 1"
        return None
    # calculate the angle between the x axis and the POCA
    # note: atan2(dy,dx) but the slope is 1/m
    theta = math.atan2(dx, dy)
    # calculate the y-intercept created by the two points
    b = p1.y - m * p1.x
    # finally calculate the point of closest approach
    pocax = -b * m / (m**2 - 1)
    pocay = pocax * dy / dx
    # calculate the dist from POCA to origin
    radius = math.sqrt(pocax**2 + pocay**2)
    if radius > 5000: return None
    # create the point and add to output
    return Point(theta, radius)

def houghtransform(list_of_points):
    transformed_points = []
    for p1, p2 in itertools.permutations(list_of_points, 2):
        new_point = getpoca(p1, p2)
        if new_point is not None:
            transformed_points.append(new_point)
    
    # y=m*x+b
    # b=y-m*x
    # m*x+b = 1/m*x
    # x=-b*m/(m**2-1), m**2-1 != 0, m!=0
    
    return transformed_points
    
def makeplot(hp, name="h1", n=30, xmin=-math.pi*2, xmax=math.pi*2, m=30, ymin=0, ymax=100):
    hist = ROOT.TH2D(name, name, n, xmin, xmax, m, ymin, ymax)
    for point in hp:
        hist.Fill(point.x, point.y)
    return hist
    
    
if __name__ == "__main__":
    import pprint
    import random
    def make_line(m=2, b=10, n=300, var=5):
        list_of_points = list(map(lambda p: Point(p+random.gauss(0, var), p*m+b+random.gauss(0, var)), [i for i in range(n)]))
        return list_of_points
        
    def getbox(points):
        xmin, xmax = float("inf"), float("-inf")
        ymin, ymax = float("inf"), float("-inf")
        for p in points:
            xmin = min(p.x, xmin)
            xmax = max(p.x, xmax)
            ymin = min(p.y, ymin)
            ymax = max(p.y, ymax)
        return xmin, xmax, ymin, ymax
        
    def reversepoca(theta, r):
        x = r*math.cos(theta)
        y = r*math.sin(theta)
        m_inv = math.tan(theta)
        if m_inv == 0: return 0, y
        m = 1/m_inv
        b = y - m*x 
        return m, b
        
    def poca(m, b):
        if m == 0: return b, 0
        m_inv = 1/m
        theta = math.atan(m_inv)
        pocax = b * m / (m**2 + 1)
        pocay = pocax * m_inv
        radius = math.sqrt(pocax**2 + pocay**2)
        return theta, radius
        
    def test():
        n = 20
        m = -5
        b = 100
        var = 0.1
        # make some lines
        list_of_points = make_line(m, b, n, var)
        #list_of_points.extend(make_line(-3, 500, 300, 3))
        xmin, xmax, ymin, ymax = getbox(list_of_points)
        # make a histogram of the lines
        h1 = makeplot(list_of_points, "h1", n, xmin, xmax, n, ymin, ymax)
        # calc the hough transform
        hp = houghtransform(list_of_points)
        xmin2, xmax2, ymin2, ymax2 = getbox(hp)
        # make a plot for the hough transform
        h2 = makeplot(hp, "h2", n, xmin2, xmax2, n, ymin2, ymax2)
        #h2.GetZaxis().SetRangeUser(0.8,1)
        max_ = h2.GetMaximum()
        maxbin = h2.GetMaximumBin()
        h2.Scale(1/max_)
        x = array.array("i", [0])
        y = array.array("i", [0])
        z = array.array("i", [0])
        h2.GetBinXYZ(maxbin, x, y, z)
        theta = h2.GetXaxis().GetBinCenter(x[0])
        radius = h2.GetYaxis().GetBinCenter(y[0])
        theta, radius = poca(m, b)
        print theta, radius
        m1, b1 = reversepoca(theta, radius)
        print m1, b1
        f1 = ROOT.TF1("f1", "%s*x+%s" % (m1, b1), xmin, xmax)
        #f2 = ROOT.TF1("f2", "%s*x+%s" % (m2, b2))
        c1 = ROOT.TCanvas("c1", "c1", 1500, 800)
        c1.Divide(2,1)
        c1.cd(1)
        h1.Draw("colz")
        f1.Draw("same")
        c1.cd(2)
        h2.Draw("colz")
        c1.Print("test.png")
    test()
        
