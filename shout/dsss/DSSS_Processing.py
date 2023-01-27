#!/usr/bin/env python3

# author: Jie Wang, jie.w@wustl.edu

# Version History:
# Version 1.0:  Initial Release.  Jan 2022.  For Python 3.7.4

import os, sys
import argparse

import json
import numpy as np
# import pandas as pd
from scipy import signal, stats
import scipy
import time
import h5py
import datetime
import math
import matplotlib.pyplot as plt

DEF_DATADIR = '/local/repository/shout/examples/measurements/' #'/local/data/' #
DEF_DFNAME= "Shout_meas_01-05-2023_10-45-52"

GPS_LOCATIONS = {
    "cbrssdr1-browning-comp": (40.76627,-111.84774),
    "cellsdr1-browning-comp": (40.76627,-111.84774),
    "cbrssdr1-hospital-comp": (40.77105,-111.83712),
    "cellsdr1-hospital-comp": (40.77105,-111.83712),
    "cbrssdr1-smt-comp": (40.76740,-111.83118),
    "cellsdr1-smt-comp": (40.76740,-111.83118),
    "cbrssdr1-ustar-comp": (40.76895,-111.84167),
    "cellsdr1-ustar-comp": (40.76895,-111.84167),
    "cbrssdr1-bes-comp": (40.76134,-111.84629),
    "cellsdr1-bes-comp": (40.76134,-111.84629),
    "cbrssdr1-honors-comp": (40.76440,-111.83699),
    "cellsdr1-honors-comp": (40.76440,-111.83699),
    "cbrssdr1-fm-comp": (40.75807,-111.85325),
    "cellsdr1-fm-comp": (40.75807,-111.85325),
    "moran-nuc1-b210": (40.77006,-111.83784),
    "moran-nuc2-b210": (40.77006,-111.83784),
    "ebc-nuc1-b210": (40.76770,-111.83816),
    "ebc-nuc2-b210": (40.76770,-111.83816),
    "guesthouse-nuc1-b210": (40.76627,-111.83632),
    "guesthouse-nuc2-b210": (40.76627,-111.83632),
    "humanities-nuc1-b210": (40.76486,-111.84319),
    "humanities-nuc2-b210": (40.76486,-111.84319),
    "web-nuc1-b210": (40.76791,-111.84561),
    "web-nuc2-b210": (40.76791,-111.84561),
    "bookstore-nuc1-b210": (40.76414,-111.84759),
    "bookstore-nuc2-b210": (40.76414,-111.84759),
    "sagepoint-nuc1-b210": (40.76278,-111.83061),
    "sagepoint-nuc2-b210": (40.76278,-111.83061),
    "law73-nuc1-b210": (40.76160,-111.85185),
    "law73-nuc2-b210": (40.76160,-111.85185),
    "garage-nuc1-b210": (40.76148,-111.84201),
    "garage-nuc2-b210": (40.76148,-111.84201),
    "madsen-nuc1-b210": (40.75786,-111.83634),
    "madsen-nuc2-b210": (40.75786,-111.83634),
    "cnode-wasatch-dd-b210": (40.77107659230161, -111.84315777334905),
    "cnode-mario-dd-b210": (40.77281166195038, -111.8409002868012),
    "cnode-moran-dd-b210": (40.77006,-111.83872),
    "cnode-guesthouse-dd-b210": (40.76769,-111.83609),
    "cnode-ustar-dd-b210": (40.76851381022761, -111.8404502186636), 
    "cnode-ebc-dd-b210": (40.76720,-111.83810),
}

