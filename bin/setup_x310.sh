#!/bin/bash

sudo apt -y install python3-gi gobject-introspection gir1.2-gtk-3.0

"/usr/lib/uhd/utils/uhd_images_downloader.py"

"/usr/bin/uhd_image_loader" --args="type=x300,addr=192.168.40.2"
