

# define some constants
INCHTOMM = -25.4 # mm/inch

getzpos = [0, 2761.3, 5602.7, 13339.6]

CALTOUSE = "Cali3x"

DEADTIME = 15
TIMEERROR = 5
AFTERPULSE_RANGE = 5# 5
CONNECTED_HIT_RANGE = 1.5

hitoffsets = None
if CALTOUSE == "Cali3x":
    hitoffsets = {
    (1,0): -3.19388698021  -0.568151854533,
    (1,1): -0.0941016747167+0.00653385137838,
    (2,0):  2.51372425597  +0.2540931567,
    (2,1):  1.09335821175  +0.0159863514478,
    (3,0):  1.75080916277  +0.136078703674,
    (3,1): -1.27380768601  +0.0178385414007,
    (4,0): -1.65439935886  -0.0542493265404,
    (4,1):  0.437920755992 +0.0144043787303
    }
elif CALTOUSE == "Survey":
    # see http://minerva-docdb.fnal.gov:8080/cgi-bin/RetrieveFile?docid=10752&filename=Proj%207002%20Req%207070%20As-found%20Survey%20of%20MINERvA%20Test%20Beam.pdf&version=3
    hitoffsets = {
    (1,0):  0.17*INCHTOMM,
    (1,1): -0.023*INCHTOMM,
    (2,0): -0.135*INCHTOMM,
    (2,1):  0.029*INCHTOMM,
    (3,0): -0.206*INCHTOMM,
    (3,1): -0.041*INCHTOMM,
    (4,0): -0.157*INCHTOMM,
    (4,1):  0.321*INCHTOMM
    }
elif CALTOUSE == "SurveyCorrected":
    INCHTOMM = -25.4 # mm/inch
    # see http://minerva-docdb.fnal.gov:8080/cgi-bin/RetrieveFile?docid=10752&filename=Project%207002%20Request%206847%20MTest%20As-found_As-set.pdf&version=5
    # this uses the 'as-set'
    hitoffsets = {
    (1,0):  0.035*INCHTOMM,
    (1,1):  0.012*INCHTOMM,
    (2,0): -0.021*INCHTOMM,
    (2,1):  0.008*INCHTOMM,
    (3,0): -0.026*INCHTOMM,
    (3,1):  0.015*INCHTOMM,
    (4,0): -0.012*INCHTOMM,
    (4,1):  0.003*INCHTOMM
    }
elif CALTOUSE == "CaliAuto10x":
    hitoffsets = {(1, 0): -3.761126920163409,
     (1, 1): -0.080091884361245105,
     (2, 0): 2.8454871646690618,
     (2, 1): 1.1594456623610494,
     (3, 0): 1.7593523871263657,
     (3, 1): -1.1824373547723153,
     (4, 0): -1.6859923366603669,
     (4, 1): 0.48452531203662169}
elif CALTOUSE == "CaliAuto10xHigherRes":
    # made with the residual hists had 240 bins instead of 60
    hitoffsets = {(1, 0): -3.7603180340506559,
     (1, 1): -0.068957875187757728,
     (2, 0): 2.8495881906840776,
     (2, 1): 1.1759650254838481,
     (3, 0): 1.7668401539740137,
     (3, 1): -1.1577588702275301,
     (4, 0): -1.6692603306564735,
     (4, 1): 0.51997654931526327}
elif CALTOUSE == "CaliAutoSlopeCal":
    # I wouldn't use these...
    hitoffsets = {(1, 0): -3.761126920163409,
     (1, 1): -0.080091884361245105,
     (2, 0): 4.4030937127737309,
     (2, 1): 2.7170522104657184,
     (3, 0): 4.9197486523152358,
     (3, 1): 1.9779589104165547,
     (4, 0): 5.8386693477263485,
     (4, 1): 8.0091869964233382}
     
def getoffset(key):
    return hitoffsets[(1, key[1])]-hitoffsets[key]
 

if __name__ == "__main__":
    print "Just printing offsets"
    import pprint
    pprint.pprint(hitoffsets)
    exit()
USEOFFSETS = True if hitoffsets is not None else False
if not USEOFFSETS: print "Warning: no offsets will be used bc none are specified"

# (wire chamber, direction): b, berr, m, merr, rms err of unknown hit
angleoffsets = None
"""{(1, 0): (0.45427266002095451,
          0.062625096497230526,
          -0.0070106548772923809,
          0.00096389822472893677, 
          0.693538102469),
 (1, 1): (-0.39829935261451971,
          0.044709424480807662,
          0.0060643494992917669,
          0.00075823745374481606,
          0.682978112583),
 (2, 0): (-0.17551682907996519,
          0.039102756267478542,
          0.0030270899001840182,
          0.00059801760325524703,
          0.535510182648),
 (2, 1): (0.19312352277121347,
          0.044398353795150516,
          -0.0028042409946381743,
          0.00067481733871196546,
          0.603056301745),
 (3, 0): (-0.22098262465745641,
          0.035968539474750746,
          0.0035481881930717251,
          0.00057186796892163703,
          0.597646930924),
 (3, 1): (0.28459485594041339,
          0.034776583197155868,
          -0.0041868824440051368,
          0.0005415605037411257,
          0.587309755918),
 (4, 0): (0.23172740709908088,
          0.0485417073038239,
          -0.0038019284687777198,
          0.00073889515256576129,
          0.993072357591),
 (4, 1): (-0.41365361933203543,
          0.061326565308061978,
          0.0053588599469242193,
          0.00085575595801157126,
          0.998937957863)}"""
          


instrument_positions = []
# downstream ToF, 0
# see http://minerva-docdb.fnal.gov:8080/cgi-bin/RetrieveFile?docid=10752&filename=Proj%207002%20Req%207070%20As-found%20Survey%20of%20MINERvA%20Test%20Beam.pdf&version=5
instrument_positions.append((563.176*INCHTOMM,0))
# detector face, 1
instrument_positions.append((647.223*INCHTOMM,0))
# veto wall, 2
instrument_positions.append((549.793*INCHTOMM,0))
# cherenkov (unknown), 3
instrument_positions.append((0,0))
# cosmic wall (unknown, est. taking avg between veto and detector), 4
instrument_positions.append((0.5*(549.793+647.223)*INCHTOMM,0))
# upstream ToF (I wouldn't trust this), 5
instrument_positions.append((-88239.3,0))
# wc 1-4, 6-9
instrument_positions.append((getzpos[0],0))
instrument_positions.append((getzpos[1],0))
instrument_positions.append((getzpos[2],0))
instrument_positions.append((getzpos[3],0))
