import ROOT
ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetOptStat(0);
import sys

killstrips = "1/63, 7/62, 1/11, 31/14, 31/62, 33/41, 40/1, 41/21, 41/23, 41/27, 41/29".split(",")
killstrips = map(lambda x: (int(x.split("/")[0]), int(x.split("/")[1])), killstrips)
for i in range(65):
    if i >= 25 and i <= 56: continue
    print i
    killstrips.append((0, i))
killstrips.sort()

if __name__ == "__main__":
    s2sfile = sys.argv[1]
    fnew = open(s2sfile, 'r')
    temp = []
    temp2 = []
    for line in fnew:
        if line[0]=='#':
            #print >>fout, line[0:-1] # Get rid of end of line character--python's print adds one
            temp.append(line.strip())
            continue
        (detstr, subdetstr, modstr, planestr, stripstr, s2sstr, ds2sstr, entriesstr, errorstr) = line.split()
        s2sstr = "1.000000"
        ds2sstr = "0.000000"
        errorstr = "00000"
        entriesstr = "10000"
        det = int(detstr)
        subdet = int(subdetstr)
        module = int(modstr)
        plane = int(planestr)
        strip = int(stripstr)
        const = float(s2sstr)
        ds2s = float(ds2sstr)
        entries = int(entriesstr)
        error = int(errorstr)
        key = module, strip
        if key in killstrips:
            errorstr = "00001"
        out = " ".join((detstr, subdetstr, modstr, planestr, stripstr, s2sstr, ds2sstr, entriesstr, errorstr))
        print out
        temp2.append(out)
    temp.extend(sorted(temp2, key=lambda x: map(float, x.split())))
    fout = open("s2s_constants_1304_allones_killed_strips.txt", "w")
    fout.write("\n".join(temp))
    fout.close()
