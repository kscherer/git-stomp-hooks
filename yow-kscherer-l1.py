
import os, sys, time
import logging
import subprocess
import common
import signal
git = common.git

#return an array of channels to subscribe to
def getDestination():
    return ["/topic/git/restart","/topic/git/ping"]

#callback when a stomp message arrives
def on_message(headers, message):

    dest = headers['destination']

    if dest == "/topic/git/restart":
        repodir = '/home/kscherer/repos/git-stomp-hooks'
        os.chdir(repodir)

        logging.info('Auto-restarting daemon to pick up changes' )

        os.environ["PATH"] = os.environ["PATH"] + ":" + repodir
        args = ["reloader.py"]
        subprocess.Popen(args)

        #send sigterm to have this instance clean up properly using sigterm handler
        os.kill(os.getpid(), signal.SIGTERM)
    else:
        logging.info('Ping message received')

