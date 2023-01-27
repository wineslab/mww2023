#!/usr/bin/python

"""This profile is intended for doing experiments using the Shout automated RF measurements framework. 

It can allocate Rooftop, Dense Deployment, Fixed Endpoint, Mobile Endpoint, and OTA lab radio+compute resources. It always also allocates a compute node for Shout's orchestrator and for running the user interface script.

Instructions:
**1) Instantiate this profile with appropriate parameters**

At the "Parameterize" step, add radios that are needed for your planned experiment. Also, speceify the freqeuncy ranges if you are planning to use with the transmitter(s) in your experiment. 

You can leave the other parameters in this profile at their defaults.

Once you have these parameters selected, click through the rest of the
profile and then click "Finish" to instantiate.  It will take 10 to 15
minutes for the experiment to finish setting up.  Once it is "green"
and all startup scripts show "finished", proceed to the next step.

**2) Open SSH sessions**

Use the following commands to start ssh and tmux sessions for the orchestor:
```
ssh -Y -p 22 -t <username>@<orch_node_hostname> 'cd /local/repository/bin && tmux new-session -A -s shout1 && exec $SHELL'
ssh -Y -p 22 -t <username>@<orch_node_hostname> 'cd /local/repository/bin && tmux new-session -A -s shout2 && exec $SHELL'
```

Use the following command to start a ssh and tmux session for each of the radio+compute resources:
```
ssh -Y -p 22 -t <username>@<radio_hostname> 'cd /local/repository/bin && tmux new-session -A -s shout && exec $SHELL'
```

Reference SSH commands can be seen on the "List View" tab next to the
compute node names.  

TMUX is helpful for doing multiple terminal sessions and allowing remote sessions to remain active even when the SSH connection to the nodes gets disconncted. A "cheat sheet" for interacting with TMUX sessions can be found here:

[TMUX Cheat Sheet](https://tmuxcheatsheet.com/)

**3) Check radio firmware on x310 (rooftop site) radios**

On each of the `cellsdr1-<site>-comp` and `cbrssdr1-<site>-comp` nodes, run `uhd_usrp_probe`.  If the output complains about a firmware mismatch, run: 

```
./setup_x310.sh
```

After the firmware update finishes, find the corresponding X310 radio devices in the "List View" on the POWDER web UI.  Click the checkbox for each device row where a firmware update was executed, then click the "gear" icon at the top of the column and select "power cycle selected".  Confirm to complete the operation and wait about 10 seconds for the devices to come back online.  Double check that the firmware updated successfully by running `uhd_usrp_probe` again.

**4) Start the Shout Orchestrator process**

In one of your `orch` SSH sessions, run:

```
./1.start_orch.sh
```

This will start the Shout orchestrator that all of the measurement clients, and command executor script will connect to.

**5) Start measurement clients**

In the SSH session for each of the nodes, run: 

```
./2.start_client.sh
```

You should see these clients connect both in the output of the client, and in the output of the orchestrator.

**6) Execute a measurement run**

With all clients connected to the orchestrator, you can now perform a measurement collection run. There are example JSON command (configuration) files located at: [This link](https://gitlab.flux.utah.edu/powder-profiles/shout-se-profile/-/tree/master/etc/cmdfiles) and `/local/repository/etc/cmdfiles` on the orchestrator node.  Select one and adjust according to your experiment plan. Once the command file is properly adjusted, update 3.run_cmd.sh to point to the correct cmd file and output location.  Next, in your other `orch` node SSH session, run:

```
./3.run_cmd.sh
```
This will run the Shout command(s) as specified in the cmd file. This will create a measurement directory in the output directory (specified in `3.run_cmd.sh`) named Shout\_meas\_<date>_<time> with the following items:

a) measurements.hdf5: Measurement dataset.

b) <cmd>.json: Cmd file used for the measurement.

c) log: Log file saved by Shout's measiface.py.

d) configuration.csv: Current POWDER radio configuration file from https://gitlab.flux.utah.edu/powderrenewpublic/powder-deployment.

e) powder-deployment.csv: Current POWDER deployment file from https://gitlab.flux.utah.edu/powderrenewpublic/powder-deployment.

f) bus<bus number>_locations.csv files: GPSd location and speed information files, one for each of the buses used in the measurement (if mobile endpoints are in use). 

Details of supported commands are available in https://gitlab.flux.utah.edu/aniqua/shout/-/blob/master/README.md.

Example measurement directories are in https://gitlab.flux.utah.edu/aniqua/shout/-/tree/master/examples.

**6) Check saved dataset**

You can run the following command to test saved measurements.hdf5:

```
cd /local/repository/shout
python3 check-data.py --datadir <shout_meas_dir>
```

"""

