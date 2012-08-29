
import os, sys
import logging
import shutil
import common
import signal
import subprocess
git = common.git

#return an array of channels to subscribe to
def getDestination():
    return ["/topic/git/wrlinux", "/topic/git/stomp-hook"]

#callback when a stomp message arrives
def on_message(headers, message):

    dest = headers['destination']
    gitdir, old_rev, new_rev, ref_name = message.strip().split(' ')

    if dest == "/topic/git/stomp-hook":
        repodir = '/var/lib/puppet/repos/git-stomp-hooks'
        os.chdir(repodir)

        #Since repo is non-bare, need to use fetch and reset
        git(['fetch','--all'])
        git(['reset','--hard','origin/master'])

        logging.info('Auto-restarting daemon to pick up changes' )

        os.environ["PATH"] = os.environ["PATH"] + ":" + repodir
        args = ["reloader.py"]
        subprocess.Popen(args)

        #send sigterm to have this instance clean up properly using sigterm handler
        os.kill(os.getpid(), signal.SIGTERM)

    else:
        branchname = os.path.basename(ref_name)
        logging.info('Update to branch %s on repo %s.' % (branchname, gitdir))

        #The convention for deleted branches is to have rev = 0000...
        if new_rev.startswith('0'):
            #deleting existing branch
            if os.path.exists(gitdir) and os.path.isdir(gitdir):
                logging.info('Deleting branch %s.' % gitdir)
                shutil.rmtree(gitdir)

        else:
            if os.path.exists(gitdir) and os.path.isdir(gitdir):
                #environment already exists, just update
                os.chdir(gitdir)
                git(['remote','update','--prune'])
