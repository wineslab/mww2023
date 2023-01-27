# /usr/bin python3
# DSSS TX/RX simulation
import scipy.signal as sig
import numpy as np
import matplotlib.pyplot as plt
import scipy

gold_codes_dict = {
    31:{0:np.array([1,1,0,0,0,1,1,0,0,1,0,1,0,0,0,1,1,1,1,0,0,0,1,0,0,0,1,1,1,1,1])},
    63:{0:np.array([0,0,0,0,0,0,0,1,1,1,0,1,0,0,0,1,1,1,1,1,0,1,0,0,1,1,1,0,0,0,0,1,1,0,1,1,1,1,1,1,0,0,1,0,0,1,1,1,0,1,1,1,1,0,0,1,1,0,0,0,0,1,0])},
    127:{0:np.array([0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,1,0,1,1,0,1,0,0,1,0,0,1,1,0,0,1,0,1,1,0,0,0,1,0,0,0,1,0,1,0,1,0,1,1,1,1,0,0,1,0,0,0,1,1,1,1,0,1,1,1,0,0,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,0,1,1,1,0,1,1,0,1,0,0,0,1,1,1,1,0,0,1,0,1,0,0,0,0,0,1,0,0,0,0,0,1,1,0,1,1,1,1,0,1])},
    511:{0:np.array([1,0,0,0,0,0,0,1,0,1,1,0,1,0,1,0,0,1,0,0,1,0,0,1,1,0,1,0,1,0,1,1,1,0,1,1,0,1,1,1,1,0,0,0,0,1,0,0,1,1,1,0,0,0,0,0,0,1,1,0,1,1,1,0,1,1,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,1,0,1,1,1,0,1,0,1,0,1,1,1,1,0,1,1,1,1,1,1,1,0,1,0,1,1,0,1,1,1,0,1,0,1,0,0,1,0,1,1,0,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,0,1,1,0,1,0,0,0,1,1,1,1,1,0,0,0,0,1,1,1,0,0,1,0,1,0,1,1,0,1,0,1,1,1,1,1,0,1,0,1,1,1,0,0,0,0,0,0,1,1,0,1,1,0,1,0,0,0,1,0,0,1,1,1,1,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,1,1,0,1,0,1,1,1,0,0,1,0,1,1,0,1,1,0,1,0,1,0,0,1,1,0,1,0,1,1,1,1,0,0,0,0,1,1,1,1,0,0,1,1,0,0,1,0,1,0,1,0,1,0,0,1,0,1,0,1,1,0,1,1,0,1,0,0,1,1,1,1,0,1,1,1,0,0,1,0,0,1,1,1,1,1,0,0,1,1,0,1,1,0,1,1,1,1,0,0,1,0,1,1,0,0,1,1,0,1,1,1,0,1,1,1,1,0,0,1,0,1,0,1,0,0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,1,1,1,1,0,1,1,0,0,0,1,0,0,1,0,1,1,0,1,1,1,0,1,0,0,1,0,1,1,0,0,0,0,1,0,1,0,0,0,1,1,0,0,1,1,0,0,1,0,0,1,0,0,0,1,0,0,1,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,0,1,0,0,1,0,1,0,1,1,1,0,1,0,1,1,1,1,1,1,0,1,0,0,1,1,1,0,1,0,1,1,1,1,0,0,0,0,0,1,0,0,1,1,1,0,1,1,1,0,1,0])},
    2047: {0:np.array([1,0,0,0,0,0,0,0,0,0,1,1,0,0,1,0,0,0,0,1,0,1,1,1,0,0,1,0,0,0,0,0,1,1,0,1,1,1,1,0,0,1,1,1,1,1,0,1,1,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,1,1,0,1,0,1,1,0,1,1,1,0,0,1,1,1,0,1,1,0,1,0,0,1,0,0,1,1,0,1,1,0,0,0,0,0,1,1,1,1,0,1,1,1,0,1,0,1,1,1,1,0,0,0,1,1,1,1,0,0,1,1,1,0,1,1,0,0,1,0,0,0,1,1,1,0,1,1,1,1,1,0,0,1,1,1,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,1,1,1,0,1,0,0,0,0,1,1,1,1,1,0,0,1,1,0,1,0,0,1,0,0,1,0,0,0,1,1,0,1,0,1,0,1,0,0,0,1,0,1,1,0,0,1,0,0,0,0,1,0,1,1,0,1,1,0,1,1,0,1,0,0,1,1,1,1,0,1,1,0,1,1,1,1,0,0,0,1,0,0,1,0,1,1,0,1,0,0,1,1,1,0,0,0,1,1,0,1,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,0,0,1,1,1,0,1,1,1,1,1,1,1,0,0,0,1,1,1,1,1,0,0,0,1,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0,1,1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,1,1,0,1,1,1,0,0,1,0,0,1,0,0,1,0,0,1,0,1,0,0,1,1,0,1,1,1,0,1,0,0,0,1,1,1,0,1,1,1,0,1,1,0,0,1,0,1,1,0,0,1,0,1,1,0,0,0,1,0,1,1,1,1,0,1,1,1,1,1,0,0,1,0,1,1,0,1,0,0,0,1,0,0,0,1,0,1,1,1,0,1,0,1,0,1,1,1,0,0,1,1,0,1,1,0,1,0,1,0,1,1,0,1,1,1,0,1,1,0,1,1,0,0,0,1,1,0,0,1,0,0,0,0,0,0,1,1,1,0,0,1,1,1,0,1,0,1,0,0,1,0,0,1,1,0,1,0,1,1,1,1,1,1,1,0,1,1,1,0,1,1,1,0,0,0,1,1,1,1,0,0,1,1,0,1,1,0,0,0,0,0,0,0,1,1,1,1,0,0,1,0,0,0,0,1,0,0,0,1,0,0,1,0,1,0,1,0,1,1,0,0,0,0,1,1,1,0,1,1,0,0,0,1,0,0,1,0,1,0,0,1,0,0,0,0,1,0,1,1,0,0,1,1,0,1,1,0,1,1,1,0,1,1,0,0,1,0,0,0,0,0,0,0,1,0,1,0,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1,0,1,0,1,0,1,0,0,1,0,0,0,1,1,0,0,0,1,0,1,1,0,1,1,1,1,0,0,1,1,0,1,1,1,1,0,0,1,0,1,0,0,1,1,1,0,1,1,0,0,1,1,1,0,1,0,1,1,0,1,1,1,1,0,0,0,1,1,0,0,1,0,1,0,0,0,1,1,1,1,1,0,1,0,0,0,0,0,0,1,1,1,1,0,1,1,0,1,0,0,0,1,0,1,1,0,1,0,1,1,1,0,0,0,1,0,0,1,0,1,1,0,0,0,1,0,1,1,1,1,1,1,0,1,1,1,1,0,0,1,1,0,1,1,0,1,1,0,0,0,0,0,1,0,0,0,1,0,1,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,1,1,0,1,1,1,0,1,0,1,1,0,1,0,0,1,0,1,0,0,1,0,1,1,0,0,1,1,0,0,1,0,1,1,0,0,1,0,0,1,1,1,1,0,0,0,0,0,1,0,1,0,0,0,0,1,0,1,0,0,1,0,1,0,0,1,0,0,1,0,0,1,0,1,1,0,0,0,1,0,0,1,1,1,1,0,0,0,0,1,0,0,1,1,1,0,0,1,0,0,1,1,1,0,0,1,1,0,0,0,0,1,0,1,1,0,0,1,1,1,1,0,1,0,1,0,1,1,1,0,0,1,1,0,0,1,1,0,1,1,0,0,0,1,1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,0,0,0,1,0,0,1,1,0,0,1,1,1,0,0,1,1,1,1,1,0,1,0,1,0,1,1,0,1,1,0,1,0,0,0,1,1,1,1,0,0,0,1,1,1,0,0,0,0,0,1,1,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,1,0,0,1,0,1,0,0,1,0,1,0,0,1,1,1,0,0,0,1,0,0,1,0,1,0,0,1,0,0,1,1,1,0,1,0,1,1,0,0,1,1,0,1,1,1,0,0,1,0,1,1,0,0,0,0,0,0,1,0,1,1,1,1,1,1,1,0,0,1,1,1,1,0,1,0,1,0,0,1,0,0,0,1,1,0,0,1,1,0,0,1,0,0,1,1,1,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,0,0,1,0,1,1,0,1,0,1,0,0,0,0,1,1,0,0,0,1,0,1,0,0,0,0,1,0,1,0,1,0,1,0,0,0,0,0,1,1,0,1,1,1,1,0,1,0,1,1,0,0,0,1,0,0,0,1,0,0,0,1,0,1,0,1,0,1,1,0,1,1,1,1,1,1,1,0,0,0,0,1,1,0,0,1,0,0,1,1,1,1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,0,1,1,0,1,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,0,1,0,1,1,0,0,1,1,0,0,1,1,0,0,0,1,0,0,0,0,1,0,1,1,0,1,1,0,1,1,1,0,1,1,1,0,1,0,0,0,0,1,1,0,0,1,0,0,1,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,1,0,0,0,0,0,1,1,1,0,0,0,1,1,0,1,0,1,1,0,0,0,1,1,0,0,1,1,1,0,0,1,0,1,1,0,1,1,0,1,1,1,0,1,0,0,1,0,1,0,1,0,0,1,1,1,1,0,0,0,0,0,0,1,0,0,1,1,1,0,1,0,0,0,0,0,0,0,1,1,1,0,0,1,0,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,0,1,1,0,1,1,0,1,0,1,1,1,1,0,0,1,0,1,1,0,0,0,0,1,0,1,1,1,1,1,0,0,0,0,1,0,1,0,0,0,0,0,0,0,1,1,1,1,0,1,0,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,1,1,0,0,0,1,1,0,0,0,0,1,1,1,0,0,1,1,0,0,1,1,1,0,1,1,1,1,0,0,1,0,1,1,1,1,1,0,1,0,0,1,0,1,1,1,0,1,0,1,1,0,1,0,0,0,1,1,1,1,0,1,0,0,0,0,1,1,0,0,0,0,0,1,0,1,0,1,0,0,1,0,1,0,0,1,1,0,0,0,0,1,0,1,0,1,0,1,1,0,0,1,0,0,0,0,1,0,1,0,1,1,0,1,1,0,0,1,0,1,1,1,1,0,1,0,0,0,0,1,1,0,1,0,0,0,0,1,0,0,0,1,1,1,1,0,0,1,0,1,1,0,1,1,1,1,1,1,1,1,0,0,1,1,0,0,1,1,1,1,0,1,1,1,1,0,1,0,0,1,0,1,0,0,0,0,1,0,1,1,0,0,1,0,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1,0,0,1,0,1,0,1,0,1,0,1,1,0,1,0,1,0,1,0,1,1,0,0,1,1,1,1,0,1,1,0,1,0,1,1,1,1,1,1,1,0,1,0,0,0,1,1,1,0,1,0,1,0,1,0,1,1,0,0,0,1,1,1,0,0,0,1,1,1,0,0,0,1,1,0,0,1,1,1,1,0,1,1,0,0,1,0,1,1,1,0,0,1,1,0,0,1,1,1,1,1,0,1,0,1,1,0,1,0,1,1,0,0,1,0,1,0,0,0,0,1,1,1,1,1,0,0,1,1,1,0,1,0,1,0,1,0,1,1,1,0,0,1,1,0,1,1,1,0,0,1,1,0,0,0,0,0,0,0,0,1,0,1,0,0,1,0,0,1,0,0,0,0,1,1,1,0,0,0,1,0,1,0,0,0,1,0,0,1,0,1,1,0,0,1,0,0,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,1,1,0,0,0,1,0,1,1,0,0,1,0,1,0,0,0,1,1,1,1,0,1,0,0,0,1,0,1,0,1,0,0,0,1,0,0,0,0,0,1,0,1,1,1,1,0,0,1,0,0,1,1,0,0,1,1,1,1,0,1,0,1,1,1,0,0,0,1,1,0,1,1,0,1,0,1,0,1,0,1,0,0,0,0,1,1,0,0,0,0,0,0,1,1,0,1,1,1,1])}

}

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
    best_shift = good_shift + np.angle((np.conjugate(new_samps[peak_locs][:-10])* new_samps[peak_locs][10:]).sum()) / (len(long_gold_code)  * 10)
    new_samps = phase_apply_shift(samps, 0, best_shift)
    best_base = np.median( np.angle(new_samps[peak_locs]))
    new_samps = phase_apply_shift(samps, best_base, best_shift)
    new_peaks = new_samps[peak_locs]
    if np.median(new_peaks) < 0:
        new_samps = new_samps*-1

    new_peaklocs = sig.find_peaks(abs(new_samps.real), distance=len(long_gold_code)-4, height=[0,np.median(abs(new_peaks.real))*3])[0]
    #new_peaklocs = sig.find_peaks(abs(new_samps.real), distance=len(long_gold_code)-4)[0]
    return new_samps, new_peaklocs, (best_base, best_shift)

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

