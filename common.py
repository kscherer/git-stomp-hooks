import subprocess
import sys
import platform
import stomp

def git(args):
    args = ['git'] + args
    git = subprocess.Popen(args, stdout = subprocess.PIPE)
    details = git.stdout.read()
    details = details.strip()
    return details

def getActiveMQServer():
    hostname = platform.node()
    site_prefix = hostname[0:3]
    if site_prefix == 'yow':
        return 'yow-lpg-amqp.wrs.com'
    elif site_prefix == 'pek':
        return 'pek-lpd-puppet.wrs.com'

    return 'ala-lpd-puppet.wrs.com'

def createStompConnection():
    return stomp.Connection([(getActiveMQServer(), 6163)], 'amq', 'secret')