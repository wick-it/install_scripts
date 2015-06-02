#!/usr/bin/python


import signal
import sys
import curses
import subprocess
import re
import os.path


# TODO: pip list --outdated
# TODO: make the highlight start on the first intalled item


######################
## INITIALISE PROGRAM
######################

myscreen = curses.initscr()
curses.start_color() # Lets you use colors when highlighting selected menu option
curses.use_default_colors()
curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE)
curses.init_pair(2, 5, -1)
curses.init_pair(3,curses.COLOR_BLACK, curses.COLOR_GREEN)


def signal_handler(signal, frame):
    curses.endwin()
    sys.exit(130)
signal.signal(signal.SIGINT, signal_handler)


######################
## DEFINE CONSTANTS
######################

MENU        = "menu"
COMMAND     = "command"
EXITMENU    = "exitmenu"
FORMAT_HIGHLIGHT  = curses.color_pair(1)
FORMAT_DIM        = curses.color_pair(2)
FORMAT_SELECTED   = curses.color_pair(3)
FORMAT_NORMAL     = curses.A_NORMAL
MENU_START_X      = 5
MENU_START_Y      = 10

PIP = "pip"
APT_GET = "apt-get"
DOTFILE = "dotfile"

menu_items = [
    {'name' :  '.bash_profile'              , 'type' : DOTFILE },
    {'name' :  '.tmux.conf'                 , 'type' : DOTFILE },
    {'name' :  '.bashrc'                    , 'type' : DOTFILE },
    {'name' :  '.vimrc'                     , 'type' : DOTFILE },
    {'name' :  '.alias'                     , 'type' : DOTFILE },
    {'name' :  'git'                        , 'type' : APT_GET },
    {'name' :  'htop'                       , 'type' : APT_GET },
    {'name' :  'ack-grep'                   , 'type' : APT_GET },
    {'name' :  'fail2ban'                   , 'type' : APT_GET },
    {'name' :  'python-pip'                 , 'type' : APT_GET },
    {'name' :  'python-dev'                 , 'type' : APT_GET },
    {'name' :  'build-essential'            , 'type' : APT_GET },
    {'name' :  'python-mysqldb'             , 'type' : APT_GET },
    {'name' :  'mysql-server'               , 'type' : APT_GET },
    {'name' :  'apache2'                    , 'type' : APT_GET },
    {'name' :  'libapache2-mod-wsgi'        , 'type' : APT_GET },
    {'name' :  'unattended-upgrades'        , 'type' : APT_GET },
    {'name' :  'texlive-latex-base'         , 'type' : APT_GET },
    {'name' :  'texlive-latex-extra'        , 'type' : APT_GET },
    {'name' :  'libapache2-mod-xsendfile'   , 'type' : APT_GET },
    {'name' :  'qrcode'                     , 'type' : PIP     },
    {'name' :  'paramiko'                   , 'type' : PIP     },
    {'name' :  'pillow'                     , 'type' : PIP     },
    {'name' :  'python-crontab'             , 'type' : PIP     },
]

end_program = False

# libjpeg62 libjpeg62-dev zlib1g-dev libfreetype6 libfreetype6-dev

MENU_OPTIONS        = len(menu_items)
ADDITIONAL_OPTIONS  = 3
SELECT_POSITION     = MENU_OPTIONS
DESELECT_POSITION   = MENU_OPTIONS + 1
INSTALL_POSITION    = MENU_OPTIONS + 2


######################
## Define functions
######################
def get_installed_status(package):
    try:
        if package['type'] == APT_GET:
            out = subprocess.check_output(['dpkg-query','-W',"-f=${Status} ${Version}",package['name']],stderr=subprocess.PIPE)
            result = re.search("installed",out)
            return result is not None
        elif package['type'] == PIP:
            out = subprocess.check_output(['pip','show',package['name']])
            return len(out) > 0
        if package['type'] == DOTFILE:
            home = os.path.expanduser('~') + '/'
            return os.path.isfile(home + package['name'])

    except:
        return False

