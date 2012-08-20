#!/usr/bin/env python

import os, sys
import pwd, grp
from stomplistenerdaemon import StompListenerDaemon

#stomp uses logging module
import logging
import logging.handlers

def setup_logging():
    logger = logging.getLogger()

    #To get more logs, change this to DEBUG
    logger.setLevel(logging.DEBUG)

    filehandler = logging.handlers.TimedRotatingFileHandler('/tmp/daemon.log',
                                                            when='midnight',
                                                            interval=1,backupCount=3)
    formatter = logging.Formatter("%(asctime)-15s %(name)s: %(message)s")
    filehandler.setFormatter(formatter)
    logger.addHandler(filehandler)

def drop_privileges(uid_name='nobody', gid_name='nobody'):
    if os.getuid() != 0:
        # We're not root so, like, whatever dude
        return

    # Get the uid/gid from the name
    running_uid = pwd.getpwnam(uid_name).pw_uid
    running_gid = grp.getgrnam(gid_name).gr_gid

    # Remove group privileges
    os.setgroups([])

    # Try setting the new uid/gid
    os.setgid(running_gid)
    os.setuid(running_uid)

    # Ensure a very conservative umask
    old_umask = os.umask(077)

if __name__ == "__main__":
    #help python find the stomp module packaged with the script
    os.chdir(os.path.dirname(sys.argv[0]))
    drop_privileges('puppet')
    setup_logging()
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