def NDA_symb_sync(z,Ns,L,BnTs,zeta=0.707,I_ord=3):
    """
    zz,e_tau = NDA_symb_sync(z,Ns,L,BnTs,zeta=0.707,I_ord=3)

           z = complex baseband input signal at nominally Ns samples
               per symbol
          Ns = Nominal number of samples per symbol (Ts/T) in the symbol 
               tracking loop, often 4
        BnTs = time bandwidth product of loop bandwidth and the symbol period,
               thus the loop bandwidth as a fraction of the symbol rate.
        zeta = loop damping factor
       I_ord = interpolator order, 1, 2, or 3
    
       e_tau = the timing error e(k) input to the loop filter

          Kp = The phase detector gain in the symbol tracking loop; for the
               NDA algoithm used here always 1
    
    Mark Wickert July 2014

    Motivated by code found in M. Rice, Digital Communications A Discrete-Time 
    Approach, Prentice Hall, New Jersey, 2009. (ISBN 978-0-13-030497-1).
    """
    # Loop filter parameters
    K0 = -1.0 # The modulo 1 counter counts down so a sign change in loop
    Kp = 1.0
    K1 = 4*zeta/(zeta + 1/(4*zeta))*BnTs/Ns/Kp/K0
    K2 = 4/(zeta + 1/(4*zeta))**2*(BnTs/Ns)**2/Kp/K0
    zz = np.zeros(len(z),dtype=np.complex128)
    #zz = np.zeros(int(np.floor(len(z)/float(Ns))),dtype=np.complex128)
    e_tau = np.zeros(len(z))
    #e_tau = np.zeros(int(np.floor(len(z)/float(Ns))))
    #z_TED_buff = np.zeros(Ns)
    c1_buff = np.zeros(2*L+1)

    vi = 0
    CNT_next = 0
    mu_next = 0
    underflow = 0
    epsilon = 0
    mm = 1
    z = np.hstack(([0], z))
    for nn in range(1,Ns*int(np.floor(len(z)/float(Ns)-(Ns-1)))):
        # Define variables used in linear interpolator control
        CNT = CNT_next
        mu = mu_next
        if underflow == 1:
            if I_ord == 1:
                # Decimated interpolator output (piecewise linear)
                z_interp = mu*z[nn] + (1 - mu)*z[nn-1]
            elif I_ord == 2:
                # Decimated interpolator output (piecewise parabolic)
                # in Farrow form with alpha = 1/2
                v2 = 1/2.*np.sum(z[nn+2:nn-1-1:-1]*[1, -1, -1, 1])
                v1 = 1/2.*np.sum(z[nn+2:nn-1-1:-1]*[-1, 3, -1, -1])
                v0 = z[nn]
                z_interp = (mu*v2 + v1)*mu + v0
            elif I_ord == 3:
                # Decimated interpolator output (piecewise cubic)
                # in Farrow form
                v3 = np.sum(z[nn+2:nn-1-1:-1]*[1/6., -1/2., 1/2., -1/6.])
                v2 = np.sum(z[nn+2:nn-1-1:-1]*[0, 1/2., -1, 1/2.])
                v1 = np.sum(z[nn+2:nn-1-1:-1]*[-1/6., 1, -1/2., -1/3.])
                v0 = z[nn]
                z_interp = ((mu*v3 + v2)*mu + v1)*mu + v0
            else:
                log.error('I_ord must 1, 2, or 3')
            # Form TED output that is smoothed using 2*L+1 samples
            # We need Ns interpolants for this TED: 0:Ns-1
            c1 = 0
            for kk in range(Ns):
                if I_ord == 1:
                    # piecewise linear interp over Ns samples for TED
                    z_TED_interp = mu*z[nn+kk] + (1 - mu)*z[nn-1+kk]
                elif I_ord == 2:
                    # piecewise parabolic in Farrow form with alpha = 1/2
                    v2 = 1/2.*np.sum(z[nn+kk+2:nn+kk-1-1:-1]*[1, -1, -1, 1])
                    v1 = 1/2.*np.sum(z[nn+kk+2:nn+kk-1-1:-1]*[-1, 3, -1, -1])
                    v0 = z[nn+kk]
                    z_TED_interp = (mu*v2 + v1)*mu + v0
                elif I_ord == 3:
                    # piecewise cubic in Farrow form
                    v3 = np.sum(z[nn+kk+2:nn+kk-1-1:-1]*[1/6., -1/2., 1/2., -1/6.])
                    v2 = np.sum(z[nn+kk+2:nn+kk-1-1:-1]*[0, 1/2., -1, 1/2.])
                    v1 = np.sum(z[nn+kk+2:nn+kk-1-1:-1]*[-1/6., 1, -1/2., -1/3.])
                    v0 = z[nn+kk]
                    z_TED_interp = ((mu*v3 + v2)*mu + v1)*mu + v0
                else:
                    raise ValueError('Error: I_ord must 1, 2, or 3')
                c1 = c1 + np.abs(z_TED_interp)**2 * np.exp(-1j*2*np.pi/Ns*kk)
            c1 = c1/Ns
            # Update 2*L+1 length buffer for TED output smoothing
            c1_buff = np.hstack(([c1], c1_buff[:-1]))
            # Form the smoothed TED output
            epsilon = -1/(2*np.pi)*np.angle(np.sum(c1_buff)/(2*L+1))
            # Save symbol spaced (decimated to symbol rate) interpolants in zz
            zz[mm] = z_interp
            e_tau[mm] = epsilon # log the error to the output vector e
            mm += 1
        else:
            # Simple zezo-order hold interpolation between symbol samples
            # we just coast using the old value
            #epsilon = 0
            pass
        vp = K1*epsilon       # proportional component of loop filter
        vi = vi + K2*epsilon  # integrator component of loop filter
        v = vp + vi           # loop filter output
        W = 1/float(Ns) + v          # counter control word
       
        # update registers
        CNT_next = CNT - W           # Update counter value for next cycle
        if CNT_next < 0:             # Test to see if underflow has occured
            CNT_next = 1 + CNT_next  # Reduce counter value modulo-1 if underflow
            underflow = 1            # Set the underflow flag
            mu_next = CNT/W          # update mu
        else:
            underflow = 0
            mu_next = mu
    # Remove zero samples at end
    zz = zz[:-(len(zz)-mm+1)]
    # Normalize so symbol values have a unity magnitude
    zz /=np.std(zz)
    e_tau = e_tau[:-(len(e_tau)-mm+1)]
    return zz, e_tau

