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

geometryFile = sys.argv[4] #'D:/VR-Cell-Proxy/ReferenceGeometry/cell228-13MG/228-13MG.CNG_segLength=8_1d_ref_6.swc'
strA = sys.argv[5].replace('[', ' ').replace(']', ' ').replace(',', ' ').split()
evalNodeArray = [int(i) for i in strA]

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

# this next section is where we initialize an run
# the yale neuron simulation
# voltage clamp is initialized here
vc = h.VClamp(pyr.soma[0](0.5))
vc.dur[0] = 15
vc.amp[0] = 0
vc.dur[1] = 35
vc.amp[1] = 50

# set up recording vectors
veclist = []      # for voltage
veclistH = []     # for h state
veclistM = []     # for m state
veclistN = []     # for n state

for i in range(0,num_sects):
    for j in range(0,pyr.all[i].nseg):
        tmpvec = h.Vector()
        tmpvec.record(pyr.all[i](j/pyr.all[i].nseg)._ref_v)
        veclist.append(tmpvec)
        tmpvec = h.Vector()
        tmpvec.record(pyr.all[i](j/pyr.all[i].nseg)._ref_h_myNA)
        veclistH.append(tmpvec)
        tmpvec = h.Vector()
        tmpvec.record(pyr.all[i](j/pyr.all[i].nseg)._ref_m_myNA)
        veclistM.append(tmpvec)
        tmpvec = h.Vector()
        tmpvec.record(pyr.all[i](j/pyr.all[i].nseg)._ref_n_myK)
        veclistN.append(tmpvec)
        
# time vector
t = h.Vector()
# recording the time
t.record(h._ref_t)

# initialize and run
h.finitialize(0)
h.dt = delta_t # time is measured in milliseconds [ms]
h.continuerun(50)

# this loop will write the python time data to 
# an output file
with open(dirName + '/pythonTimes.dat','w') as f:
    for j in range(0,t.__len__()):     
        f.write("%s\n" %t[j])

# this loop writes the output V,m,n,h state variables to
# output files
for i in evalNodeArray:
    with open(dirName + '/dataV/vm_x_'+ str(i)+'.dat','w') as f:
        for val in veclist[i]:
            f.write("%s\n" %val)
    with open(dirName + '/dataH/h_x_'+ str(i)+'.dat','w') as f:
        for val in veclistH[i]:
            f.write("%s\n" %val)
    with open(dirName + '/dataM/m_x_'+ str(i)+'.dat','w') as f:
        for val in veclistM[i]:
            f.write("%s\n" %val)
    with open(dirName + '/dataN/n_x_'+ str(i)+'.dat','w') as f:
        for val in veclistN[i]:
            f.write("%s\n" %val)
    print('save data'+str(i))