# Library imports
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab.pnext as pn
import geni.rspec.emulab.spectrum as spectrum
import geni.rspec.igext as ig
import geni.rspec.emulab.route as route


# Global Variables
shout_image = \
        "urn:publicid:IDN+emulab.net+image+PowderTeam:U18-GR-PBUF"
orch_image = shout_image
x310_node_image = shout_image
nuc_image = shout_image
sm_image = shout_image

# List of CBAND rooftop X310 radios.
cband_radios = [
    ("cbrssdr1-bes",
     "Behavioral"),
    ("cbrssdr1-browning",
     "Browning"),
#    ("cbrssdr1-dentistry",
#     "Dentistry"),
    ("cbrssdr1-fm",
     "Friendship Manor"),
    ("cbrssdr1-hospital",
     "Hospital"),
    ("cbrssdr1-honors",
     "Honors"),
#    ("cbrssdr1-meb",
#     "MEB"),
    ("cbrssdr1-smt",
     "SMT"),
    ("cbrssdr1-ustar",
     "USTAR"),
]

# List of Cellular radios; These are "RX only" as of 1/12/23
cell_radios = [
    ("cellsdr1-bes",
     "Behavioral"),
#    ("cellsdr1-browning",
#     "Browning"),
#    ("cellsdr1-dentistry",
#     "Dentistry"),
#    ("cellsdr1-fm",
#     "Friendship Manor"),
    ("cellsdr1-hospital",
     "Hospital"),
#    ("cellsdr1-honors",
#     "Honors"),
#    ("cellsdr1-meb",
#     "MEB"),
    ("cellsdr1-smt",
     "SMT"),
#    ("cellsdr1-ustar",
#     "USTAR"),
]

# A list of endpoint sites.
fe_sites = [
    ('urn:publicid:IDN+bookstore.powderwireless.net+authority+cm',
     "Bookstore"),
    ('urn:publicid:IDN+cpg.powderwireless.net+authority+cm',
     "Garage"),
    ('urn:publicid:IDN+ebc.powderwireless.net+authority+cm',
     "EBC"),
    ('urn:publicid:IDN+guesthouse.powderwireless.net+authority+cm',
     "GuestHouse"),
    ('urn:publicid:IDN+humanities.powderwireless.net+authority+cm',
     "Humanities"),
    ('urn:publicid:IDN+law73.powderwireless.net+authority+cm',
     "Law73"),
    ('urn:publicid:IDN+madsen.powderwireless.net+authority+cm',
     "Madsen"),
    ('urn:publicid:IDN+moran.powderwireless.net+authority+cm',
     "Moran"),
    ('urn:publicid:IDN+sagepoint.powderwireless.net+authority+cm',
     "SagePoint"),
    ('urn:publicid:IDN+web.powderwireless.net+authority+cm',
     "WEB"),
]

# A list of mobile endpoint sites.
me_sites = [
    ("All", "All"),
]

# List of OTA lab X310 radios.
ota_x310_radios = [
    "ota-x310-1",
    "ota-x310-2",
    "ota-x310-3",
    "ota-x310-4",
]

# List of OTA lab NUC+B210 devices.
ota_b210_devices = [
    "ota-nuc1",
    "ota-nuc2",
    "ota-nuc3",
    "ota-nuc4",
]

# List of dense radios.
dense_radios = [
    ("cnode-wasatch",
     "Wasatch"),
    ("cnode-mario",
     "Mario"),
    ("cnode-moran",
     "Moran"),
    ("cnode-guesthouse",
     "Guesthouse"),
    ("cnode-ebc",
     "EBC"),
    ("cnode-ustar",
     "USTAR"),
]

