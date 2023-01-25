import h5py
import json
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
from utm import from_latlon
from dateutil import parser
from datetime import datetime, timedelta
from IPython import embed
from dsss.gold import *
import scipy.signal as sig

def convert_gps_to_utm(gps_coordinates, origin_to_subtract=None):
    if isinstance(gps_coordinates, (np.ndarray, np.generic)):
        lat = gps_coordinates[:,0]
        lon = gps_coordinates[:,1]
    else:
        lat, lon = gps_coordinates
    x,y,_,_ = from_latlon(lat, lon)
    if origin_to_subtract is not None:
        x -= origin_to_subtract[0]
        y -= origin_to_subtract[1]
    return np.vstack((x, y)).T

GPS_LOCATIONS = {
    "cbrssdr1-browning-comp": (40.76627,-111.84774),
    "cellsdr1-browning-comp": (40.76627,-111.84774),
    "cbrssdr1-hospital-comp": (40.77105,-111.83712),
    "cellsdr1-hospital-comp": (40.77105,-111.83712),
    "cbrssdr1-smt-comp": (40.76740,-111.83118),
    "cellsdr1-smt-comp": (40.76740,-111.83118),
    "cbrssdr1-ustar-comp": (40.76895,-111.84167),
    "cellsdr1-ustar-comp": (40.76895,-111.84167),
    "cbrssdr1-bes-comp": (40.76134,-111.84629),
    "cellsdr1-bes-comp": (40.76134,-111.84629),
    "cbrssdr1-honors-comp": (40.76440,-111.83699),
    "cellsdr1-honors-comp": (40.76440,-111.83699),
    "cbrssdr1-fm-comp": (40.75807,-111.85325),
    "cellsdr1-fm-comp": (40.75807,-111.85325),
    "moran-nuc1-b210": (40.77006,-111.83784),
    "moran-nuc2-b210": (40.77006,-111.83784),
    "ebc-nuc1-b210": (40.76770,-111.83816),
    "ebc-nuc2-b210": (40.76770,-111.83816),
    "guesthouse-nuc1-b210": (40.76627,-111.83632),
    "guesthouse-nuc2-b210": (40.76627,-111.83632),
    "humanities-nuc1-b210": (40.76486,-111.84319),
    "humanities-nuc2-b210": (40.76486,-111.84319),
    "web-nuc1-b210": (40.76791,-111.84561),
    "web-nuc2-b210": (40.76791,-111.84561),
    "bookstore-nuc1-b210": (40.76414,-111.84759),
    "bookstore-nuc2-b210": (40.76414,-111.84759),
    "sagepoint-nuc1-b210": (40.76278,-111.83061),
    "sagepoint-nuc2-b210": (40.76278,-111.83061),
    "law73-nuc1-b210": (40.76160,-111.85185),
    "law73-nuc2-b210": (40.76160,-111.85185),
    "garage-nuc1-b210": (40.76148,-111.84201),
    "garage-nuc2-b210": (40.76148,-111.84201),
    "madsen-nuc1-b210": (40.75786,-111.83634),
    "madsen-nuc2-b210": (40.75786,-111.83634),
    "cnode-wasatch-dd-b210": (40.77107659230161, -111.84315777334905),
    "cnode-mario-dd-b210": (40.77281166195038, -111.8409002868012),
    "cnode-moran-dd-b210": (40.77006,-111.83872),
    "cnode-guesthouse-dd-b210": (40.76769,-111.83609),
    "cnode-ustar-dd-b210": (40.76851381022761, -111.8404502186636), 
    "cnode-ebc-dd-b210": (40.76720,-111.83810),
}

origin = np.array([ 426446.25, 4511295.75])
converted_coords = {key:convert_gps_to_utm(GPS_LOCATIONS[key], origin) for key in GPS_LOCATIONS}

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

