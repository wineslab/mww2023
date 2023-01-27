# DSSS Transmission and Reception Experiment with Separate TX/RX scripts
This markdown is to walk through the DSSS (direct spread spectrum sequence) transmission and reception experiment using separate TX/RX scripts.

## Instantiate an Experiment

**Log onto [POWDER](https://powderwireless.net/) &rarr;  `Experiments` &rarr; `Start Experiment` &rarr; `Change Profile` &rarr; [one example profile](https://www.powderwireless.net/show-profile.php?profile=2a6f2d5e-7319-11ec-b318-e4434b2381fc) &rarr; `Select Profile` &rarr; `Next` &rarr; Parameterize &rarr; `Next` &rarr; Finalize &rarr; `Next` &rarr; `Finish`**

`Parameterize`: 
1. Compute node.
2. Radios, 2 at least. Check [resource availibilty](https://www.powderwireless.net/resinfo.php?embedded=true) to find open radios or reserve them beforehand.
3. Frequency range, 10MHz max.

## SSH into Nodes
After your experiment is ready, SSH into the nodes via:
```
ssh -p 22 usrname@node.cluster.net -Y
```
One example is:
```
ssh -p 22 jon@pc07-fort.emulab.net -Y
```

**On the receiver node, please make sure the following packages are installed for the python analysis script:**

- SciPy
- NumPy
- Matplotlib

Most of the time only the scipy package is outdated. Update it via:
```
pip3 install scipy
```

## Transmission
1. Get the transmission scripts ready by:
```
git clone https://gitlab.flux.utah.edu/Jie_Wang/qam-dsss.git
```
2. Go to `Standlone_Exp/` folder and edit the `parameters.json`.

Parameters in `parameters.json`:
* `txrate` and `rxrate`: the transmitted bandwidth and sampling rate at RX.

* `txgain` and `rxgain`: TX and RX gain.

* `txfreq` and `rxfreq`: TX and RX carrier/center frequency.

* `gold_length`: gold code length. It can be 31, 63, 127, 511 and 2047. Longer gold code means more robustness to interference but lower symbol rate.

* `txnode` and `rxnode`: nodes for transmission and reception.

* `nsamps`: number of samples to be collected.

* `txtimeout`: time to stop the transmission.

* `use_lo_offset`: whether to use `lo_offset` for LO leakage removal.

3. Run the TX script by:
```
python3 separate_TX.py -c parameters.json
```

## Reception and Analysis
1. Get the transmission scripts ready by:
```
git clone https://gitlab.flux.utah.edu/Jie_Wang/qam-dsss.git
```
2. Go to `Standlone_Exp/` folder and edit the `parameters.json` to match the transmission parameters.
3. Run the RX analysis script by:
```
python3 separate_RX.py -t -c parameters.json
```
