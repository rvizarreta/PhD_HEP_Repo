MINERVAPROPATH = '/minerva/data/users/minervacal/data_processing_s2s_eroica'
MINERVAPROVERSION = 'v10r8pre'
OUTPATH = '/minerva/app/users/marshalc/cmtuser/Minerva_v10r7p3/Cal/RockMuonCalibration/scripts/s2s/output'
outfile = open('master_s2s_script.sh', 'w')
infile = open('s2seras.txt', 'r')

for line in infile:
  (run1, subrun1, run2, subrun2) = line.split()[0:4]
  workpath = OUTPATH + '/s2s_' + run1
  print >> outfile, 'mkdir', workpath
  print >> outfile, 'source make_s2s.sh', MINERVAPROPATH, MINERVAPROVERSION, run1, subrun1, run2, subrun2

infile.close()
outfile.close()
