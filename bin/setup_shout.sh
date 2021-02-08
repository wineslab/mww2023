#!/bin/bash

cd /local/repository/
git pull origin master
git submodule init
git submodule update
