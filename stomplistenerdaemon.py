
import os, sys, time
import common
import stomp
import signal
import daemon
import logging

#load the actions specific to this host
#This way one git repo can be used on multiple machines
import platform
HostHandler = __import__(platform.node())

class StompListener(stomp.ConnectionListener):
    def on_error(self, headers, message):
        print('received an error %s' % message)
    def on_message(self, headers, message):
        dest = headers['destination']
        logging.info('On channel {} received message\n {}'.format(dest, message) )
        gitdir, old_rev, new_rev, ref_name = message.strip().split(' ')
        HostHandler.on_message(dest, gitdir, old_rev, new_rev, ref_name)

class StompListenerDaemon(daemon.Daemon):
    """
    Implementation of python daemon class
    including a signal handler and connection to stomp.
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
        signal.signal(signal.SIGTERM, self.set_stop)

        conn=common.createStompConnection()
        conn.set_listener('Git',StompListener())
        conn.start()
        conn.connect(wait=True)

        destinations=HostHandler.getDestination()
        for dest in destinations:
            conn.subscribe(destination=dest, ack='auto')

        # main work loop
        while not self.is_stopping():
            time.sleep(60)

        # SIGTERM receieved so we have exited loop
        conn.stop()
