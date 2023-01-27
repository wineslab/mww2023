#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

#
# SDR interaction class
#

import multiprocessing as mp
#from gnuradio import uhd 
import uhd
import numpy as np
import datetime
import time
import matplotlib.pyplot as plt

class Radio:
    ASYNC_WAIT = 0.5
    RX_CLEAR_COUNT = 1000
    LO_ADJ = 1e6
    WAIT_TIME = 5

    def __init__(self, usrp_args = "", rx_txrx = False, external_clock = False, chan = 0):
        self.usrp = None
        self.usrp_args = usrp_args
        self.channel = chan
        self.rx_txrx = rx_txrx
        self.rxstreamer = None
        self.txstreamer = None
        self.logger = mp.get_logger()
        self.external_clock = external_clock

    def init_radio(self):
        self.usrp = uhd.usrp.MultiUSRP(self.usrp_args)
        if self.rx_txrx:
            self.usrp.set_rx_antenna("TX/RX")
        print('Using antenna:', self.usrp.get_rx_antenna())
        self._setup_streamers()

        # Set time source and clock source to gpsdo
        if self.external_clock:
            self.usrp.set_time_source('external', 0)
            self.usrp.set_clock_source('external', 0)

    def _setup_streamers(self):
        # Set up streamers
        st_args = uhd.usrp.StreamArgs("fc32", "sc16")
        st_args.channels = [self.channel]
        self.txstreamer = self.usrp.get_tx_stream(st_args)
        self.rxstreamer = self.usrp.get_rx_stream(st_args)

    def _stop_txstreamer(self):
        # Send a mini EOB packet
        metadata = uhd.types.TXMetadata()
        metadata.end_of_burst = True
        self.txstreamer.send(np.zeros((1, 0), dtype=np.complex64), metadata)

    def _flush_rxstreamer(self):
        # For collecting metadata from radio command (i.e., errors, etc.)
        metadata = uhd.types.RXMetadata()
        # Figure out the size of the receive buffer and make it
        buffer_samps = self.rxstreamer.get_max_num_samps()
        recv_buffer = np.empty((1, buffer_samps), dtype=np.complex64)
        # Loop several times and read samples to clear out gunk.
        rx_stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_done)
        rx_stream_cmd.num_samps = buffer_samps * self.RX_CLEAR_COUNT
        rx_stream_cmd.stream_now = True
        self.rxstreamer.issue_stream_cmd(rx_stream_cmd)
        for i in range(self.RX_CLEAR_COUNT):
            samps = self.rxstreamer.recv(recv_buffer, metadata)
            if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
                print(metadata.strerror())

    def _synchronize(self): # GPSDo based synchoronization following cir_rx8d.py
        """
        start_time = 3  # needs to be greater than 2, To-do: read it from args
        user_start_time = (start_time,)
        # Convert local time to sturct_time format
        local_time = time.time()
        user_time = time.localtime(local_time)

        # Create future time in struct_time format
        t = user_time[0:4]+user_start_time+(0,)+user_time[6:9]

        # Convert future time to seconds
        future_time = time.mktime(t)
        self.logger.info('Start time in Sec: %d' %future_time)

        local_time = time.time()
        start = int(future_time-local_time)
        """
        self.usrp.set_time_unknown_pps(uhd.types.TimeSpec(0))
        curr_hw_time = self.usrp.get_time_last_pps()
        while curr_hw_time==self.usrp.get_time_last_pps():
            pass
        time.sleep(0.05)

        self.usrp.set_time_next_pps(uhd.types.TimeSpec(0)) #uhd.time_spec_t(0)

        # Sleep for a couple seconds to make sure all usrp time registers latched and settled
        time.sleep(2)
        #print("Start time = ", start)
        #return uhd.types.TimeSpec(start)

        
    def tune(self, freq, gain, rate, use_lo_offset):
        # Set rate (if provided)
        if rate:
            self.currate = rate

            # self.logger.debug("Setting master clock rate = %f" %(rate*2))
            # self.usrp.set_master_clock_rate(rate*2)
            self.logger.debug("Setting tx rate = %f" %rate)
            self.usrp.set_tx_rate(rate, self.channel)
            self.logger.debug("Setting rx rate = %f" %rate)
            self.usrp.set_rx_rate(rate, self.channel)


        ## Set tx bandwidth (if provided)
        #if bw:
            #self.usrp.set_tx_bandwidth(bw, self.channel)

        # Set the USRP freq
        if use_lo_offset:
            # Push the LO offset outside of sampling freq range
            lo_off = self.currate/2 + self.LO_ADJ
            self.usrp.set_rx_freq(uhd.types.TuneRequest(freq, lo_off), self.channel)
            self.usrp.set_tx_freq(uhd.types.TuneRequest(freq, lo_off), self.channel)
        else:
            self.usrp.set_rx_freq(uhd.types.TuneRequest(freq), self.channel)
            self.usrp.set_tx_freq(uhd.types.TuneRequest(freq), self.channel)
        

        # Set the USRP gain
        self.usrp.set_rx_gain(gain, self.channel)
        self.usrp.set_tx_gain(gain, self.channel)

        # Flush rx stream
        self._flush_rxstreamer()

    def recv_samples(self, nsamps, start_time=None, rate = None):
        # Set the sampling rate if necessary
        if rate and rate != self.currate:
            self.usrp.set_rx_rate(rate, self.channel)
            self._flush_rxstreamer()

        # Create the array to hold the return samples.
        samples = np.empty((1, nsamps), dtype=np.complex64)

        # For collecting metadata from radio command (i.e., errors, etc.)
        metadata = uhd.types.RXMetadata()

        # Figure out the size of the receive buffer and make it
        buffer_samps = self.rxstreamer.get_max_num_samps()
        recv_buffer = np.zeros((1, buffer_samps), dtype=np.complex64)

        # Set up the device to receive exactly `nsamps` samples.
        rx_stream_cmd = uhd.types.StreamCMD(uhd.types.StreamMode.num_done)
        rx_stream_cmd.num_samps = nsamps
        rx_stream_cmd.stream_now = True

        # Do synchronization
        if start_time:
            sleep_time = start_time - time.time()
            if sleep_time > 0:
                time.sleep(sleep_time)
            else:
                self.logger.info("Late: %f" % sleep_time)

        if self.external_clock:
            self._synchronize()
            rx_stream_cmd.stream_now = False     # To handle set_start_time(uhd.time_spec(start))
            rx_stream_cmd.time_spec = uhd.types.TimeSpec(self.WAIT_TIME) # To handle set_start_time(uhd.time_spec(start)) 

        # Set up rx stream 
        self.rxstreamer.issue_stream_cmd(rx_stream_cmd)

        # Loop until we get the number of samples requested.  Append each
        # batch received to the return array.
        recv_samps = 0
        t = 0 # For debugging
        while recv_samps < nsamps:
            samps = self.rxstreamer.recv(recv_buffer, metadata, self.WAIT_TIME+2)

            if metadata.error_code != uhd.types.RXMetadataErrorCode.none:
                print(metadata.strerror())
            if samps:
                #print(t, 'Got samples ', time.time())
                real_samps = min(nsamps - recv_samps, samps)
                samples[:, recv_samps:recv_samps + real_samps] = \
                    recv_buffer[:, 0:real_samps]
                recv_samps += real_samps
            #else:
                #print(t, 'No samples ', time.time())
            #t += 1

        dt = datetime.datetime.now()

        # Done.  Return samples.
        return samples, dt

    def send_samples(self, samples, rate = None):
        # Set the sampling rate if necessary
        if rate and rate != self.currate:
            self.usrp.set_tx_rate(rate, self.channel)

        # Metadata for the TX command
        meta = uhd.types.TXMetadata()
        meta.has_time_spec = False
        meta.start_of_burst = True

        # Metadata from "async" status call
        as_meta = uhd.types.TXAsyncMetadata()
        
        # Figure out the size of the receive buffer and make it
        max_tx_samps = self.txstreamer.get_max_num_samps()
        #print(max_tx_samps)
        tot_samps = samples.size

        tx_buffer = np.zeros((1, max_tx_samps), dtype=np.complex64)
        
        tx_samps = 0
        while tx_samps < tot_samps:
            nsamps = min(tot_samps - tx_samps, max_tx_samps)
            tx_buffer[:, 0:0 + nsamps] = samples[:, tx_samps:tx_samps + nsamps]
            if nsamps < max_tx_samps:
                tx_buffer[:, nsamps:] = 0. + 0.j
                meta.end_of_burst = True
            tx_samps += self.txstreamer.send(tx_buffer, meta)
        if self.txstreamer.recv_async_msg(as_meta, self.ASYNC_WAIT):
            if as_meta.event_code != uhd.types.TXMetadataEventCode.burst_ack:
                self.logger.debug("Async error code: %s", as_meta.event_code)
        else:
            self.logger.info("Timed out waiting for TX async.")

    def xmit_samples(self, samples, duration, rate=None):
        # Set the sampling rate if necessary
        if rate and rate != self.currate:
            self.usrp.set_tx_rate(rate, self.channel)
            tot_samps = duration*rate
        else:
            tot_samps = duration*self.currate
        repeated_samples = np.hstack((samples, samples))

        # Metadata for the TX command
        meta = uhd.types.TXMetadata()
        meta.has_time_spec = False
        meta.start_of_burst = True

        # Metadata from "async" status call
        as_meta = uhd.types.TXAsyncMetadata()
        
        # Figure out the size of the receive buffer and make it
        n_tx_samps = self.txstreamer.get_max_num_samps()
        tx_buffer = np.zeros((1, n_tx_samps), dtype=np.complex64)

        tx_samps = 0
        start = 0
        len_samples = samples.shape[-1]
        while tx_samps < tot_samps:
            end = start + n_tx_samps
            tx_buffer[:, 0:0 + n_tx_samps] = repeated_samples[:, start:end]
            tx_samps += self.txstreamer.send(tx_buffer, meta)
            end = end % len_samples
            start = end

        if self.txstreamer.recv_async_msg(as_meta, self.ASYNC_WAIT):
            if as_meta.event_code != uhd.types.TXMetadataEventCode.burst_ack:
                self.logger.debug("Async error code: %s", as_meta.event_code)
        else:
            self.logger.info("Timed out waiting for TX async.")
        
        return

