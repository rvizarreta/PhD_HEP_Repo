import ROOT

ROOT.gROOT.SetBatch(1)

# compare_to_previous will plot the ratio of the constant to the previous IOV
compare_to_previous = True
# compare_to_DB will plot the ratio of the constant to the version in /minerva/data/calibrations
compare_to_DB = True
db_dir = "/minerva/data/calibrations/s2s_tables/minerva/v5/"
db_prefix = "s2s_constants" # full det
db_prefix_frozen = "s2s_constants_gen2_prime" # frozen det
# Make a pdf of all the plots
do_print = True

# LE
iovs = [ 846, 900, 1049, 1140, 2000, 2218, 2491, 2621, 2751, 3099, 3415, 3543, 3596, 3650, 3712, 3809, 3837, 3874 ]
# ME
#iovs = [ 6015, 6059, 6152, 6200, 8029, 10036, 10056, 10115, 10205, 10229, 10246 ]

n = len(iovs)

consts = []
errors = []
errorsdb = []
dconst = []
dconstdb = []
for i in range(n):
  first_mod = -5
  if iovs[i] < 2000:
    first_mod = 51
  consts.append( ROOT.TH2D("const_%05d"%iovs[i],"New constants run %d;Module;Strip"%iovs[i],2*(115-first_mod),first_mod,115,127,1,128) )
  errors.append( ROOT.TH2D("error_%05d"%iovs[i],"New errors run %d;Module;Strip"%iovs[i],2*(115-first_mod),first_mod,115,127,1,128) )
  errorsdb.append( ROOT.TH2D("errordb_%05d"%iovs[i],"DB Errors run %d;Module;Strip"%iovs[i],2*(115-first_mod),first_mod,115,127,1,128) )
  dconstdb.append( ROOT.TH2D("changedb_%05d"%iovs[i],"New / DB run %d;Module;Strip"%iovs[i],2*(115-first_mod),first_mod,115,127,1,128) )
for i in range(n-1):
  dconst.append( ROOT.TH2D("change_%05d"%iovs[i],"Ratio (new) IOVs %d / %d;Module;Strip"%(iovs[i+1],iovs[i]),2*(115-first_mod),first_mod,115,127,1,128) )


for i in range(n):

  # Make a dictionary of the constant in the DB
  dbdict = {}
  if compare_to_DB:
    lines = []
    if iovs[i] < 2000:
      dbfile = open( db_dir + "%s_%04d.txt" % (db_prefix_frozen,iovs[i]) )
      lines = dbfile.readlines()
    else:
      dbfile = open( db_dir + "%s_%04d.txt" % (db_prefix,iovs[i]) )
      lines = dbfile.readlines()
    for line in lines:
      if line[0] == "#":
        continue
      (det, subdet, modstr, plstr, strstr, s2sstr, ds2s, ent, errstr) = line.split()
      module = int(modstr)
      plane = int(plstr)
      strip = int(strstr)
      s2s = float(s2sstr)
      error = int(errstr)
      if error == 0:
        dbdict[10000*module + 1000*plane + strip] = s2s
      else:
        dbdict[10000*module + 1000*plane + strip] = -1.0

  print "Period begining with run %d" % iovs[i]
  f = open( "../s2s_constants_%d.txt" % iovs[i], "r" )
  lines = f.readlines()
  for line in lines:
    if line[0] == "#":
      continue
    (det, subdet, modstr, plstr, strstr, s2sstr, ds2s, ent, errstr) = line.split()
    module = int(modstr)
    plane = int(plstr)
    strip = int(strstr)
    s2s = float(s2sstr)
    error = int(errstr)
    if error != 0:
      errors[i].Fill( module+0.5*(plane-1), strip, 1.0 )
      if compare_to_DB:
        if dbdict[10000*module + 1000*plane + strip] == -1.0:
          errorsdb[i].Fill( module+0.5*(plane-1), strip )
    else:
      errors[i].Fill( module+0.5*(plane-1), strip, 0.0 )
      consts[i].Fill( module+0.5*(plane-1), strip, s2s )
      if i != 0:
        b = consts[i].FindBin( module+0.5*(plane-1), strip )
        bold = consts[i-1].FindBin( module+0.5*(plane-1), strip )
        old = consts[i-1].GetBinContent(bold)
        olderr = errors[i-1].GetBinContent(bold)
        if olderr == 0 and old > 0.0:
          dconst[i-1].Fill( module+0.5*(plane-1), strip, s2s/old )
      if compare_to_DB:
        old = dbdict[10000*module + 1000*plane + strip]
        if old == -1.0: # error
          errorsdb[i].Fill( module+0.5*(plane-1), strip )
        else:
          b = dconstdb[i].FindBin( module+0.5*(plane-1), strip )
          dconstdb[i].SetBinContent( b, s2s / old )

# print the book
if do_print:
  c = ROOT.TCanvas()
  c.Print("ComparisonBook.pdf[")
  for i in range(n):
    consts[i].SetMinimum(0.0)
    consts[i].SetMaximum(2.0)
    consts[i].Draw("COLZ")
    c.Print("ComparisonBook.pdf")
  if compare_to_previous:
    for i in range(n-1):
      dconst[i].SetMinimum(0.8)
      dconst[i].SetMaximum(1.2)
      dconst[i].Draw("COLZ")
      c.Print("ComparisonBook.pdf")
      #c.Print("dconst_%05d_%05d.png" % (iovs[i],iovs[i+1]))
  if compare_to_DB:
    for i in range(n):
      dconstdb[i].SetMinimum(0.8)
      dconstdb[i].SetMaximum(1.2)
      dconstdb[i].Draw("COLZ")
      c.Print("ComparisonBook.pdf")
      #c.Print("dconst_%05d_%05d.png" % (iovs[i],iovs[i+1]))
  for i in range(n):
    errors[i].Draw("COLZ")
    c.Print("ComparisonBook.pdf")
    errorsdb[i].Draw("COLZ")
    c.Print("ComparisonBook.pdf")
  c.Print("ComparisonBook.pdf]")

# write to file
tf = ROOT.TFile("comparison.root","RECREATE")
tf.cd()
for i in range(n):
  consts[i].Write()
  errors[i].Write()
  errorsdb[i].Write()
  if compare_to_DB: dconstdb[i].Write()
for i in range(n-1):
  if compare_to_previous: dconst[i].Write()
