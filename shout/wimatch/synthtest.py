#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

import sys
import random as rand
import itertools
import argparse

import numpy as np
import z3

from qparser import select
from folxformer import FOLxFormer

rand.seed(42)

radios = [
    {'name': 'rad1', 'cls': 'bs', 'type': 'x310', 'minfreq': 3400, 'maxfreq': 3800, 'bw': 160},
    {'name': 'rad2', 'cls': 'bs', 'type': 'x310', 'minfreq': 3400, 'maxfreq': 3800, 'bw': 160},
    {'name': 'rad3', 'cls': 'bs', 'type': 'x310', 'minfreq': 3400, 'maxfreq': 3800, 'bw': 160},
    {'name': 'rad4', 'cls': 'bs', 'type': 'x310', 'minfreq': 3400, 'maxfreq': 3800, 'bw': 160},
    {'name': 'rad5', 'cls': 'bs', 'type': 'x310', 'minfreq': 3400, 'maxfreq': 3800, 'bw': 160},
    {'name': 'rad6', 'cls': 'bs', 'type': 'x310', 'minfreq': 3400, 'maxfreq': 3800, 'bw': 160}
]

def mklbdata():
    lbdata = {}
    for r1, r2 in itertools.combinations([a['name'] for a in radios],2):
        if not r1 in lbdata:
            lbdata[r1] = {}
        if not r2 in lbdata:
            lbdata[r2] = {}
        lbdata[r1][r2] = []
        lbdata[r2][r1] = []
        mu = rand.uniform(5, 30)
        sigma = 2.5
        for f in range(3550, 3560):
            val = rand.gauss(mu, sigma)
            lbdata[r1][r2].append((val, f*1e6))
            lbdata[r2][r1].append((val, f*1e6))
    return lbdata

def main(args):
    lbdata = mklbdata()
    for r1,rows in lbdata.items():
        for r2,rdat in rows.items():
            avg = np.mean([a[0] for a in rdat])
            print("%s,%s: %0.1f" % (r1, r2, avg))
    xformer = FOLxFormer()
    xformer.load_radio_records(radios)
    xformer.load_lbdata(lbdata)
    ptree = select.parse(args.query)
    xformer.process_select(ptree)
    s = xformer.emit_solver()
    #print(s)
    if s.check() == z3.sat:
        print("\nSAT!!\n")
        print(s.model())
    else:
        print("unsat")

def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", type=str, required=True, help="Radio selection query")
    return parser.parse_args()
        
if __name__ == "__main__":
    main(parse_args())