freq_ranges = {
    "ISM-900": [914.87, 915.13],
    "ISM-2400": [2400.00, 2483.50],
    "CBAND": [3358.00, 3600.00], 
    "ISM-5800": [5725.00, 5850.00]
}

# Add one or more lines to reference datasets you want to mount to
# the orchestrator node.
datasets = {
    "ChangeMeToFriendlyName": "ChangeMeToDatasetURN",
}

# Top-level request object.
request = portal.context.makeRequestRSpec()

# Helper function that allocates a PC + X310 radio pair, with Ethernet
# link between them.
def x310_node_pair(x310_radio_name, inparams):
    radio_link = request.Link("%s-link" % x310_radio_name)
    radio_link.bandwidth = 10*1000*1000 # 10Gbps expressed in Kbps

    node = request.RawPC("%s-comp" % x310_radio_name)
    node.hardware_type = inparams.nodetype
    node.disk_image = x310_node_image

    if inparams.start_vnc:
        node.startVNC()

    if inparams.ignore_isbw:
        radio_link.best_effort = True

    node_radio_if = node.addInterface("usrp_if")
    node_radio_if.addAddress(rspec.IPv4Address("192.168.40.1",
                                               "255.255.255.0"))
    radio_link.addInterface(node_radio_if)

    radio = request.RawPC("%s-x310" % x310_radio_name)
    radio.component_id = x310_radio_name
    radio_link.addNode(radio)


# Helper function to connect orch to a dataset
def connect_to_dataset(node, dataset_name):
    # We need a link to talk to the remote file system, so make an interface.
    iface = node.addInterface()

    # The remote file system is represented by special node.
    fsnode = request.RemoteBlockstore("fsnode", "/" + dataset_name)

    # This URN is displayed in the web interfaace for your dataset.
    fsnode.dataset = datasets[dataset_name]
    
    # Now we add the link between the node and the special node
    fslink = request.Link("fslink")
    fslink.addInterface(iface)
    fslink.addInterface(fsnode.interface)

    # Special attributes for this link that we must set.
    fslink.best_effort = True
    fslink.vlan_tagging = True

# Node type parameter for PCs to be paired with X310 radios.
# Restricted to those that are known to work well with them.
portal.context.defineParameter(
    "nodetype",
    "Compute node type",
    portal.ParameterType.STRING, "d740",
    ["d740","d430"],
    "Type of compute node to be paired with the X310 Radios (Rooftop/Dense sites)",
)

# Node type for the orchestrator.
portal.context.defineParameter(
    "orchtype",
    "Orchestrator node type",
    portal.ParameterType.STRING, "d740",
    ["None", "d430","d740", "d710", ""],
    "Type of compute node for the orchestrator (unset == 'any available')",
)

portal.context.defineParameter(
    "dataset",
    "Dataset to connect",
    portal.ParameterType.STRING, "None",
    ["SpectSet","ADSBRecordings","None"],
    "Name of the remote dataset to connect with orch",
)

# Set of Rooftop CBAND X310 radios to allocate
portal.context.defineStructParameter(
    "cband_radio_sites", "CBAND Radio Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="CBAND X310 radios.",
    members=[
        portal.Parameter(
            "radio",
            "CBAND Radio Site",
            portal.ParameterType.STRING,
            cband_radios[0], cband_radios,
            longDescription="CBAND X310 radio will be allocated from selected site."
        ),
    ])

# Set of Dense Deployment radio sites to allocate
portal.context.defineStructParameter(
    "dense_radios", "Dense Site Radios", [],
    multiValue=True,
    min=0,
    multiValueTitle="Dense Site NUC+B210 radios to allocate.",
    members=[
        portal.Parameter(
            "device",
            "SFF Compute + NI B210 device",
            portal.ParameterType.STRING,
            dense_radios[0], dense_radios,
            longDescription="A Small Form Factor compute with attached NI B210 device at the given Dense Deployment site will be allocated."
        ),
    ])

# Set of Mobile Endpoint devices to allocate
portal.context.defineStructParameter(
    "me_radio_sites", "Mobile Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Mobile Endpoint Supermicro+B210 radios.",
    members=[
        portal.Parameter(
            "site",
            "ME Site",
            portal.ParameterType.STRING,
            me_sites[0], me_sites,
            longDescription="An `ed1` device will be selected at the site."
        ),
    ])

