#!/usr/bin/python

import scripts_menu

def tryer():
    return False

menu_items = [
   {'name' :  '.bash_profile'              , 'type' : scripts_menu.DOTFILE },
   {'name' :  '.tmux.conf'                 , 'type' : scripts_menu.DOTFILE },
   {'name' :  '.bashrc'                    , 'type' : scripts_menu.DOTFILE },
   {'name' :  '.vimrc'                     , 'type' : scripts_menu.DOTFILE },
   {'name' :  '.alias'                     , 'type' : scripts_menu.DOTFILE },
   {'name' :  'git'                        , 'type' : scripts_menu.APT_GET },
   {'name' :  'htop'                       , 'type' : scripts_menu.APT_GET },
   {'name' :  'ack-grep'                   , 'type' : scripts_menu.APT_GET },
   {'name' :  'fail2ban'                   , 'type' : scripts_menu.APT_GET },
   {'name' :  'python-pip'                 , 'type' : scripts_menu.APT_GET },
   {'name' :  'python-dev'                 , 'type' : scripts_menu.APT_GET },
   {'name' :  'build-essential'            , 'type' : scripts_menu.APT_GET },
   {'name' :  'python-mysqldb'             , 'type' : scripts_menu.APT_GET },
   {'name' :  'mysql-server'               , 'type' : scripts_menu.APT_GET },
   {'name' :  'apache2'                    , 'type' : scripts_menu.APT_GET },
   {'name' :  'libapache2-mod-wsgi'        , 'type' : scripts_menu.APT_GET },
   {'name' :  'unattended-upgrades'        , 'type' : scripts_menu.APT_GET },
   {'name' :  'texlive-latex-base'         , 'type' : scripts_menu.APT_GET },
   {'name' :  'texlive-latex-extra'        , 'type' : scripts_menu.APT_GET },
   {'name' :  'libapache2-mod-xsendfile'   , 'type' : scripts_menu.APT_GET },
   {'name' :  'libsystemd-login0'          , 'type' : scripts_menu.APT_GET },
   {'name' :  'qrcode'                     , 'type' : scripts_menu.PIP     },
   {'name' :  'paramiko'                   , 'type' : scripts_menu.PIP     },
   {'name' :  'pillow'                     , 'type' : scripts_menu.PIP     },
   {'name' :  'python-crontab'             , 'type' : scripts_menu.PIP     },
   {'name' :  'TEST-FILE'                  , 'type' : scripts_menu.CUSTOM  , 'check_install_def': tryer , 'install_def': tryer},
   {'name' :  'google-api-python-client'   , 'type' : scripts_menu.PIP     },
]

obj = scripts_menu.Installation_menu(menu_items,verbose=True)
