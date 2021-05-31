#!/usr/bin/python

"""
This profile is intended for doing any experiment using Shout. 

This profile can allocate X310 radios (+ compute), FE NUC1+B210, FE NUC2+B210, ME, and compute node (for Shout's orchestrator). 

Instructions:
**1) Instantiate this profile with appropriate parameters**

At the "Parameterize" step, add radios that are needed for your planned experiment. Also, speceify the freqeuncy ranges if you are planning to use transmitter(s) in your experiment. 


You can leave the other parameters in this profile at their defaults.

Once you have these parameters selected, click through the rest of the
profile and then click "Finish" to instantiate.  It will take 10
to 15 minutes for the experiment to finish setting up.  Once it
is "green", proceed to the next step.


**2) Open SSH sessions**

Use the following commands to start ssh and tmux sessions for the orchestor:

ssh -Y -p 22 -t <username>@<orch_node_hostname> 'cd /local/repository/bin && tmux new-session -A -s main &&  exec $SHELL'
ssh -Y -p 22 -t <username>@<orch_node_hostname> 'cd /local/repository/bin && tmux new-session -A -s aux &&  exec $SHELL'


Use the following command to start a ssh and tmux session for each of the radio:
ssh -Y -p 22 -t <username>@<radio_hostname> 'cd /local/repository/bin && tmux new-session -A -s main &&  exec $SHELL'


Reference SSH commands can be seen on the "List View" tab next to the
compute node names.  If you have an `ssh://` handler setup on your
browser, you can click these commands to open a corresponding SSH
session (they are hyperlinks).


**3) Check radio firmware on x310 (rooftop site) radios**

On each of the `cellsdr1-<site>-comp` and `cbrssdr1-<site>-comp` nodes, run `uhd_usrp_probe`.  If
the output complains about a firmware mismatch, run: 

```
sh setup_x310.sh
```

After the firmware update finishes, find the corresponding X310 radio devices in the "List View" on the
POWDER web UI.  Click the checkbox for each device row where a
firmware update was executed, then click the "gear" icon at the top of
the column and select "power cycle selected".  Confirm to complete the
operation and wait about 10 seconds for the devices to come back
online.  Double check that the firmware has updated by running
`uhd_usrp_probe` again.


**4) Start the Shout Orchestrator process**

In one of your `orch` SSH sessions, run:

```
sh 1.start_orch.sh
```

This will start the Shout orchestrator that all of the measurement
clients, and command executor script will connect to.




**5) Start measurement clients**

In the SSH session for each of the nodes, run: 

```
sh 2.start_client.sh
```

You should see these clients connect both in the output of the client, and
in the output of the orchestrator.


**6) Execute a measurement run**

With all clients connected to the orchestrator, you can now perform a
measurement collection run.  There are JSON command files located
here: `/local/repository/etc/`.  Select one and adjust according to your experiment plan (details of cmds and cmd files are available in https://gitlab.flux.utah.edu/aniqua/shout). Once the command
file is properly adjusted, update line # 3 of 3.run_cmd.sh to point to the correct cmd file. 
Next, execute the following command in your other
`orch` SSH session:

```
sh 3.run_cmd.sh
```

**7) Check collected data**

"""

# Library imports
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab.pnext as pn
import geni.rspec.emulab.spectrum as spectrum
import geni.rspec.igext as ig


# Global Variables
meas_disk_image = \
        "urn:publicid:IDN+emulab.net+image+PowderTeam:U18-GR-PBUF"
orch_image = meas_disk_image
x310_node_image = meas_disk_image
nuc_image = meas_disk_image
sm_image = meas_disk_image

#b210_setup_cmd = "/local/repository/bin/setup_b210.sh"
#x310_setup_cmd = "/local/repository/bin/setup_x310.sh"
#orch_setup_cmd = "/local/repository/bin/install_gps.sh"

# Top-level request object.
request = portal.context.makeRequestRSpec()

# Helper function that allocates a PC + X310 radio pair, with Ethernet
# link between them.
def x310_node_pair(x310_radio_name, node_type):
    radio_link = request.Link("%s-link" % x310_radio_name)

    node = request.RawPC("%s-comp" % x310_radio_name)
    node.hardware_type = node_type
    node.disk_image = x310_node_image

    #node.addService(rspec.Execute(shell="bash",command=x310_setup_cmd))

    node_radio_if = node.addInterface("usrp_if")
    node_radio_if.addAddress(rspec.IPv4Address("192.168.40.1",
                                               "255.255.255.0"))
    radio_link.addInterface(node_radio_if)

    radio = request.RawPC("%s-x310" % x310_radio_name)
    radio.component_id = x310_radio_name
    radio_link.addNode(radio)

