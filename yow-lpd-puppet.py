
import os, sys
import logging
import shutil
import common
import signal
import subprocess
git = common.git

#return an array of channels to subscribe to
def getDestination():
    return ["/topic/git/puppet", "/topic/git/stomp-hook"]

#callback when a stomp message arrives
def on_message(headers, message):

    dest = headers['destination']
    gitdir, old_rev, new_rev, ref_name = message.strip().split(' ')

    if dest == "/topic/git/stomp-hook":
        repodir = '/var/lib/puppet/repos/git-stomp-hooks'
        os.chdir(repodir)

        logging.info('Auto-restarting daemon to pick up changes' )

        os.environ["PATH"] = os.environ["PATH"] + ":" + repodir
        subprocess.Popen(args)

        #send sigterm to have this instance clean up properly using sigterm handler
        os.kill(os.getpid(), signal.SIGTERM)

    else:
        #use the default environment.
        branchname = os.path.basename(ref_name)
        puppet_env_base = '/etc/puppet/environments'
        puppet_env = puppet_env_base + '/' + branchname

        #The convention for deleted branches is to have rev = 0000...
        if len(new_rev.strip('0')) == 0:
            #deleting existing branch
            if os.path.exists(puppet_env) and os.path.isdir(puppet_env):
                logging.info('Deleting environment %s.' % puppet_env)
                shutil.rmtree(puppet_env)

        else:
            if os.path.exists(puppet_env) and os.path.isdir(puppet_env):
                #environment already exists, just update
                os.chdir(puppet_env)
                git(['fetch','--all'])
                git(['reset','--hard','origin/' + branchname])
                logging.info('Updated environment %s.' % puppet_env)
            else:
                #new branch, so clone puppet repo to new branch
                os.chdir(puppet_env_base)
                git(['clone',
                     'git://ala-git.wrs.com/users/buildadmin/wr-puppet-modules.git',
                     '--branch',
                     branchname,
                     branchname])
                logging.info('Created environment %s.' % puppet_env)
