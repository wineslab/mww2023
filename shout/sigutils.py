#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

# Signal and other math utility functions

import numpy as np
import scipy.signal as sig

def mk_sine(nsamps, wampl, wfreq, srate):
    vals = np.ones((1,nsamps), dtype=np.complex64) * np.arange(nsamps)
    return wampl * np.exp(vals * 2j * np.pi * wfreq/srate)

def butter_filt(samps, flo, fhi, srate, order = 5):
    nyq = 0.5*srate
    b, a = sig.butter(order, [flo/nyq, fhi/nyq], btype='band')
    return sig.lfilter(b, a, samps)

def DFT_filt(samps, flo, fhi, srate):
    F = np.fft.fft(samps)
    freqs = np.fft.fftfreq(len(samps), d=1/srate)
    F_filtered = F * (freqs >= flo) * (freqs <= fhi)
    return np.fft.ifft(F_filtered)

def butter_filt_with_shift(samps, fshift, fpass, srate, order=5):
    '''
    samps: The iq samples
    fshift: The center frequency of your signal, which is shifted down to DC
    fpass: The bandwidth of your filter
    srate: The sampe rate
    '''
    nyq = 0.5*srate
    shift_seq = np.exp(-2j * np.pi * fshift / srate * np.arange(len(samps)))
    shift_samps = samps * shift_seq
    b, a = sig.butter(order, fpass/nyq, btype='low')
    fsamps =  sig.lfilter(b,a, shift_samps)
    return fsamps / shift_seq

def get_avg_power(samps):
    return 10.0 * np.log10(np.sum(np.square(np.abs(samps)))/len(samps))

def compute_psd(nfft, samples):
    """Return the power spectral density of `samples`"""
    window = np.hamming(nfft)
    result = np.multiply(window, samples)
    result = np.fft.fftshift(np.fft.fft(result, nfft))
    result = np.square(np.abs(result))
    result = np.nan_to_num(10.0 * np.log10(result))
    return result

def haversine(lat1, lon1, lat2, lon2):
    EARTH_RADIUS = 6370
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    newlon = lon2 - lon1
    newlat = lat2 - lat1

    haver_formula = np.sin(newlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(newlon/2.0)**2

    dist = 2 * np.arcsin(np.sqrt(haver_formula))
    km = EARTH_RADIUS * dist
    return km
