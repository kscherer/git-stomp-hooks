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
        return 'yow-lpd-puppet2.wrs.com'
    elif site_prefix == 'pek':
        return 'pek-lpd-puppet.wrs.com'

    return 'ala-lpd-puppet.wrs.com'

def createStompConnection():
    #local debugging and testing with stompserver
    if platform.node() == 'yow-kscherer-d1':
        return stomp.Connection([('localhost', 61613)])

    return stomp.Connection([(getActiveMQServer(), 6163)], 'amq', 'secret')
