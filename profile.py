#!/usr/bin/python

"""
Allocate some number of X310 radios (+ compute), FE NUC1+B210, and FE NUC2+B210, for doing measurements. 
Work for both CBRS and Cellular band resources.

Instructions:


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
clisetup_cmd = "/local/repository/bin/cli-startup.sh"
orchsetup_cmd = "/local/repository/bin/orch-startup.sh"

# Top-level request object.
request = portal.context.makeRequestRSpec()

# Helper function that allocates a PC + X310 radio pair, with Ethernet
# link between them.
def x310_node_pair(x310_radio_name, node_type):
    radio_link = request.Link("%s-link" % x310_radio_name)

    node = request.RawPC("%s-comp" % x310_radio_name)
    node.hardware_type = node_type
    node.disk_image = x310_node_image

    #node.addService(rspec.Execute(shell="bash",command=clisetup_cmd + " %s" % orchhost))

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
    portal.ParameterType.STRING, "None",
    ["None", "d430","d740"],
    "Type of compute node for the orchestrator (unset == 'any available')",
)

# Node type for the GPS client.
portal.context.defineParameter(
    "gpsclienttype",
    "GPS client node type",
    portal.ParameterType.STRING, "None",
    ["None", "d430","d740"],
    "Type of compute node for the GPS client (unset == 'any available')",
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
    ("urn:publicid:IDN+bus-4407.powderwireless.net+authority+cm",
     "Bus4407"),
    ("urn:publicid:IDN+bus-6185.powderwireless.net+authority+cm",
     "Bus6185"),
    ("urn:publicid:IDN+bus-4409.powderwireless.net+authority+cm",
     "Bus4409"),
    ("urn:publicid:IDN+bus-4410.powderwireless.net+authority+cm",
     "Bus4410"),
    ("urn:publicid:IDN+bus-4417.powderwireless.net+authority+cm",
     "Bus4417"),
    ("urn:publicid:IDN+bus-4208.powderwireless.net+authority+cm",
     "Bus4208"),
    ("urn:publicid:IDN+bus-4329.powderwireless.net+authority+cm",
     "Bus4329"),
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

# Set of Fixed Endpoint devices to allocate (nuc1)
portal.context.defineStructParameter(
    "fe_radio_sites_nuc1", "Fixed Endpoint Sites", [],
    multiValue=True,
    min=0,
    multiValueTitle="Fixed Endpoint NUC1+B210 radios to allocate for CBRS.",
    members=[
        portal.Parameter(
            "site",
            "FE Site",
            portal.ParameterType.STRING,
            fe_sites[0], fe_sites,
            longDescription="A `nuc1` device will be selected at the site."
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
            2620.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Downlink Frequency Max",
            portal.ParameterType.BANDWIDTH,
            2630.0,
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
            2500.0,
            longDescription="Values are rounded to the nearest kilohertz."
        ),
        portal.Parameter(
            "freq_max",
            "Uplink Frequency Max",
            portal.ParameterType.BANDWIDTH,
            2510.0,
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

# Now verify.
portal.context.verifyParameters()

# Allocate orchestrator node
if params.orchtype != "None":
    orch = request.RawPC("orch")
    orch.disk_image = orch_image
    orch.hardware_type = params.orchtype
    orch.addService(rspec.Execute(shell="bash", command=orchsetup_cmd))

# Allocate GPS client node
if params.gpsclienttype != "None":
    orch = request.RawPC("gps")
    orch.disk_image = orch_image
    orch.hardware_type = params.gpsclienttype
    orch.addService(rspec.Execute(shell="bash", command=orchsetup_cmd))

# Request PC + CBRS X310 resource pairs.
for rsite in params.cbrs_radio_sites:
    x310_node_pair(rsite.radio, params.nodetype)

# Request PC + Cellular X310 resource pairs.
for rsite in params.cell_radio_sites:
    x310_node_pair(rsite.radio, params.nodetype)

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
    #nuc.addService(rspec.Execute(shell="bash", command=clisetup_cmd))

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
    #nuc.addService(rspec.Execute(shell="bash", command=clisetup_cmd))


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
    node.addService(rspec.Execute(shell="bash", command=clisetup_cmd))

    
# Request frequency range(s)
for frange in params.cbrs_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

for frange in params.b7_ul_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)

for frange in params.b7_dl_freq_ranges:
    request.requestSpectrum(frange.freq_min, frange.freq_max, 0)
    
# Emit!
portal.context.printRequestRSpec()
