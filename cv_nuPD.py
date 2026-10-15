# main01.py is a part of the PYTHIA event generator.
# Copyright (C) 2023 Torbjorn Sjostrand.
# PYTHIA is licenced under the GNU GPL v2 or later, see COPYING for details.
# Please respect the MCnet Guidelines, see GUIDELINES for details.

# Keywords: basic usage; charged multiplicity; python;

# This is a simple test program. It fits on one slide in a talk.  It
# studies the charged multiplicity distribution at the LHC.

# To set the path to the Pythia 8 Python interface do either
# (in a shell prompt):
#      export PYTHONPATH=$(PREFIX_LIB):$PYTHONPATH
# or the following which sets the path from within Python.
from array import array
from tqdm import tqdm
import sys
cfg = open("Makefile.inc")
lib = "../lib"
for line in cfg:
    if line.startswith("PREFIX_LIB="): lib = line[11:-1]; break
sys.path.insert(0, lib)

# Import the Pythia module.
import pythia8
import ROOT

import matplotlib.pyplot as plt
import numpy as np

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("output_file_name")
parser.add_argument("n_events", type = int)
parser.add_argument("seed", type = int)
parser.add_argument("energy", type = float, default = 400)
args = parser.parse_args()

pythia = pythia8.Pythia()
#pythia.readString("Top:gg2ttbar = on") # Switch on process.
#pythia.readString("Top:qqbar2ttbar = on");
#pythia.readString("HardQCD:qqbar2ccbar = on");
#pythia.readString("HardQCD:all = on");
pythia.readString("SoftQCD:all = on");
#pythia.readString("HardQCD:gg2ccbar = on") # Switch on process.
#pythia.readString("LowEnergyQCD:all = on")
pythia.readString("Beams:frameType = 2") # Fixed target
pythia.readString("Beams:eA = {}".format(args.energy)) # SPS
pythia.readString("Beams:eB = 0") # Fixed-target

pythia.readString("Random:setSeed = on");
pythia.readString("Random:seed = {}".format(args.seed));

pythia.readString("Next:numberCount = 0");
pythia.init() # Initialize; incoming pp beams is default.

out_vars = [["id", "int"],
            ["status", "int"],
            ["px", "double"],
            ["py", "double"],
            ["pz", "double"],
            ["e", "double"],
            ["xProd", "double"],
            ["yProd", "double"],
            ["zProd", "double"],
            ["tProd", "double"],
            ["y", "double"],
            ["eta", "double"],
            ["mother1", "int"],
            ["mother2", "int"]]
            
f_out = ROOT.TFile(args.output_file_name+"_{}.root".format(args.seed), "recreate")
tree_out = ROOT.TTree("pythia", "SPS pythia events with neutrino in NP04 acceptance")

var_vecs = {}
var_vecs["index"] = ROOT.vector("int")(0)
tree_out.Branch("index", "std::vector<int>", var_vecs["index"])
for var_name, var_type in out_vars :
    var_vecs[var_name] = ROOT.vector(var_type)(0)
    tree_out.Branch(var_name, "std::vector<{}>".format(var_type), var_vecs[var_name])

h_p = ROOT.TH1D("secondary_p", "Secondary protons;Energy[GeV];Frequency", 8, 0, 400)
h_n = ROOT.TH1D("secondary_n", "Secondary neutrons;Energy[GeV];Frequency", 8, 0, 400)

N = args.n_events

for iEvent in tqdm(range(N)) :
    pythia.next() # Generate event.
    iNu = 0
    hasNu = False
    hasFinalStateP = False
    xi = 0
    for particle in pythia.event :
#        print(particle.id(), particle.status(), particle.px(), particle.py(), particle.pz(), particle.vProd().px())
        if particle.status() >= 0 and abs(particle.id()) == 2212:
            h_p.Fill(particle.e())
        if particle.status() >= 0 and abs(particle.id()) == 2112:
            h_n.Fill(particle.e())
            
#        if abs(particle.id()) in [12, 14, 16] :
#
#            if particle.pz() < 0 :
#                continue
#            tx = particle.px()/particle.pz()
#            x_720 = tx*72000
#
#            #if x_720 > -712 + 300:
#            if x_720 > 1500:
#                continue
#            #if x_720 < -712 - 300:
#            if x_720 < -1500:
#                continue
#
#            ty = particle.py()/particle.pz()
#            y_720 = ty*72000
#
##            if y_720 < 461 - 300:
#            if y_720 < -1500:
#                continue
##            if y_720 > 461 + 300:
#            if y_720 > 1500:
#                continue
#
#            hasNu = True
#            break

#    if hasNu :
     for particle in pythia.event :
         if particle.isFinal() or abs(particle.id()) in [411, 421, 431, 4122, 111, 113, 213, 221, 331, 223, 333, 511, 521, 443, 553]:
             for var_name, var_type in out_vars :
#                    print(var_name, particle.id(), getattr(particle, var_name))
                 var_vecs[var_name].push_back(getattr(particle, var_name)())
    tree_out.Fill()
    for var_name, var_type in out_vars :
        var_vecs[var_name].clear()

print("Neutrino FRACTION {:.2e} = {}/{}".format(tree_out.GetEntries()/N, tree_out.GetEntries(), N))

tree_out.Write()

h_p.Scale(1./N)
h_n.Scale(1./N)

h_p.Write()
h_n.Write()


meta_tree_out = ROOT.TTree("meta", "Metadata for SPS pythia events with neutrino in NP04 acceptance")
sigmaTotal = array('f', [ 0. ])
meta_tree_out.Branch('sigmaTotal', sigmaTotal, "sigmaTotal/F")
nEvents = array('f', [ 0. ])
meta_tree_out.Branch('nEvents', nEvents, "nEvents/F")

sigmaTotal[0] = pythia.getSigmaTotal()
nEvents[0] = float(N)

meta_tree_out.Fill()

meta_tree_out.Write()
f_out.Close()

pythia.stat()
