import h5py
import json
import os
import numpy as np
from sigutils import butter_filt_with_shift, get_avg_power
import matplotlib.pyplot as plt
from IPython import embed

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

data_folder = 'data'
data_date = ''

rx_data = {}
measurement_folders = os.listdir(data_folder)
duplicate = 0

ustar = 'cbrssdr1-ustar-comp'
hospital = 'cbrssdr1-hospital-comp'
fm = 'cbrssdr1-fm-comp'
honors = 'cbrssdr1-honors-comp'
bes = 'cbrssdr1-bes-comp'
smt = 'cbrssdr1-smt-comp'

all_samples = {}
for folder in measurement_folders:
    if 'Shout_meas_' + data_date not in folder: continue
    config_file = os.path.join(data_folder,folder, 'save_iq_w_tx_cw.json')
    config_dict = json.load(open(config_file))[0]
    nsamps = config_dict['nsamps']
    rxrate = config_dict['rxrate']
    rxfreq = config_dict['rxfreq']
    rxrepeat = config_dict['rxrepeat']
    datafile = os.path.join(data_folder, folder,'measurements.hdf5')

    try:
        data = h5py.File(datafile, 'r')
    except:
        continue

    def save_measurements(obj, measurement_types, data_array):
        if 'rxsamples' in measurement_types:
            if config_dict['return_iq']:
                samples = np.array(obj['rxsamples']).squeeze()
                if 'bus' in rx_node:
                    locs = np.array(obj['rxloc']).squeeze()
                else:
                    loc = GPS_LOCATIONS[rx_node]
                    locs = np.array([ loc] * len(samples))
                for samps, loc in zip(samples, locs):
                    samps = butter_filt_with_shift(samps, 1e3, 6e3, 2e6)
                    rssi = get_avg_power(samps)
                    data_array.append([loc[:2], rssi, samps])
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
                    rx_gains = list(data[cmd][timestamp][tx_info][tx_gain].keys() )
                    for rx_gain in rx_gains:
                        rx_nodes = list(data[cmd][timestamp][tx_info][tx_gain][rx_gain].keys() )
                        for rx_node in rx_nodes:
                            #if rx_node == hospital:
                            #    import pdb
                            #    pdb.set_trace()
                            if not rx_node in all_samples:
                                all_samples[tx_info][rx_node] = []
                            measurement_types = list(data[cmd][timestamp][tx_info][tx_gain][rx_gain][rx_node].keys() )
                            obj = data[cmd][timestamp][tx_info][tx_gain][rx_gain][rx_node]
                            save_measurements(obj, measurement_types, all_samples[tx_info][rx_node])
            else: # No transmitter active, we're actually down one more level:
                rx_gains = list(data[cmd][timestamp][tx_info].keys() )
                for rx_gain in rx_gains:
                    rx_nodes = list(data[cmd][timestamp][tx_info][rx_gain].keys() )
                    for rx_node in rx_nodes:
                        if not rx_node in all_samples:
                            all_samples[tx_info][rx_node] = []
                        #if rx_node == hospital:
                        #    import pdb
                        #    pdb.set_trace()
                        measurement_types = list(data[cmd][timestamp][tx_info][rx_gain][rx_node].keys() )
                        obj = data[cmd][timestamp][tx_info][rx_gain][rx_node]
                        save_measurements(obj, measurement_types, all_samples[tx_info][rx_node])


#all_locs = {tx_node: {rx_node:np.array([samp[0] for samp in all_samples[tx_node][rx_node]]) for rx_node in all_samples[tx_node]} for tx_node in all_samples}
#all_rssi = {tx_node: {rx_node:np.array([samp[1] for samp in all_samples[tx_node][rx_node]]) for rx_node in all_samples[tx_node]} for tx_node in all_samples}
all_iq = {tx_node: {rx_node:np.array([samp[2] for samp in all_samples[tx_node][rx_node]]) for rx_node in all_samples[tx_node]} for tx_node in all_samples}
relevant_data = {tx_node: {rx_node:np.array([np.concatenate((np.array([samp[1]]),samp[0])) for samp in all_samples[tx_node][rx_node]]) for rx_node in all_samples[tx_node]} for tx_node in all_samples}
image = plt.imread("map_img.png")
#Corners: 
BL = (40.750, -111.860)
TR = (40.775, -111.817)

def plot_on_map(rx_device, tx_device, savefig=False, BL=BL, TR=TR):
    rssi_data = relevant_data[tx_device][rx_device][:,0]
    rx_locs = relevant_data[tx_device][rx_device][:,1:]
    if 'bus' in rx_device:
        plt.figure(figsize=(10,10))
        plt.imshow(image, extent=(BL[1], TR[1], BL[0], TR[0]), zorder=1, alpha=0.75)
        if tx_device != 'wo_tx':
            tx_loc = GPS_LOCATIONS[tx_device]
            plt.scatter(tx_loc[1], tx_loc[0], marker='v', s=80, label='Transmitter', c='blue')
        cb = plt.scatter(rx_locs[:,1], rx_locs[:,0],c=rssi_data, zorder=2, cmap='plasma', vmin=rssi_data.min(), vmax=rssi_data.max(), label=rx_device)
        x_min = min(rx_locs[:,1].min(), tx_loc[1])
        x_max = max(rx_locs[:,1].max(), tx_loc[1])
        y_min = min(rx_locs[:,0].min(), tx_loc[0])
        y_max = max(rx_locs[:,0].max(), tx_loc[0])
        plt.xlim(x_min - 0.002, x_max + 0.002)
        plt.ylim(y_min - 0.002, y_max + 0.002)
        plt.colorbar(cb)
        plt.tight_layout()
        plt.legend()
        if savefig:
            plt.savefig('rx_%s__tx_%s.png' % (rx_device, tx_device) )
            plt.cla()
            plt.close('all')
        else:
            plt.show()

#for loc in rx_data:
#    if 'bus' not in loc: continue
#    rx_data[loc] = np.vstack(rx_data[loc])
#    rx_data[loc] = rx_data[loc][rx_data[loc][:,0] != 0]
#    rx_data[loc] = rx_data[loc][rx_data[loc][:,1] != 0]
#    plot_on_map(rx_data[loc], loc, savefig=True)
#    plot_on_map(rx_data[loc], loc, savefig=False)
#    np.savetxt(loc+'.txt', rx_data[loc], header='RSSI,Latitude,Longitude', delimiter=',', fmt='%.15f')

for tx_dev in all_samples.keys():
    for rx_dev in all_samples[tx_dev].keys():
        if 'bus' in rx_dev:
            plot_on_map(rx_dev, tx_dev, savefig=True)

embed()

