import time
import optparse

parser = optparse.OptionParser()

parser.add_option("--dir", dest="directory", action="store", type="string", help="top-level directory for MinosFileDB", default="/minerva/data/calibrations/minos/MinosFileDB")
parser.add_option("--file", dest="fullpath", action="store", type="string", help="full path to file that you want to show", default=None)
parser.add_option("--year", dest="year", action="store", type="int", help="year of the files you want to show times for", default=None)
parser.add_option("--month", dest="month", action="store", type="int", help="month of the files you want to show times for", default=None)

(options, commands) = parser.parse_args()

loc = options.directory
if options.fullpath != None:
  loc = fullpath
else:
  if options.year == None:
    options.year = time.localtime()[0]
  if options.month == None:
    options.month = time.localtime()[1]
  loc += "/MinosFileDB_%04d-%02d.opts" % (options.year, options.month)

try:
  minoslist = open( loc, 'r' )
  lines = minoslist.readlines()
  for line in lines:
    if line.find("sntp_data") == -1:
      continue
    stuff = line.split("/")[-1]
    start = int(stuff.split()[1])
    end = int(stuff.split()[2].split('\"')[0])
    run = int(stuff.split()[0][1:9])
    subrun = int(stuff.split()[0][10:14])
    s = time.localtime(start)
    e = time.localtime(end)
    print "%d/%02d: Start %04d-%02d-%02d %02d:%02d:%02d End %04d-%02d-%02d %02d:%02d:%02d" % (run, subrun, s[0], s[1], s[2], s[3], s[4], s[5], e[0], e[1], e[2], e[3], e[4], e[5])
except IOError:
  print "ERROR - Input file not valid: %s" % loc
