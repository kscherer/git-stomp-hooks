
import os, sys
import logging
import common
git = common.git

#return an array of channels to subscribe to
def getDestination():
    return ["/topic/git/puppet"]

#callback when a stomp message arrives
def on_message(dest, gitdir, old_rev, new_rev, ref_name):
    os.chdir('/home/kscherer/devel/stomp/bare2')
    logging.info('Updating bare2')

    #prune will delete branches that have been deleted from origin
    #only works of repo is bare and has remote mirror configured
    git(['remote','update','--prune'])
