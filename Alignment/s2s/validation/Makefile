CXX = g++
CXXFLAGS = -g -Wall -fPIC
ROOTFLAGS = `root-config --cflags --glibs`

BINARIES = MakeErrorPlots
TARGETS = MakeErrorPlots.o

#--- if using 'make all' ---#
all : $(TARGETS)

#--- if making individual targets ---#

MakeErrorPlots.o : MakeErrorPlots.cxx
	$(CXX) $(INCLUDE) $(CXXFLAGS) $(ROOTFLAGS) -o $*.o $(LDLIBS) -c $*.cxx #compile
	$(CXX) $(INCLUDE) $(CXXFLAGS) $(ROOTFLAGS) $(LDLIBS) -o $* $*.o        #link
        
clean:
	rm -f $(BINARIES) $(TARGETS)

