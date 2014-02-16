#! /usr/bin/env python2
"""
Profiler for OpenTTD

Author: Adam Samalik
"""

import sys, os, shutil, re


"""
Game represents user's OpenTTD directory
Game.installed returns true if game is installed
Game.path returns user's game directory path
"""
class Game:
    _home = os.path.expanduser("~")
    _linux = os.path.join(_home, ".openttd")
    _windows = os.path.join(_home, "Documents", "OpenTTD")
    path = ""
    installed = False

    def __init__(self):
        if os.path.exists(self._linux):
            self.path = self._linux
            self.installed = True
        elif os.path.exists(self._windows):
            self.path = self._windows
            self.installed = True


"""
Needed by ProfilerUI
"""
class ProfilerError(Exception):
    def __init__(self, value):
        self.value = "ERROR: "+value
    def __str__(self):
        return repr(self.value)
        


"""
OpenTTD Profiler
needs user's game dicrectory path as an argument 
Profiler.installed - returns true/false
Profiler.active - returns active profile
Profiler.profiles - returns list of all profiles
Profiler.activate(name) - activates a profile
Profiler.new(name) - new empty profile
Profiler.save_as(name) - saves current state as a new profile
Profiler.remove(name) - removes unactive profile 
Profiler.install - makes a fresh installation
"""
class Profiler:
    _dirname = "profiler"
    _game_path = ""
    _profiler_path = ""
    _config_path = ""

    profiles = []
    installed = False
    active = ""

    def __init__(self, game_path):
        self._game_path = game_path
        self._profiler_path = os.path.join(self._game_path, self._dirname)
        self._config_path = os.path.join(self._profiler_path, "active.profile")
        if self._check_installation():
            self._load_active()
            self._load_profiles()
            self.installed = True

    def _check_installation(self):
        if os.path.exists(self._config_path):
            return True
        else:
            return False

    def _load_active(self):
        f = open(self._config_path, 'r')
        self.active = f.read()
        f.close()

    def _save_active(self, name):
        f = open(self._config_path, 'w')
        f.write(name)
        f.close()
        self.active = name

    def _load_profiles(self):
        del self.profiles[:]
        for f in os.listdir(self._profiler_path):
            if os.path.isdir(os.path.join(self._profiler_path, f)):
                self.profiles.append(f)

    def _get_home_filelist(self):
        files = []
        for f in os.listdir(self._game_path):
            if f != self._dirname:
                files.append(f)
        return files

    def activate(self, name):
        if name not in self.active and name in self.profiles:
            source = self._get_home_filelist()
            destination = os.path.join(self._profiler_path, self.active)
            os.makedirs(destination)
            for s in source:
                shutil.move(os.path.join(self._game_path,s), destination)
            source2 = os.listdir(os.path.join(self._profiler_path, name))
            destination2 = self._game_path
            for s in source2:
                shutil.move(os.path.join(self._profiler_path, name ,s), destination2)
            os.rmdir(os.path.join(self._profiler_path, name))
            self._save_active(name)
            self._load_profiles()
        else:
            if name in self.active:
                raise ProfilerError("Profile \""+name+"\" is already active!")
            else:
                raise ProfilerError("Profile \""+name+"\" doesn't exist!")
                

    def new(self, name):
        if name not in self.profiles and name != self.active:
            profile = os.path.join(self._profiler_path, name)
            os.makedirs(profile)
            self.profiles.append(name)
        else:
            raise ProfilerError("Profile \""+name+"\" already exists!")

    def save_as(self, name):
        if name not in self.profiles and name != self.active:
            files = self._game_path
            destination = os.path.join(self._profiler_path, name)
            shutil.copytree(files, destination, ignore=shutil.ignore_patterns(self._dirname))
            self.profiles.append(name)
        else:
            raise ProfilerError("Profile \""+name+"\" already exists!")

    def remove(self, name):
        if name in self.profiles:
            profile = os.path.join(self._profiler_path, name)
            shutil.rmtree(profile)
            self.profiles.remove(name)
        else:
            raise ProfilerError("Profile \""+name+"\" doesn't exist!")
    
    def install(self):
        if not os.path.exists(self._profiler_path):
            os.makedirs(self._profiler_path)
            self._save_active("default")
            self.installed = True
        else:
            raise ProfilerError("Error! Directory \"profiler\" already found but Profiler has not been installed! Installation has been aborted to prevent data loss. Please check "+self._profiler_path+" manually and delete it before installation.")



