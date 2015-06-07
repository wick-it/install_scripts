#!/usr/bin/python


import signal
import sys
import curses
import subprocess
import re
import os.path


# TODO: pip list --outdated
# TODO: make the highlight start on the first intalled item
# TODO: first item can sometimes not be highlighted
# TODO: check screensize and change script accordingly
# TODO: upgrade: apt-get --just-print upgrade 2>&1 | perl -ne 'if (/Inst\s([\w,\-,\d,\.,~,:,\+]+)\s\[([\w,\-,\d,\.,~,:,\+]+)\]\s\(([\w,\-,\d,\.,~,:,\+]+)\)? /i) {print "PROGRAM: $1 INSTALLED: $2 AVAILABLE: $3\n"}'

PIP     = "pip"
APT_GET = "apt-get"
DOTFILE = "dotfile"
CUSTOM  = "custom"



class Installation_menu:

######################
## INITIALISE PROGRAM
######################

    myscreen = None
    position = 0


    def signal_handler(self, signal, frame):
        curses.endwin()
        sys.exit(130)


######################
## DEFINE CONSTANTS
######################
    end_program = False
    verbose     = False
    constants   = {}

    constants['pip']                = PIP
    constants['apt_get']            = APT_GET
    constants['dotfile']            = DOTFILE
    constants['custom']             = CUSTOM
    constants['menu']               = "menu"
    constants['command']            = "command"
    constants['exitmenu']           = "exitmenu"
    constants['format_normal']      = curses.A_NORMAL
    constants['menu_start_x']       = 10
    constants['menu_start_y']       = 5
    constants['additional_options'] = 3

    end_program = False


    def determine_longest_name(self):
        longest = 0
        for item in self.menu_items:
            if len(item['name']) > longest:
                longest = len(item['name'])
        return longest