class GoldUtil():
    def __init__(self):
        # Check the SHOUT GitLab repo for functions to generate gold codes.
        self.gold_codes_dict = {
            31:{0:np.array([1,1,0,0,0,1,1,0,0,1,0,1,0,0,0,1,1,1,1,0,0,0,1,0,0,0,1,1,1,1,1])},
            63:{0:np.array([0,0,0,0,0,0,0,1,1,1,0,1,0,0,0,1,1,1,1,1,0,1,0,0,1,1,1,0,0,0,0,1,1,0,1,1,1,1,1,1,0,0,1,0,0,1,1,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0])},
            127:{0:np.array([0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,1,1,0,1,0,0,1,0,0,1,1,0,0,1,0,1,1,0,0,0,1,0,0,0,1,0,1,0,1,0,1,1,1,1,0,0,1,0,0,0,1,1,1,1,0,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,1,1,0,1,1,1,1,0,1])},
            511:{0:np.array([1,0,0,0,0,0,0,1,0,1,1,0,1,0,1,0,0,1,0,0,1,0,0,1,1,0,1,0,1,0,1,1,1,0,1,1,0,1,1,1,1,0,0,0,0,1,0,0,1,1,1,0,0,0,0,0,0,1,1,0,1,1,1,0,1,1,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1,1,1,0,1,0,1,0,0,1,0,1,1,0,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,0,1,1,0,1,0,0,0,1,1,1,1,1,0,0,0,0,1,1,1,0,0,1,0,1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,0,0,0,0,0,0,1,1,0,1,1,0,1,0,0,0,1,0,0,1,1,1,1,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,1,1,0,1,0,1,1,1,0,0,1,0,1,1,0,1,1,0,1,0,1,0,0,1,1,0,1,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,1,1,0,0,1,0,1,0,1,0,1,0,0,1,0,1,0,1,1,0,1,1,0,1,0,0,1,1,1,1,0,1,1,1,0,0,1,0,0,1,1,1,1,1,0,0,1,1,0,1,1,0,1,1,1,1,0,0,1,0,1,1,0,0,1,1,0,1,1,1,0,1,1,1,1,0,0,1,0,1,0,1,0,0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,1,1,1,1,0,1,1,0,0,0,1,0,0,1,0,1,1,0,1,1,1,0,1,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,1,1,0,0,1,1,0,0,1,0,0,1,0,0,0,1,0,0,1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,0,0,1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,1,0,1,0,0,1,1,1,0,1,0,1,1,1,1,0,0,0,0,0,1,0,0,1,1,1,0,1,1,1,0,1,0])},
            1023:{0:np.array([1,0,0,0,0,0,0,0,0,1,1,1,0,1,0,1,1,1,0,0,0,0,0,1,0,0,0,1,1,1,0,0,0,0,1,0,0,0,0,1,1,0,0,0,1,1,1,0,1,1,1,0,0,1,1,1,1,1,0,1,0,0,1,1,1,0,1,0,1,0,1,0,1,0,0,0,0,1,0,0,0,1,0,1,0,1,0,0,0,0,1,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,0,1,0,1,0,0,0,1,1,0,1,1,1,0,0,1,1,1,0,0,1,0,0,0,0,1,0,0,0,0,0,1,1,1,0,0,1,0,0,0,0,0,1,0,1,0,1,0,1,1,0,1,0,1,1,0,1,1,0,1,0,0,1,0,1,0,0,1,1,1,1,1,0,0,0,0,1,1,0,0,1,0,0,1,0,0,1,0,1,0,1,0,0,0,1,0,1,1,1,0,0,0,1,1,0,0,1,1,1,1,1,1,1,0,1,0,0,1,1,0,0,1,1,0,1,0,0,0,1,1,0,0,1,1,1,1,0,1,1,1,0,1,1,1,1,1,0,1,0,0,1,1,1,0,1,1,0,0,0,1,0,1,1,0,1,0,0,0,1,0,0,1,1,1,0,1,0,0,1,0,1,1,1,0,0,0,0,0,1,0,0,1,1,1,1,0,1,0,1,0,0,1,0,0,0,1,1,0,1,1,1,0,0,0,0,0,0,1,0,0,1,1,1,0,0,1,1,0,0,0,1,0,1,0,1,0,1,1,0,0,1,1,0,1,0,1,0,0,0,0,0,1,1,1,1,1,1,0,1,1,1,1,1,0,0,0,0,1,1,0,1,1,1,0,0,0,0,1,1,0,0,1,0,1,0,1,1,0,1,1,1,0,1,1,1,1,0,0,1,1,1,1,1,1,0,0,1,0,1,1,1,1,0,0,1,1,1,0,1,0,0,0,0,0,1,1,0,0,0,0,0,0,1,0,0,1,1,0,1,0,1,1,0,1,0,1,0,0,0,1,1,1,1,1,0,1,1,0,0,0,0,1,0,0,1,1,1,1,0,1,1,0,1,1,0,1,0,1,0,0,1,0,1,1,1,0,0,1,1,1,1,1,0,0,0,1,0,0,1,0,1,1,0,0,0,1,1,1,0,0,0,1,0,1,1,0,0,1,1,1,1,1,0,0,1,1,0,1,0,0,0,0,1,0,1,0,1,1,0,0,1,1,0,1,1,1,0,1,1,1,0,0,0,1,0,0,1,1,1,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,0,1,1,1,0,1,0,1,1,0,1,1,0,0,0,0,1,1,0,0,0,1,0,1,0,1,1,0,0,1,1,1,1,1,0,1,0,1,0,1,0,1,0,0,1,1,1,0,0,1,0,1,1,1,0,1,0,1,1,0,1,1,1,1,0,1,1,0,1,0,0,1,1,0,1,0,1,1,1,0,0,0,1,1,0,1,1,1,0,0,0,1,1,1,0,1,0,1,1,0,0,1,1,1,0,0,1,1,0,1,1,0,1,0,1,0,1,0,0,1,1,1,1,0,0,1,1,1,0,1,1,0,0,1,1,1,1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,1,0,1,0,0,1,1,1,1,1,1,1,1,0,1,1,0,0,0,0,1,0,0,0,1,0,0,0,0,1,1,0,1,0,1,0,0,1,0,1,0,1,1,1,1,1,0,0,1,0,1,0,0,0,0,1,0,1,1,0,0,0,0,0,1,1,0,1,0,1,1,0,0,0,1,1,0,0,0,0,1,0,1,0,1,1,0,0,1,0,0,1,1,0,1,0,0,1,0,0,0,1,0,1,0,0,1,1,1,1,1,0,1,1,1,0,0,0,0,1,1,0,0,0,0,1,0,0,0,1,0,1,1,0,1,1,1,0,1,1,1,1,0,0,0,1,0,0,0,0,1,1,1,0,0,1,1,1,0,0,0,0,1,1,1,0,0,0,0,1,1,0,1,0,1,1,0,1,0,1,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,1,0,0,1,0,0,1,1,1,1,0,1,1,1,1,1,0,0,1,0,0,0,0,0,0,1,0,1,1,1,0,1,1,1,1,1,0,0,0,1,0,1,0,1,1,1,1,1,1,0,0,0,0,0,0,1,0,1,1,0,0,0,1,0,0,1,0,0,1,0,0,0,0,1,0,1,1,1,0,0,1])},
            2047: {0:np.array([1,0,0,0,0,0,0,0,0,0,1,1,0,0,1,0,0,0,0,1,0,1,1,1,0,0,1,0,0,0,0,0,1,1,0,1,1,1,1,0,0,1,1,1,1,1,0,1,1,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,1,0,1,0,1,1,0,1,1,1,0,0,1,1,1,0,1,1,0,1,0,0,1,0,0,1,1,0,1,1,0,0,0,0,0,1,1,1,1,0,1,1,1,0,1,0,1,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,0,1,1,0,0,1,0,0,0,1,1,1,0,1,1,1,1,1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,0,1,0,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,0,1,0,0,1,0,0,0,1,1,0,1,0,1,0,1,0,0,0,1,0,1,1,0,0,1,0,0,0,0,1,0,1,1,0,1,1,0,1,1,0,1,0,0,1,1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,0,1,0,1,1,0,1,0,0,1,1,1,0,0,0,1,1,0,1,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,1,1,0,1,1,1,0,0,1,0,0,1,0,0,1,0,0,1,0,1,0,0,1,1,0,1,1,1,0,1,0,0,0,1,1,1,0,1,1,1,0,1,1,0,0,1,0,1,1,0,0,1,0,1,1,0,0,0,1,0,1,1,1,1,0,1,1,1,1,1,0,0,1,0,1,1,0,1,0,0,0,1,0,0,0,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,1,1,0,1,1,0,1,0,1,0,1,1,0,1,1,1,0,1,1,0,1,1,0,0,0,1,1,0,0,1,0,0,0,0,0,0,1,1,1,0,0,1,1,1,0,1,0,1,0,0,1,0,0,1,1,0,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,0,1,1,0,0,0,0,0,0,0,1,1,1,1,0,0,1,0,0,0,0,1,0,0,0,1,0,0,1,0,1,0,1,0,1,1,0,0,0,0,1,1,1,0,1,1,0,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,1,0,1,1,0,0,1,1,0,1,1,0,1,1,1,0,1,1,0,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1,0,1,0,1,0,1,0,0,1,0,0,0,1,1,0,0,0,1,0,1,1,0,1,1,1,1,0,0,1,1,0,1,1,1,1,0,0,1,0,1,0,0,1,1,1,0,1,1,0,0,1,1,1,0,1,0,1,1,0,1,1,1,1,0,0,0,1,1,0,0,1,0,1,0,0,0,1,1,1,1,1,0,1,0,0,0,0,0,0,1,1,1,1,0,1,1,0,1,0,0,0,1,0,1,1,0,1,0,1,1,1,0,0,0,1,0,0,1,0,1,1,0,0,0,1,0,1,1,1,1,1,1,0,1,1,1,1,0,0,1,1,0,1,1,0,1,1,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,1,1,0,1,1,1,0,1,0,1,1,0,1,0,0,1,0,1,0,0,1,0,1,1,0,0,1,1,0,0,1,0,1,1,0,0,1,0,0,1,1,1,1,0,0,0,0,0,1,0,1,0,0,0,0,1,0,1,0,0,1,0,1,0,0,1,0,0,1,0,0,1,0,1,1,0,0,0,1,0,0,1,1,1,1,0,0,0,0,1,0,0,1,1,1,0,0,1,0,0,1,1,1,0,0,1,1,0,0,0,0,1,0,1,1,0,0,1,1,1,1,0,1,0,1,0,1,1,1,0,0,1,1,0,0,1,1,0,1,1,0,0,0,1,1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0,1,0,0,1,1,0,0,1,1,1,0,0,1,1,1,1,1,0,1,0,1,0,1,1,0,1,1,0,1,0,0,0,1,1,1,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,1,0,0,1,0,1,0,0,1,0,1,0,0,1,1,1,0,0,0,1,0,0,1,0,1,0,0,1,0,0,1,1,1,0,1,0,1,1,0,0,1,1,0,1,1,1,0,0,1,0,1,1,0,0,0,0,0,0,1,0,1,1,1,1,1,1,1,0,0,1,1,1,1,0,1,0,1,0,0,1,0,0,0,1,1,0,0,1,1,0,0,1,0,0,1,1,1,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,0,0,1,0,1,1,0,1,0,1,0,0,0,0,1,1,0,0,0,1,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,0,0,0,1,1,0,1,1,1,1,0,1,0,1,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1,0,1,0,1,1,0,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,1,0,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,1,1,0,1,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,0,1,0,1,1,0,0,1,1,0,0,1,1,0,0,0,1,0,0,0,0,1,0,1,1,0,1,1,0,1,1,1,0,1,1,1,0,1,0,0,0,0,1,1,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,1,1,0,0,0,1,1,0,0,1,1,1,0,0,1,0,1,1,0,1,1,0,1,1,1,0,1,0,0,1,0,1,0,1,0,0,1,1,1,1,0,0,0,0,0,0,1,0,0,1,1,1,0,1,0,0,0,0,0,0,0,1,1,1,0,0,1,0,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,0,1,1,0,1,0,1,1,1,1,0,0,1,0,1,1,0,0,0,0,1,0,1,1,1,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1,1,1,1,0,1,0,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0,1,1,1,0,0,1,1,0,0,1,1,1,0,1,1,1,1,0,0,1,0,1,1,1,1,1,0,1,0,0,1,0,1,1,1,0,1,0,1,1,0,1,0,0,0,1,1,1,1,0,1,0,0,0,0,1,1,0,0,0,0,0,1,0,1,0,1,0,0,1,0,1,0,0,1,1,0,0,0,0,1,0,1,0,1,0,1,1,0,0,1,0,0,0,0,1,0,1,0,1,1,0,1,1,0,0,1,0,1,1,1,1,0,1,0,0,0,0,1,1,0,1,0,0,0,0,1,0,0,0,1,1,1,1,0,0,1,0,1,1,0,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,0,1,1,1,1,0,1,0,0,1,0,1,0,0,0,0,1,0,1,1,0,0,1,0,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1,0,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,1,1,0,0,1,1,1,1,0,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,0,0,1,1,1,0,1,0,1,0,1,0,1,1,0,0,0,1,1,1,0,0,0,1,1,1,0,0,0,1,1,0,0,1,1,1,1,0,1,1,0,0,1,0,1,1,1,0,0,1,1,0,0,1,1,1,1,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0,0,0,0,1,1,1,1,1,0,0,1,1,1,0,1,0,1,0,1,0,1,1,1,0,0,1,1,0,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,1,0,1,0,0,1,0,0,1,0,0,0,0,1,1,1,0,0,0,1,0,1,0,0,0,1,0,0,1,0,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1,0,0,1,0,1,0,0,0,1,1,1,1,0,1,0,0,0,1,0,1,0,1,0,0,0,1,0,0,0,0,0,1,0,1,1,1,1,0,0,1,0,0,1,1,0,0,1,1,1,1,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,1,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,1,1,1,1])}
        }
        self.gold_id = 0
        self.simple_bits = np.array([1,1,1,1,0,0,1,0])

    def SRRC(self, alpha, SPS, span):
        """ 
        Square-root raised cosine (SRRC) filter design

        Input
        -----
            alpha: roll-off factor between 0 and 1.  it indicates how quickly its frequency content transitions from its max to zero.
            SPS:   samples per symbol = sampling rate / symbol rate
            span:  the number of symbols in the filter to the left and right of the center tap.  the SRRC filter will have 2*span + 1 symbols in the impulse response.

        Output
        ------
        SRRC filter taps
        """
        if ((int(SPS) - SPS) > 1e-10):
            SPS = int(SPS)
        if ((int(span) - span) > 1e-10):
            span = int(span)
        if (alpha < 0):
            raise ValueError('SRRC design: alpha must be between 0 and 1')
        if (SPS <= 1):
            raise ValueError('SRRC design: SPS must be greater than 1')

        n = np.arange(-SPS*span, SPS*span+1)+1e-9

        h = (1/np.sqrt(SPS))*( (np.sin(np.pi*n*(1-alpha)/SPS)) + \
            (4*alpha*n/SPS)*(np.cos(np.pi*n*(1+alpha)/SPS)) ) /\
            ( (np.pi*n/SPS) * (1 - (4*alpha*n/SPS)**2) )
        return h  

    def get_gold_code(self, nbits):
        return self.gold_codes_dict[nbits][self.gold_id]

    def clock_sync(self, samples, sps, interpo_factor=16):
        '''
        source: https://pysdr.org/content/sync.html
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

    def DD_carrier_sync(self, z, M, BnTs, zeta=0.707, mod_type = 'MPSK', type = 0, open_loop = False):
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

    def Freq_Offset_Correction(self, samples, fs, order=2, debug=False):
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

    def calc_stats(self, corr, peak_locs, debug=False):
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