# Set of Fixed Endpoint devices to allocate (nuc2)
portal.context.defineStructParameter(
    "fe_radio_sites_nuc2", "TX/RX Fixed Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Fixed Endpoint NUC2+B210 radios (TX/RX capable).",
    members=[
        portal.Parameter(
            "site",
            "FE Site",
            portal.ParameterType.STRING,
            fe_sites[0], fe_sites,
            longDescription="A `nuc2` device will be selected at the site."
        ),
    ])

# Set of Fixed Endpoint devices to allocate (nuc1)
portal.context.defineStructParameter(
    "fe_radio_sites_nuc1", "RX-only Fixed Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Fixed Endpoint NUC1+B210 radios (RX only).",
    members=[
        portal.Parameter(
            "site",
            "FE Site",
            portal.ParameterType.STRING,
            fe_sites[0], fe_sites,
            longDescription="A `nuc1` device will be selected at the site."
        ),
    ])

# Set of OTA Lab X310 radios to allocate
portal.context.defineStructParameter(
    "ota_lab_x310s", "OTA Lab X310 Radios", [],
    multiValue=True,
    min=0,
    multiValueTitle="OTA Lab X310 radios.",
    members=[
        portal.Parameter(
            "radio",
            "OTA Lab Radio",
            portal.ParameterType.STRING,
            ota_x310_radios[0], ota_x310_radios,
            longDescription="An X310 radio in the OTA Lab along with associated compute node will be allocated."
        ),
    ])

# Set of OTA Lab NUC+B210 devices to allocate
portal.context.defineStructParameter(
    "ota_lab_b210s", "OTA Lab B210 Radios", [],
    multiValue=True,
    min=0,
    multiValueTitle="OTA Lab NUC+B210 radios.",
    members=[
        portal.Parameter(
            "device",
            "NUC+B210 device",
            portal.ParameterType.STRING,
            ota_b210_devices[0], ota_b210_devices,
            longDescription="A NUC+B210 device in the OTA lab will be allocated."
        ),
    ])

# Set of Cellular X310 radios to allocate
portal.context.defineStructParameter(
    "cell_radio_sites", "Cellular Radio Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Cellular X310 radios to allocate.",
    members=[
        portal.Parameter(
            "radio",
            "Cellular Radio Site",
            portal.ParameterType.STRING,
            cell_radios[0], cell_radios,
            longDescription="Cellular X310 radio will be allocated from selected site."
        ),
    ])

### Frequency/spectrum parameters