gold_codes_dict = {
    31:{0:np.array([1,1,0,0,0,1,1,0,0,1,0,1,0,0,0,1,1,1,1,0,0,0,1,0,0,0,1,1,1,1,1])},
    63:{0:np.array([0,0,0,0,0,0,0,1,1,1,0,1,0,0,0,1,1,1,1,1,0,1,0,0,1,1,1,0,0,0,0,1,1,0,1,1,1,1,1,1,0,0,1,0,0,1,1,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0])},
    127:{0:np.array([0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,1,1,0,1,0,0,1,0,0,1,1,0,0,1,0,1,1,0,0,0,1,0,0,0,1,0,1,0,1,0,1,1,1,1,0,0,1,0,0,0,1,1,1,1,0,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,1,1,0,1,1,1,1,0,1])},
    511:{0:np.array([1,0,0,0,0,0,0,1,0,1,1,0,1,0,1,0,0,1,0,0,1,0,0,1,1,0,1,0,1,0,1,1,1,0,1,1,0,1,1,1,1,0,0,0,0,1,0,0,1,1,1,0,0,0,0,0,0,1,1,0,1,1,1,0,1,1,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1,1,1,0,1,0,1,0,0,1,0,1,1,0,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,0,1,1,0,1,0,0,0,1,1,1,1,1,0,0,0,0,1,1,1,0,0,1,0,1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,0,0,0,0,0,0,1,1,0,1,1,0,1,0,0,0,1,0,0,1,1,1,1,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,1,1,0,1,0,1,1,1,0,0,1,0,1,1,0,1,1,0,1,0,1,0,0,1,1,0,1,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,1,1,0,0,1,0,1,0,1,0,1,0,0,1,0,1,0,1,1,0,1,1,0,1,0,0,1,1,1,1,0,1,1,1,0,0,1,0,0,1,1,1,1,1,0,0,1,1,0,1,1,0,1,1,1,1,0,0,1,0,1,1,0,0,1,1,0,1,1,1,0,1,1,1,1,0,0,1,0,1,0,1,0,0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,1,1,1,1,0,1,1,0,0,0,1,0,0,1,0,1,1,0,1,1,1,0,1,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,1,1,0,0,1,1,0,0,1,0,0,1,0,0,0,1,0,0,1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,0,0,1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,1,0,1,0,0,1,1,1,0,1,0,1,1,1,1,0,0,0,0,0,1,0,0,1,1,1,0,1,1,1,0,1,0])},
    2047: {0:np.array([1,0,0,0,0,0,0,0,0,0,1,1,0,0,1,0,0,0,0,1,0,1,1,1,0,0,1,0,0,0,0,0,1,1,0,1,1,1,1,0,0,1,1,1,1,1,0,1,1,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,1,0,1,0,1,1,0,1,1,1,0,0,1,1,1,0,1,1,0,1,0,0,1,0,0,1,1,0,1,1,0,0,0,0,0,1,1,1,1,0,1,1,1,0,1,0,1,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,0,1,1,0,0,1,0,0,0,1,1,1,0,1,1,1,1,1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,0,1,0,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,0,1,0,0,1,0,0,0,1,1,0,1,0,1,0,1,0,0,0,1,0,1,1,0,0,1,0,0,0,0,1,0,1,1,0,1,1,0,1,1,0,1,0,0,1,1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,0,1,0,1,1,0,1,0,0,1,1,1,0,0,0,1,1,0,1,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,1,1,0,1,1,1,0,0,1,0,0,1,0,0,1,0,0,1,0,1,0,0,1,1,0,1,1,1,0,1,0,0,0,1,1,1,0,1,1,1,0,1,1,0,0,1,0,1,1,0,0,1,0,1,1,0,0,0,1,0,1,1,1,1,0,1,1,1,1,1,0,0,1,0,1,1,0,1,0,0,0,1,0,0,0,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,1,1,0,1,1,0,1,0,1,0,1,1,0,1,1,1,0,1,1,0,1,1,0,0,0,1,1,0,0,1,0,0,0,0,0,0,1,1,1,0,0,1,1,1,0,1,0,1,0,0,1,0,0,1,1,0,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,0,1,1,0,0,0,0,0,0,0,1,1,1,1,0,0,1,0,0,0,0,1,0,0,0,1,0,0,1,0,1,0,1,0,1,1,0,0,0,0,1,1,1,0,1,1,0,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,1,0,1,1,0,0,1,1,0,1,1,0,1,1,1,0,1,1,0,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1,0,1,0,1,0,1,0,0,1,0,0,0,1,1,0,0,0,1,0,1,1,0,1,1,1,1,0,0,1,1,0,1,1,1,1,0,0,1,0,1,0,0,1,1,1,0,1,1,0,0,1,1,1,0,1,0,1,1,0,1,1,1,1,0,0,0,1,1,0,0,1,0,1,0,0,0,1,1,1,1,1,0,1,0,0,0,0,0,0,1,1,1,1,0,1,1,0,1,0,0,0,1,0,1,1,0,1,0,1,1,1,0,0,0,1,0,0,1,0,1,1,0,0,0,1,0,1,1,1,1,1,1,0,1,1,1,1,0,0,1,1,0,1,1,0,1,1,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,1,1,0,1,1,1,0,1,0,1,1,0,1,0,0,1,0,1,0,0,1,0,1,1,0,0,1,1,0,0,1,0,1,1,0,0,1,0,0,1,1,1,1,0,0,0,0,0,1,0,1,0,0,0,0,1,0,1,0,0,1,0,1,0,0,1,0,0,1,0,0,1,0,1,1,0,0,0,1,0,0,1,1,1,1,0,0,0,0,1,0,0,1,1,1,0,0,1,0,0,1,1,1,0,0,1,1,0,0,0,0,1,0,1,1,0,0,1,1,1,1,0,1,0,1,0,1,1,1,0,0,1,1,0,0,1,1,0,1,1,0,0,0,1,1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0,1,0,0,1,1,0,0,1,1,1,0,0,1,1,1,1,1,0,1,0,1,0,1,1,0,1,1,0,1,0,0,0,1,1,1,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,1,0,0,1,0,1,0,0,1,0,1,0,0,1,1,1,0,0,0,1,0,0,1,0,1,0,0,1,0,0,1,1,1,0,1,0,1,1,0,0,1,1,0,1,1,1,0,0,1,0,1,1,0,0,0,0,0,0,1,0,1,1,1,1,1,1,1,0,0,1,1,1,1,0,1,0,1,0,0,1,0,0,0,1,1,0,0,1,1,0,0,1,0,0,1,1,1,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,0,0,1,0,1,1,0,1,0,1,0,0,0,0,1,1,0,0,0,1,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,0,0,0,1,1,0,1,1,1,1,0,1,0,1,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1,0,1,0,1,1,0,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,1,0,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,1,1,0,1,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,0,1,0,1,1,0,0,1,1,0,0,1,1,0,0,0,1,0,0,0,0,1,0,1,1,0,1,1,0,1,1,1,0,1,1,1,0,1,0,0,0,0,1,1,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,1,1,0,0,0,1,1,0,0,1,1,1,0,0,1,0,1,1,0,1,1,0,1,1,1,0,1,0,0,1,0,1,0,1,0,0,1,1,1,1,0,0,0,0,0,0,1,0,0,1,1,1,0,1,0,0,0,0,0,0,0,1,1,1,0,0,1,0,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,0,1,1,0,1,0,1,1,1,1,0,0,1,0,1,1,0,0,0,0,1,0,1,1,1,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1,1,1,1,0,1,0,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0,1,1,1,0,0,1,1,0,0,1,1,1,0,1,1,1,1,0,0,1,0,1,1,1,1,1,0,1,0,0,1,0,1,1,1,0,1,0,1,1,0,1,0,0,0,1,1,1,1,0,1,0,0,0,0,1,1,0,0,0,0,0,1,0,1,0,1,0,0,1,0,1,0,0,1,1,0,0,0,0,1,0,1,0,1,0,1,1,0,0,1,0,0,0,0,1,0,1,0,1,1,0,1,1,0,0,1,0,1,1,1,1,0,1,0,0,0,0,1,1,0,1,0,0,0,0,1,0,0,0,1,1,1,1,0,0,1,0,1,1,0,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,0,1,1,1,1,0,1,0,0,1,0,1,0,0,0,0,1,0,1,1,0,0,1,0,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1,0,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,1,1,0,0,1,1,1,1,0,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,0,0,1,1,1,0,1,0,1,0,1,0,1,1,0,0,0,1,1,1,0,0,0,1,1,1,0,0,0,1,1,0,0,1,1,1,1,0,1,1,0,0,1,0,1,1,1,0,0,1,1,0,0,1,1,1,1,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0,0,0,0,1,1,1,1,1,0,0,1,1,1,0,1,0,1,0,1,0,1,1,1,0,0,1,1,0,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,1,0,1,0,0,1,0,0,1,0,0,0,0,1,1,1,0,0,0,1,0,1,0,0,0,1,0,0,1,0,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1,0,0,1,0,1,0,0,0,1,1,1,1,0,1,0,0,0,1,0,1,0,1,0,0,0,1,0,0,0,0,0,1,0,1,1,1,1,0,0,1,0,0,1,1,0,0,1,1,1,1,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,1,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,1,1,1,1])}

}

