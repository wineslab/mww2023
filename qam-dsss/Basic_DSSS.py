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

def main():
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

    # DSSS
    # INPUT: PN sequence and modulated values
    # OUTPUT: spread values
    gold_length = 63
    samps_per_chip = 6 # default

    gold_code = gold_codes_dict[gold_length][0]*2-1
    # long_gold_code = np.repeat(gold_code, samps_per_chip) # Repeat elements of an array
    long_gold_code = np.zeros(len(gold_code)*samps_per_chip)
    long_gold_code[::samps_per_chip] = gold_code
    repeated_gold_code = np.tile(long_gold_code, len(x)) # repeat the gold_code sequence by len(xI) times
    DSSS_x = repeated_gold_code* np.repeat(x, len(long_gold_code)) # short code [np.newaxis, :]

    # Pulse-shape filter
    # INPUT: DSSS values
    # OUTPUT: baseband transmit signal x
    sps = samps_per_chip #int(gold_length*samps_per_chip) #samples per symbol (sps)=tx_rate/symbol_rate
    pulse = SRRC(0.5, sps, 5)
    pulse_x = np.convolve(DSSS_x, pulse) # np.convolve can only handle real values

    # Up-convert
    # INPUT: pulse_x, baseband signal
    # OUTPUT: signal, bandpass signal
    f_0         = 0.35
    n           = np.arange(len(pulse_x))
    signal      = np.sqrt(2)* pulse_x * np.cos((2 * np.pi * f_0)*n) -\
                  np.sqrt(2)*np.zeros(len(pulse_x))* np.sin((2 * np.pi * f_0)*n)
    
    signal = signal + 0.2*np.random.rand(len(signal));

    # plt.figure()
    # plt.plot(signal, '-o')
    # # plt.ylim([-1.5, 1.5])
    # plt.xlabel('Sample',fontsize=15)
    # plt.ylabel('bandpass signal',fontsize=15)

    ########################### RX ###########################
    # Down-convert
    # INPUT: up_s, bandpass signal
    # OUTPUT: s, baseband signal
    f_0         = 0.35
    n           = np.arange(len(pulse_x))
    sigrx       = np.sqrt(2)* signal * np.cos((2 * np.pi * f_0)*n)

    # Matched filter
    # INPUT: baseband transmitted signal sigrx
    # OUTPUT: matched-filtered signal y
    pulse       = SRRC(0.5, sps, 5)
    # y           = sig.correlate(sigrx, pulse)[:-(len(pulse)-1)]
    y       = scipy.signal.lfilter(pulse, 1, sigrx) 

    plt.figure()
    plt.plot(pulse_x, '-o', label='pulse shaped signal')
    plt.plot(y[sps*5:]*(max(pulse_x)/max(y)), '-x', label='matched filtering')
    plt.xlabel('Sample',fontsize=15)
    plt.ylabel('matched-filtered signal',fontsize=15)
    plt.legend()

    # Despread
    # INPUT: matched-filtered signal y
    # OUTPUT: despread values
    corr = sig.correlate(y, long_gold_code)[sps*5*2:]
    # corr = scipy.signal.lfilter(long_gold_code, 1, y)[sps*5*2:]
    
    # DSSS peak detection
    # INPUT: despread samples
    # OUTPUT: Symbol Samples
    yhat = corr[len(long_gold_code)-1::len(long_gold_code)]

    plt.figure()
    plt.plot(corr[len(long_gold_code)-1:], '-o') #
    plt.plot(np.arange(len(yhat))*len(long_gold_code), yhat, 'o', label='DSSS peaks')
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
        print('bit error rate: {}%'.format(ber*100))
    else:
        print('length of detected bits does not match')
    
    plt.show()
    
def test():
    barker = np.array([int(b)*2-1 for b in "10110111000"])
    pulse = SRRC(0.5, 6, 5)
    pulse_x = np.convolve(barker, pulse)

    plt.figure()
    plt.plot(pulse_x, '-o')
    plt.xlabel('Sample',fontsize=15)
    plt.ylabel('Value',fontsize=15)

    plt.figure()
    plt.plot(pulse, '-*')
    plt.show()

    


if __name__=="__main__":
    main()