"""
User interface for Profiler
Needs Profiler instance as an argument
start it with .start() method
"""
class ProfilerUI:
    _profiler = None

    def __init__(self, game):
        self._profiler = Profiler(game.path)

    def _about(self):
        self._message("OpenTTD Profiler adds profiles into your game! Separates all user data including settings, graphics and saved games.")

    def start(self):
        if self._profiler.installed:
            self._main_menu()
        else:
            print "There is no Profiler installed in your OpenTTD!"
            answer = raw_input("Install Profiler? [y/N]:")
            if answer in ("y", "Y", "yes"):
                try:
                    self._profiler.install()
                    self._message("Installation complete!")
                    self._main_menu()
                except ProfilerError as detail:
                    self._message(detail.value)
                except (IOError, OSError) as detail:
                    self._message(str(detail))


    def _ask_name(self):
        while True:
            answer = raw_input("Please type a name (leave empty to cancel): ")
            if re.match("[^/\:]", answer) is not None or answer is "": 
                return answer
            else:
                self._message("Please avoid using \\, / and :")

    """
    Give me a list of options and I will ask user what option he wants.
    I'll return a number of that option 
    or -1 if the user doesn't want to choose anything (or types some ***)
    """
    def _ask_from_list(self, options):
        print ""
        for o in range(0,len(options)):
            print str(o)+"  "+options[o]
        answer = raw_input("Type a number (or nothing exit/go back): ")
        options_str = map(str, range(0, len(options)))
        if answer in options_str:
            return int(answer)
        else:
            return -1

    def _main_menu(self):
        running = True
        while running:
            print "\n\n..:: OpenTTD Profiler ::..\n"
            print "          Active:  "+self._profiler.active
            print " Other installed:  "+', '.join(self._profiler.profiles)
            options = [
                "New empty profile",
                "Load profile",
                "Save as profile",
                "Delete profile",
                "About OpenTTD Profiler"
            ]
            answer = self._ask_from_list(options)
            try:
                if answer == options.index("New empty profile"):
                    self._new()
                elif answer == options.index("Load profile"):
                    self._load()
                elif answer == options.index("Save as profile"):
                    self._save()
                elif answer == options.index("Delete profile"):
                    self._remove()
                elif answer == options.index("About OpenTTD Profiler"):
                    self._about()
                else:
                    running = False
            except ProfilerError as detail:
                self._message(detail.value)
            except (IOError, OSError) as detail:
                self._message(str(detail))

    def _message(self, message):
        print "\n"+message
        raw_input("Press Enter to continue...")

    def _new(self):
        print "\nNEW profile"
        name = self._ask_name()
        if len(name) > 0:
            self._profiler.new(name)
            self._message("Profile \""+name+"\" has been created")
        else:
            self._message("Canceled. No new profil created.")

    def _load(self):
        print "\nSelect a profile to be loaded:"
        answer = self._ask_from_list(self._profiler.profiles)
        if answer >= 0:
            profile = self._profiler.profiles[answer]
            self._profiler.activate(profile)
            self._message("Profile \""+profile+"\" has been loaded.")
        else:
            self._message("Canceled. No profile loaded.")
            
    def _save(self):
        print "SAVE active profile as"
        name = self._ask_name()
        if not len(name)==0:
            self._profiler.new(name)
            self._message("Active profile has been saved as \""+profile+"\".")
        else:
            self._message("Canceled. Nothing saved.")

    def _remove(self):
        print "\nSelect a profile to be deleted:"
        answer = self._ask_from_list(self._profiler.profiles)
        if answer >= 0:
            profile = self._profiler.profiles[answer]
            print "\nAttention: This opperation is irreversible!"
            really = raw_input("Do you really want to delete profile "+profile+" forever? [y/N]: ")
            if really in ("y", "Y", "yes"):
                self._profiler.remove(profile)
                self._message("Profile \""+profile+"\" has been deleted.")
            else:
                self._message("You answered no. No profile deleted.")
        else:
            self._message("Canceled. No profile deleted.")



def main():
    game = Game()
    if game.installed:
        ui = ProfilerUI(game)
        ui.start()
    else:
        print "OpenTTD is not installed. (or haven't been run for the first time)"
    

if __name__ == "__main__":
    main()