def initialise_menu(menu_items):
    for item in menu_items:
        item['installed'] = get_installed_status(item)
        if item['installed']:
            item['name'] = item['name'] + ' (installed)'
        item['selected']  = False

def get_initial_position():
    position = 0
    for item in menu_items:
        if item['installed'] == False:
            return position
        position += 1
    return SELECT_POSITION

def install_selected_items():
    for item in menu_items:
        if item['selected']:
            if item['type'] == DOTFILE:
                home = os.path.expanduser('~') + '/'
                subprocess.call(['ln','-sf',home + '.dotfiles/dotfiles/' + item['name'],home + item['name']])
    curses.endwin()
    print "Installed " + item['name']
    sys.exit(0)


def handle_select_event(position):
    if position > 0 and position < MENU_OPTIONS:
        if menu_items[position]['selected']:
            menu_items[position]['selected'] = False
        else:
            menu_items[position]['selected'] = True
    elif position == SELECT_POSITION:
        for item in menu_items:
            item['selected'] = True
    elif position == DESELECT_POSITION:
        for item in menu_items:
            item['selected'] = False
    elif position == INSTALL_POSITION:
        install_selected_items()



def draw_menu(position):
    counter = 0
    for menu_item in menu_items:
        item_format = None
        if position == counter:
            item_format = FORMAT_HIGHLIGHT
        elif menu_item['installed']:
            item_format = FORMAT_DIM
        elif menu_item['selected']:
            item_format = FORMAT_SELECTED
        else:
            item_format = FORMAT_NORMAL
        myscreen.addstr(
            MENU_START_X + counter
            , MENU_START_Y
            , menu_item['name']
            , item_format
        )
        counter += 1
    select_format   = FORMAT_NORMAL
    deselect_format = FORMAT_NORMAL
    install_format  = FORMAT_NORMAL
    if position == SELECT_POSITION:
        select_format   = FORMAT_HIGHLIGHT
    if position == DESELECT_POSITION:
        deselect_format = FORMAT_HIGHLIGHT
    if position == INSTALL_POSITION:
        install_format  = FORMAT_HIGHLIGHT
    myscreen.addstr(MENU_START_X + counter + 2 , MENU_START_Y + 3  , "Select all"             ,select_format  )
    myscreen.addstr(MENU_START_X + counter + 2 , MENU_START_Y + 18 , "Deselect all"           ,deselect_format)
    myscreen.addstr(MENU_START_X + counter + 2 , MENU_START_Y + 35 , "Install selected items" ,install_format )

    myscreen.addstr(0,0,"")
    myscreen.refresh()


def get_new_position(new_position,old_position,direction):
        if direction == 'down' and new_position == 0:
           return old_position
        elif direction == 'up' and new_position == MENU_OPTIONS - 1 + ADDITIONAL_OPTIONS:
            return old_position
        elif direction == 'up' and new_position < MENU_OPTIONS - 1 + ADDITIONAL_OPTIONS:
            if is_allowed_position(new_position+1):
                new_position += 1
            else:
                new_position = get_new_position(new_position+1,old_position,direction)
        elif direction == 'down' and new_position > 0:
            if is_allowed_position(new_position-1):
                new_position -= 1
            else:
                new_position = get_new_position(new_position-1,old_position,direction)
        return new_position


def is_allowed_position(position):
    if position < MENU_OPTIONS:
        return not menu_items[position]['installed']
    elif position < MENU_OPTIONS + ADDITIONAL_OPTIONS :
        return True
    else:
        return False

######################
## EXECUTE PROGRAM
######################


def execute():
    initialise_menu(menu_items)
    position = get_initial_position()
    draw_menu(position)

    while(end_program == False):
        input_character = myscreen.getch()
        if input_character == 106: # k
            position = get_new_position(position,position,'up')
        elif input_character == 107: # j
            position = get_new_position(position,position,'down')
        elif input_character == 32: # spacebar
            handle_select_event(position)

        draw_menu(position)

execute()
curses.endwin()

