#!/bin/bash


ORCHNAME="orch"

EMUBOOT=/var/emulab/boot
REPODIR=/local/repository
SHOUTSRC=/local/repository/shout
CLILOG=/var/tmp/ccontroller.log

# Install dependencies for GRC
REQUIRED_PKG="python3-gi"
PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
echo Checking for $REQUIRED_PKG: $PKG_OK
if [ "" = "$PKG_OK" ]; then
  echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
  sudo apt-get update
  sudo apt -y install python3-gi gobject-introspection gir1.2-gtk-3.0
fi

cd $REPODIR
git submodule update --init --remote || \
    { echo "Failed to update git submodules!" && exit 1; }

sudo ntpdate -u ops.emulab.net && \
    sudo ntpdate -u ops.emulab.net || \
	echo "Failed to update clock via NTP!"

sudo rm $CLILOG

ORCHDOM=`$REPODIR/bin/getexpdom.py`
ORCHHOST="$ORCHNAME.$ORCHDOM"

$SHOUTSRC/meascli.py -s $ORCHHOST

exit 0


#ip="155.98.37.211"

#today=$(date +"%m_%d_%Y")
#now=$(date +"%T")

#out="/var/emulab/save/$today"
#mkdir "$out"
#out="/var/emulab/save/$today/$now"
#mkdir "$out"

#cd /local/repository/shout
#python3 meascli.py -p 2000 -s $ip -l "$out/log" 
#python3 meascli.py -p 2000 -s $ip 