######################
## Define functions
######################

    def initialise_constants(self):

        curses.start_color() # Lets you use colors when highlighting selected menu option
        curses.use_default_colors()
        curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(2, 5, -1)
        curses.init_pair(3,curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(4, 2, -1)

        self.constants['format_highlight']   = curses.color_pair(1)
        self.constants['format_dim']         = curses.color_pair(2)
        self.constants['format_selected']    = curses.color_pair(3)
        self.constants['format_upgrade']     = curses.color_pair(4)

        self.constants['menu_options']       = len(self.menu_items)
        self.constants['select_position']    = self.constants['menu_options']
        self.constants['deselect_position']  = self.constants['menu_options'] + 1
        self.constants['install_position']   = self.constants['menu_options'] + 2

        self.constants['menu_max_y'], self.constants['menu_max_x'] = self.myscreen.getmaxyx()

        self.constants['minimum_required_x'] = self.constants['menu_start_x'] + self.determine_longest_name()
        self.constants['minimum_required_y'] = self.constants['menu_start_y'] + self.constants['menu_options']

    def validate_screen_size_or_quit(self):
        if self.constants['menu_max_y'] < self.constants['minimum_required_y']:
            curses.endwin()
            print "Program gracefully closed after seeing window is too small"
            sys.exit(0)
        elif self.constants['menu_max_x'] < self.constants['minimum_required_x']:
            curses.endwin()
            print "Program gracefully closed after seeing window is too small"
            sys.exit(0)


    def get_installed_status(self,package):
        try:
            if package['type'] == self.constants['apt_get']:
                out = subprocess.check_output(['dpkg-query','-W',"-f=${Status} ${Version}",package['name']],stderr=subprocess.PIPE)
                result = re.search("installed",out)
                return result is not None
            elif package['type'] == self.constants['pip']:
                out = subprocess.check_output(['pip','show',package['name']])
                return len(out) > 0
            elif package['type'] == self.constants['dotfile']:
                home = os.path.expanduser('~') + '/'
                return os.path.isfile(home + package['name'])
            if package['type'] == self.constants['custom']:
                return package['check_install_def']()

        except:
            return False

    def set_all_installed_statuses(self):
        for item in self.menu_items:
            item['installed'] = self.get_installed_status(item)
            #if item['installed']: Maybe find something else here
            #    item['name'] = item['name'] + ' (installed)'
            item['selected']  = False


    def get_hash_of_all_upgradeble_packages(self):

        all_upgradeble_packages = {}
        out = subprocess.check_output(['apt-get','--just-print','upgrade'])
        lines = out.split('\n')
        for line in lines:
            matches = re.search(
                'Inst\s([\w,\-,\d,\.,~,:,\+]+)\s\[([\w,\-,\d,\.,~,:,\+]+)\]\s\(([\w,\-,\d,\.,~,:,\+]+)\)?',
                line,
                re.IGNORECASE
            )
            if matches is not None and len(matches.groups()) == 3:
                all_upgradeble_packages[matches.group(1)] = {
                    'current'   :   matches.group(2),
                    'new'       :   matches.group(3)
                }
        return all_upgradeble_packages

    def get_all_upgraded_statuses(self):
        upgradeble_packages = self.get_hash_of_all_upgradeble_packages()
        for item in self.menu_items:
            if item['installed']:
                if item['name'] in upgradeble_packages.keys():
                    item['name'] = item['name']
                    item['upgradeable'] = True
                else:
                    item['upgradeable'] = False
                    item['name'] = item['name']

            #if item['installed']: Maybe find something else here


    def get_initial_position(self):
        position = 0
        for item in self.menu_items:
            if item['installed'] == False or item['upgradeable'] == True:
                return position
            position += 1
        return self.constants['select_position']

    def install_selected_items(self):
        curses.endwin()
        for item in self.menu_items:
            if item['selected']:
                if item['type'] == DOTFILE:
                    home = os.path.expanduser('~') + '/'
                    subprocess.call(['ln','-sf',home + '.dotfiles/dotfiles/' + item['name'],home + item['name']])
                elif item['type'] == CUSTOM:
                    item['install_def']()
                elif item['type'] == APT_GET:
                    subprocess.call(['sudo','apt-get','install',item['name']])
                elif item['type'] == PIP:
                    subprocess.call(['sudo','pip','install',item['name']])
                print "Installed " + item['name']

        sys.exit(0)


    def handle_select_event(self):
        if self.position >= 0 and self.position < self.constants['menu_options']:
            if self.menu_items[self.position]['selected']:
                self.menu_items[self.position]['selected'] = False
            else:
                self.menu_items[self.position]['selected'] = True
        elif self.position == self.constants['select_position']:
            for item in self.menu_items:
                item['selected'] = True
        elif self.position == self.constants['deselect_position']:
            for item in self.menu_items:
                item['selected'] = False
        elif self.position == self.constants['install_position']:
            self.install_selected_items()



    def draw_menu(self):
        counter = 0
        for menu_item in self.menu_items:
            item_format = None
            item_append = ""
            if self.position == counter:
                item_format = self.constants['format_highlight']
            elif menu_item['selected']:
                item_format = self.constants['format_selected']
            elif menu_item['installed']:
                if menu_item['upgradeable']:
                    item_format = self.constants['format_upgrade']
                    item_append = " (upgradeable)"
                else:
                    item_format = self.constants['format_dim']
                    item_append = " (installed)"
            else:
                item_format = self.constants['format_normal']
            self.myscreen.addstr(
                self.constants['menu_start_y'] + counter
                , self.constants['menu_start_x']
                , menu_item['name'] + item_append
                , item_format
            )
            counter += 1
        select_format   = self.constants['format_normal']
        deselect_format = self.constants['format_normal']
        install_format  = self.constants['format_normal']
        if self.position == self.constants['select_position']:
            select_format   = self.constants['format_highlight']
        if self.position == self.constants['deselect_position']:
            deselect_format = self.constants['format_highlight']
        if self.position == self.constants['install_position']:
            install_format  = self.constants['format_highlight']
        self.myscreen.addstr(self.constants['menu_start_y'] + counter + 2 , self.constants['menu_start_x'] + 3  , "Select all"             ,select_format  )
        self.myscreen.addstr(self.constants['menu_start_y'] + counter + 2 , self.constants['menu_start_x'] + 18 , "Deselect all"           ,deselect_format)
        self.myscreen.addstr(self.constants['menu_start_y'] + counter + 2 , self.constants['menu_start_x'] + 35 , "Install selected items" ,install_format )

        self.myscreen.addstr(0,0,"")
        self.myscreen.refresh()


    def get_new_position(self,new_position,old_position,direction):
            if direction == 'down' and new_position == 0:
               return old_position
            elif direction == 'up' and new_position == self.constants['menu_options'] - 1 + self.constants['additional_options']:
                return old_position
            elif direction == 'up' and new_position < self.constants['menu_options'] - 1 + self.constants['additional_options']:
                if self.is_allowed_position(new_position+1):
                    new_position += 1
                else:
                    new_position = self.get_new_position(new_position+1,old_position,direction)
            elif direction == 'down' and new_position > 0:
                if self.is_allowed_position(new_position-1):
                    new_position -= 1
                else:
                    new_position = self.get_new_position(new_position-1,old_position,direction)
            return new_position


    def is_allowed_position(self,position):
        if position < self.constants['menu_options']:
            if self.menu_items[position]['installed']:
                return self.menu_items[position]['upgradeable']
            else:
                return True
        elif position < self.constants['menu_options'] + self.constants['additional_options']:
            return True
        else:
            return False

######################
## EXECUTE PROGRAM
######################

    def set_instant_io_flush(self):
        sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0) # set io flush to instant, because else the print messages will not be displayed

    def catch_ctrlc_command_and_quit_nicely(self):
        signal.signal(signal.SIGINT, self.signal_handler)

    def start_listening_to_key_commands(self):
        self.position = self.get_initial_position()
        self.draw_menu()

        while(self.end_program == False):
            input_character = self.myscreen.getch()
            if input_character == 106: # k
                self.position = self.get_new_position(self.position,self.position,'up')
            elif input_character == 107: # j
                self.position = self.get_new_position(self.position,self.position,'down')
            elif input_character == 32: # spacebar
                self.handle_select_event()

            self.draw_menu()


    def run_program(self,screen):
        self.myscreen = screen
        self.initialise_constants()
        self.validate_screen_size_or_quit()
        self.catch_ctrlc_command_and_quit_nicely()
        self.start_listening_to_key_commands()


    def __init__(self, menu_items, verbose=False):
        self.set_instant_io_flush()
        self.menu_items = menu_items
        self.verbose = verbose
        if verbose:
            sys.stdout.write("Retrieving installed status...")
        self.set_all_installed_statuses()
        if verbose:
            sys.stdout.write("  Done!\n")

        if verbose:
            sys.stdout.write("Retrieving upgraded status...")
        self.get_all_upgraded_statuses()
        if verbose:
            sys.stdout.write("  Done!\n")

        curses.wrapper(self.run_program)

