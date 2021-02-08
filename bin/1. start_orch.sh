#!/bin/bash
ip -4 -brief address show
cd /local/repository/shout
python3 orchestrator.py -p 2000