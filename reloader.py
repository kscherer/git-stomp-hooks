#!/usr/bin/env python

import os, sys, time
import subprocess

#Give stomp daemon time to exit
time.sleep(2)

args = ["git-stomp-listener.py","start"]
subprocess.check_call(args)

sys.exit()