# original bit string
simple_bits = np.array([1,1,1,1,0,0,1,0])

# plot setting
bbox_to_anchor = (0.5, 1.0)


def traverse_dataset(meas_folder, numrx, numnoise):
    '''
    Traverse through the whole measurement file collected by SHOUT
    The measurement file includes raw IQ samples for each transmitter-receiver pair.
    INPUT
    ----
        meas_folder: path to the measurement folder. Example: "SHOUT/Results/Shout_meas_01-04-2023_18-50-26"
        num_rx: the number of repeated runs. Default: "rxrepeat" parameter set by the json file
        numnoise: the number of repeated runs for collecting noise only. Default: "wotxrepeat" parameter set by the json file
    OUTPUT
    ----
        data: Collected IQ samples w/ transmission. It is indexed by the TX name
        noise: Collected IQ samples w/o transmission. It is indexed by the TX name
        txrxloc: transmitter and receiver names for indexing purpose
    '''
    rx_data = {}
    noise = {}
    rxloc = {}

    try:
        dataset = h5py.File(meas_folder + '/measurements.hdf5', "r")
    except: 
        pass
    print("Dataset meta data:", list(dataset.attrs.items()))
    for cmd in dataset.keys():
        print("Command:", cmd)
        if cmd == 'saveiq':
            cmd_time = list(dataset[cmd].keys())[0]
            print("  Timestamp:", get_time_string(cmd_time))
            print("  Command meta data:", list(dataset[cmd][cmd_time].attrs.items()))
            for rx_gain in dataset[cmd][cmd_time].keys():
                print("   RX gain:", rx_gain)
                for rx in dataset[cmd][cmd_time][rx_gain].keys():
                    print("     RX:", rx)
                    print("       Measurement items:", list(dataset[cmd][cmd_time][rx_gain][rx].keys()))
        elif cmd == 'saveiq_w_tx':
            cmd_time = list(dataset[cmd].keys())[0]
            print("  Timestamp:", get_time_string(cmd_time))
            print("  Command meta data:", list(dataset[cmd][cmd_time].attrs.items()))
            for tx in dataset[cmd][cmd_time].keys():
                #print("   TX:", tx)
                
                if tx == 'wo_tx':
                    for rx_gain in dataset[cmd][cmd_time][tx].keys():
                        #print("       RX gain:", rx_gain)
                        #print(dataset[cmd][cmd_time][tx][rx_gain].keys())
                        for rx in dataset[cmd][cmd_time][tx][rx_gain].keys():
                            #print("         RX:", rx)
                            #print("           Measurement items:", list(dataset[cmd][cmd_time][tx][rx_gain][rx].keys()))
                            
                            samplesNotx =  dataset[cmd][cmd_time][tx][rx_gain][rx]['rxsamples'][:numnoise, :]
                            namelist = rx.split('-')
                            noise[namelist[1]] = samplesNotx
                else:
                    for tx_gain in dataset[cmd][cmd_time][tx].keys():
                        #print("     TX gain:", tx_gain)
                        for rx_gain in dataset[cmd][cmd_time][tx][tx_gain].keys():
                            #print("       RX gain:", rx_gain)
                            #print(dataset[cmd][cmd_time][tx][tx_gain][rx_gain].keys())
                            for rx in dataset[cmd][cmd_time][tx][tx_gain][rx_gain].keys():
                                #print("         RX:", rx)
                                #print("         Measurement items:", list(dataset[cmd][cmd_time][tx][tx_gain][rx_gain][rx].keys()))
                                #print("         samples shape", np.shape(dataset[cmd][cmd_time][tx][tx_gain][rx_gain][rx]['rxsamples']))
                                # print("         rxloc", (dataset[cmd][cmd_time][tx][tx_gain][rx_gain][rx]['rxloc'][0]))
                                # import pdb;pdb.set_trace()
                                #repeat = np.shape(dataset[cmd][cmd_time][tx][tx_gain][rx_gain][rx]['rxsamples'])[0]
                                #print("         repeat", repeat)

                                # data check
                                rxloc.setdefault(tx, []).extend([rx]*numrx)
                                rxsamples = dataset[cmd][cmd_time][tx][tx_gain][rx_gain][rx]['rxsamples'][:numrx, :]
                                rx_data.setdefault(tx, []).append(np.array(rxsamples))

        else:                       
            print('Unsupported command: ', cmd)

    return rx_data, noise, rxloc

def get_gold_code(nbits, code_id):
    '''
    get gold code
    INPUT
    ----
        nbits: number of gold code length. The dictionary currently supports 31, 63, 127, 511 and 2047 bits
        code_id: 0
    '''
    return gold_codes_dict[nbits][code_id]#.astype(np.complex64)