def srrcDesign ( SPS, span, beta ):
	invalidParameter = False
	if (SPS <= 1):
		print('srrcDesign.py: SPS must be greater than 1')
		invalidParameter = True
	if ((int(SPS) - SPS) > 1e-10):
		print('srrcDesign.py: SPS must be an integer')
		invalidParameter = True
	if (span < 1):
		print('srrcDesign.py: span must be greater than or equal to 1')
		invalidParameter = True
	if ((int(span) - span) > 1e-10):
		print('srrcDesign.py: span must be an integer')
		invalidParameter = True
	if (beta < 0):
		print('srrcDesign.py: beta must be greater than or equal to 0')
		invalidParameter = True

	# check to see if a bad parameter was passed in
	if (invalidParameter):
		# return empty filter weights
		return []
	else: # parameters valid, proceed with design
		# build the time indexing
		nList = np.arange(-span*SPS,(span*SPS)+1)
		# pre-allocate memory for weights
		weights = np.zeros(len(nList))
		# compute the weights on a sample by sample basis
		for index in range(len(nList)):
			# select the time index
			n = nList[index]
			# design equations
			if (n == 0):
				weights[index] = (1/np.sqrt(SPS))*((1-beta) + (4*beta/np.pi))
			elif (np.abs(n*4*beta) == SPS):
				weights[index] = (beta/np.sqrt(2*SPS))*( (1+(2/np.pi))*np.sin(np.pi/(4*beta)) + (1-(2/np.pi))*np.cos(np.pi/(4*beta)) )
			else:
				weights[index] = (1/np.sqrt(SPS))*( (np.sin(np.pi*n*(1-beta)/SPS)) + (4*beta*n/SPS)*(np.cos(np.pi*n*(1+beta)/SPS)) ) / ( (np.pi*n/SPS) * (1 - (4*beta*n/SPS)**2) )
		# scale the weights to 0 dB gain at f=0
		weights = weights/np.sqrt(SPS)

		return weights


def get_gold_code(nbits, code_id):
    return gold_codes_dict[nbits][code_id].astype(np.complex64)


