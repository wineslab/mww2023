#!/usr/bin/python

"""
Allocate some number of X310 radios (+ compute) for doing measurements.

Instructions:

None.

"""

# Library imports
import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.emulab.pnext as pn
import geni.rspec.emulab.spectrum as spectrum
import geni.rspec.igext as ig


# Global Variables
x310_node_disk_image = \
        "urn:publicid:IDN+emulab.net+image+PowderTeam:U18-GR-PBUF"
setup_command = "/local/repository/startup.sh"
installs = ["gnuradio"]

# Top-level request object.
request = portal.context.makeRequestRSpec()

# Helper function that allocates a PC + X310 radio pair, with Ethernet
# link between them.
def x310_node_pair(idx, x310_radio_name, node_type):
    radio_link = request.Link("radio-link-%d" % idx)

    node = request.RawPC("%s-comp" % x310_radio_name)
    node.hardware_type = node_type
    node.disk_image = x310_node_disk_image

    #service_command = " ".join([setup_command] + installs)
    #node.addService(rspec.Execute(shell="bash", command=service_command))

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

# List of CBRS rooftop X310 radios.
rooftop_names = [
    ("cbrssdr1-bes",
     "Behavioral"),
    ("cbrssdr1-browning",
     "Browning"),
    ("cbrssdr1-dentistry",
     "Dentistry"),
    ("cbrssdr1-fm",
     "Friendship Manor"),
    ("cbrssdr1-honors",
     "Honors"),
    ("cbrssdr1-smt",
     "SMT"),
    ("cbrssdr1-ustar",
     "USTAR"),
]

# Set of X310 radios to allocate
portal.context.defineStructParameter(
    "radio_sites", "Radio Sites", [],
    multiValue=True,
    min=1,
    multiValueTitle="X310 radios to allocate.",
    members=[
        portal.Parameter(
            "radio",
            "Radio Site",
            portal.ParameterType.STRING,
            rooftop_names[0], rooftop_names,
            longDescription="X310 radio will be allocated from selected site."
        ),
    ])

# Frequency/spectrum parameters
portal.context.defineStructParameter(
    "freq_ranges", "Range", [],
    multiValue=True,
    min=1,
    multiValueTitle="Frequency ranges for over-the-air operation.",
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

# Bind and verify parameters
params = portal.context.bindParameters()

for i, frange in enumerate(params.freq_ranges):
    if frange.freq_min < 3400 or frange.freq_min > 3800 \
       or frange.freq_max < 3400 or frange.freq_max > 3800:
        perr = portal.ParameterError("Frequencies must be between 3400 and 3800 MHz", ["freq_ranges[%d].freq_min" % i, "freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)
    if frange.freq_max - frange.freq_min < 1:
        perr = portal.ParameterError("Minimum and maximum frequencies must be separated by at least 1 MHz", ["freq_ranges[%d].freq_min" % i, "freq_ranges[%d].freq_max" % i])
        portal.context.reportError(perr)

portal.context.verifyParameters()

# Request frequency range(s)
for frange in params.freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

# Request PC + X310 resource pairs.
i = 0
for rsite in params.radio_sites:
    x310_node_pair(i, rsite.radio, params.nodetype, installs)
    i += 1

# Emit!
portal.context.printRequestRSpec()