def symb_sync(z, N,BnTs,zeta=0.707):
    dsI, dsQ = z.real, z.imag
    # compute the loop filter coefficients K1t and K2t
    # INPUT:  BnTs, N, zeta
    # OUTPUT: K1t and K2t
    Kp = 2*2.7
    K0 = -1

    th = BnTs/(zeta+0.25/zeta)
    th = th/N
    K1 = 4*zeta*th/(1 + 2*zeta*th + th*th)
    K2 = K1*th/zeta

    K1t = K1/(K0*Kp)
    K2t = K2/(K0*Kp)


    TEDout = np.zeros(len(dsI))
    strobeSave = np.zeros(len(dsI))
    x_2_I = np.zeros(len(dsI))
    x_2_Q = np.zeros(len(dsI))
    r_hat_I = np.zeros(len(dsI))
    r_hat_Q = np.zeros(len(dsI))
    v = np.zeros(len(dsI))
    mmuu = np.zeros(len(dsI))
    k = 0
    strobe = 0
    NCO_next = 0
    mu_next = 0

    for n in range(len(z)):
        NCO = NCO_next
        mu  = mu_next
        mu2 = mu*mu

        # Quadratic (2nd order) Farrow filter
        #     alpha = 0.5;
        #     h_I  = [ alpha*mu^2 - alpha*mu,  ...
        #             -alpha*mu^2 + (1+alpha)*mu,  ...
        #             -alpha*mu^2 + (alpha-1)*mu + 1, ...
        #              alpha*mu^2 - alpha*mu];
        # Cubic (3nd order) Farrow filter
        h_I  = [ (1/6)*mu**3 - (1/6)*mu, -0.5*  mu**3 + 0.5*mu**2 + mu,  \
                 0.5*  mu**3 - mu**2 - 0.5* mu + 1, -(1/6)*mu**3 + 0.5*mu**2 - (1/3)*mu]

        x_2_I[n] = h_I[0]*dsI[n] + h_I[1]*dsI[n-1] + h_I[2]*dsI[n-2] + h_I[3]*dsI[n-3]
        x_2_Q[n] = h_I[0]*dsQ[n] + h_I[1]*dsQ[n-1] + h_I[2]*dsQ[n-2] + h_I[3]*dsQ[n-3]

        if strobe == 1:
            # Timing Error Detector
            TEDout[n] = x_2_I[n-1]*(np.sign(x_2_I[n-2]) - np.sign(x_2_I[n])) +\
                        x_2_Q[n-1]*(np.sign(x_2_Q[n-2]) - np.sign(x_2_Q[n]))
        else:
            TEDout[n] = 0

        # Loop Filter
        v[n] = v[n-1] + (K1t + K2t)*TEDout[n] - K1t*TEDout[n-1]

        if strobe == 1:
            mmuu[k] = mu
            r_hat_I[k] = x_2_I[n]
            r_hat_Q[k] = x_2_Q[n]
            k = k+1

        # Mod 1 counter, delay,
        W = 1/N + v[n]
        NCO_next = NCO - W
        if NCO_next < 0:
            NCO_next = 1 + NCO_next
            strobe = 1
            mu_next = NCO/W
        else:
            strobe = 0
            mu_next = mu
        strobeSave[n] = strobe
        
    return r_hat_I+1j*r_hat_Q

