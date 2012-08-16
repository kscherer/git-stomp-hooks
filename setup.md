Development and test setup for Stomp git hooks

First create a bare repo

  git init --bare bare1

If there isn't a git daemon running start it like this:

  git daemon --export-all --enable=receive-pack --base-path=$PWD

Create the clone of bare1 that will be used to test pushes

  git clone git://localhost/bare1 bare1clone
  git clone --bare git://localhost/bare1 bare2

Since bare2 is a bare clone, it needs to be setup to follow bare1
master branch

  cd bare2
  git remote add --mirror=fetch master git://localhost/bare1

Get latest stomp.py code from here:
http://code.google.com/p/stomppy/downloads/detail?name=stomp.py-3.1.3.tar.gz

The workflow is:
1) Commit in bare1clone and push to bare1
2) Post-recieve in bare1 sends commit info to /topic/git/puppet using
stomp
3) Stomp Listener receives stomp broadcast and updates bare2

Clone the files from
ala-git.wrs.com/git/users/kscherer/git-stomp-hooks

In the hooks directory of bare clone being pushed to, link both
post-receive and post-receive-stomp.py. This will enable the broadcast
to stomp after a push.

On the mirror clone, run git-stomp-listener.py start to start the
listening service.