# Node type parameter for PCs to be paired with X310 radios.
# Restricted to those that are known to work well with them.
portal.context.defineParameter(
    "nodetype",
    "Compute node type",
    portal.ParameterType.STRING, "d740",
    ["d740","d430"],
    "Type of compute node to be paired with the X310 Radios",
)

# Node type for the orchestrator.
portal.context.defineParameter(
    "orchtype",
    "Orchestrator node type",
    portal.ParameterType.STRING, "d740",
    ["None", "d430","d740"],
    "Type of compute node for the orchestrator (unset == 'any available')",
)


# List of CBRS rooftop X310 radios.
cbrs_radios = [
    ("cbrssdr1-bes",
     "Behavioral"),
    ("cbrssdr1-browning",
     "Browning"),
    ("cbrssdr1-dentistry",
     "Dentistry"),
    ("cbrssdr1-fm",
     "Friendship Manor"),
    ("cbrssdr1-hospital",
     "Hospital"),
    ("cbrssdr1-honors",
     "Honors"),
    ("cbrssdr1-meb",
     "MEB"),
    ("cbrssdr1-smt",
     "SMT"),
    ("cbrssdr1-ustar",
     "USTAR"),
]

# List of Cellular radios
cell_radios = [
    ("cellsdr1-bes",
     "Behavioral"),
    ("cellsdr1-browning",
     "Browning"),
    ("cellsdr1-dentistry",
     "Dentistry"),
    ("cellsdr1-fm",
     "Friendship Manor"),
    ("cellsdr1-hospital",
     "Hospital"),
    ("cellsdr1-honors",
     "Honors"),
    ("cellsdr1-meb",
     "MEB"),
    ("cellsdr1-smt",
     "SMT"),
    ("cellsdr1-ustar",
     "USTAR"),
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
    ('urn:publicid:IDN+bus-4208.powderwireless.net+authority+cm',
     "Bus 4208"),
    ('urn:publicid:IDN+bus-4329.powderwireless.net+authority+cm',
     "Bus 4329"),
    ('urn:publicid:IDN+bus-4330.powderwireless.net+authority+cm',
     "Bus 4330"),
    ('urn:publicid:IDN+bus-4407.powderwireless.net+authority+cm',
     "Bus 4407"),
    ('urn:publicid:IDN+bus-4408.powderwireless.net+authority+cm',
     "Bus 4408"),
    ('urn:publicid:IDN+bus-4409.powderwireless.net+authority+cm',
     "Bus 4409"),
    ('urn:publicid:IDN+bus-4410.powderwireless.net+authority+cm',
     "Bus 4410"),
    ('urn:publicid:IDN+bus-4555.powderwireless.net+authority+cm',
     "Bus 4555"),
    ('urn:publicid:IDN+bus-4603.powderwireless.net+authority+cm',
     "Bus 4603"),
    ('urn:publicid:IDN+bus-4604.powderwireless.net+authority+cm',
     "Bus 4604"),
    ('urn:publicid:IDN+bus-4734.powderwireless.net+authority+cm',
     "Bus 4734"),
    ('urn:publicid:IDN+bus-4817.powderwireless.net+authority+cm',
     "Bus 4817"),
    ('urn:publicid:IDN+bus-4964.powderwireless.net+authority+cm',
     "Bus 4964"),
    ('urn:publicid:IDN+bus-5175.powderwireless.net+authority+cm',
     "Bus 5175"),
    ('urn:publicid:IDN+bus-6180.powderwireless.net+authority+cm',
     "Bus 6180"),
    ('urn:publicid:IDN+bus-6181.powderwireless.net+authority+cm',
     "Bus 6181"),
    ('urn:publicid:IDN+bus-6182.powderwireless.net+authority+cm',
     "Bus 6182"),
    ('urn:publicid:IDN+bus-6183.powderwireless.net+authority+cm',
     "Bus 6183"),
    ('urn:publicid:IDN+bus-6185.powderwireless.net+authority+cm',
     "Bus 6185"),
    ('urn:publicid:IDN+bus-6186.powderwireless.net+authority+cm',
     "Bus 6186"),
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
]


