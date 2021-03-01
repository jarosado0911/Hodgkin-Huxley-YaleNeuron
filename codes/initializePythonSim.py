#import neuron functionality
import neuron
import array
import math
import os
import csv
import sys
#check neuron version
print(neuron.__version__)

#import particular functionality
from neuron import h
from neuron.units import ms, mV

# load .hoc files with more functionalities
h.load_file('stdrun.hoc')
h.load_file('import3d.hoc')

# load my channels I made in the neuron gui
h.load_file("jamesChannels.hoc")

# dx and dt are passed as arguments to the script
dx = float(sys.argv[1])
delta_t = float(sys.argv[2])
dirName = sys.argv[3]

# this makes output folders for the voltage
# and state variables m,h,n

os.mkdir(dirName)
os.mkdir(dirName + "/dataV")
os.mkdir(dirName + "/dataH")
os.mkdir(dirName + "/dataM")
os.mkdir(dirName + "/dataN")

geometryFile = sys.argv[4] #'D:/VR-Cell-Proxy/ReferenceGeometry/cell228-13MG/228-13MG.CNG_segLength=8_1d_ref_6.swc'

# load an swc morphology file
class Pyramidal:
    def __init__(self):
        self.load_morphology()
        # do discretization, ion channels, etc here#
    def load_morphology(self):
        cell = h.Import3d_SWC_read()
        cell.input(geometryFile)
        i3d = h.Import3d_GUI(cell, 0)
        i3d.instantiate(self)

# instantiate the cell, i.e. declare it as 'pyr'
pyr = Pyramidal()
  
# set the sections with specific biophysics in this case the same for each section
# the biophysics for the channels are set in the hoc file which is loaded above!
for sec in pyr.all:
    frac, whole = math.modf((sec.L/dx)*1)
    if (whole ==0):
        sec.nseg=1           # number segments in each section
    elif (frac >= 0.5):
        sec.nseg=math.ceil((sec.L/dx)*1)
    else:
        sec.nseg=math.floor((sec.L/dx)*1)
    
    if ((sec.nseg % 2) == 0):
        sec.nseg = sec.nseg + 1

    sec.Ra = 250          # uniform resistance Ohm.cm
    sec.cm = 1.0          # uniform capacitance uF/cm2
    #sec.diam = 0.5        # uniform diameter um

    #load my channels
    sec.insert('myNA')
    sec.insert('myK')
    sec.insert('myLK')

# I made counters to count the number of sections of a particular type
# is this really necessary I can use iterators?
num_dend_sect=0
num_soma_sect=0
num_apic_sect=0
num_sects = 0
for sec in pyr.dend:
    num_dend_sect = num_dend_sect + 1
for seg in pyr.soma:
    num_soma_sect = num_soma_sect + 1
for seg in pyr.all:
    num_sects = num_sects + 1
    
print('A section is an unbranched length of cell!')
print('Number of Soma Sections in the cell: ', num_soma_sect)
print('Number of Dend Sections in the cell: ', num_dend_sect)
print('Number of Sections in the cell: ', num_sects)


# this sections is for determining the centers of the sections
# yale neuron does not use points like I do in my matlab code
# it calculates the voltage corresponding to a segment on an unbranched piece
# of cable, each segment has a center
xout =[]
yout =[]
zout =[]

# this code was borrowed from t. carnevale
# from the yale neuron forum
for sec in pyr.all:
    testsec = sec
    nn = testsec.n3d()+1
    xx = h.Vector(nn)
    yy = h.Vector(nn)
    zz = h.Vector(nn)
    mylength = h.Vector(nn)

    for ii in range(0,nn-1):
        xx.x[ii]=testsec.x3d(ii)
        yy.x[ii]=testsec.y3d(ii)
        zz.x[ii]=testsec.z3d(ii)
        mylength.x[ii]=testsec.arc3d(ii)
    
    mylength.div(mylength.x[nn-2])

    myrange = h.Vector(testsec.nseg+2)
    myrange.indgen(1/testsec.nseg)
    myrange.sub(1/(2*testsec.nseg))
    myrange.x[0]=0
    myrange.x[testsec.nseg+1]=1

    xint = h.Vector(testsec.nseg+2)
    yint = h.Vector(testsec.nseg+2)
    zint = h.Vector(testsec.nseg+2)

    xint.interpolate(myrange,mylength,xx)
    yint.interpolate(myrange,mylength,yy)
    zint.interpolate(myrange,mylength,zz)

    x_xtra = [0.0]*testsec.nseg
    y_xtra = [0.0]*testsec.nseg
    z_xtra = [0.0]*testsec.nseg

    for ii in range(0,testsec.nseg):
        x_xtra[ii]=xint.x[ii]
        y_xtra[ii]=yint.x[ii]
        z_xtra[ii]=zint.x[ii]
        xout.append(x_xtra[ii])
        yout.append(y_xtra[ii])
        zout.append(z_xtra[ii])

# this will write the coordinate locations to a 
# .txt output file
with open(dirName + '/allLocs.txt', 'w') as f:
    for xcoord in xout:
        f.write("%s " % xcoord)
    f.write("\n")
    for ycoord in yout:
        f.write("%s " % ycoord)
    f.write("\n")
    for zcoord in zout:
        f.write("%s " % zcoord)

# this loop collects the diameter information of each
# segment peice        
rout = []
for sec in pyr.all:
    for seg in sec:
        rout.append(sec.diam)

# this loop write the diameter information to an
# output file
with open(dirName + '/diam.txt','w') as f:
    for d in rout:
        f.write("%s\n" % d)

# the code collects the node (segment indices) for each 
# unbranched cable and writes it to an output file
count = 0;
sCount = 0;
indList = [];
for i in range(0,num_sects):
    sCount = sCount + 1
    indList = []
    for j in range(0,pyr.all[i].nseg):
        count = count + 1
        indList.append(count)
    with open(dirName + '/section%s.dat' %sCount,'w') as f:
        for n in indList:
            f.write("%s\n" %n)