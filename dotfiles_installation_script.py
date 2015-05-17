#!/usr/bin/python

import subprocess

subprocess.call(['clear'])


#tmux ssh
print "Make sure tmux does link to old ssh agent"
subprocess.call(['sudo','cp','tmux','/usr/local/bin'])

#make symbolic links to everywhere
print "Starting to make symbolic links"
print "vimrc,",
subprocess.call(['ln','-sf','/home/dlos/.dotfiles/dotfiles/.vimrc','/home/dlos/.vimrc'])
print "tmux.conf,",
subprocess.call(['ln','-sf','/home/dlos/.dotfiles/dotfiles/.tmux.conf','/home/dlos/.tmux.conf'])
print "site_packages,",
subprocess.call(['ln','-sf','/home/dlos/.dotfiles/dotfiles/.site_packages','/home/dlos/.site_packages'])
print "bash_profile,",
subprocess.call(['ln','-sf','/home/dlos/.dotfiles/dotfiles/.bash_profile','/home/dlos/.bash_profile'])

print "completed!"
