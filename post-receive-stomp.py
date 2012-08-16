
import subprocess
import sys, os
import platform
import stomp
import common

git = common.git

def main():
    git_dir = ''
    if git(['rev-parse','--is-bare-repository']) == 'true':
        git_dir = os.getcwd()
    else:
        git_dir = os.path.dirname(os.getcwd())

    conn=common.createStompConnection()
    conn.start()
    conn.connect(wait=True)

    dest=sys.argv[1]
    lines = sys.stdin.readlines()
    for line in lines:
        old_rev, new_rev, ref_name = line.strip().split(' ')
        message="{} {} {} {}".format(git_dir,old_rev,new_rev,ref_name)
        conn.send(message=message, destination=dest, headers={}, ack='auto')

    conn.stop()

if __name__ == '__main__':
    main()
