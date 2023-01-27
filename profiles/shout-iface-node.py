#!/usr/bin/python

"""Use this profile to connect to the orchestrator of a separate, existing Shout automated RF measurements experiment. 

Instructions:
**1) Instantiate this profile with the name of the orchestrator to use.**

At the "Parameterize" step, paste in the hostname of the orchestrator as shown in the "Node" column of the "List View" of the existing Shout experiment. Click through the rest of the instantion wizard steps to instantiate.  It will take about 5-10 minutes for the experiment to finish setting up.  Once it is "green" and the "Startup" column for the single node in the experiment shows "finished", proceed to the next step.

**2) Open SSH sessions**

Use the following commands to start ssh and tmux sessions to the "iface" node:
```
ssh -Y -p 22 -t <username>@<iface_node_hostname> 'cd /local/repository/bin && tmux new-session -A -s measiface1 && exec $SHELL'
ssh -Y -p 22 -t <username>@<iface_node_hostname> 'cd /local/repository/bin && tmux new-session -A -s measiface2 && exec $SHELL'
```

A reference SSH command for the "iface" node can be seen on the "List View" tab of the instantiated experiment.

TMUX is helpful for doing multiple terminal sessions and allowing remote sessions to remain active even when the SSH connection to the nodes gets disconncted. A "cheat sheet" for interacting with TMUX sessions can be found here:

[TMUX Cheat Sheet](https://tmuxcheatsheet.com/)

**3) Execute a Shout measurement run**

Before executing, make sure that the separate Shout experiment is running its orchestrator, and that the appropriate set of measurement clients are connected. Once this is confirmed, you can perform measurement collection runs. There are example Shout JSON command (configuration) files located at: [This link](https://gitlab.flux.utah.edu/powder-profiles/shout-se-profile/-/tree/master/etc/cmdfiles) and `/local/repository/etc/cmdfiles` on the node.  Select one and edit it according to your measurement plan. Once the command file is properly adjusted, edit the `3.run_cmd.sh` script to point to the correct cmd file and output location.vNext, in your other "iface" node SSH session, run:

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

**4) Check saved dataset**

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
startup_script = "/local/repository/bin/ifnode-setup.sh"

# Add one or more lines to reference datasets you want to mount to
# the orchestrator node.
datasets = {
    "ChangeMeToFriendlyName": "ChangeMeToDatasetURN",
}

# Top-level request object.
request = portal.context.makeRequestRSpec()

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

portal.context.defineParameter(
    "orchnode",
    "Node name of existing Shout orchestrator",
    portal.ParameterType.STRING, "pc03-meb",
)

portal.context.defineParameter(
    "nodetype",
    "Node type to use",
    portal.ParameterType.STRING, "d430",
    ["d430","d740"],
    "Type of compute node to use for this Shout measurement interface node experiment.",
    advanced=True,
)

portal.context.defineParameter(
    "dataset",
    "Dataset to connect",
    portal.ParameterType.STRING, "None",
    ["SpectSet","ADSBRecordings","None"],
    "Name of the remote dataset to connect (optional).",
    advanced=True,
)

# Start VNC?
portal.context.defineParameter(
    "start_vnc",
    "Start X11 VNC on all compute nodes",
    portal.ParameterType.BOOLEAN, True,
    advanced=True,
)

# Bind and verify parameters
params = portal.context.bindParameters()

if params.orchnode == "":
    perr = portal.ParameterError("You must specify an orchestrator node id!",
                                 ["orchnode",])
    portal.context.reportError(perr)

# Now verify parameters.
portal.context.verifyParameters()

# Declare that we may be starting X11 VNC on the compute nodes.
if params.start_vnc:
    request.initVNC()

# Allocate the iface node
ifnode = request.RawPC("iface")
ifnode.disk_image = shout_image
ifnode.hardware_type = params.nodetype
if params.dataset != "None": 
    connect_to_dataset(ifnode, params.dataset)
if params.start_vnc:
    ifnode.startVNC()
ifnode.addService(rspec.Execute(shell="sh", command=startup_script + " " + params.orchnode))

# Emit!
portal.context.printRequestRSpec()