def DD_carrier_sync(z, M, BnTs, zeta=0.707, mod_type = 'MPSK', type = 0, open_loop = False):
    """
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
    Kp = 2.7 # What is it for the different schemes and modes?
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
            e_phi[nn] = np.imag(z_prime[nn]/a_hat[nn])
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

def CostasLoop(samples, fs, order=2, debug=False):
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
    # loop_theta = 2*np.pi*fs
    # beta = 4*(loop_theta**2)/(1+np.sqrt(2)*loop_theta+loop_theta**2)
    # alpha = 2*np.sqrt(2)*loop_theta/(1+np.sqrt(2)*loop_theta+loop_theta**2)
    # print('beta, alpha',beta, alpha)
    
    alpha = 0.02 
    # beta = 0.009
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

def SRRC(alpha, SPS, span):
    '''
    alpha: roll-off factor between 0 and 1. 
           it indicates how quickly its frequency content transitions from its max to zero.
    SPS:   samples per symbol = sampling rate / symbol rate
    span:    the number of symbols in the filter to the left and right of the center tap.
		   the SRRC filter will have 2*span + 1 symbols in the impulse response.
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

def main(msgsend=False, debug=False):
    ########################### Transmission ###########################
    if msgsend:
        # Signal Generation
        # INPUT:  none
        # OUTPUT: binary data
        bitstring = "1110101011110110111000"
        databits = np.array([int(c) for c in bitstring])

        # Modulation
        # INPUT:  binary data
        # OUTPUT: BPSK modulated values
        symbol2value = {0: int(-1), 1: int(+1)}
        x = np.array([symbol2value[bit] for bit in databits])

        plt.figure()
        plt.plot(x, '-o')
        plt.xlabel('Sample',fontsize=15)
        plt.ylabel('BPSK modulated values',fontsize=15)

    # DSSS Generation
    # INPUT: gold code length
    # OUTPUT: gold code sequence
    gold_length = 63
    gold_code = gold_codes_dict[gold_length][0]*2-1

    # Up sampling
    # INPUT: gold code sequence
    # OUTPUT: up-sampled values at sampling rate samps_per_chip
    samps_per_chip = 6 # default
    DSSS = np.zeros(len(gold_code)*samps_per_chip)
    DSSS[::samps_per_chip] = gold_code

    if msgsend:
        # Spread Spectrum with DSSS
        # INPUT: PN sequence and modulated values
        # OUTPUT: spread values
        repeated_gold_code = np.tile(DSSS, len(x)) # repeat the gold_code sequence by len(xI) times
        MsgDSSS = repeated_gold_code * np.repeat(x, len(DSSS)) # short code [np.newaxis, :]


    # Pulse-shape filter
    # INPUT: DSSS values
    # OUTPUT: baseband transmit signal, signal_baseband
    # Note: np.convolve can only handle real values
    sps = samps_per_chip #int(gold_length*samps_per_chip) #samples per symbol (sps)=tx_rate/symbol_rate
    pulse = SRRC(0.5, sps, 5)
    if msgsend:
        signal_baseband = np.convolve(MsgDSSS, pulse,mode='same')#[:-(samps_per_chip*5)] #,mode='same'
        # signal_adjust = np.zeros(int(len(signal_baseband)-2*samps_per_chip*5))
        # signal_adjust[:(samps_per_chip*5)] = (signal_baseband[-(samps_per_chip*5):] + signal_baseband[(samps_per_chip*5):(2*samps_per_chip*5)])/2
        # signal_adjust[-(samps_per_chip*5):] = (signal_baseband[-(2*samps_per_chip*5):-(samps_per_chip*5)] +signal_baseband[:(samps_per_chip*5)])/2
        # signal_adjust[(samps_per_chip*5):-(samps_per_chip*5)] = signal_baseband[(samps_per_chip*5*2):-(samps_per_chip*5*2)]
        signal_baseband = np.tile(signal_baseband, 2)
    else:
        signal_baseband = np.convolve(DSSS, pulse) 

    # Up-convert
    # INPUT: signal_baseband, baseband signal
    # OUTPUT: signal, bandpass signal
    fc         = 3555e6
    n           = np.arange(len(signal_baseband))
    signal1      = np.sqrt(2)* signal_baseband * np.cos((2 * np.pi * fc)*n) -\
                  np.sqrt(2)*np.zeros(len(signal_baseband))* np.sin((2 * np.pi * fc)*n)
    
    # Add noise
    signal1 = signal1 + 0.2*np.random.rand(len(signal1))

    # Adding a Time Delay
    # Create and apply fractional delay filter
    delay = 0.4 # fractional delay, in samples
    N = 21 # number of taps
    n = np.arange(-N//2, N//2) # ...-3,-2,-1,0,1,2,3...
    h = np.sinc(n - delay) # calc filter taps
    h *= np.hamming(N) # window the filter to make sure it decays to 0 on both sides
    h /= np.sum(h) # normalize to get unity gain, we don't want to change the amplitude/power
    signal1 = np.convolve(signal1, h) # apply filter

    # Frequency offset
    fs = 2e6 # assume our sample rate is 1 MHz
    fo = 16e3 # simulate freq offset
    Ts = 1/fs # calc sample period
    t = np.arange(0, Ts*len(signal1), Ts) # create time vector
    signal = signal1 * np.exp(1j*2*np.pi*fo*t) # perform freq shift

    plt.figure()
    ax1 = plt.subplot(211)
    ax1.plot(signal1.real, label='In-phase') 
    ax1.plot(signal1.imag, label='Quadrature')
    plt.ylabel('Before Freq Offset') #received signal amplitude
    ax2 = plt.subplot(212)
    ax2.plot(signal.real, label='In-phase') 
    ax2.plot(signal.imag, label='Quadrature')
    plt.ylabel('After Freq Offset')

    ########################### Reception ###########################
    # Down-convert
    # INPUT: up_s, bandpass signal
    # OUTPUT: s, baseband signal
    fc          = 3555e6
    n           = np.arange(len(signal))
    signalRX    = np.sqrt(2)* signal * np.cos((2 * np.pi * fc)*n) - 1j* \
                  np.sqrt(2)* signal * np.sin((2 * np.pi * fc)*n)


    # Matched filter
    # INPUT: baseband samples signalRX
    # OUTPUT: matched-filtered samples, MFsamp
    # Note that: signal.correlate can handle complex samples
    #            np.convolve and scipy.signal.lfilter can handle real values only
    # Usage: MFsamp = scipy.signal.lfilter(pulse, 1, signalRX)
    #        MFsamp = sig.correlate(signalRX, pulse)[:-(len(pulse)-1)]
    pulse       = SRRC(0.5, sps, 5)
    MFsamp = (sig.lfilter(pulse, 1, signalRX.real) + 1j* \
             sig.lfilter(pulse, 1, signalRX.imag))
    # MFsamp = sig.correlate(signalRX, pulse)[:-(len(pulse)-1)]

    if debug:
        plt.figure()
        plt.plot(signal_baseband, '-o', label='pulse shaped signal')
        plt.plot(MFsamp[sps*5:]*(max(signal_baseband)/max(MFsamp)).real, '-x', label='matched filtering (real)')
        plt.xlabel('Sample',fontsize=15)
        plt.ylabel('matched-filtered signal',fontsize=15)
        plt.legend()

    # Coarse Frequency Offset Sync
    # INPUT: matched-filtered samples
    # OUTPUT: coarsely synced samples
    FreqsyncSamp = Freq_Offset_Correction(MFsamp, fs, order=2)

    # Clock Synchronization
    SymsyncSamp = clock_sync(FreqsyncSamp, sps, interpo_factor=16)

    # Fine Freq Synchronization
    FreqsyncSamp1, a_hat, e_phi, theta_h = DD_carrier_sync(SymsyncSamp, 2, 0.02)
    # FreqsyncSamp1 = CostasLoop(SymsyncSamp, fs, debug=False)
    # print('len(FreqsyncSamp1) len(DSSS)', len(FreqsyncSamp1), len(DSSS))
    print('a_hat, e_phi, theta_h', a_hat, e_phi, theta_h)
        
    # Despread
    # INPUT: matched-filtered signal y
    # OUTPUT: despread values
    # alternative: corr = scipy.signal.lfilter(DSSS, 1, MFsamp)[sps*5*2:]
    corr = sig.correlate(FreqsyncSamp1, DSSS)[len(DSSS)//2-1:-(len(DSSS)//2)]#[len(DSSS)-1:]

    # # Symbol Synchronization
    # # SymsyncSamp,e_tau = NDA_symb_sync(corr,len(DSSS),5,1e-3,zeta=0.707,I_ord=3)
    # SymsyncSamp = symb_sync(corr, len(DSSS), 1e-3,zeta=1)
    
    plt.figure()
    plt.plot(corr.real, '-o',label='real')
    plt.plot(corr.imag, '-+',label='imaginary')
    plt.xlabel('Sample',fontsize=15)
    plt.ylabel('correlation',fontsize=15)
    plt.legend()

    if msgsend:
        # DSSS peak detection
        # INPUT: despread samples
        # OUTPUT: Symbol Samples
        idx = np.argmax(np.abs(corr[:int(len(DSSS)*1.5)]))
        yhat = corr[idx::len(DSSS)]
        
        # numsymbol = len(databits)
        # if len(yhat)!=numsymbol:
        #     yhat = yhat[:numsymbol]
        
        plt.plot(np.arange(len(yhat))*len(DSSS)+idx, yhat.real, 'o', label='DSSS peaks')

        # Symbol decisions
        # INPUT: Symbol Samples yhat
        # OUTPUT: Bits
        bitsout = (yhat.real>0).astype(int)
    
        print('num of symbols: ', len(yhat))
        print('original string is:    ', databits)
        print('demodulated string is: ', bitsout)
        if len(bitsout)==len(databits):
            ber = sum(databits!=bitsout)/len(databits)
            print('bit error rate: {}%'.format(ber*100))
        else:
            print('length of detected bits does not match')
    
    plt.show()

if __name__=="__main__":
    main(msgsend=True)
