from sys import argv
TBMODE = True # Turn to false for Minerva
UseBlank = 0
if len(argv) == 2 and argv[1] == '-blank': UseBlank = 1
print '<?xml version="1.0" encoding="ISO-8859-1"?>'
print '<!DOCTYPE DDDB SYSTEM "../../../DTD/structure.dtd">'
print '<DDDB>'
file = open('AlignmentConstants.txt')
for line in file:
  (str1, modstr, str2, planestr, str3, shiftstr, str4, rotstr) = line.split()
  mod = int(modstr)
  plane = int(planestr)
  shift = float(shiftstr)
  rot = float(rotstr)
  if UseBlank: (shift, rot) = (0, 0)
  if TBMODE:
    print '  <condition classID="6" name="MTModule%03d_Plane%d">' % (mod, plane)
  else:
    print '  <condition classID="6" name="Module%03d_Plane%d">' % (mod, plane)
  print '    <paramVector name="dPosXYZ" type="double">%f 0 0</paramVector>' % shift
  print '    <paramVector name="dRotXYZ" type="double">0 0 %f</paramVector>' % rot
  print '  </condition>'

print '</DDDB>'
