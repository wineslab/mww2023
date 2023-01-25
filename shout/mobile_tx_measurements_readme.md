## On the orchestrator:
In a tmux window, run 
```
cd /local/repositiory/bin
./1.start_orch.sh
```
Edit `3.run_cmd.sh` to specify the output data directory `OUT`, the number of `REPEAT`s, and the desired `CMD`, which is the name of the json file in `/local/repository/etc/cmdfiles`.

Edit `/local/repository/etc/cmdfiles/save_iq_w_tx_cw.json`:
* Set `txfreq` and `rxfreq`
* Set `txrate` and `rxrate`
* Set `rxrepeat`
* Set `txclients` 
* Set `nsamps` 

## On the clients:

If you don't want devices synchronized:
edit line 35 in `bin/2.start_client.sh`:
```
$SHOUTSRC/meascli.py -xc -s $ORCHHOST 
```
Or if you want to force synchronization:
```
$SHOUTSRC/meascli.py -c -s $ORCHHOST 
```

## Back on orchestrator
Run 
```
./3.run_cmd.sh
```

## After data collection:
In `get_rss_data.py`, set the `data_folder` containing the `Shout_meas_...` folders on line 56, the filter bandwidth on line 96, and the command-filename on line 73, if used.

Run `get_rss_data.py` to generate plots of each mobile bus for each transmitter on the map. Note that the map is low resolution and not correctly aligned with the GPS coordinates, this should be fixed at some point. This will drop you into an IPython shell to explore the data. Relevant objects are