def explore_gold_data(data_folder='data', data_date='', correlate=True):
    """
    data_folder: The directory of the Shout_meas_... folders
    data_date: The date of the data recorded, for filtering
    """
    data_folder = 'data'
    data_date = '12-22-2022'

    rx_data = {}
    measurement_folders = os.listdir(data_folder)
    duplicate = 0

    # Shortcut variables for convenience
    ustar = 'cbrssdr1-ustar-comp'
    hospital = 'cbrssdr1-hospital-comp'
    fm = 'cbrssdr1-fm-comp'
    honors = 'cbrssdr1-honors-comp'
    bes = 'cbrssdr1-bes-comp'
    smt = 'cbrssdr1-smt-comp'
    guesthouse = 'guesthouse-nuc2-b210'
    humanities = 'humanities-nuc2-b210'

    all_samples = {}
    for folder in measurement_folders:
        if 'Shout_meas_' + data_date not in folder: continue
        config_file = os.path.join(data_folder,folder, 'save_iq_w_tx_gold.json')
        config_dict = json.load(open(config_file))[0]
        nsamps = config_dict['nsamps']
        rxrate = config_dict['rxrate']
        rxfreq = config_dict['rxfreq']
        gold_id = config_dict['gold_id']
        gold_length = config_dict['gold_length']
        if 'samps_per_chip' not in config_dict:
            samps_per_chip = 2
        else:
            samps_per_chip = config_dict['samps_per_chip']
        gold_code = get_gold_code(gold_length, gold_id) * 2 - 1
        long_gold_code = np.repeat(gold_code, samps_per_chip)
        rxrepeat = config_dict['rxrepeat']
        datafile = os.path.join(data_folder, folder,'measurements.hdf5')

        try:
            data = h5py.File(datafile, 'r')
        except:
            continue
        print(datafile)

        def save_measurements(obj, measurement_types, data_array):
            if 'rxsamples' in measurement_types:
                if config_dict['return_iq']:
                    samples = np.array(obj['rxsamples']).squeeze()
                    if 'bus' in rx_node:
                        locs = np.array(obj['rxloc']).squeeze()
                    else:
                        loc = GPS_LOCATIONS[rx_node]
                        locs = np.array([ loc] * len(samples))
                    for samp, loc in zip(samples, locs):
                        pulse = srrcDesign(samps_per_chip, 5, 0.5)

                        #samp = butter_filt_with_shift(samp, 0, 2e6, 2e6)
                        MFsamps = np.convolve(pulse, samp, mode='same')
                        corr = sig.correlate(MFsamps, long_gold_code, mode='same')
                        data_array.append([loc[:2], corr])
                else:
                    peaks = np.array(obj['rxsamples']).squeeze()

        cmd = [arg for arg in data.keys() if 'save' in arg][0]
        timestamps = list(data[cmd].keys() )
        for timestamp in timestamps:
            tx_infos = list(data[cmd][timestamp].keys() )
            for tx_info in tx_infos:
                if not tx_info in all_samples:
                    all_samples[tx_info] = {}
                if tx_info != 'wo_tx':
                    tx_gains = list(data[cmd][timestamp][tx_info].keys() )
                    for tx_gain in tx_gains:
                        #if tx_gain <= '30.0': continue
                        rx_gains = list(data[cmd][timestamp][tx_info][tx_gain].keys() )
                        for rx_gain in rx_gains:
                            rx_nodes = list(data[cmd][timestamp][tx_info][tx_gain][rx_gain].keys() )
                            for rx_node in rx_nodes:
                                #if rx_node == hospital:
                                #    import pdb
                                #    pdb.set_trace()
                                if not rx_node in all_samples[tx_info]:
                                    all_samples[tx_info][rx_node] = []
                                measurement_types = list(data[cmd][timestamp][tx_info][tx_gain][rx_gain][rx_node].keys() )
                                obj = data[cmd][timestamp][tx_info][tx_gain][rx_gain][rx_node]
                                save_measurements(obj, measurement_types, all_samples[tx_info][rx_node])
                else: # No transmitter active, we're actually down one more level:
                    rx_gains = list(data[cmd][timestamp][tx_info].keys() )
                    for rx_gain in rx_gains:
                        rx_nodes = list(data[cmd][timestamp][tx_info][rx_gain].keys() )
                        for rx_node in rx_nodes:
                            if not rx_node in all_samples[tx_info]:
                                all_samples[tx_info][rx_node] = []
                            #if rx_node == hospital:
                            #    import pdb
                            #    pdb.set_trace()
                            measurement_types = list(data[cmd][timestamp][tx_info][rx_gain][rx_node].keys() )
                            obj = data[cmd][timestamp][tx_info][rx_gain][rx_node]
                            save_measurements(obj, measurement_types, all_samples[tx_info][rx_node])


    locs = {tx_node: {rx_node:np.array([samp[0] for samp in all_samples[tx_node][rx_node]]) for rx_node in all_samples[tx_node]} for tx_node in all_samples}
    corrs = {tx_node: {rx_node:np.array([samp[1] for samp in all_samples[tx_node][rx_node]]) for rx_node in all_samples[tx_node]} for tx_node in all_samples}
    #iq = {tx_node: {rx_node:np.array([samp[2] for samp in all_samples[tx_node][rx_node]]) for rx_node in all_samples[tx_node]} for tx_node in all_samples}
    image = plt.imread("../map_img.png")
    #Corners: 
    BL = (40.757480731726524, -111.85367459265498)
    TR = (40.77376508414718, -111.82576682152072)

    def plot_on_map(rx_device, tx_device, savefig=False):
        tx_loc = GPS_LOCATIONS[tx_device]
        if 'bus' in rx_device:
            plt.figure(figsize=(10,10))
            plt.imshow(image, extent=(BL[1], TR[1], BL[0], TR[0]), zorder=1, alpha=0.5,aspect='equal')
            plt.scatter(tx_loc[1], tx_loc[0], marker='x', s=50)
            plt.scatter(data[:,2], data[:,1],c=data[:,0], zorder=2, cmap='plasma', vmin=data[:,0].min(), vmax=data[:,0].max())
            plt.tight_layout()
            if savefig:
                plt.savefig('rx_%s__tx_%s.png' % (rx_device, tx_device) )
                plt.cla()
            else:
                plt.show()


    bit_string='11110010'
    #for loc in rx_data:
    #    if 'bus' not in loc: continue
    #    rx_data[loc] = np.vstack(rx_data[loc])
    #    rx_data[loc] = rx_data[loc][rx_data[loc][:,0] != 0]
    #    rx_data[loc] = rx_data[loc][rx_data[loc][:,1] != 0]
    #    plot_on_map(rx_data[loc], loc, savefig=True)
    #    plot_on_map(rx_data[loc], loc, savefig=False)
    #    np.savetxt(loc+'.txt', rx_data[loc], header='RSSI,Latitude,Longitude', delimiter=',', fmt='%.15f')

    """
    Overall approach for detection:
    1. Get the appropriate base shift and frequency scaling, so our data is all contained in the real domain.
    * Get the peaks. Remove the first and last. First scale the base shift to maximize the mean of the first 5 abs(peaks), (ignoring the first), 
        then add the linear scaling until median(abs(peaks)) is maximized.
    * Check the average of the first peaks, and multiply by negative 1 if the value is netagive.
    2. Get statistics
    * Template match with our known bit string. Count the number of matching bits as we slide across. Should peak at the length of the string. Provide stats on how often we exactly match the bit string and how many bit failures we have.
    * Record SNR, which can be easily seen as power of signal when we have all matching bits vs power of non-peak values.
    """
    def apply_shift(samps, base=0, shift=0):
        return samps * np.power(np.e, -1j*2*np.pi*np.linspace(base, base+shift, len(samps)))

    def plot_shift(samps, use_phase=False, force_base_bounds=None, force_shift_bounds=None):
        fig, ax = plt.subplots()
        line1, = ax.plot(samps.real)
        line2, = ax.plot(samps.imag)
        peak_locs = sig.find_peaks(abs(samps), distance=len(long_gold_code) - 4)[0]
        line3 = ax.scatter(peak_locs, np.angle(samps[peak_locs])/10, marker='.', alpha=0.5, c='black')
        fig.subplots_adjust(bottom=0.4)
        if use_phase:
            base_bounds = [-3,3]
            shift_bounds = [-0.01,0.01]
        else:
            base_bounds = [0,1]
            shift_bounds = [-40,40]
        if force_base_bounds is not None:
            base_bounds = force_base_bounds
        if force_shift_bounds is not None:
            shift_bounds = force_shift_bounds
        axbase = fig.add_axes([0.1, 0.15, 0.8, 0.03])
        axshift = fig.add_axes([0.1, 0.05, 0.8, 0.03])
        base_slider = Slider(
            ax=axbase,
            label='Base',
            valmin=base_bounds[0],
            valmax=base_bounds[1],
            valinit=0,
        )
        shift_slider = Slider(
            ax=axshift,
            label='Shift',
            valmin=shift_bounds[0],
            valmax=shift_bounds[1],
            valinit=0,
        )
        def update(val):
            if use_phase:
                new_samps = phase_apply_shift(samps, base_slider.val, shift_slider.val)
            else:
                new_samps = apply_shift(samps, base_slider.val, shift_slider.val)
            line1.set_ydata(new_samps.real)
            line2.set_ydata(new_samps.imag)
            line3.set_offsets(np.vstack((peak_locs, np.angle(new_samps[peak_locs])/len(bit_string))).T )
            fig.canvas.draw_idle()
        base_slider.on_changed(update)
        shift_slider.on_changed(update)
        plt.show()

    def phase_apply_shift(samps, base=0, shift=0):
        return samps * np.power(np.e, -1j*(base + shift*np.arange(len(samps))))

    def phase_correct_freq_drift(samps, peak_locs, base=None, shift=None, eps=0.01, angle_mod=-np.pi):
        peak_locs = peak_locs[1:-1]
        peaks = samps[peak_locs]
        if angle_mod == 0:
            diffs = (np.diff( np.angle(peaks))) / len(long_gold_code)
        else:
            diffs = (np.diff( np.angle(peaks))  % angle_mod) / len(long_gold_code)
        count, bins = np.histogram(diffs)
        max_bin = count.argmax()
        low, high = bins[max_bin:max_bin+2]
        good_shift = diffs[ (low < diffs) * (diffs < high)].mean()
        new_samps = phase_apply_shift(samps, 0, good_shift)
        best_shift = good_shift + np.angle((np.conjugate(new_samps[peak_locs][:-len(bit_string)])* new_samps[peak_locs][len(bit_string):]).sum()) / (len(long_gold_code)  * len(bit_string))
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
        """ Find sequence in an array using NumPy only.

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


    def correct_freq_drift(samps, peak_locs, bit_string):
        bits = np.array([int(c) for c in bit_string])
        new_samples, new_locs, new_params = phase_correct_freq_drift(samps,peak_locs, angle_mod=-np.pi)
        signs = ((np.sign(new_samples[new_locs].real) + 1) / 2)
        new_samples_tmp, new_locs_tmp, new_params_tmp = phase_correct_freq_drift(samps,peak_locs, angle_mod=np.pi)
        signs_tmp = ((np.sign(new_samples_tmp[new_locs_tmp].real) + 1) / 2)
        if len(search_sequence_numpy(signs, bits)) < len(search_sequence_numpy(signs_tmp, bits)):
            new_samples = new_samples_tmp
            new_locs = new_locs_tmp
            new_params = new_params_tmp
        return new_samples, new_locs, new_params
        
        #base_range = [0,0.6]
        #shift_range = [-10,20]
        #if base is not None:
        #    if isinstance(base, Iterable):
        #        base_range = base
        #    else:
        #        base_range = [base-100*eps, base+100*eps]
        #if shift is not None:
        #    if isinstance(shift, Iterable):
        #        shift_range = shift
        #    else:
        #        shift_range = [shift-100*eps, shift+100*eps]
        #peak_locs = peak_locs[1:-1]
        #peaks = samps[peak_locs]
        #def local_apply_shift(base=0, shift=0j):
        #    return peaks * np.power(np.e, -1j*2*np.pi*np.linspace(base, base+shift, len(samps))[peak_locs])

        ## Find the base that maximizes the first peak.
        #base_search_scale=10
        #shift_search_scale=10
        ## Coarse tuning
        #best_base_score = abs(peaks.real)[:3].mean()
        #best_base = 0
        #for base in np.arange(base_range[0], base_range[1], base_search_scale*eps):
        #    new_peaks = local_apply_shift(base)
        #    new_score = abs(new_peaks.real)[:3].mean()
        #    if new_score > best_base_score:
        #        best_base_score = new_score
        #        best_base = base
        #best_shift_score = np.median(abs(peaks.real))
        #best_shift = 0
        #for shift in np.arange(shift_range[0], shift_range[1], shift_search_scale*eps):
        #    new_peaks = local_apply_shift(best_base, shift)
        #    new_score = np.median(abs(new_peaks.real))
        #    if new_score > best_shift_score:
        #        best_shift_score = new_score
        #        best_shift = shift 
        ## Fine tuning
        #for base in np.arange(best_base-base_search_scale*eps, best_base+base_search_scale*eps, eps):
        #    new_peaks = local_apply_shift(base, best_shift)
        #    new_score = abs(new_peaks.real)[:3].mean()
        #    if new_score > best_base_score:
        #        best_base_score = new_score
        #        best_base = base
        #for shift in np.arange(best_shift-shift_search_scale*eps, best_shift+shift_search_scale*eps, eps):
        #    new_peaks = local_apply_shift(best_base, shift)
        #    new_score = np.median(abs(new_peaks.real))
        #    if new_score > best_shift_score:
        #        best_shift_score = new_score
        #        best_shift = shift 
        #new_peaks = local_apply_shift(best_base, best_shift)
        #mult = -1 if np.median(new_peaks) < 0 else 1
        #new_samps = apply_shift(samps*mult, best_base, best_shift)
        #new_peaklocs = sig.find_peaks(abs(new_samps.real), distance=len(long_gold_code)-4, height=[0,np.median(abs(new_peaks.real))*3])[0]
        ##new_peaklocs = sig.find_peaks(abs(new_samps.real), distance=len(long_gold_code)-4)[0]
        #return new_samps, new_peaklocs, (best_base, best_shift, mult)
        
    def plot_sync_message(samps0): 
        plocs0 = sig.find_peaks(abs(samps0), distance=len(long_gold_code)-4)[0]
        new_samps, plocs1, _ = correct_freq_drift(samps0, plocs0, bit_string)
        plt.plot(abs(samps0), alpha=0.7, label='Old')
        plt.plot(new_samps.real, label='New Real')
        plt.scatter(plocs0, new_samps[plocs0].real,c='yellow')
        plt.scatter(plocs1, new_samps[plocs1].real,c='tab:green')
        plt.legend()
        plt.show()

    def plot_peaks(source_name=ustar, zoom=False, sample_bounds=[0,100], num_rows=4, num_cols=3, **peak_kwargs):
        fig, axs_cbrs = plt.subplots(num_rows,num_cols,sharex=True,sharey=True, figsize=(17,10))
        results = {}
        for ax, key in zip(axs_cbrs.flatten(), corrs[source_name].keys()):
            print('here')
            source_loc = converted_coords[source_name]
            dest_loc = converted_coords[key]
            dist = np.linalg.norm(source_loc - dest_loc)
            dat = corrs[source_name][key]
            current_ind = 0
            dflat = dat.flatten()
            print(key, dist)
            for samples in dat[sample_bounds[0]:sample_bounds[1]]:
                peak_locs = sig.find_peaks(abs(samples), distance=len(long_gold_code)-4, **peak_kwargs)[0]
                try:
                    new_samples, new_locs, _ = correct_freq_drift(samples,peak_locs,bit_string)
                    ax.scatter( new_locs+current_ind, new_samples.real[new_locs], c='tab:orange')
                    ax.plot(np.arange(0, len(new_samples))+current_ind, abs(new_samples), c='tab:green',alpha=0.7)
                    ax.plot(np.arange(0, len(new_samples))+current_ind, new_samples.real, c='tab:blue',alpha=1)
                except KeyboardInterrupt:
                    raise
                except:
                    pass
                    ax.scatter( peak_locs+current_ind, samples.real[peak_locs], c='tab:orange')
                    ax.plot(np.arange(0, len(samples))+current_ind, abs(samples), c='tab:green',alpha=0.7)
                    ax.plot(np.arange(0, len(samples))+current_ind, samples.real, c='tab:blue',alpha=1)
                #    ax.plot(np.arange(0, len(samples))+current_ind, samples.imag, c='tab:green',alpha=0.7)
                #else:
                current_ind += len(samples)
            ax.set_title(key+' Distance: %.0f m' % dist)
        if zoom:
            ax.set_xlim(390000,405000)
        plt.show()
        #return results

    def get_stats(samples, peak_locs, bit_string):
        if samples.max() == 0:
            return { 'bit_error_rate': 1, 'snr':0, 'power':0}
        peaks = samples[peak_locs]
        if isinstance(bit_string, np.ndarray):
            bits = bit_string.copy()
        elif isinstance(bit_string, str):
            bits = np.array([int(c) for c in bit_string])
        if 0 in bits:
            bits = bits * 2 - 1
        bit_matches = sig.correlate(np.sign(peaks.real), bits, mode='same') # mode='same')
        locs = sig.find_peaks(bit_matches, distance=len(bits))[0]
        error_rates = 1 - bit_matches[locs][1:-1] / len(bits)
        inds = np.where(bit_matches == bit_matches.max() )[0]
        noise_mask = np.ones(len(samples), dtype=bool)
        noise_mask[:peak_locs[0]] = False
        noise_mask[peak_locs[-1]:] = False
        noise_mask[peak_locs] = False
        perfect_peak_values = abs(np.concatenate([peaks.real[i - len(bits)//2:i+len(bits)//2] for i in inds]))
        noise_values = samples[noise_mask]
        stats = {
            'bit_error_rate': 1 if np.isnan(error_rates.mean()) else error_rates.mean(),
            'snr': perfect_peak_values.mean() / abs(noise_values).mean(),
            'power': 10.0 * np.log10(np.sum(np.square(np.abs(perfect_peak_values)))/len(perfect_peak_values))
        }
        return stats

    def plot_stats(bit_string, source_name=ustar):
        all_stats = {source_name:{}}
        for loc in corrs[source_name]:
            all_stats[source_name][loc] = []
            for samps0 in corrs[source_name][loc]:
                if samps0.max() == 0: continue
                plocs0 = sig.find_peaks(abs(samps0), distance=len(long_gold_code)-4)[0]
                samples, peak_locs, _ = correct_freq_drift(samps0, plocs0, bit_string)
                stats = get_stats(samples, peak_locs, bit_string)
                all_stats[source_name][loc].append(stats)
        fig, axs = plt.subplots(1,3, sharex=True)
        index = 0
        markers = ['*', 'v', '^', '.', 'o', '1', '2', '3', '4']
        for loc in all_stats[source_name]:
            ber = np.array([data['bit_error_rate'] for data in all_stats[source_name][loc]])
            bad_inds = np.isnan(ber)
            ber = ber[~bad_inds]
            snr = np.array([data['snr'] for data in all_stats[source_name][loc]])
            power = np.array([data['power'] for data in all_stats[source_name][loc]])
            axs[0].plot(np.where(~bad_inds)[0], ber, label=loc, marker=markers[index])
            axs[1].plot(snr, label=loc, marker=markers[index])
            axs[2].plot(power, label=loc, marker=markers[index])
            index += 1
        axs[0].set_ylabel('BER [%]')
        axs[1].set_ylabel('SNR (Linear)')
        axs[2].set_ylabel('RSS [dB]')
        axs[0].set_title('BER')
        axs[1].set_title('SNR (Linear)')
        axs[2].set_title('RSS [dB]')
        handles, labels = axs[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='upper center', ncols=3)
        plt.show()

    embed()
