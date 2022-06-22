# --------------------------------
# File      : main.py
# Author    : Doomlad
# Date      : 06/16/2022
# Info      : Mod Version Maintainer is an open source Minecraft mods versioning utility
#             designed to be cross platform compatible written entirely in Python.
# --------------------------------
#
# Copyright 2022 Doomlad
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be
# used to endorse or promote products derived from this software without specific prior
# written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
# SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT
# OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
# TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __init__ import *
from mvm import ModVersionMaintainer

__version__ = "0.1.0"


def main():
    print(f"{Fore.LIGHTMAGENTA_EX}Welcome to {Fore.LIGHTCYAN_EX}Mod Version Maintainer (MVM){Fore.LIGHTMAGENTA_EX} v{__version__} - Copyright 2022 Doomlad{Style.RESET_ALL}")

    # TODO: rewrite this so it reads disclaimer from github repo and just creates a disclaimer.txt file with AGREE=YES in it.
    with open('disclaimer.txt', 'r') as file:
        disclaimer_msg = file.read()

    if "AGREE=YES" in disclaimer_msg:
        pass
    else:
        print(f"\n{Fore.LIGHTMAGENTA_EX}MVM is preparing for first time launch...{Style.RESET_ALL}\n")
        # Print disclaimer message and ask user to accept or deny; continue is accept, exit if deny
        disclaimer = input(f"{Fore.YELLOW}{disclaimer_msg}\n\n{Fore.LIGHTMAGENTA_EX}Agree? (Y)es/(N)o: {Style.RESET_ALL}")

        if disclaimer in ['y', 'yes']:
            with open('disclaimer.txt', 'a') as file:
                file.write('\nAGREE=YES')
        else:
            input("You have chosen to not accept the disclaimer. Program will exit when you press the ENTER key.")
            exit()
    
    # Instantiate MVM object
    mvm = ModVersionMaintainer()

    # Prompt user for %appdata% roaming .minecraft/mods folder
    # TODO: Store this in a config file and just read from it instead of asking everytime.
    yn_default = input(f"\n{Fore.LIGHTGREEN_EX}Default mods folder location: [{mvm.mods_folder}]\n{Fore.LIGHTMAGENTA_EX}Confirm? (Y)es/(N)o: {Style.RESET_ALL}")

    # If its not in the default location, have the user provide the absolute path
    if yn_default.lower() in ["n", "no"]: 
        mvm.mods_folder = input(f"\nMods folder not in default location, please provide the full path to your mods folder.\n{Fore.LIGHTMAGENTA_EX}Path: {Style.RESET_ALL}")

    # Call process mods method
    mvm.process_mods()    

    # Process links based on game version and mod type
    mvm.process_links(mvm.mod_type, mvm.mc_version)

    
    os.system('pause')


if __name__ == '__main__':
    main()