def SRRC(alpha, SPS, span):
    '''
    Square-root raised cosine (SRRC) filter design
    INPUT
    ----
        alpha: roll-off factor between 0 and 1.
                it indicates how quickly its frequency content transitions from its max to zero.
        SPS:   samples per symbol = sampling rate / symbol rate
        span:  the number of symbols in the filter to the left and right of the center tap.
                the SRRC filter will have 2*span + 1 symbols in the impulse response.
    OUTPUT
    ----
    SRRC filter taps
    '''
    if ((int(SPS) - SPS) > 1e-10):
        SPS = int(SPS)
    if ((int(span) - span) > 1e-10):
        span = int(span)
    if (alpha < 0):
       raise ValueError('SRRC design: alpha must be between 0 and 1')
    if (SPS <= 1):
        raise ValueError('SRRC design: SPS must be greater than 1')

    n = np.arange(-SPS*span, SPS*span+1)+1e-9

    weights = (1/np.sqrt(SPS))*( (np.sin(np.pi*n*(1-alpha)/SPS)) + \
              (4*alpha*n/SPS)*(np.cos(np.pi*n*(1+alpha)/SPS)) ) /\
              ( (np.pi*n/SPS) * (1 - (4*alpha*n/SPS)**2) )

    return weights

def calcDistLatLong(coord1, coord2):
    '''
    Calculate distance between two nodes using lat/lon coordinates
    INPUT: coordinates, coord1, coord2
    OUTPUT: distance between the coordinates
    '''
    
    R = 6373000.0 # approximate radius of earth in meters

    lat1 = math.radians(coord1[0])
    lon1 = math.radians(coord1[1])
    lat2 = math.radians(coord2[0])
    lon2 = math.radians(coord2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a    = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    dist = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return dist

def get_time_string(timestamp):
    '''
    Helper function to get data and time from timestamp
    INPUT: timestamp
    OUTPUT: data and time. Example: 01-04-2023, 19:50:27
    '''
    date_time = datetime.datetime.fromtimestamp(int(timestamp))
    return date_time.strftime("%m-%d-%Y, %H:%M:%S")

def JsonLoad(folder):
    '''
    Load parameters from the saved json file
    INPUT
    ----
        folder: path to the measurement folder. Example: "SHOUT/Results/Shout_meas_01-04-2023_18-50-26"
    OUTPUT
    ----
        samps_per_chip: samples per chip
        wotxrepeat: number of repeating IQ sample collection w/o transmission. Used as an input to traverse_dataset() func
        rxrate: sampling rate at the receiver side
        note: user can return more parameters
    '''
    config_file = folder+'/save_iq_w_tx_gold.json'
    config_dict = json.load(open(config_file))[0]
    nsamps = config_dict['nsamps']
    sync = config_dict['sync']
    rxrate = config_dict['rxrate']
    rxfreq = config_dict['rxfreq']
    gold_id = config_dict['gold_id']
    wotxrepeat = config_dict['wotxrepeat']
    gold_length = config_dict['gold_length']
    if 'samps_per_chip' not in config_dict:
        samps_per_chip = 2
    else:
        samps_per_chip = config_dict['samps_per_chip']
    gold_code = get_gold_code(gold_length, gold_id) * 2 - 1
    long_gold_code = np.repeat(gold_code, samps_per_chip)
    rxrepeat = config_dict['rxrepeat']

    return long_gold_code, rxrepeat, wotxrepeat, samps_per_chip, rxrate, sync

def clock_sync(samples, sps, interpo_factor=16):
    '''
    source: 
    '''
    # Input Sample Interpolation for shifting them by a fraction of a sample
    samples_interpolated = signal.resample_poly(samples, interpo_factor, 1) # we'll use 32 as the interpolation factor, arbitrarily chosen, seems to work better than 16
    mu = 0.01 # initial estimate of phase of sample
    out = np.zeros(len(samples) + 10, dtype=np.complex64)
    out_rail = np.zeros(len(samples) + 10, dtype=np.complex64) # stores values, each iteration we need the previous 2 values plus current value
    i_in = 0 # input samples index
    i_out = 2 # output index (let first two outputs be 0)
    while i_out < len(samples) and i_in+interpo_factor < len(samples):
        out[i_out] = samples_interpolated[i_in*interpo_factor + int(mu*interpo_factor)] # grab what we think is the "best" sample
        out_rail[i_out] = int(np.real(out[i_out]) > 0) + 1j*int(np.imag(out[i_out]) > 0)
        x = (out_rail[i_out] - out_rail[i_out-2]) * np.conj(out[i_out-1])
        y = (out[i_out] - out[i_out-2]) * np.conj(out_rail[i_out-1])
        mm_val = np.real(y - x)
        mu += sps + 0.01*mm_val
        i_in += int(np.floor(mu)) # round down to nearest int since we are using it as an index
        mu = mu - np.floor(mu) # remove the integer part of mu
        i_out += 1 # increment output index
    x = out[2:i_out] # remove the first two, and anything after i_out (that was never filled out)
    
    return samples

def DD_carrier_sync(z, M, BnTs, zeta=0.707, mod_type = 'MPSK', type = 0, open_loop = False):
    """
    source:  https://scikit-dsp-comm.readthedocs.io/en/latest/synchronization.html
    z_prime,a_hat,e_phi = DD_carrier_sync(z,M,BnTs,zeta=0.707,type=0)
    Decision directed carrier phase tracking
    
    INPUT
    ----    
        z = complex baseband PSK signal at one sample per symbol
        M = The PSK modulation order, i.e., 2, 8, or 8.
        BnTs = time bandwidth product of loop bandwidth and the symbol period,
               thus the loop bandwidth as a fraction of the symbol rate.
        zeta = loop damping factor
        type = Phase error detector type: 0 <> ML, 1 <> heuristic
    
    OUTPUT
    ----
        z_prime = phase rotation output (like soft symbol values)
        a_hat = the hard decision symbol values landing at the constellation
               values
        e_phi = the phase error e(k) into the loop filter

        Ns = Nominal number of samples per symbol (Ts/T) in the carrier 
            phase tracking loop, almost always 1
        Kp = The phase detector gain in the carrier phase tracking loop; 
            This value depends upon the algorithm type. For the ML scheme
            described at the end of notes Chapter 9, A = 1, K 1/sqrt(2),
            so Kp = sqrt(2).
    
    Mark Wickert July 2014
    Updated for improved MPSK performance April 2020
    Added experimental MQAM capability April 2020

    Motivated by code found in M. Rice, Digital Communications A Discrete-Time 
    Approach, Prentice Hall, New Jersey, 2009. (ISBN 978-0-13-030497-1).
    """
    Ns = 1
    z_prime = np.zeros_like(z)
    a_hat = np.zeros_like(z)
    e_phi = np.zeros(len(z))
    theta_h = np.zeros(len(z))
    theta_hat = 0

    # Tracking loop constants
    Kp = 1 # What is it for the different schemes and modes?
    K0 = 1 
    K1 = 4*zeta/(zeta + 1/(4*zeta))*BnTs/Ns/Kp/K0 # C.46 in the rice book
    K2 = 4/(zeta + 1/(4*zeta))**2*(BnTs/Ns)**2/Kp/K0
    
    # Initial condition
    vi = 0
    # Scaling for MQAM using signal power
    # and known relationship for QAM.
    if mod_type == 'MQAM':
        z_scale = np.std(z) * np.sqrt(3/(2*(M-1)))
        z = z/z_scale
    for nn in range(len(z)):
        # Multiply by the phase estimate exp(-j*theta_hat[n])
        z_prime[nn] = z[nn]*np.exp(-1j*theta_hat)
        if mod_type == 'MPSK':
            if M == 2:
                a_hat[nn] = np.sign(z_prime[nn].real) + 1j*0
            elif M == 4:
                a_hat[nn] = (np.sign(z_prime[nn].real) + \
                             1j*np.sign(z_prime[nn].imag))/np.sqrt(2)
            elif M > 4:
                # round to the nearest integer and fold to nonnegative
                # integers; detection into M-levels with thresholds at mid points.
                a_hat[nn] = np.mod((np.rint(np.angle(z_prime[nn])*M/2/np.pi)).astype(np.int),M)
                a_hat[nn] = np.exp(1j*2*np.pi*a_hat[nn]/M)
            else:
                print('M must be 2, 4, 8, etc.')
        elif mod_type == 'MQAM':
            # Scale adaptively assuming var(x_hat) is proportional to 
            if M ==2 or M == 4 or M == 16 or M == 64 or M == 256:
                x_m = np.sqrt(M)-1
                if M == 2: x_m = 1
                # Shift to quadrant one for hard decisions 
                a_hat_shift = (z_prime[nn] + x_m*(1+1j))/2
                # Soft IQ symbol values are converted to hard symbol decisions
                a_hat_shiftI = np.int16(np.clip(np.rint(a_hat_shift.real),0,x_m))
                a_hat_shiftQ = np.int16(np.clip(np.rint(a_hat_shift.imag),0,x_m))
                # Shift back to antipodal QAM
                a_hat[nn] = 2*(a_hat_shiftI + 1j*a_hat_shiftQ) - x_m*(1+1j)
            else:
                print('M must be 2, 4, 16, 64, or 256');
        if type == 0:
            # Maximum likelihood (ML) Rice
            e_phi[nn] = z_prime[nn].imag * a_hat[nn].real - \
                        z_prime[nn].real * a_hat[nn].imag
        elif type == 1:
            # Heuristic Rice
            e_phi[nn] = np.angle(z_prime[nn]) - np.angle(a_hat[nn])
            # Wrap the phase to [-pi,pi]  
            e_phi[nn] = np.angle(np.exp(1j*e_phi[nn]))
        elif type == 2:
            # Ouyang and Wang 2002 MQAM paper
            e_phi[nn] = imag(z_prime[nn]/a_hat[nn])
        else:
            print('Type must be 0 or 1')
        vp = K1*e_phi[nn]      # proportional component of loop filter
        vi = vi + K2*e_phi[nn] # integrator component of loop filter
        v = vp + vi        # loop filter output
        theta_hat = np.mod(theta_hat + v,2*np.pi)
        theta_h[nn] = theta_hat # phase track output array
        if open_loop:
            theta_hat = 0 # for open-loop testing
    
    # Normalize MQAM outputs
    if mod_type == 'MQAM': 
        z_prime *= z_scale
    return z_prime, a_hat, e_phi, theta_h

def Freq_Offset_Correction(samples, fs, order=2, debug=False):
    '''
    Coarse frequency offset correction
    INPUT
    ----
        samples: samples after matched filtering
        fs: sampling rate at the RX
        order: 2 for BPSK and 4 for QPSK
        debug: flag for plotting power spectral density for debugging
    OUTPUT
    ----
        corrsamp: samples after freq synchronization
    '''
    psd = np.fft.fftshift(np.abs(np.fft.fft(samples**order)))
    f = np.linspace(-fs/2.0, fs/2.0, len(psd))

    max_freq = f[np.argmax(psd)]
    Ts = 1/fs # calc sample period
    t = np.arange(0, Ts*len(samples), Ts) # create time vector
    corrsamp = samples * np.exp(-1j*2*np.pi*max_freq*t/2.0)
    
    if debug:
        print('offset estimate: {} KHz'.format(max_freq/2000) )
        plt.figure()
        plt.plot(f, psd, label='before correction')
        plt.plot(f, np.fft.fftshift(np.abs(np.fft.fft(corrsamp**2))), label='after correction')
        plt.legend()
        plt.show()

    return corrsamp

def CostasLoop(samples, fs, order=2, debug=False):
    '''
    Frequency synchronization based on Costas loop
    '''
    # For QPSK
    def phase_detector(sample, order):
        if order==4:
            if sample.real > 0:
                a = 1.0
            else:
                a = -1.0
            if sample.imag > 0:
                b = 1.0
            else:
                b = -1.0
            return a * sample.imag - b * sample.real
        elif order==2:
            # This is the error formula for 2nd order Costas Loop (e.g. for BPSK)
            return np.real(sample) * np.imag(sample) 

    N = len(samples)
    phase = 0
    freq = 0
    # These next two params is what to adjust, to make the feedback loop faster or slower (which impacts stability)
    alpha = 4.9e-5 
    beta = 0.08
    out = np.zeros(N, dtype=np.complex64)
    freq_log = []
    for i in range(N):
        out[i] = samples[i] * np.exp(-1j*phase) # adjust the input sample by the inverse of the estimated phase offset
        error = phase_detector(out[i], order)

        # Advance the loop (recalc phase and freq offset)
        freq += (beta * error)
        freq_log.append(freq * fs / (2*np.pi)) # convert from angular velocity to Hz for logging
        phase += freq + (alpha * error)

        # Optional: Adjust phase so its always between 0 and 2pi, recall that phase wraps around every 2pi
        while phase >= 2*np.pi:
            phase -= 2*np.pi
        while phase < 0:
            phase += 2*np.pi

    if debug:
        # Plot freq over time to see how long it takes to hit the right offset
        plt.figure()
        plt.plot(freq_log,'.-')
        plt.title('Fine Frequency Synchronization Using a Costas Loop')
        plt.show()
        
    return out

def phase_correct_freq_drift(samps, peak_locs, long_gold_code, bitsring, angle_mod=-np.pi):
    """
    author: Frost Mitchell 
    Correct frequency offset between signals, with phase correction of angle_mod
    """
    def phase_apply_shift(samps, base=0, shift=0):
        return samps * np.power(np.e, -1j*(base + shift*np.arange(len(samps))))
    peak_locs = peak_locs[1:-1]
    peaks = samps[peak_locs]
    diffs = (np.diff( np.angle(peaks))  % angle_mod) / 254
    count, bins = np.histogram(diffs)
    max_bin = count.argmax()
    low, high = bins[max_bin:max_bin+2]
    good_shift = diffs[ (low < diffs) * (diffs < high)].mean()
    new_samps = phase_apply_shift(samps, 0, good_shift)
    best_shift = good_shift + np.angle((np.conjugate(new_samps[peak_locs][:-len(bitsring)])* new_samps[peak_locs][len(bitsring):]).sum()) / (len(long_gold_code)  * len(bitsring))
    new_samps = phase_apply_shift(samps, 0, best_shift)
    best_base = np.median( np.angle(new_samps[peak_locs]))
    new_samps = phase_apply_shift(samps, best_base, best_shift)
    new_peaks = new_samps[peak_locs]
    if np.median(new_peaks) < 0:
        new_samps = new_samps*-1

    new_peaklocs = signal.find_peaks(abs(new_samps.real), distance=len(long_gold_code)-4, height=[0,np.median(abs(new_peaks.real))*3])[0]
    
    return new_samps, new_peaklocs, (best_base, best_shift)

def calc_stats(corr, peak_locs, debug=False):
    '''
    Calculate stats including SINR and RSS.
    INPUT
    ----
        corr: results after correlating with gold code
        peak_locs: locations for detected peaks (peaks stand for matching with the known gold code sequence)
    OUTPUT
    ----
        SINR: signal to interference plus noise ratio
        RSS:  received signal strength
    '''
    ##### Calculate SINR #####
    peaks = corr[peak_locs]
    if len(peaks):
        noise_mask = np.ones(len(corr), dtype=bool)
        noise_mask[:peak_locs[0]] = False
        noise_mask[peak_locs[-1]:] = False
        noise_mask[peak_locs] = False
        noise = corr[noise_mask]
        SINRdB = 10.0 * np.log10( np.mean(np.abs(peaks)**2)/np.mean(np.abs(noise)**2) )

        if debug:
            plt.figure()
            plt.plot(abs(corr), '-+',label='amplitude')
            plt.plot(abs(noise), 'o',label='noise')
            plt.xlabel('Sample',fontsize=15)
            plt.ylabel('correlation',fontsize=15)
            plt.legend()
            plt.show()

        ##### Calculate Power #####
        powerdB = 10.0 * np.log10(np.mean(np.abs(peaks)**2))
    else:
        SINRdB, powerdB = 0, 0

    return SINRdB, powerdB


def plot_stats(statsdic, disdic):
    '''
    function for plotting stats
    INPUT
    ----
        statsdic: statistics dictionary indexed by TX and then RX
        disdic: distance dictionary indexed by TX and then RX
    FIGURES
    ----
        figure 1: SINR/RSSI (dB) vs. repeated runs
        figure 2: average of SINR/RSSI (dB) over repeated runs vs. distance
    '''
    fig1, axs1 = plt.subplots(1,2, sharex=True, figsize=(10,6.5)) # plot stats of repeated runs
    fig2, axs2 = plt.subplots(1,2, sharex=True, figsize=(10,6.5)) # plot stats vs. distance
    markers = ['*', 'v', '^', 'o', '1', '2', '3', '4', '.']

    alldists = []
    sinrmeans = []
    rssimeans = []
    for txloc in statsdic:
        for j, rxloc in enumerate(statsdic[txloc]):
            stats = np.array(statsdic[txloc][rxloc])
            dis = np.array(disdic[txloc][rxloc])
            meandis = np.mean(dis)
            sinr = np.mean(stats[:,0])
            rssi = np.mean(stats[:,1])
            alldists.append(meandis)
            sinrmeans.append(sinr)
            rssimeans.append(rssi)

            axs1[0].plot(stats[:,0],marker=markers[j], label=rxloc)
            axs1[1].plot(stats[:,1],marker=markers[j], label=rxloc)

            axs2[0].plot(meandis, sinr, marker='o', label=rxloc)
            axs2[1].plot(meandis, rssi, marker='o', label=rxloc)
        
        axs2[0].set_title('TX: '+txloc,fontsize=13)
        axs2[1].set_title('TX: '+txloc,fontsize=13)

        axs1[0].set_title('TX: '+txloc,fontsize=13)
        axs1[1].set_title('TX: '+txloc,fontsize=13)

    m1, b1 = np.polyfit(alldists, np.nan_to_num(sinrmeans), 1)
    #print("m1, b1: {}, {}".format(m1,b1))
    axs2[0].plot(alldists, m1*np.array(alldists) + b1, label="polyfit")
    m2, b2 = np.polyfit(alldists, np.nan_to_num(rssimeans), 1)
    #print("m2, b2: {}, {}".format(m2,b2))
    axs2[1].plot(alldists, m2*np.array(alldists) + b2, label="polyfit")
        
    axs1[0].set_ylabel('SINR (dB)',fontsize=13)
    axs1[1].set_ylabel('RSSI [dB]',fontsize=13)
    handles, labels = axs1[0].get_legend_handles_labels()
    #fig1.legend(handles, labels, loc='upper center',ncol=4, fontsize=10, bbox_to_anchor=bbox_to_anchor)
    fig1.text(0.5, 0.02, 'Repeated Run Index', va='center', ha='center', rotation='horizontal', fontsize=13)
    

    axs2[0].set_ylabel('SINR (dB), pfslope = %f' % m1,fontsize=13)
    axs2[1].set_ylabel('RSSI (dB), pfslope = %f' % m2,fontsize=13)
    handles, labels = axs2[0].get_legend_handles_labels()
    #fig2.legend(handles, labels, loc='upper center',ncol=4, fontsize=10, bbox_to_anchor=bbox_to_anchor)
    fig2.text(0.5, 0.02, 'Distance (m)', va='center', ha='center', rotation='horizontal', fontsize=13)
    # plt.tight_layout()
    #plt.show()

# main
def main(folder, method='peak_find'):
    '''
    main function for loading and processing the data
    INPUT
    ----
        folder: path to the measurement folder. Example: "SHOUT/Results/Shout_meas_01-04-2023_18-50-26"
        method: method used to detect peaks as gold code matching.
    FIGURES
    ----
        figure 1: correlation amplitude vs. sample index for all the RXs and one TX. Peaks are marked in orange dots
        figure 2: correlation (real and imaginary) vs. sample index for all the RXs and one TX. Peaks are marked in orange dots
    '''
    # load the gold code
    goldcode, Rxrepeat, Wotxrepeat, samps_per_chip, samp_rate, sync = JsonLoad(folder)

    # load the data
    rx_data, _, txrxloc = traverse_dataset(folder, Rxrepeat, Wotxrepeat)

    # going through each transmitter-receiver pair
    stats, dis = {}, {}

    # going through each transmitter
    for txloc in rx_data:
        #if txloc != 'cbrssdr1-ustar-comp':continue
        #print('\n\n\nTX: {}'.format(txloc))
        rx_data[txloc] = np.vstack(rx_data[txloc])
        #print('[Debug] data', np.shape(rx_data[txloc]))

        stats[txloc] = {}
        dis[txloc] = {}
        
        # plot correlation
        fig1, axes1 = plt.subplots(int(np.ceil(len(txrxloc[txloc])/(3*Rxrepeat))),3,sharex=True,sharey=True, figsize=(15,10))
        #fig2, axes2 = plt.subplots(int(np.ceil(len(txrxloc[txloc])/(3*Rxrepeat))),3,sharex=True,sharey=True, figsize=(15,10))
        axes1 = axes1.flatten()
        #axes2 = axes2.flatten()
        axind = 0

        lastrxloc = ""
        run = 0
        for j, rxloc in enumerate(txrxloc[txloc]):
            # if rxloc != 'cbrssdr1-ustar-comp':continue
            if rxloc == lastrxloc:
                run += 1
            else:
                run = 1
            lastrxloc = rxloc
            print('Processing TX: {}, RX: {}, Run: {}'.format(txloc, rxloc, run))

            namelist = (rxloc.split('-'))
            TXnamelist = (txloc.split('-'))
            distance = calcDistLatLong(GPS_LOCATIONS[txloc], GPS_LOCATIONS[rxloc])

            # matched filtering
            pulse = SRRC(0.5, samps_per_chip, 5)
            MFsamp = signal.lfilter(pulse, 1, rx_data[txloc][j,:].real) + 1j* \
                     signal.lfilter(pulse, 1, rx_data[txloc][j,:].imag)
            # Coarse Frequency Offset Sync
            FreqsyncSamp = Freq_Offset_Correction(MFsamp, samp_rate, order=2, debug=False)
            # Clock Synchronization
            if not sync:
                FreqsyncSamp = clock_sync(FreqsyncSamp, samp_rate, interpo_factor=16)
            # Fine Freq Synchronization
            # FreqsyncSamp1 = CostasLoop(SymsyncSamp, samp_rate, debug=False)
            FreqsyncSamp1, _, _, _ = DD_carrier_sync(FreqsyncSamp, 2, 0.02, zeta=0.707)
            
            # Despread with gold code
            correlation = signal.correlate(FreqsyncSamp1, goldcode)[len(goldcode)//2-1:-(len(goldcode)//2)]

            if method=='peak_find':
                # Symbol Samples: method 1
                corr_abs = abs(correlation)
                hmin = (np.mean(corr_abs)+corr_abs.max())/2
                idx = signal.find_peaks(corr_abs, distance=len(goldcode)-4, height=hmin)[0] 
                
                # # avoid interference via peak value upper bound
                # nbits = len(simple_bits)
                # if len(idx)<nbits:
                #     hmax = np.mean(corr_abs) + 3*np.std(corr_abs)
                #     idx = signal.find_peaks(corr_abs, distance=len(goldcode)-4, height=[hmin,hmax])[0]
                yhat = correlation[idx]
            elif method=='simple':
                # Symbol Samples: method 2
                corr_abs = abs(correlation)
                ind = np.argmax(corr_abs[:int(len(goldcode)*1.5)])
                idx = np.arange(len(corr_abs))[ind::len(goldcode)]
                yhat = correlation[idx]
            else:
                # Despread with gold code
                correlation = signal.correlate(MFsamp, goldcode)[len(goldcode)//2-1:-(len(goldcode)//2)]
                print('len(correlation)', len(correlation))

                corr_abs = abs(correlation)
                peak_locs = signal.find_peaks(corr_abs, distance=len(goldcode)-4)[0]
                new_corr, new_peak_locs, _ = phase_correct_freq_drift(correlation, peak_locs, goldcode, simple_bits, angle_mod=-np.pi)
                if abs(((np.sign(new_corr[new_peak_locs].real)+1)/2).mean() - 0.7) > 0.05:
                    new_corr, idx, _ = phase_correct_freq_drift(correlation, peak_locs, goldcode, simple_bits, angle_mod=np.pi)
                yhat = new_corr[idx]

            # correlation plotting
            if axind == j//Rxrepeat:
                if method=='peak_find' or method=='simple':
                    axes1[axind].plot(abs(correlation), '-+',label='amplitude',alpha=0.7)
                else:
                    axes1[axind].plot(abs(new_corr), '-+',label='amplitude',alpha=0.7)
                if method=='peak_find':
                    axes1[axind].axhline(hmin,color='k', label='Minimal peak height',alpha=0.7)
                    axes1[axind].plot(idx, abs(yhat), 'o', label='DSSS peaks',alpha=0.7)
                elif method=='simple':
                    axes1[axind].plot(np.arange(len(yhat))*len(goldcode)+ind, abs(yhat), 'o', label='DSSS peaks',alpha=0.7)
                else:
                    axes1[axind].plot(idx, abs(yhat), 'o', label='DSSS peaks',alpha=0.7)

                axes1[axind].set_ylabel('Correlation',fontsize=13)
                axes1[axind].set_title('TX: {} RX: {} (dist: {:.2f})'.format(TXnamelist[1], namelist[1], distance),fontsize=11)

                #axes2[axind].plot(correlation.real, '-o',label='real',alpha=0.7)
                #axes2[axind].plot(correlation.imag, '-+',label='imaginary',alpha=0.7)
                #if method=='simple':
                #    axes2[axind].plot(np.arange(len(yhat))*len(goldcode)+ind, yhat.real, 'o', label='DSSS peaks',alpha=0.7)
                #else:
                #    axes2[axind].plot(idx, (yhat).real, 'o', label='DSSS peaks',alpha=0.7)

                #axes2[axind].set_ylabel('Correlation',fontsize=13)
                #axes2[axind].set_title('TX: {} RX: {} (dist: {:.2f}m)'.format(TXnamelist[1], namelist[1], distance),fontsize=11)

                axind += 1

            # symbol decisions
            bitsout = (yhat.real>0).astype(int) 
            #print('\noriginal string is:    ', len(simple_bits), simple_bits)
            #print('demodulated string is: ', len(bitsout), bitsout)

            # STATS: SINR, RSS and BER
            SINR, power = calc_stats(correlation, idx)
            
            txbits = np.tile(simple_bits, int(len(bitsout)//len(simple_bits)+1))[:len(bitsout)]
            if len(yhat):
                BER = sum(bitsout!=txbits)/len(bitsout)
                #print('BER', BER)
            
            # stats saving
            stats[txloc].setdefault(rxloc, []).append([SINR, power])
            dis[txloc].setdefault(rxloc, []).append(distance)

        # correlation plotting: labels 
        handles, labels = axes1[0].get_legend_handles_labels()
        fig1.legend(handles, labels, loc='upper center',ncol=3, fontsize=12, bbox_to_anchor=bbox_to_anchor)
        fig1.text(0.5, 0.02, 'Sample Index', va='center', ha='center', rotation='horizontal', fontsize=13)
        # fig1.tight_layout()

        #handles, labels = axes2[0].get_legend_handles_labels()
        #fig2.legend(handles, labels, loc='upper center',ncol=3, fontsize=12, bbox_to_anchor=bbox_to_anchor)
        #fig2.text(0.5, 0.02, 'Sample Index', va='center', ha='center', rotation='horizontal', fontsize=13)
        # fig2.tight_layout()
        # plt.show()
        
    #### stats plotting ####
    print("Plotting figures...")

    # Dumping data into a json file
    with open("measurements.json", "w") as fp:
        json.dump(stats,fp)

    plot_stats(stats, dis)
    plt.show()

def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--datadir", type=str, default=DEF_DATADIR, help="The directory where the data file resides. Default: %s" % DEF_DATADIR)
    parser.add_argument("-f", "--dfname", type=str, default=DEF_DFNAME, help="The name of one measurement file. Default: %s" % DEF_DFNAME)
    return parser.parse_args()

if __name__=="__main__":
    '''
    Example measurements
    ----
        ../examples/measurements/Shout_meas_01-05-2023_10-45-52
        ../examples/measurements/Shout_meas_01-06-2023_08-08-31
    '''
    args = parse_args()
    folder = args.datadir+args.dfname
    main(folder, method='peak_find')
