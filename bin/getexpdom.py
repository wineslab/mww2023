#!/usr/bin/env python3

import sys
import subprocess
import xml.etree.ElementTree as ET

GENIGET = "/usr/bin/geni-get"
PORTALDOM = "emulab.net"

ns = {
    'rspec': 'http://www.geni.net/resources/rspec/3',
    'elab':  'http://www.protogeni.net/resources/rspec/ext/emulab/1',
}

mani = subprocess.run([GENIGET, "manifest"], stdout=subprocess.PIPE).stdout.decode('utf-8')
mtree = ET.fromstring(mani)
portal = mtree.find("./elab:portal", ns)
domain = ".".join([portal.attrib['experiment'], portal.attrib['project'], PORTALDOM])
print(domain)
