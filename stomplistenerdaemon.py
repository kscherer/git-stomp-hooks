
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
        logging.error('received an error %s' % message)
    def on_message(self, headers, message):
        HostHandler.on_message(headers, message)

class AutoConnectListener(stomp.ConnectionListener):
    def __init__(self, connection ):
        self.__connection = connection
        self.__destinations = HostHandler.getDestination()

    def on_connecting(self, host_and_port):
        self.__connection.connect()

    def on_connected(self, headers, body):
        for dest in self.__destinations:
            self.__connection.subscribe(destination=dest, ack='auto')

    def on_disconnected(self):
        logging.info('Received disconnect event')

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

        #setup a reasonable umask after daemon code cleared it
        os.umask(022)

        conn=common.createStompConnection()
        conn.set_listener('Auto',AutoConnectListener(conn))
        conn.set_listener('Git',StompListener())

        destinations=HostHandler.getDestination()
        # main work loop
        while not self.is_stopping():
            if not conn.connected:
                logging.info('Attempting to restart connection')
                try:
                    conn.start()
                except:
                    #Wait a bit and try again
                    logging.info('Connection failed. Will try again.')

            time.sleep(2)

        # SIGTERM receieved so we have exited loop
        logging.info('Main loop exited')
        conn.stop()
