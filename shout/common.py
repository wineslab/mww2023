#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

#
# Common functions and definitions.
#

import logging
import multiprocessing as mp

import numpy as np
import matplotlib.pyplot as plt

import measurements_pb2 as measpb

IPRANGES = ['127.0.0.0/8', '155.98.32.0/20']
SERVICE_PORT = 5555
LISTEN_IP = '0.0.0.0'
LOGFMAT = '%(asctime)s:%(levelname)s: %(message)s'
LOGDATEFMAT = '%Y-%m-%d %H:%M:%S'
LOGLEVEL = logging.DEBUG
DATA_OUTDIR="./mcondata"
DATA_FILE_NAME="measurements.hdf5"

class OrchCalls:
    GETCLIENTS = "getclients"

def get_attr(msg, key):
    for kv in msg.attributes:
        if kv.key == key: return kv.val
    return None

def add_attr(msg, key, val):
    attr = msg.attributes.add()
    attr.key = key
    attr.val = str(val)

def get_function(msg):
    return get_attr(msg, "funcname")

def mk_result(uuid, ptype, funcname):
    rmsg = measpb.SessionMsg()
    rmsg.uuid = uuid
    rmsg.type = measpb.SessionMsg.RESULT
    rmsg.peertype = ptype
    add_attr(rmsg, "funcname", funcname)
    return rmsg

def encode_samples(msg, samps):
    for samp in samps:
        msamp = msg.samples.add()
        msamp.r, msamp.j = samp.real, samp.imag

def decode_samples(msg):
    samps = []
    if msg.samples:
        samps = np.array([complex(c.r, c.j)
                          for c in msg.samples],
                         dtype=np.complex64)
    return samps

def plot_proc(title, *args):
    def doplot():
        plt.suptitle(title)
        plt.plot(*args)
        plt.show()
    plproc = mp.Process(target=doplot)
    plproc.start()
