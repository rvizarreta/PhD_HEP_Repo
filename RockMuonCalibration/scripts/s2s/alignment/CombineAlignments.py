
def findValues(mylist,value):
    value = value.strip() # Don't want whitespace being the issue. 
    # Just want the module/plane number.
    offset = 12
    if "MT" in value: offset += 2
    value = value[value.find("name=") + offset:]
    print "New value name", value
    values = [] #dPosxyz[0,2] dRotXYZ[3,5]
    posvalues = [0,0,0]
    rotvalues = [0,0,0]
    for i in range(0,len(mylist)):
        line = mylist[i]
        if line.find(value)!=-1:
            posline = mylist[i+1]
            rotline = mylist[i+2]
            print posline,rotline
            posvalues = posline.split(">")[1].split("<")[0].split()
            rotvalues = rotline.split(">")[1].split("<")[0].split()
            break # all done
    else: print "WARNING: Wasn't able to find", value
    print posvalues,rotvalues
    values = values+posvalues
    values = values+rotvalues
    print "Final",values
    return values
import sys
if len(sys.argv) < 3:
    print "Useage: python CombineAlignment.py <original> <new>"
    exit()
outfilename = sys.argv[2].replace("newAlignment", "combinedAlignment")
print "Output", outfilename
originalAlignment = open(sys.argv[1]).readlines()
newAlignment = open(sys.argv[2]).readlines()
combinedAlignment = open(outfilename,"w")

combinedAlignment.write(newAlignment[0])
combinedAlignment.write(newAlignment[1])
combinedAlignment.write(newAlignment[2])



for i,line in enumerate(originalAlignment[2:-1]):
    if line.find('condition classID')!=-1:
        origvalues = findValues(originalAlignment,line)
        newvalues = findValues(newAlignment,line)
        combined = [float(a)+float(b) for a,b in zip(origvalues,newvalues)]
        print "Find constants in original",origvalues
        print "Find constants in new",newvalues
        print "Combined",combined
        combinedAlignment.write(line)
        combinedAlignment.write('    <paramVector name="dPosXYZ" type="double">%f %f %f</paramVector>\n'%(combined[0],combined[1],combined[2]))
        combinedAlignment.write('    <paramVector name="dRotXYZ" type="double">%f %f %f</paramVector>\n'%(combined[3],combined[4],combined[5]))
        combinedAlignment.write("  </condition>\n")
        
        


combinedAlignment.write("</DDDB>\n")
