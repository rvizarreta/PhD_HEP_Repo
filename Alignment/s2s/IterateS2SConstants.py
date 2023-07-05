fold = open('s2s_constants_old.txt', 'r')
fcorr = open('fit_corrections.txt', 'r')
fout = open('s2s_constants.txt', 'w')
# Make a dictionary where oldconstants[10000*module + 1000*plane + strip] = old s2s
oldconstants = {}
# Make a dictionary where fitcorrection[10*module+plane] = fit correction
fitcorrection = {}

for line in fold:
  if line[0]=='#':
    continue
  (detstr, subdetstr, modstr, planestr, stripstr, s2sstr, ds2sstr, entriesstr, errorstr) = line.split()
  module = int(modstr)
  plane = int(planestr)
  strip = int(stripstr)
  const = float(s2sstr)
  error = int(errorstr)
  if error == 0:
    oldconstants[10000*module + 1000*plane + strip] = const # first iteration has error == 0 always, const = 1.0 for errors
  else:
    oldconstants[10000*module + 1000*plane + strip] = 1.0

for line in fcorr:
  if line[0]=='#':
    continue
  (modstr, planestr, corrstr) = line.split()
  module = int(modstr)
  plane = int(planestr)
  corr = float(corrstr)
  fitcorrection[10*module + plane] = corr

fnew = open('s2s_constants_new.txt', 'r')
avgconst = 0.0
n = 0
for line in fnew:
  if line[0]=='#':
    continue
  (detstr, subdetstr, modstr, planestr, stripstr, s2sstr, ds2sstr, entriesstr, errorstr) = line.split()
  det = int(detstr)
  subdet = int(subdetstr)
  module = int(modstr)
  plane = int(planestr)
  strip = int(stripstr)
  const = float(s2sstr)
  ds2s = float(ds2sstr)
  entries = int(entriesstr)
  error = int(errorstr)
  oldconst = oldconstants[10000*module + 1000*plane + strip]
  correction = fitcorrection[10*module + plane]
  newconst = const*oldconst*correction
  if error == 0:
    avgconst += newconst
    n += 1

avgconst /= n
print 'Average constant for %d good channels: %7.6f' % (n, avgconst)
fnew.close()

fnew = open('s2s_constants_new.txt', 'r')
avgconst2 = 0.0
n = 0
for line in fnew:
  if line[0]=='#':
    print >>fout, line[0:-1] # Get rid of end of line character--python's print adds one
    continue
  (detstr, subdetstr, modstr, planestr, stripstr, s2sstr, ds2sstr, entriesstr, errorstr) = line.split()
  det = int(detstr)
  subdet = int(subdetstr)
  module = int(modstr)
  plane = int(planestr)
  strip = int(stripstr)
  const = float(s2sstr)
  ds2s = float(ds2sstr)
  entries = int(entriesstr)
  error = int(errorstr)
  oldconst = oldconstants[10000*module + 1000*plane + strip]
  correction = fitcorrection[10*module + plane]
  newconst = const*oldconst*correction / avgconst
  if error == 0:
    avgconst2 += newconst
    n += 1
  print >>fout, '%d %d %d %d %d %f %f %d %05d' % (det, subdet, module, plane, strip, newconst, ds2s, entries, error)

print 'Average constant for %d good channels: %7.6f' % (n, avgconst2/n)

fout.close()
