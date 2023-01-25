#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

import re
import argparse

import z3
import h5py
import numpy as np

from qparser import select
from folxformer import FOLxFormer

DEF_DFNAME = "./mcondata/measurements.hdf5"

MEASGRP = "measure_paths"
RADGRP = "static_data/radios"
RAD_ATTRS = ("name", "cls", "type", "minfreq", "maxfreq", "bw")

def fetch_radios(dfile):
    rads = []
    radgrp = dfile[RADGRP]
    for rname, rdata in radgrp.items():
        rdent = {}
        for rattr in RAD_ATTRS:
            if rattr == "name":
                val = re.sub(r'^nuc2-', "", rdata.attrs[rattr])
            else:
                val = rdata.attrs[rattr]
            rdent[rattr] = val
        rads.append(rdent)
    return rads

def fetch_lbvals(dfile):
    lbtbl = {}
    measgrps = dfile[MEASGRP]
    for tstamp,mgrp in measgrps.items():
        freq = mgrp.attrs['freq']
        fstep = mgrp.attrs['freq_step']
        for txname, rxgrp in mgrp.items():
            txname = re.sub(r'-(comp|b210)$', "", txname)
            if not txname in lbtbl:
                lbtbl[txname] = {}
            for rxname, rxdata in rxgrp.items():
                rxname = re.sub(r'-(comp|b210)$', "", rxname)
                if not rxname in lbtbl[txname]:
                    lbtbl[txname][rxname] = []
                avgpwrs = rxdata['avgpower'][1] - rxdata['avgpower'][0]
                fsteps = np.arange(freq+fstep, freq+fstep*avgpwrs.size, step=fstep)
                lbtbl[txname][rxname] += list(zip(avgpwrs, fsteps))
                #lb = np.mean(rxdata['avgpower'][1] - rxdata['avgpower'][0])
                #lbtbl[txname][rxname] = lb
    return lbtbl

def main(args):
    dfile = h5py.File(args.dfname, "r")
    ptree = select.parse(args.query)
    xformer = FOLxFormer()
    xformer.load_radio_records(fetch_radios(dfile))
    xformer.load_lbdata(fetch_lbvals(dfile))
    xformer.process_select(ptree)
    s = xformer.emit_solver()
    print(s.assertions())
    if s.check() == z3.sat:
        print("\nSAT!!\n")
        print(s.model())
    else:
        print("unsat")

def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--dfname", type=str, default=DEF_DFNAME, help="The name of the HDF5 format data file. Default: %s" % DEF_DFNAME)
    parser.add_argument("-q", "--query", type=str, required=True, help="Radio selection query")
    return parser.parse_args()

if __name__ == "__main__":
    main(parse_args())
