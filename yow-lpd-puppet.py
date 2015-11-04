
import os
import logging
import shutil
import common
import signal
import subprocess
git = common.git
RUBY193 = "/opt/rh/ruby193/root"


def getDestination():
    """return an array of channels to subscribe to"""
    return ["/topic/git/puppet", "/topic/git/stomp-hook"]


def trigger_librarian_puppet(puppet_env):
    """Call librarian-puppet install in the puppet environment dir"""
    args = [RUBY193 + '/usr/local/bin/librarian-puppet', 'install', '--quiet', '--destructive']
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=puppet_env,
                            env={"LD_LIBRARY_PATH": RUBY193 + "/usr/lib64",
                                 "PATH": "/bin:/usr/bin:/usr/sbin:/sbin",
                                 "HOME": "/var/lib/puppet"})
    details = proc.stdout.read()
    details = details.strip()
    return details


def on_message(headers, message):
    """callback when a stomp message arrives"""

    dest = headers['destination']
    gitdir, old_rev, new_rev, ref_name = message.strip().split(' ')

    if dest == "/topic/git/stomp-hook":
        repodir = '/var/lib/puppet/repos/git-stomp-hooks'
        os.chdir(repodir)

        #Since repo is non-bare, need to use fetch and reset
        git(['fetch', '--all'])
        git(['reset', '--hard', 'origin/master'])

        logging.info('Auto-restarting daemon to pick up changes')

        os.environ["PATH"] = os.environ["PATH"] + ":" + repodir
        args = ["reloader.py"]
        subprocess.Popen(args)

        #send sigterm to have this instance clean up properly using sigterm handler
        os.kill(os.getpid(), signal.SIGTERM)

    else:
        #use the default environment.
        branchname = os.path.basename(ref_name)
        puppet_env_base = '/etc/puppet/environments'
        puppet_env = os.path.join(puppet_env_base, branchname)

        #The convention for deleted branches is to have rev = 0000...
        if len(new_rev.strip('0')) == 0:
            #deleting existing branch
            if os.path.exists(puppet_env) and os.path.isdir(puppet_env):
                logging.info('Deleting environment %s.', puppet_env)
                shutil.rmtree(puppet_env)

        else:
            if os.path.exists(puppet_env) and os.path.isdir(puppet_env):
                #environment already exists, just update
                os.chdir(puppet_env)
                git(['fetch', '--all'])
                git(['reset', '--hard', 'origin/' + branchname])

                logging.info('Updated environment %s.', puppet_env)
            else:
                #new branch, so clone puppet repo to directory with name of branch
                os.chdir(puppet_env_base)
                git(['clone', '--branch', branchname,
                     'git://ala-git.wrs.com/users/buildadmin/wr-puppet-modules.git',
                     branchname])
                os.chdir(puppet_env)
                logging.info('Created environment %s.', puppet_env)

            # Trigger librarian-puppet on every run because attempts
            # to be smarter about it haven't worked
            trigger_librarian_puppet(puppet_env)

        #trigger restart of puppet master
        subprocess.Popen(['/bin/touch', '/etc/puppet/rack/tmp/restart.txt'], stdout=subprocess.PIPE)
