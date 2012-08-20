#!/usr/bin/env python

import os, sys
from stomplistenerdaemon import StompListenerDaemon

#stomp uses logging module
import logging
import logging.handlers
logger = logging.getLogger()

#To get more logs, change this to DEBUG
logger.setLevel(logging.ERROR)

filehandler = logging.handlers.TimedRotatingFileHandler('/tmp/daemon.log',when='midnight',interval=1,backupCount=3)
formatter = logging.Formatter("%(asctime)-15s %(name)s: %(message)s")
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)

#help python find the stomp module packaged with the script
os.chdir(os.path.dirname(sys.argv[0]))

if __name__ == "__main__":
    daemon = StompListenerDaemon('/var/tmp/stomp-listener.pid')
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
