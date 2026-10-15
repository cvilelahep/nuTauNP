#!/bin/bash

OUT_DIR=/Users/cvilela/DUNE/NuTauPD/MC/
N_PER_FILE=10000000
N_FILES=100

n_parallel=4

#for E in 25 75 125 175 225 275 325 375
for E in 400
do
    mkdir -p ${OUT_DIR}/${E}/
    for i in `seq ${N_FILES}`
    do
	python3 cv_nuPD.py nuPD_${N_PER_FILE}_softQCD_${E} ${N_PER_FILE} ${i} ${E} &
	if (( $i % $n_parallel == 0))
	then
	    wait
           mv nuPD_${N_PER_FILE}_softQCD_${E}_*.root ${OUT_DIR}/${E}/
	fi
    done
done
