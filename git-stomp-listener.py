#!/usr/bin/env python

import os, sys, time
import stomp
from daemon import Daemon

import signal
from signal import SIGTERM

import logging
import logging.handlers
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

filehandler = logging.handlers.TimedRotatingFileHandler('/tmp/daemon.log',when='midnight',interval=1,backupCount=9)
formatter = logging.Formatter("%(asctime)-15s %(name)s: %(message)s")
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)

import common
git = common.git

def updateRepo(gitdir, old_rev, new_rev, ref_name):
    os.chdir('/home/kscherer/devel/stomp/bare2')
    logger.info('Updating %s'% ref_name)
    
    #prune will delete branches that have been deleted from origin
    git(['remote','update','--prune'])

class MyListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print('received an error %s' % message)
    def on_message(self, headers, message):
        for k,v in headers.iteritems():
            logger.info('header: key %s , value %s' %(k,v))
        logger.info('received message\n %s'% message)
        gitdir, old_rev, new_rev, ref_name = message.strip().split(' ')
        updateRepo(gitdir, old_rev, new_rev, ref_name)

class StompListenerDaemon(Daemon):
    """
    Test implementation of python daemon class 
    including a signal handler.
    """
    def __init__(self,*args,**kwargs):
        # call init for parent
        super(StompListenerDaemon,self).__init__(*args,**kwargs)

        # init stuff particular to child
        self.stopping = False

    def set_stop(self,*args,**kwargs):
        """
        Signal handler. When executed we are going
        set stopping to True so daemon can exit
        """
        self.stopping = True

    def is_stopping(self):
        """
        Have we been told to stop?
        """
        return self.stopping

    def run(self):
        """
        Daemon run method. The actual stuff done
        by the daemon
        """
        # register our signal handler
        signal.signal(SIGTERM, self.set_stop)

        dest='/topic/git/puppet'
        conn=common.createStompConnection()
        conn.set_listener('Git',MyListener())
        conn.start()
        conn.connect(wait=True)
        conn.subscribe(destination=dest, ack='auto')

        # main work loop
        while not self.is_stopping():
            time.sleep(60)

        # SIGTERM receieved so we have exited loop
        conn.stop()

if __name__ == "__main__":
    daemon = StompListenerDaemon('/tmp/stomp-listener.pid')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        elif 'status' == sys.argv[1]:
            daemon.status()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart|status" % sys.argv[0]
        sys.exit(2)
