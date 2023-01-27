#!/usr/bin/env python3


import scipy.signal as sig
import numpy as np
import argparse
import logging
import time
import json
import socket
import multiprocessing as mp

from utils import Radio, GoldUtil

DEF_LOGFILE="/var/tmp/ccontroller.log"
LOGFMAT = '%(asctime)s:%(levelname)s: %(message)s'
LOGDATEFMAT = '%Y-%m-%d %H:%M:%S'
LOGLEVEL = logging.DEBUG


class TX_TASK():
    TIMEZONE = 'US/Mountain'
    DEF_TOFF = 5
    
    def __init__(self,args):
        self.GoldCls = GoldUtil()
        self.start_time = 0

        self._setup_logger(args.logfile)
        #To-do: check this
        if args.usetxrx:
            usetxrx = True
        else:
            usetxrx = False
        

        if 'txnode' in args and args['txnode']:
            self.txname = args['txnode']
        else:
            self.txname = socket.gethostname().split('.',1)[0]

        if "cbrs" in  self.txname or "cell" in  self.txname or args.useexternalclock:
            useexternalclock = True
        else:
            useexternalclock = False
        self.radio = Radio(args.args, usetxrx, useexternalclock)

    def _tune_radio(self, args):
        self.radio.tune(args['txfreq'], args['txgain'], args['txrate'], args['use_lo_offset'])
    
    def _setup_logger(self, logfile):
        fmat = logging.Formatter(fmt=LOGFMAT, datefmt=LOGDATEFMAT)
        shandler = logging.StreamHandler()
        shandler.setFormatter(fmat)
        fhandler = logging.FileHandler(logfile)
        fhandler.setFormatter(fmat)
        self.logger = mp.get_logger()
        self.logger.setLevel(LOGLEVEL)
        self.logger.addHandler(shandler)
        self.logger.addHandler(fhandler)
    
    def _get_samps_frm_file(self, filename): 
        '''
        load samples from the binary file
        '''
        # File should be in GNURadio's format, i.e., interleaved I/Q samples as float32
        samples = np.fromfile(filename, dtype=np.float32)
        samps = (samples[::2] + 1j*samples[1::2]).astype((np.complex64))
            
        return samps

    def _do_xmit_samps(self, args):
            """
            Transmit samples, from one of several sample sources:

            args['txfile']:  transmit samples from the specified file (see singal_library/)
            BPSK-DSSS modulated samples
            """

            self._tune_radio(args)		

            if 'txfile' in args and args['txfile']:
                samples = self._get_samps_frm_file(args['txfile'])
                self.logger.debug("Transmitting from " + args['txfile'])
            else:
                tx_rate = args['txrate']
                gold_length = args['gold_length'] # spread factor / process gain
                samps_per_chip = args['samps_per_chip'] 
                chip_rate = tx_rate / samps_per_chip
                symbol_rate = chip_rate  / gold_length

                # Currently lookup, should switch to generation function (or precompute codes)
                gold_code = self.GoldCls.get_gold_code(int(gold_length))
                # up sampling
                long_gold_code = np.zeros(len(gold_code)*samps_per_chip)
                long_gold_code[::samps_per_chip] = gold_code * 2 - 1
                
                # Samples are BPSK-DSSS modulated IQ values
                if 0 in self.GoldCls.simple_bits:
                    # BPSK modulation
                    symbols = (self.GoldCls.simple_bits * 2 - 1) 
                # DSSS spreading
                repeated_gold_code = np.tile(long_gold_code, len(symbols))
                samples = repeated_gold_code * np.repeat(symbols, len(long_gold_code))
                
                # SRRC pulse shape filter
                pulse = self.GoldCls.SRRC(0.5, samps_per_chip, 5)
                samples = np.convolve(samples, pulse, mode='same')[np.newaxis, :]
            
            duration = args['txtimeout'] if 'txtimeout' in args and args['txtimeout'] else 30
            self.radio.xmit_samples(samples, duration)
            

    def _clear_start_time(self):
        self.start_time = 0

    def _set_start_time(self, toff = DEF_TOFF):
        self.start_time = np.ceil(time.time()) + toff
    
    def run(self, cmdfile):
        self.radio.init_radio()

        # Read in and execute commands
        with open(cmdfile) as cfile:
            commands = json.load(cfile)
        cmd = commands[0]

        cmd['timezone'] = self.TIMEZONE
        if 'sync' in cmd and cmd['sync']:
            if 'toff' in cmd:
                self._set_start_time(cmd['toff'])
            elif not self.start_time:
                self._set_start_time()
            cmd['start_time'] = self.start_time
        else:
            self._clear_start_time()

        self.logger.info("Starting TX...")
        self._do_xmit_samps(cmd)
        self.logger.info('TX done!')

        return

def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--args", help="USRP radio arguments", default="", type=str)
    parser.add_argument("-c", "--cmdfile", help="JSON command file to execute", type=str, required=True)
    parser.add_argument("-l", "--logfile", type=str, default=DEF_LOGFILE)
    parser.add_argument("-t", "--usetxrx", help="Receive using the TX/RX port", action="store_true")
    parser.add_argument("-u", "--useexternalclock", help="Use external clock", action="store_true")
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    oneend = TX_TASK(args)
    oneend.run(args.cmdfile)
