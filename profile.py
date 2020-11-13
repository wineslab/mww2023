#!/usr/bin/python

"""
Allocate some number of X310 radios (+ compute) for doing measurements. 
Can allocate both CBRS and Cellular band X310 Radios as well as FE
NUC+B210 resources.

Instructions:

Do all the things.

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
#setup_command = "/local/repository/bin/startup.sh"

# Top-level request object.
request = portal.context.makeRequestRSpec()

# Helper function that allocates a PC + X310 radio pair, with Ethernet
# link between them.
def x310_node_pair(x310_radio_name, node_type, orchhost):
    radio_link = request.Link("%s-link" % x310_radio_name)

    node = request.RawPC("%s-comp" % x310_radio_name)
    node.hardware_type = node_type
    node.disk_image = x310_node_image

    #node.addService(rspec.Execute(shell="bash",
    #                              command=setup_command + " %s" % orchhost))

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
    portal.ParameterType.STRING, "",
    ["", "d430","d740"],
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
     "Central Parking Garage"),
    ('urn:publicid:IDN+ebc.powderwireless.net+authority+cm',
     "Eccles Broadcast Center"),
    ('urn:publicid:IDN+guesthouse.powderwireless.net+authority+cm',
     "Guest House"),
    ('urn:publicid:IDN+humanities.powderwireless.net+authority+cm',
     "Humanities"),
    ('urn:publicid:IDN+law73.powderwireless.net+authority+cm',
     "Law73 Building"),
    ('urn:publicid:IDN+madsen.powderwireless.net+authority+cm',
     "Madsen Clinic"),
    ('urn:publicid:IDN+moran.powderwireless.net+authority+cm',
     "Moran Eye Center"),
    ('urn:publicid:IDN+sagepoint.powderwireless.net+authority+cm',
     "Sage Point"),
    ('urn:publicid:IDN+web.powderwireless.net+authority+cm',
     "Warnock Engineering Building"),
]

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

# Set of Fixed Endpoint devices to allocate
portal.context.defineStructParameter(
    "fe_radio_sites", "Fixed Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Fixed Endpoint NUC+B210 radios to allocate.",
    members=[
        portal.Parameter(
            "site",
            "FE Site",
            portal.ParameterType.STRING,
            fe_sites[0], fe_sites,
            longDescription="A `nuc2` device will be selected at the site."
        ),
    ])


# Frequency/spectrum parameters
portal.context.defineStructParameter(
    "cbrs_freq_ranges", "CBRS Frequency Ranges", [],
    multiValue=True,
    min=1,
    multiValueTitle="Frequency ranges for CBRS operation.",
    members=[
        portal.Parameter(
            "freq_min",
            "Frequency Min",
            portal.ParameterType.BANDWIDTH,
            3550.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Frequency Max",
            portal.ParameterType.BANDWIDTH,
            3560.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])

portal.context.defineStructParameter(
    "b7_freq_ranges", "Band 7 Frequency Ranges", [],
    multiValue=True,
    min=1,
    multiValueTitle="Frequency ranges for Band 7 cellular operation.",
    members=[
        portal.Parameter(
            "ul_freq_min",
            "Uplink Frequency Min",
            portal.ParameterType.BANDWIDTH,
            2500.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "ul_freq_max",
            "Uplink Frequency Max",
            portal.ParameterType.BANDWIDTH,
            2570.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "dl_freq_min",
            "Downlink Frequency Min",
            portal.ParameterType.BANDWIDTH,
            2620.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "dl_freq_max",
            "Downlink Frequency Max",
            portal.ParameterType.BANDWIDTH,
            2690.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
    ])

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

for i, frange in enumerate(params.b7_freq_ranges):
    if frange.ul_freq_min < 2500 or frange.ul_freq_min > 2570 \
       or frange.ul_freq_max < 2500 or frange.ul_freq_max > 2570:
        perr = portal.ParameterError("Band 7 uplink frequencies must be between 2500 and 2570 MHz", ["b7_freq_ranges[%d].ul_freq_min" % i, "b7_freq_ranges[%d].ul_freq_max" % i])
        portal.context.reportError(perr)
    if frange.ul_freq_max - frange.ul_freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["b7_freq_ranges[%d].ul_freq_min" % i, "b7_freq_ranges[%d].ul_freq_max" % i])
        portal.context.reportError(perr)
    if frange.dl_freq_min < 2620 or frange.dl_freq_min > 2690 \
       or frange.dl_freq_max < 2620 or frange.dl_freq_max > 2690:
        perr = portal.ParameterError("Band 7 downlink frequencies must be between 2620 and 2690 MHz", ["b7_freq_ranges[%d].dl_freq_min" % i, "b7_freq_ranges[%d].dl_freq_max" % i])
        portal.context.reportError(perr)
    if frange.dl_freq_max - frange.dl_freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["b7_freq_ranges[%d].dl_freq_min" % i, "b7_freq_ranges[%d].dl_freq_max" % i])
        portal.context.reportError(perr)

# Now verify.
portal.context.verifyParameters()

# Allocate orchestrator node
orch = request.RawPC("orch")
orch.disk_image = orch_image
orch.hardware_type = params.orchtype

# Request PC + CBRS X310 resource pairs.
for rsite in params.cbrs_radio_sites:
    x310_node_pair(rsite.radio, params.nodetype, orch.name)

# Request PC + Cellular X310 resource pairs.
for rsite in params.cell_radio_sites:
    x310_node_pair(rsite.radio, params.nodetype, orch.name)

# Request nuc2+B210 radio resources at FE sites.
for fesite in params.fe_radio_sites:
    nuc = ""
    for urn,sname in fe_sites:
        if urn == fesite.site:
            nuc = request.RawPC("%s-b210" % sname)
            break
    nuc.component_manager_id = fesite.site
    nuc.component_id = "nuc2"
    nuc.disk_image = nuc_image
    
# Request frequency range(s)
for frange in params.cbrs_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

for frange in params.b7_freq_ranges:
    request.requestSpectrum(frange.ul_freq_min, frange.ul_freq_max, 0)
    request.requestSpectrum(frange.dl_freq_min, frange.dl_freq_max, 0)
    
# Emit!
portal.context.printRequestRSpec()
