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

def symbol_sync(samples, sps):
    mu = 0 # initial estimate of phase of sample
    out = np.zeros(len(samples) + 10, dtype=np.complex)
    out_rail = np.zeros(len(samples) + 10, dtype=np.complex) # stores values, each iteration we need the previous 2 values plus current value
    i_in = 0 # input samples index
    i_out = 2 # output index (let first two outputs be 0)
    while i_out < len(samples) and i_in+16 < len(samples):
        out[i_out] = samples[i_in + int(mu)] # grab what we think is the "best" sample
        out_rail[i_out] = int(np.real(out[i_out]) > 0) + 1j*int(np.imag(out[i_out]) > 0)
        x = (out_rail[i_out] - out_rail[i_out-2]) * np.conj(out[i_out-1])
        y = (out[i_out] - out[i_out-2]) * np.conj(out_rail[i_out-1])
        mm_val = np.real(y - x)
        mu += sps + 0.3*mm_val
        i_in += int(np.floor(mu)) # round down to nearest int since we are using it as an index
        mu = mu - np.floor(mu) # remove the integer part of mu
        i_out += 1 # increment output index
    out = out[2:i_out] # remove the first two, and anything after i_out (that was never filled out)
    samples = out # only include this line if you want to connect this code snippet with the Costas Loop later on
    return samples

def SRRC(alpha, SPS, span):
    '''
    alpha: roll-off factor between 0 and 1. 
           it indicates how quickly its frequency content transitions from its max to zero.
    SPS:   samples per symbol = sampling rate / symbol rate
    span:    the number of symbols in the filter to the left and right of the center tap.
		   the SRRC filter will have 2*span + 1 symbols in the impulse response.
    '''
    if ((int(SPS) - SPS) > 1e-10):
        raise ValueError('SRRC design: SPS must be an integer')
    if ((int(span) - span) > 1e-10):
        raise ValueError('SRRC design: span must be an integer')
    if (alpha < 0):
       raise ValueError('SRRC design: alpha must be between 0 and 1')
    if (SPS <= 1):
        raise ValueError('SRRC design: SPS must be greater than 1')

    n = np.arange(-SPS*span, SPS*span+1)+1e-9

    weights = (1/np.sqrt(SPS))*( (np.sin(np.pi*n*(1-alpha)/SPS)) + \
              (4*alpha*n/SPS)*(np.cos(np.pi*n*(1+alpha)/SPS)) ) /\
              ( (np.pi*n/SPS) * (1 - (4*alpha*n/SPS)**2) )

    return weights

def main(msgsend=False):
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
    sps = samps_per_chip #int(gold_length*samps_per_chip) #samples per symbol (sps)=tx_rate/symbol_rate
    pulse = SRRC(0.5, sps, 5)
    if msgsend:
        signal_baseband = np.convolve(MsgDSSS, pulse) # np.convolve can only handle real values
    else:
        signal_baseband = np.convolve(DSSS, pulse) # np.convolve can only handle real values

    # Up-convert
    # INPUT: signal_baseband, baseband signal
    # OUTPUT: signal, bandpass signal
    f_0         = 0.35
    n           = np.arange(len(signal_baseband))
    signal      = np.sqrt(2)* signal_baseband * np.cos((2 * np.pi * f_0)*n) -\
                  np.sqrt(2)*np.zeros(len(signal_baseband))* np.sin((2 * np.pi * f_0)*n)
    
    signal = signal + 0.2*np.random.rand(len(signal));

    ########################### RX ###########################
    # Down-convert
    # INPUT: up_s, bandpass signal
    # OUTPUT: s, baseband signal
    f_0         = 0.35
    n           = np.arange(len(signal_baseband))
    signalRX       = np.sqrt(2)* signal * np.cos((2 * np.pi * f_0)*n)

    # Matched filter
    # INPUT: baseband transmitted signal signalRX
    # OUTPUT: matched-filtered signal y
    # Note that: signal.correlate can handle complex samples
    #            np.convolve and scipy.signal.lfilter can handle real values only
    # Usage: corr = scipy.signal.lfilter(pulse, 1, signalRX)
    #        corr = sig.correlate(signalRX, pulse)
    pulse       = SRRC(0.5, sps, 5)
    corr = scipy.signal.lfilter(pulse, 1, signalRX)
    # corr = sig.correlate(signalRX, pulse)[:-(len(pulse)-1)]

    plt.figure()
    plt.plot(signal_baseband, '-o', label='pulse shaped signal')
    plt.plot(corr[sps*5:]*(max(signal_baseband)/max(corr)), '-x', label='matched filtering')
    plt.xlabel('Sample',fontsize=15)
    plt.ylabel('matched-filtered signal',fontsize=15)
    plt.legend()

    # Despread
    # INPUT: matched-filtered signal y
    # OUTPUT: despread values
    # alternative: corr1 = scipy.signal.lfilter(DSSS, 1, corr)[sps*5*2:]
    corr1 = sig.correlate(corr, DSSS)[sps*5*2:]
    
    plt.figure()
    plt.plot(corr1, '-o')
    plt.xlabel('Sample',fontsize=15)
    plt.ylabel('correlation',fontsize=15)

    if msgsend:
        # DSSS peak detection
        # INPUT: despread samples
        # OUTPUT: Symbol Samples
        yhat = corr1[len(DSSS)-1::len(DSSS)]

        plt.figure()
        plt.plot(corr1[len(DSSS)-1:], '-o')
        plt.plot(np.arange(len(yhat))*len(DSSS), yhat, 'o', label='DSSS peaks')
        plt.xlabel('Sample',fontsize=15)
        plt.ylabel('correlation',fontsize=15)
        plt.legend()

        # Symbol decisions
        # INPUT: Symbol Samples yhat
        # OUTPUT: Bits
        bitsout = (yhat>0).astype(int)
    
        print('num of symbols: ', len(yhat))
        print('original string is:    ', databits)
        print('demodulated string is: ', bitsout)
        if len(bitsout)==len(databits):
            ber = sum(databits!=bitsout)/len(databits)
            print('bit error rate', ber)
        else:
            print('length of detected bits does not match')
    
    plt.show()

if __name__=="__main__":
    main(msgsend=True)
