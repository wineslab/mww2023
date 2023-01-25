#!/usr/bin/env python3

# Copyright 2020-2021 University of Utah

# Signal and other math utility functions

import numpy as np
import scipy.signal as sig
import matplotlib.pyplot as plt
from dsss.gold import gold_codes_dict, simple_bits 

def SRRC(alpha, SPS, span):
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

def get_gold_code(nbits, code_id):
    return gold_codes_dict[nbits][code_id]#.astype(np.complex64)

def get_gold_stats(samples, peak_locs, bits=simple_bits):
    """
    Return bit error rate, SNR, and power of samples. Note the SNR and power 
    calculations only include the data that matches our known Tx bit pattern.
    """
    if samples.max() == 0:
        return { 'bit_error_rate': 1, 'snr':0, 'power':0}
    peaks = samples[peak_locs]
    if len(peaks):
        ##### Calculate BER #####    
        demodbits = (peaks.real>0).astype(int) 
        txbits = np.tile(bits, int(len(demodbits)//len(bits)+1))[:len(demodbits)]
        BER = sum(demodbits!=txbits)/len(txbits)

        ##### Calculate SNR #####
        noise_mask = np.ones(len(samples), dtype=bool)
        noise_mask[:peak_locs[0]] = False
        noise_mask[peak_locs[-1]:] = False
        noise_mask[peak_locs] = False
        noise = samples[noise_mask]
        SNRdB = 10.0 * np.log10( np.mean(np.abs(peaks)**2)/np.mean(np.abs(noise)**2) )

        ##### Calculate Power #####
        powerdB = 10.0 * np.log10(np.mean(np.abs(peaks)**2))

        stats = {
            'bit_error_rate': BER,
            'snr': SNRdB,
            'power': powerdB
        }
        return stats
    else:
        return { 'bit_error_rate': 1, 'snr':0, 'power':0}

    # if 0 in bits:
    #     bits = bits * 2 - 1
    # bit_matches = sig.correlate(np.sign(peaks.real), bits, mode='same')
    # locs = sig.find_peaks(bit_matches, distance=len(bits))[0]
    # error_rates = 1 - bit_matches[locs][1:-1] / len(bits)
    # inds = np.where(bit_matches == bit_matches.max() )[0]
    # noise_mask = np.ones(len(samples), dtype=bool)
    # noise_mask[:peak_locs[0]] = False
    # noise_mask[peak_locs[-1]:] = False
    # noise_mask[peak_locs] = False
    # perfect_peak_values = abs(np.concatenate([peaks.real[i - len(bits)//2:i+len(bits)//2] for i in inds]))
    # noise_values = samples[noise_mask]
    # stats = {
    #     'bit_error_rate': error_rates.mean(),
    #     'snr': perfect_peak_values.mean() / abs(noise_values).mean(),
        # 'power': 10.0 * np.log10(np.sum(np.square(np.abs(perfect_peak_values)))/len(perfect_peak_values))
    # }
    

def clock_sync(samples, sps, interpo_factor=16):
    # Input Sample Interpolation for shifting them by a fraction of a sample
    samples_interpolated = sig.resample_poly(samples, interpo_factor, 1) # we'll use 32 as the interpolation factor, arbitrarily chosen, seems to work better than 16
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

def Freq_Offset_Correction(samples, fs, order=2, debug=False):
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

def DD_carrier_sync(z, M, BnTs, zeta=0.707, mod_type = 'MPSK', type = 0, open_loop = False):
    """
    source:  https://scikit-dsp-comm.readthedocs.io/en/latest/synchronization.html
    z_prime,a_hat,e_phi = DD_carrier_sync(z,M,BnTs,zeta=0.707,type=0)
    Decision directed carrier phase tracking
    
           z = complex baseband PSK signal at one sample per symbol
           M = The PSK modulation order, i.e., 2, 8, or 8.
        BnTs = time bandwidth product of loop bandwidth and the symbol period,
               thus the loop bandwidth as a fraction of the symbol rate.
        zeta = loop damping factor
        type = Phase error detector type: 0 <> ML, 1 <> heuristic
    
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

def apply_shift(samps, base=0, shift=0):
    return samps * np.power(np.e, -1j*2*np.pi*np.linspace(base, base+shift, len(samps)))

def phase_correct_freq_drift(samps, peak_locs, long_gold_code, angle_mod=-np.pi):
    """
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
    best_shift = good_shift + np.angle((np.conjugate(new_samps[peak_locs][:-len(simple_bits)])* new_samps[peak_locs][len(simple_bits):]).sum()) / (len(long_gold_code)  * 10)
    new_samps = phase_apply_shift(samps, 0, best_shift)
    best_base = np.median( np.angle(new_samps[peak_locs]))
    new_samps = phase_apply_shift(samps, best_base, best_shift)
    new_peaks = new_samps[peak_locs]
    if np.median(new_peaks) < 0:
        new_samps = new_samps*-1

    new_peaklocs = sig.find_peaks(abs(new_samps.real), distance=len(long_gold_code)-4, height=[0,np.median(abs(new_peaks.real))*3])[0]
    #new_peaklocs = sig.find_peaks(abs(new_samps.real), distance=len(long_gold_code)-4)[0]
    return new_samps, new_peaklocs, (best_base, best_shift)

def search_sequence_numpy(arr,seq):
    """
    Find sequence in an array using NumPy only.

    Parameters
    ----------    
    arr    : input 1D array
    seq    : input 1D array

    Output
    ------    
    Output : 1D Array of indices in the input array that satisfy the 
    matching of input sequence in the input array.
    In case of no match, an empty list is returned.
    """
    # Store sizes of input array and sequence
    Na, Nseq = arr.size, seq.size
    # Range of sequence
    r_seq = np.arange(Nseq)
    # Create a 2D array of sliding indices across the entire length of input array.
    # Match up with the input sequence & get the matching starting indices.
    M = (arr[np.arange(Na-Nseq+1)[:,None] + r_seq] == seq).all(1)
    # Get the range of those indices as final output
    if M.any() >0:
        return np.where(np.convolve(M,np.ones((Nseq),dtype=int))>0)[0]
    else:
        return []         # No match found


def correct_freq_drift(samps, peak_locs, bits):
    """
    Calculate the Frequency offset between Tx and Rx and return new samples

    Parameters
    ----------
    samps     : 1D array of complex IQ samples 
    peak_locs : 1D array of indices of peaks in samps
    bits      : 1D array of bits, transmitted signal from {0,1}

    Output
    ------
    new_samples : 1D array of offset-corrected complex IQ samples
    new_locs    : 1D array of indices of peaks in samps
    new_params  : Tuple: (base, shift) where base is added to phase of each sample, and shift is added to each sample sequentially (see apply_shift)
    """
    new_samples, new_locs, new_params = phase_correct_freq_drift(samps,peak_locs, angle_mod=-np.pi)
    signs = ((np.sign(new_samples[new_locs].real) + 1) / 2)
    new_samples_tmp, new_locs_tmp, new_params_tmp = phase_correct_freq_drift(samps,peak_locs, angle_mod=np.pi)
    signs_tmp = ((np.sign(new_samples_tmp[new_locs_tmp].real) + 1) / 2)
    if len(search_sequence_numpy(signs, bits)) < len(search_sequence_numpy(signs_tmp, bits)):
        new_samples = new_samples_tmp
        new_locs = new_locs_tmp
        new_params = new_params_tmp
    return new_samples, new_locs, new_params
