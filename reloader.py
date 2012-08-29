#!/usr/bin/env python

import os, sys, time
import subprocess
import common
git = common.git

#Give stomp daemon time to exit
time.sleep(2)

#Since repo is non-bare, need to use fetch and reset
#git(['fetch','--all'])
#git(['reset','--hard','origin/master'])

args = ["git-stomp-listener.py","start"]
subprocess.check_call(args)

sys.exit()
