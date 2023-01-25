#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

#
# Measurement client/server RPC call definitions
#
import measurements_pb2 as measpb
from common import get_attr, add_attr

RPCCALLS = {}

class RPCCall:
    def __init__(self, funcname, funcargs = {}):
        self.funcname = funcname
        self.funcargs = funcargs

    def encode(self, **kwargs):
        cmsg = measpb.SessionMsg()
        cmsg.type = measpb.SessionMsg.CALL
        add_attr(cmsg, 'funcname', self.funcname)
        for aname,adict in self.funcargs.items():
            if aname in kwargs:
                add_attr(cmsg, aname, kwargs[aname])
        return cmsg

    def decode(self, cmsg):
        argdict = {}
        argdict['start_time'] = cmsg.start_time
        cattrs = {kv.key: kv.val for kv in cmsg.attributes}
        for aname,adict in self.funcargs.items():
            if aname in cattrs:
                if adict['type'] == bool:
                    argdict[aname] = True if cattrs[aname] == 'True' else False
                else:
                    argdict[aname] = adict['type'](cattrs[aname])
            else:
                argdict[aname] = adict['default']
        return argdict

    
RPCCALLS['txsine'] = \
    RPCCall('txsine',
            {
                'duration':  {'type': int, 'default': 0},
                'freq':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 30.0},
                'rate':      {'type': float, 'default': 1e6},
                'wfreq':     {'type': float, 'default': 1e5},
                'wampl':     {'type': float, 'default': 0.3},
            })

RPCCALLS['rxsamples'] = \
    RPCCall('rxsamples',
            {
                'nsamps':    {'type': int, 'default': 256},
                'freq':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 30.0},
                'rate':      {'type': float, 'default': 1e6},
            })

RPCCALLS['txsamples'] = \
    RPCCall('txsamples',
            {
                'freq':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 30.0},
                'rate':      {'type': float, 'default': 1e6},
            })

RPCCALLS['tune'] = \
    RPCCall('tune',
            {
                'freq':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 30.0},
                'rate':      {'type': float, 'default': 1e6},
            })

RPCCALLS['measure_power'] = \
    RPCCall('measure_power',
            {
                'nsamps':    {'type': int, 'default': 256},
                'get_samples': {'type': bool, 'default': False},
                'filter_bw': {'type': float, 'default': 1e4},
                'freq':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 30.0},
                'rate':      {'type': float, 'default': 1e6},
                'wfreq':     {'type': float, 'default': 1e5},
            })

RPCCALLS['seq_rxsamples'] = \
    RPCCall('seq_rxsamples',
            {
                'nsamps':    {'type': int, 'default': 256},
                'freq':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 30.0},
                'rate':      {'type': float, 'default': 1e6},
                'freq_step': {'type': float, 'default': 5e4},
                'time_step': {'type': float, 'default': 1},
            })

RPCCALLS['seq_sine'] = \
    RPCCall('seq_sine',
            {
                'freq':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 30.0},
                'rate':      {'type': float, 'default': 1e6},
                'wampl':     {'type': float, 'default': 0.3},
                'freq_step': {'type': float, 'default': 5e4},
                'time_step': {'type': float, 'default': 1},
            })

RPCCALLS['seq_measure'] = \
    RPCCall('seq_measure',
            {
                'nsamps':    {'type': int, 'default': 256},
                'get_samples': {'type': bool, 'default': False},
                'filter_bw': {'type': float, 'default': 1e4},
                'freq':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 30.0},
                'rate':      {'type': float, 'default': 1e6},
                'freq_step': {'type': float, 'default': 5e4},
                'time_step': {'type': float, 'default': 1},
            })

RPCCALLS['txiq'] = \
    RPCCall('txiq',
            {
                'nsamps':     {'type': int, 'default': 1024},
                'freq':       {'type': float, 'default': None},
                'rate':       {'type': float, 'default': None},
                'gain':       {'type': float, 'default': 30.0},
                'bw':         {'type': float, 'default': None},
                'sync':       {'type': bool, 'default': True},
                'txfile':     {'type': str, 'default': None},
                'sine_wfreq': {'type': float, 'default': None},
                'sine_wampl': {'type': float, 'default': None},
                'duration':  {'type': int, 'default': 0},
                'use_lo_offset':{'type': bool, 'default': False},
                'use_pulse_shaping':{'type': bool, 'default': True},
                'gold_id':     {'type': int, 'default': -1},
                'gold_length':     {'type': int, 'default': 63},
                'samps_per_chip':     {'type': int, 'default': 2},
                'return_stats':{'type': bool, 'default': False}, #If True, a gold_code function
                'nsymbols':    {'type': int, 'default': 32},
            })

RPCCALLS['rxiq'] = \
    RPCCall('rxiq',
            {
                'nsamps':    {'type': int, 'default': 1024},
                'freq':      {'type': float, 'default': None},
                'rate':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 50.0},
                'sync':      {'type': bool, 'default': True},
                'bw':        {'type': float, 'default': None},
                'use_lo_offset':{'type': bool, 'default': False},
                'filter_bw': {'type': float, 'default': 0},
                'wfreq':     {'type': float, 'default': 1e5},
                'use_lo_offset':{'type': bool, 'default': False},
                'use_pulse_shaping':{'type': bool, 'default': True},
                'gold_length':{'type': int, 'default': 63},
                'gold_id':{'type': int, 'default': -1},
                'samps_per_chip':{'type': int, 'default': 2},
                'return_iq':{'type': bool, 'default': False}, #If True, a gold_code function
                'return_stats':{'type': bool, 'default': False}, #If True, a gold_code function
                'nsymbols':    {'type': int, 'default': 0},
                'on_client_repeat':    {'type': int, 'default': 1},
            })
RPCCALLS['rxrssi'] = \
    RPCCall('rxrssi',
            {
                'nsamps':    {'type': int, 'default': 1024},
                'freq':      {'type': float, 'default': None},
                'rate':      {'type': float, 'default': None},
                'gain':      {'type': float, 'default': 50.0},
                'sync':      {'type': bool, 'default': True},
                'bw':        {'type': float, 'default': None},
                'filter_bw': {'type': float, 'default': 0},
                'wfreq':     {'type': float, 'default': 1e5},
                'use_lo_offset':{'type': bool, 'default': False},
                'on_client_repeat':    {'type': int, 'default': 1},
            })

RPCCALLS['exit'] = RPCCall('exit', {})
