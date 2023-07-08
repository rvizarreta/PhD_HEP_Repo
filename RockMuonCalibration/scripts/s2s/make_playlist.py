import os
from sys import argv, exit

prefix = argv[1]
version = argv[2]
minrun = int(argv[3])
minsubrun = int(argv[4])
maxrun = int(argv[5])
maxsubrun = int(argv[6])

print '-- s2s script parameters --'
print '   -- data_processing directory', prefix
print '   -- data_processing version', version
print '   -- first run', minrun, minsubrun
print '   -- last run', maxrun, maxsubrun

if minrun < 2000 and maxrun < 2000:
  det = 'downstream'
elif minrun >= 2000 and maxrun >= 2000:
  det = 'minerva'
else:
  exit('IOV must be either Downstream or Minerva')

playlist = open('playlist.txt', 'w')

rundir = prefix+"/"
print 'rundir:' + rundir
list = os.listdir(rundir)
list.sort()
for ntuple in list:
  run = int(ntuple.split("_")[1])
  subrun = int(ntuple.split("_")[2])
  print str(run) + ' ' + str(subrun) + ' ' + rundir + ntuple 
  playlist.write(str(run) + ' ' + str(subrun) + ' ' + rundir + ntuple + '\n')
  
playlist.close()
