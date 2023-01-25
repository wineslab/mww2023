#!/usr/bin/env python3

# General purpose utility functions

import numpy as np
import requests
import json
import datetime
import subprocess
import shlex
import json
import csv
import os



EPOCH = datetime.datetime.utcfromtimestamp(0)
TIMEFORMAT = '%Y-%m-%d %H:%M:%S.%f'

def get_samps_frm_file(filename): 
	'''
    load samples from the binary file
    '''
    # File should be in GNURadio's format, i.e., interleaved I/Q samples as float32
	samples = np.fromfile(filename, dtype=np.float32)
	samps = (samples[::2] + 1j*samples[1::2]).astype((np.complex64))
		
	return samps


def get_shout_version():
	command = "git log -1 --pretty=format:%h" 
	process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
	version = process.stdout.readline().decode("utf-8")
	return version

def run_gps_logger(bus, duration, out):
	glfile = out + "/bus-"+bus+"_locations.csv"
	if os.path.isfile(glfile):
		header = False
	else:
		header = True
	with open(glfile, mode='a') as gpslogfile:
		gpslog = csv.writer(gpslogfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
		if header:
			gpslog.writerow(["Time (UTC)" , "Lat", "Lon", "Alt", "Speed (meters/sec)"])

		command = "timeout %s gpspipe -w control.bus-%s.powderwireless.net" %(duration, bus)
		process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
		count = 0 
		while True:
			output = process.stdout.readline()
			if not output and process.poll() is not None:
				break
			try:
				gps_info = json.loads(output)
			except:
				print("Encountered problems in running GPS client. Exiting...")
				gpslogfile.flush()
				gpslogfile.close()
				exit(1)

			if gps_info['class'] == 'TPV':
				#print(gps_info['time'], datetime.datetime.now(datetime.timezone.utc))
				gpslog.writerow([gps_info['time'], gps_info['lat'], gps_info['lon'], gps_info['alt'], gps_info['speed']])
				#count += 1
				#if count == 60:
				gpslogfile.flush()
				#count = 0
				
		print('Finished bus ', bus)
		gpslogfile.flush()
		gpslogfile.close()
		return process.poll()


def convert_net_time_to_datetime(net_time): # Based on https://stackoverflow.com/questions/5786448/date-conversion-net-json-to-iso
	timepart = net_time.split('(')[1].split(')')[0]
	milliseconds = int(timepart[:-5])
	hours = int(timepart[-5:]) / 100
	adjustedseconds = milliseconds / 1000 + hours * 3600
	dt = EPOCH + datetime.timedelta(seconds=adjustedseconds)
	return dt


def get_bus_location(name):
	busname = name.replace("-b210", "").replace("bus", "")
	loc_url = "https://www.uofubus.com/Services/JSONPRelay.svc/GetMapVehiclePoints?ApiKey=ride1791"
	info = json.loads(requests.get(loc_url).text)
	for bus in info:
		if bus['Name'] == busname:
			return [bus['Latitude'], bus['Longitude'], bus['GroundSpeed']]#, convert_net_time_to_datetime(bus['TimeStamp'])
	return []


def add_to_measurements(meas, dt, power=None, bus=None):
	meas.append(dt.month)
	meas.append(dt.day)
	meas.append(dt.hour)
	meas.append(dt.minute)
	meas.append(dt.second)
	meas.append(dt.microsecond)
	if power:
		meas.append(power)

	if bus:
		for b in bus:
			meas.append(b)
		
		"""
		meas.append(bus_dt.month)
		meas.append(bus_dt.day)
		meas.append(bus_dt.hour)
		meas.append(bus_dt.minute)
		meas.append(bus_dt.second)
		meas.append(bus_dt.microsecond)
		"""

def measurements_to_dataset(dataset, index, meas, name):
	month, day, hour, minute, second, microsecond = map(int, meas[:6])
	year = datetime.datetime.now(datetime.timezone.utc).year
	rxtime_str = datetime.datetime(year, month, day, hour, minute, second, microsecond).strftime(TIMEFORMAT)
	dataset['rxtime'][index] = str(rxtime_str)

	"""
	n = len(meas)
	if n > 6:
		dataset['rxloc'][index] = [meas[6], meas[7], 0.0]
		dataset['rxspeed'][index] = meas[8]
		dataset['rxlocflag'][index] = 'uofubusapi'

	"""

def rssi_measurements_to_dataset(dataset, index, meas, name):
	month, day, hour, minute, second, microsecond = map(int, meas[:6])
	year = datetime.datetime.now(datetime.timezone.utc).year
	rxtime_str = datetime.datetime(year, month, day, hour, minute, second, microsecond).strftime(TIMEFORMAT)
	dataset['rxtime'][index] = str(rxtime_str)
	dataset['rssi'][index] = float(meas[6])
		

def update_rx_loc(dataset, client, datadir):
	locfile = datadir + client.replace("-b210", "")+'_locations.csv'
	if os.path.isfile(locfile):
		with open(locfile, mode='r') as locfile_csv:
			loc = list(csv.reader(locfile_csv))
			loci = 1
			total = len(dataset['rxloc'])
			for i in range(total):
				if dataset['rxtime'][i] == '':
					print("Missing entry: ", i, dataset['rxtime'][i])
					continue
				lat, lon, alt, speed, loci = get_gpsd_loc(dataset['rxtime'][i], loc, loci)
				if lat != 0:
					dataset['rxloc'][i] = [lat, lon, alt]
					dataset['rxspeed'][i] = speed
					#dataset['rxlocflag'][i] = 'gpsd'
	else:
		print("GPS location file not found: %s" %locfile)

def update_tx_loc(dataset, clients, datadir):
	for t,client in enumerate(clients):
		locfile = datadir + client.replace("-b210", "")+'_locations.csv'
		if os.path.isfile(locfile):
			with open(locfile, mode='r') as locfile_csv:
				loc = csv.reader(locfile_csv)
				if os.path.isfile(locfile):
					loc = list(csv.reader(locfile_csv))
					loci = 1
					total = len(dataset['txloc'])
					for i in range(total):
						if dataset['rxtime'][i] == '':
							print("Missing entry: ", i, dataset['rxtime'][i])
							continue
						lat, lon, alt, speed, loci = get_gpsd_loc(dataset['rxtime'][i], loc, loci)
						if lat != 0:
							dataset['txloc'][i][t] = [lat, lon, alt]
							dataset['txspeed'][i][t] = speed
							#dataset['rxlocflag'][i][t] = 'gpsd'
		else:
			print("GPS location file not found: %s" %locfile)


def get_gpsd_loc(rxtime, loc, li):
	rxtime = datetime.datetime.strptime(rxtime, TIMEFORMAT)
	rxtime_utc = datetime.datetime.utcfromtimestamp(float(rxtime.strftime("%s")))
	timestamp = str(rxtime_utc).replace(' ', 'T')
	
	n = len(loc)
	for i in range(li, n):
		if loc[i][0].startswith(timestamp):
			return float(loc[i][1]), float(loc[i][2]), float(loc[i][3]), float(loc[i][4]), i+1
	
	return 0, 0, 0, 0, li


def round_center_freq(cf, res):
	return np.round(cf/res, 0)*res
