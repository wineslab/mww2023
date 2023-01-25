# DSSS Transmission and Reception Experiment With SHOUT
This markdown is to walk through the DSSS (direct spread spectrum sequence) transmission and reception experiment using SHOUT.

## Instantiate an Experiment
1. Log onto [POWDER](https://powderwireless.net/) 
2. Select the [shout-long-measurement](https://www.powderwireless.net/show-profile.php?profile=2a6f2d5e-7319-11ec-b318-e4434b2381fc) profile. If you do not have access to the profile, one can be created via:
    **`Experiments` &rarr; `Create Experiment Profile` &rarr; `Git Repo` &rarr; add [repo link](https://gitlab.flux.utah.edu/frost/proj-radio-meas) &rarr; select the profile**
3. Start an experiment by specifying all necessary parameters [compute node type, radio types and frequency range] and finish. If the radios are not available, please create a reservation ahead of time.

## SSH into Nodes
Follow the profile [instructions](https://gitlab.flux.utah.edu/frost/proj-radio-meas/-/blob/master/profile.py) `step 2` to SSH into the nodes including the orchestrator and clients.

## Transmission
Files to modify before running an experiment:
1. **./3.run_cmd.sh**: make sure that the CMD in line 16 is `save_iq_w_tx_gold`
2. **save_iq_w_tx_gold.json**: 
Path: `/local/repository/etc/cmdfiles/save_iq_w_tx_gold.json`

Parameters:
* `txrate` and `rxrate`: the transmitted bandwidth and sampling rate at RX
* `txgain` and `rxgain`: TX and RX gain.
* `txfreq` and `rxfreq`: TX and RX carrier/center frequency.
* `gold_id`: always 0, no change needed.
* `gold_length`: gold code length. It can be 31, 63, 127, 511 and 2047. Longer gold code means more robustness to interference but lower symbol rate.
* `txclients` and `rxclients`: nodes for transmission and reception.
* `rxrepeat`: number of repeated runs.

Once the files are modified, run the experiment by following the profile [instructions](https://gitlab.flux.utah.edu/frost/proj-radio-meas/-/blob/master/profile.py) `step 4`.

## Reception
Once the experiment is done, measurements will be sent back to the orchestrator automatically. One can check the collected measurements via `ls /local/data/`.

## Analysis
Run the analysis script `DSSS_Processing.py` with the data directory and the measurement folder name. One example is:
```
python3 /local/repository/shout/dsss/DSSS_Processing.py -o /local/data/ -f Shout_meas_01-05-2023_10-45-52
```
Arguments:
`-o`: path to new measurements. Example ones are stored in `/local/repository/shout/examples/measurements/`.

`-f`: the measurement folder name. Examples are `Shout_meas_01-05-2023_10-45-52` and `Shout_meas_01-06-2023_08-08-31`

Correlation steps:
1. Matched filtering: it correlates the received signal with the known pulse shape which, in this implementation, is a square-root-raised-cosine (SRRC) pulse.

2. Frequency synchronization: it is to correct frequency offset for later BPSK demodulation. This can be skipped if only SNR and RSSI metrics are needed.

3. Despreading: it despreads the signal by correlating the matched-filtered samples with the known gold code sequence.

4. Peak finding: it estimates the indices of maximum correlation which represents the best match between the samples and the gold code sequence.
