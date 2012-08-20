
import os, sys
import logging
import shutil
import common
git = common.git

#return an array of channels to subscribe to
def getDestination():
    return ["/topic/git/puppet", "/topic/git/stomp-hook"]

#callback when a stomp message arrives
def on_message(dest, gitdir, old_rev, new_rev, ref_name):
    if dest == "/topic/git/stomp-hook":
        os.chdir('/var/lib/puppet/repos/git-stomp-hooks')

        #prune will delete branches that have been deleted from origin
        git(['remote','update','--prune'])
    else:
        branchname = os.path.basename(refname)
        puppet_env_base = '/etc/puppet/environments'
        puppet_env = puppet_env_base + '/' + branchname

        if new_rev.startswith('0'):
            #deleting existing branch
            if os.path.exists(puppet_env) and os.path.isdir(puppet_env):
                shutil.rmtree(puppet_env)

        else:
            if os.path.exists(puppet_env) and os.path.isdir(puppet_env):
                #environment already exists, just update
                git(['fetch','--all'])
                git(['reset','--hard','origin/' + branchname])
            else:
                #new branch, so clone puppet repo to new branch
                git(['clone',
                     'git://ala-git.wrs.com/users/buildadmin/wr-puppet-modules.git',
                     puppet_env_base,
                     '--branch',
                     branchname])