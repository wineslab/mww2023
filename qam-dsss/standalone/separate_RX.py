#!/usr/bin/env python3

import sys
import scipy.signal as sig
import numpy as np
import argparse
import logging
import time
import json
import socket
import multiprocessing as mp
import matplotlib.pyplot as plt

from utils import Radio, GoldUtil

DEF_LOGFILE="/var/tmp/ccontroller.log"
LOGFMAT = '%(asctime)s:%(levelname)s: %(message)s'
LOGDATEFMAT = '%Y-%m-%d %H:%M:%S'
LOGLEVEL = logging.DEBUG

# for RX
DATA_OUTDIR="/local/data/" 
DATA_FILE_NAME="measurements.hdf5" 


class TX_TASK():
    TIMEZONE = 'US/Mountain'
    DEF_TOFF = 5
    TOFF = 0.5
    SAMPLEOFF = 1024 # First couple of samples are misleading
    
    def __init__(self,args):
        self.GoldCls = GoldUtil()
        self.start_time = 0
        self.args = args
        self._setup_logger(args.logfile)
        #To-do: check this
        if args.usetxrx:
            usetxrx = True
        else:
            usetxrx = False
        
        if 'txnode' in args and args['txnode']:
            self.txname = args['txnode']
        else:
            self.txname = socket.gethostname().split('.',1)

        if "cbrs" in  self.txname or "cell" in  self.txname or args.useexternalclock:
            useexternalclock = True
        else:
            useexternalclock = False
        self.radio = Radio(args.args, usetxrx, useexternalclock)

    def _tune_radio(self, args):
        self.radio.tune(args['rxfreq'], args['rxgain'], args['rxrate'], args['use_lo_offset'])
    
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
    
    def _get_samps_frm_file(self, filename): # File should be in GNURadio's format, i.e., interleaved I/Q samples as float32
        data = np.fromfile(filename, dtype=np.float32)
        n = len(data)
        nsamps = n//2
        samps = np.zeros((1,nsamps), np.complex64)
        j = 0 
        for i in range(nsamps):
            samps[0][i] = data[j] + 1j*data[j+1]
            j = (j+2)%n
            
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
                gold_code = self.GoldCls.get_gold_code(gold_length)  * 2 - 1
                # up sampling
                long_gold_code = np.zeros(len(gold_code)*samps_per_chip)
                long_gold_code[::samps_per_chip] = gold_code
                
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
            self.logger.info('TX done!')

    def _recv_samps(self, args):
        samps, dt = self.radio.recv_samples(args['nsamps'], args['start_time'] if 'start_time' in args else None)
        return samps[0], dt

    def _do_recv_gold_codes(self, args):
        """
        Collect raw IQ samples or demodulated signal from a transmitted gold_code, optionally 
        calculating stats such as SNR, BER, and signal power.
        """
        # Set RX params
        tx_rate = args['rxrate']
        gold_length = args['gold_length'] # spread factor / process gain
        samps_per_chip = args['samps_per_chip'] 
        chip_rate = tx_rate / samps_per_chip
        symbol_rate = chip_rate  / gold_length

        args['nsamps'] = args['nsamps'] + self.SAMPLEOFF
        self._tune_radio(args)
        
        samps, _ = self._recv_samps(args)
        samps = samps[self.SAMPLEOFF:]

        gold_code = self.GoldCls.get_gold_code(gold_length)  * 2 - 1
        long_gold_code = np.repeat(gold_code, samps_per_chip)

        # matched filtering
        pulse = self.GoldCls.SRRC(0.5, samps_per_chip, 5)
        MFsamps = sig.lfilter(pulse, 1, samps.real) + 1j* \
                    sig.lfilter(pulse, 1, samps.imag)
        # Coarse Frequency Offset Sync
        FreqsyncSamp = self.GoldCls.Freq_Offset_Correction(MFsamps, tx_rate, order=2, debug=False)
        # Clock Synchronization
        if 'sync' in args and not args['sync']:
            FreqsyncSamp = self.GoldCls.clock_sync(FreqsyncSamp, tx_rate, interpo_factor=16)
        # Fine Freq Synchronization
        FreqsyncSamp1, _, _, _ = self.GoldCls.DD_carrier_sync(FreqsyncSamp, 2, 0.01)
        # Despreading with gold code
        correlation = sig.correlate(FreqsyncSamp1, long_gold_code)[len(long_gold_code)//2-1:-(len(long_gold_code)//2)]

        if args['method']=='peak_find':
            # Symbol Samples: method 1
            corr_abs = abs(correlation)
            hmin = (np.mean(corr_abs)+corr_abs.max())/2
            idx = sig.find_peaks(corr_abs, distance=len(long_gold_code)-4, height=hmin)[0] 
            yhat = correlation[idx]
        else:
            # Symbol Samples: method 2
            corr_abs = abs(correlation)
            ind = np.argmax(corr_abs[:int(len(long_gold_code)*1.5)])
            idx = np.arange(len(corr_abs))[ind::len(long_gold_code)]
            yhat = correlation[idx]

        if 'return_stats' in args and args['return_stats']:
            # STATS: SINR, RSS and BER
            SINR, power = self.GoldCls.calc_stats(correlation, idx)
            print('\n\n\n[RESULTS] SINR: {:.3f}dB, power: {:.3f}dB'.format(SINR, power))

            # symbol decisions
            #bitsout = (yhat.real>0).astype(int) 
            #print('[RESULTS] original string is:    ', self.GoldCls.simple_bits, len(self.GoldCls.simple_bits),'bits')
            #print('[RESULTS] demodulated string is: ', bitsout, len(bitsout),'bits')
            if not self.args.doplots:
                sys.exit()

        # plot correlation
        # import pdb; pdb.set_trace()
        plt.figure()
        plt.plot(abs(correlation), '-+',label='amplitude')
        if args['method']=='peak_find':
            plt.axhline(hmin,color='k', label='Minimal peak height')
            plt.plot(idx, abs(yhat), 'o', label='DSSS peaks')
        else:
            plt.plot(np.arange(len(yhat))*len(long_gold_code)+ind, abs(yhat), 'o', label='DSSS peaks')
        plt.xlabel('Sample Index',fontsize=15)
        plt.ylabel('Correlation',fontsize=15)
        plt.title('TX: {} RX: {}'.format(args["txnode"], args["rxnode"]))
        plt.legend(fontsize=11, shadow=False)
        if 'savefig' in args and args['savefig']:
            plt.savefig("CorrAmp.png")

        #plt.figure()
        #plt.plot(correlation.real, '-o',label='real')
        #plt.plot(correlation.imag, '-+',label='imaginary')
        #if args['method']=='peak_find':
        #    plt.plot(idx, (yhat).real, 'o', label='DSSS peaks')
        #else:
        #    plt.plot(np.arange(len(yhat))*len(long_gold_code)+ind, yhat.real, 'o', label='DSSS peaks')
        #plt.xlabel('Sample Index',fontsize=15)
        #plt.ylabel('Correlation',fontsize=15)
        #plt.title('TX: {} RX: {}'.format(args["txnode"], args["rxnode"]))
        #plt.legend(fontsize=11, shadow=False)
        #plt.tight_layout()
        #if 'savefig' in args and args['savefig']:
        #    plt.savefig("CorrRealImag.png")

        plt.show()
        return 

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
        
        self._do_recv_gold_codes(cmd)


def parse_args():
    """Parse the command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--args", help="USRP radio arguments", default="", type=str)
    parser.add_argument("-c", "--cmdfile", help="JSON command file to execute", type=str, required=True)
    parser.add_argument("-l", "--logfile", type=str, default=DEF_LOGFILE)
    parser.add_argument("-t", "--usetxrx", help="Receive using the TX/RX port", action="store_true")
    parser.add_argument("-u", "--useexternalclock", help="Use external clock", action="store_true")
    parser.add_argument("-o", "--datadir", help="Directory to save data into. Default: %s" % DATA_OUTDIR, type=str, default=DATA_OUTDIR)
    parser.add_argument("-f", "--dfname", help="HDF5 results file (inside 'datadir'). Default: %s" % DATA_FILE_NAME, type=str, default=DATA_FILE_NAME)
    parser.add_argument("-p", "--doplots", help="Plot signal correlation graph for received samples.", action="store_true")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    oneend = TX_TASK(args)
    oneend.run(args.cmdfile)