freq_ranges = {
	"ISM-900": [914.87,	915.13],
	"ISM-2400": [2400.00, 2483.50],
	"BAND7-U": [2500.00, 2570.00], 
	"BAND7-D": [2620.00, 2690.00],
	"CBRS": [3550.00, 3700.00], 
	"ISM-5800": [5725.00, 5850.00]
}

# Set of Fixed Endpoint devices to allocate (nuc1)
portal.context.defineStructParameter(
    "fe_radio_sites_nuc1", "Fixed Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Fixed Endpoint NUC1+B210 radios to allocate.",
    members=[
        portal.Parameter(
            "site",
            "FE Site",
            portal.ParameterType.STRING,
            fe_sites[0], fe_sites,
            longDescription="A `nuc1` device will be selected at the site."
        ),
    ])


# Set of Fixed Endpoint devices to allocate (nuc2)
portal.context.defineStructParameter(
    "fe_radio_sites_nuc2", "Fixed Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Fixed Endpoint NUC2+B210 radios to allocate for cellular.",
    members=[
        portal.Parameter(
            "site",
            "FE Site",
            portal.ParameterType.STRING,
            fe_sites[0], fe_sites,
            longDescription="A `nuc2` device will be selected at the site."
        ),
    ])


# Set of Mobile Endpoint devices to allocate
portal.context.defineStructParameter(
    "me_radio_sites", "Mobile Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Mobile Endpoint Supermicro+B210 radios to allocate.",
    members=[
        portal.Parameter(
            "site",
            "ME Site",
            portal.ParameterType.STRING,
            me_sites[0], me_sites,
            longDescription="An `ed1` device will be selected at the site."
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


# Set of CBRS X310 radios to allocate
portal.context.defineStructParameter(
    "cbrs_radio_sites", "CBRS Radio Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="CBRS X310 radios to allocate.",
    members=[
        portal.Parameter(
            "radio",
            "CBRS Radio Site",
            portal.ParameterType.STRING,
            cbrs_radios[0], cbrs_radios,
            longDescription="CBRS X310 radio will be allocated from selected site."
        ),
    ])


# Set of OTA Lab X310 radios to allocate
portal.context.defineStructParameter(
    "ota_lab_x310s", "OTA Lab Radios", [],
    multiValue=True,
    min=0,
    multiValueTitle="Over-the-air Lab X310 radios to allocate.",
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
    "ota_lab_b210s", "OTA Lab B210 Devices", [],
    multiValue=True,
    min=0,
    multiValueTitle="OTA Lab NUC+B210 radios to allocate.",
    members=[
        portal.Parameter(
            "device",
            "NUC+B210 device",
            portal.ParameterType.STRING,
            ota_b210_devices[0], ota_b210_devices,
            longDescription="A NUC+B210 device in the OTA lab will be allocated."
        ),
    ])

# Frequency/spectrum parameters
portal.context.defineStructParameter(
    "cbrs_freq_ranges", "CBRS Frequency Ranges", [],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges for CBRS operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Min",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["CBRS"][0],
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Max",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["CBRS"][0] + 10.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])


"""
portal.context.defineStructParameter(
    "b7_dl_freq_ranges", "Band 7 Downlink Frequency Ranges", [],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges for Band 7 Downlink cellular operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Downlink Frequency Min",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["BAND7-D"][0],
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Downlink Frequency Max",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["BAND7-D"][0]+10.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])

portal.context.defineStructParameter(
    "b7_ul_freq_ranges", "Band 7 Uplink Frequency Ranges", [],
    multiValue=True,
    min=0,
    multiValueTitle="Frequency ranges for Band 7 Uplink cellular operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Uplink Frequency Min",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["BAND7-U"][0],
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Uplink Frequency Max",
            portal.ParameterType.BANDWIDTH,
            freq_ranges["BAND7-U"][0]+10.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])



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

"""


# Bind and verify parameters
params = portal.context.bindParameters()


for i, frange in enumerate(params.cbrs_freq_ranges):
    if frange.freq_min < 3400 or frange.freq_min > 3800 \
       or frange.freq_max < 3400 or frange.freq_max > 3800:
        perr = portal.ParameterError("CBRS frequencies must be between 3400 and 3800 MHz", ["cbrs_freq_ranges[%d].freq_min" % i, "cbrs_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["cbrs_freq_ranges[%d].freq_min" % i, "cbrs_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
"""
for i, frange in enumerate(params.b7_ul_freq_ranges):
    if frange.freq_min < 2500 or frange.freq_min > 2570 \
       or frange.freq_max < 2500 or frange.freq_max > 2570:
        perr = portal.ParameterError("Band 7 uplink frequencies must be between 2500 and 2570 MHz", ["b7_ul_freq_ranges[%d].freq_min" % i, "b7_ul_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["b7_ul_freq_ranges[%d].freq_min" % i, "b7_ul_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    

for i, frange in enumerate(params.b7_dl_freq_ranges):
    if frange.freq_min < 2620 or frange.freq_min > 2690 \
       or frange.freq_max < 2620 or frange.freq_max > 2690:
        perr = portal.ParameterError("Band 7 downlink frequencies must be between 2620 and 2690 MHz", ["b7_dl_freq_ranges[%d].freq_min" % i, "b7_dl_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["b7_dl_freq_ranges[%d].freq_min" % i, "b7_dl_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)

for i, frange in enumerate(params.ism900_freq_ranges):
    if frange.freq_min < freq_ranges["ISM-900"][0] or frange.freq_min > freq_ranges["ISM-900"][1] \
       or frange.freq_max < freq_ranges["ISM-900"][0] or frange.freq_max > freq_ranges["ISM-900"][1]:
        perr = portal.ParameterError("ISM-900 frequencies must be between %f and %f MHz" % (freq_ranges["ISM-900"][0], freq_ranges["ISM-900"][1]), ["ism900_freq_ranges[%d].freq_min" % i, "ism900_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["ism900_freq_ranges[%d].freq_min" % i, "ism900_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)

for i, frange in enumerate(params.ism2400_freq_ranges):
    if frange.freq_min < freq_ranges["ISM-2400"][0] or frange.freq_min > freq_ranges["ISM-2400"][1] \
       or frange.freq_max < freq_ranges["ISM-2400"][0] or frange.freq_max > freq_ranges["ISM-2400"][1]:
        perr = portal.ParameterError("ISM-2400 frequencies must be between %f and %f MHz" % (freq_ranges["ISM-2400"][0], freq_ranges["ISM-2400"][1]), ["ism2400_freq_ranges[%d].freq_min" % i, "ism2400_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["ism2400_freq_ranges[%d].freq_min" % i, "ism2400_freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
"""


# Now verify.
portal.context.verifyParameters()

# Allocate orchestrator node
if params.orchtype != "None":
    orch = request.RawPC("orch")
    orch.disk_image = orch_image
    orch.hardware_type = params.orchtype
    #orch.addService(rspec.Execute(shell="bash", command=orch_setup_cmd))

# Request PC + CBRS X310 resource pairs.
for rsite in params.cbrs_radio_sites:
    x310_node_pair(rsite.radio, params.nodetype)

# Request PC + Cellular X310 resource pairs.
for rsite in params.cell_radio_sites:
    x310_node_pair(rsite.radio, params.nodetype)

# Request PC + OTA Lab X310 resource pairs.
for dev in params.ota_lab_x310s:
    x310_node_pair(dev.radio, params.nodetype)


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
    #nuc.addService(rspec.Execute(shell="bash", command=b210_setup_cmd))

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
    #nuc.addService(rspec.Execute(shell="bash", command=b210_setup_cmd))


# Request ed1+B210 radio resources at ME sites.
for mesite in params.me_radio_sites:
    node = ""
    for urn,sname in me_sites:
        if urn == mesite.site:
            node = request.RawPC("%s-b210" % sname)
            break
    node.component_manager_id = mesite.site
    node.component_id = "ed1"
    node.disk_image = sm_image
    #node.addService(rspec.Execute(shell="bash", command=b210_setup_cmd))

 
# Request NUC+B210 radio resources in the OTA Lab.
for dev in params.ota_lab_b210s:
    node = request.RawPC("%s-b210" % dev.device)
    node.component_id = dev.device
    node.disk_image = sm_image
    #node.addService(rspec.Execute(shell="bash",
    #     

# Request frequency range(s)
for frange in params.cbrs_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)
""" 
for frange in params.b7_ul_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

for frange in params.b7_dl_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

for frange in params.ism900_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

for frange in params.ism2400_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)
"""
    
# Emit!
portal.context.printRequestRSpec()
