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