# CBAND
portal.context.defineStructParameter(
    "cband_freq_ranges", "CBAND Frequency Ranges", [],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges for CBAND operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Min",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["CBAND"][0],
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Max",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["CBAND"][0] + 10.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])

# ISM - 900MHz
portal.context.defineStructParameter(
    "ism900_freq_ranges", "ISM-900 Frequency Ranges", [],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges for ISM-900 operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Min",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["ISM-900"][0],
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Max",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["ISM-900"][0] + 10.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])

# ISM - 2400MHz
portal.context.defineStructParameter(
    "ism2400_freq_ranges", "ISM-2400 Frequency Ranges", [],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges for ISM-2400 operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Min",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["ISM-2400"][0],
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Max",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["ISM-2400"][0] + 10.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])

# Start VNC?
portal.context.defineParameter("start_vnc", 
                               "Start X11 VNC on all compute nodes",
                               portal.ParameterType.BOOLEAN, True)

# Ignore inter-switch bandwidth limitations (advanced param)?
portal.context.defineParameter("ignore_isbw",
                               "Ignore interswitch bandwith limitations on radio-to-compute links. (Do not use unless you have a specific reason to do so.)",
                               portal.ParameterType.BOOLEAN, False,
                               advanced=True)

# Bind and verify parameters
params = portal.context.bindParameters()

for i, frange in enumerate(params.cband_freq_ranges):
    if frange.freq_min < 3400 or frange.freq_min > 3800 \
       or frange.freq_max < 3400 or frange.freq_max > 3800:
        perr = portal.ParameterError("CBAND frequencies must be between 3358 and 3700 MHz", ["cband_freq_ranges[%d].freq_min" % i, "cband_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["cband_freq_ranges[%d].freq_min" % i, "cband_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)

for i, frange in enumerate(params.ism900_freq_ranges):
    if frange.freq_min < freq_ranges["ISM-900"][0] or frange.freq_min > freq_ranges["ISM-900"][1] \
       or frange.freq_max < freq_ranges["ISM-900"][0] or frange.freq_max > freq_ranges["ISM-900"][1]:
        perr = portal.ParameterError("ISM-900 frequencies must be between %f and %f MHz" % (freq_ranges["ISM-900"][0], freq_ranges["ISM-900"][1]), ["ism900_freq_ranges[%d].freq_min" % i, "ism900_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < .2:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 200 KHz", ["ism900_freq_ranges[%d].freq_min" % i, "ism900_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)

for i, frange in enumerate(params.ism2400_freq_ranges):
    if frange.freq_min < freq_ranges["ISM-2400"][0] or frange.freq_min > freq_ranges["ISM-2400"][1] \
       or frange.freq_max < freq_ranges["ISM-2400"][0] or frange.freq_max > freq_ranges["ISM-2400"][1]:
        perr = portal.ParameterError("ISM-2400 frequencies must be between %f and %f MHz" % (freq_ranges["ISM-2400"][0], freq_ranges["ISM-2400"][1]), ["ism2400_freq_ranges[%d].freq_min" % i, "ism2400_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["ism2400_freq_ranges[%d].freq_min" % i, "ism2400_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)

# Now verify parameters.
portal.context.verifyParameters()

# Declare that we may be starting X11 VNC on the compute nodes.
if params.start_vnc:
    request.initVNC()

# Allocate orchestrator node
if params.orchtype != "None":
    orch = request.RawPC("orch")
    orch.disk_image = orch_image
    orch.hardware_type = params.orchtype
    if params.dataset != "None": 
        connect_to_dataset(orch, params.dataset)
    if params.start_vnc:
        orch.startVNC()

# Request PC + CBAND X310 resource pairs.
for rsite in params.cband_radio_sites:
    x310_node_pair(rsite.radio, params)

# Request PC + Cellular X310 resource pairs.
for rsite in params.cell_radio_sites:
    x310_node_pair(rsite.radio, params)

# Request PC + OTA Lab X310 resource pairs.
for dev in params.ota_lab_x310s:
    x310_node_pair(dev.radio, params)

# Request nuc1+B210 radio resources at FE sites.
for fesite in params.fe_radio_sites_nuc1:
    nuc = ""
    for urn,sname in fe_sites:
        if urn == fesite.site:
            nuc = request.RawPC("%s-nuc1-b210" % sname)
            break
    nuc.component_manager_id = fesite.site
    nuc.component_id = "nuc1"
    nuc.disk_image = nuc_image
    if params.start_vnc:
        nuc.startVNC()

# Request nuc2+B210 radio resources at FE sites.
for fesite in params.fe_radio_sites_nuc2:
    nuc = ""
    for urn,sname in fe_sites:
        if urn == fesite.site:
            nuc = request.RawPC("%s-nuc2-b210" % sname)
            break
    nuc.component_manager_id = fesite.site
    nuc.component_id = "nuc2"
    nuc.disk_image = nuc_image
    if params.start_vnc:
        nuc.startVNC()

# Request ed1+B210 radio resources at ME sites.
for mesite in params.me_radio_sites:
    if mesite.site == "All":
        obj = request.requestAllRoutes()
        obj.disk_image = nuc_image
        if params.start_vnc:
            obj.startVNC()

# Request NUC+B210 radio resources at the requested Dense Deployment sites.
for dev in params.dense_radios:
    node = request.RawPC("%s-dd-b210" % dev.device)
    node.component_id = dev.device
    node.disk_image = sm_image
    if params.start_vnc:
        node.startVNC()

# Request NUC+B210 radio resources in the OTA Lab.
for dev in params.ota_lab_b210s:
    node = request.RawPC("%s-b210" % dev.device)
    node.component_id = dev.device
    node.disk_image = sm_image
    if params.start_vnc:
        node.startVNC()

# Request frequency range(s)
for frange in params.cband_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

for frange in params.ism900_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

for frange in params.ism2400_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)
    
# Emit!
portal.context.printRequestRSpec()
