MINERVAPROPATH = '/minerva/data/users/minervacal/data_processing_validation'
MINERVAPROVERSION = 'v10r7p3'
OUTPATH = '/minerva/app/users/marshalc/cmtuser/Minerva_v10r7p3/Cal/RockMuonCalibration/scripts/s2s/output/validation'
outfile = open('master_val_script.sh', 'w')
infile = open('s2seras.txt', 'r')

print >> outfile, 'mkdir',OUTPATH

for line in infile:
  (run1, subrun1, run2, subrun2) = line.split()[0:4]
  workpath = OUTPATH + '/val_' + run1
  print >> outfile, 'mkdir', workpath
  print >> outfile, 'source do_validation.sh', MINERVAPROPATH, MINERVAPROVERSION, run1, subrun1, run2, subrun2

infile.close()
outfile.close()
