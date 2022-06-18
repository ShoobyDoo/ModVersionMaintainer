# --------------------------------
# File      : mvm.py
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

import sqlite3
import glob
import re
import time
import cloudscraper


# Some global variables
__version__ = "1.0.0"
mods_folder = r"C:\Users\shoai\AppData\Roaming\.minecraft\mods"
mods_dict = {}
curseforge_url = r"https://www.curseforge.com/minecraft/mc-mods/"
mod_types = {'forge': 'releasetype', 'fabric': '-releasetype'}

# List of known aliases, for when some mod name urls dont resolve after auto split
# Will be most likely moved to a publicly accessible file and regularly updated once
# further testing is performed.
known_aliases = {
    'fabric': 'fabric-api',
    'xaeros': 'xaeros-minimap',
    'iris': 'irisshaders'
    }


def main():
    global mods_folder
    global mods_dict
    global curseforge_url

    # TODO: Welcome banner, temporarily has prepping first launch msg, will be changed once config file is implemented
    print(f"Welcome to Mod Version Maintainer (MVM) v{__version__} - Copyright 2022 Doomlad\n\nPreparing first launch...")

    # Disclaimer
    with open('disclaimer.txt', 'r') as file:
        disclaimer_msg = file.read()

    # Print disclaimer message and ask user to accept or deny; continue is accept, exit if deny
    disclaimer = input(f"{disclaimer_msg}\n\n(Y)es/(N)o: ")
    # TODO: remove this
    disclaimer = 'y'
    if disclaimer in ['y', 'yes']:
        pass
    else:
        input("You have chosen to not accept the disclaimer. Program will exit when you press the ENTER key.")
        exit()

    # Prompt user for %appdata% roaming .minecraft/mods folder
    yn_default = input(f"\nDefault mods folder location: [{mods_folder}]\nConfirm? (Y)es/(N)o: ")

    # If its not in the default location, have the user provide the absolute path
    if yn_default.lower() in ["n", "no"]: mods_folder = input("\nMods folder not in default location, please provide the full path to your mods folder.\nPath: ")

    # Create (since first run) and connect to the master mods database
    db_connect = sqlite3.connect('mods.db')
    print("\nMods database created.")

    # Create cursor object and execute a query to create a table called mods (which will stores the currently installed mods)
    cursor = db_connect.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mods (name text, file text)''')
    print("Mods table created.\n\nScanning for mods...")

    # Set mod type to unknown for now, will be updated if keywords fabric or forge are found in jars
    mod_type = "unknown"

    # Search for all .jar files in the mods folder
    mods = glob.glob(f"{mods_folder}/*.jar")

    # Master loop; most processing will happen here; loop through each mod in the mods folder
    for mod in mods: 
        # Split at path folders to extract just the .jar file name
        jar_file = mod.split('\\')[-1]

        # Search for those keywords in the jar file name and update the mod_type variable to respective value
        if "fabric" in jar_file.lower():
            mod_type = "fabric"
        elif "forge" in jar_file.lower():
            mod_type = "forge"

        # Most mod jar file names are delimited by either a dash or an underscore.
        # If the delimiter is found in the file name, split at it and extract the very first index,
        # which will hopefully be the mod name.
        # 
        # We're kinda guessing here so this is likely to break on a mod that doesn't use those
        # delimiters but this will be updated in the future for most edge cases.
        if '-' in jar_file:
            mod_name = jar_file.split('-')[0]
        elif '_' in jar_file:
            mod_name = jar_file.split('_')[0]

        # TODO: Update the master mods_dict (temporary for testing, use db instead)
        mods_dict.update({mod_name: jar_file})

        # Get index of current mod + 1 since zero indexed to get the mod in the list and print the mod and file name
        print(f"{mods.index(mod) + 1}. {mod_name.ljust(33)} | {jar_file}")

    # Let user know how many total mods were parsed, then let user know that we're checking for the mod type
    # This will be later used to determine the filter that needs to be applied when scraping the webpage for download links
    print(f"Total mods parsed: {len(mods)}\n\nDetermining mods type (forge/fabric)...")

    # If the mod type remained unknown, it means none of the mods gave an indication of what type they were. We need to prompt the user instead
    if mod_type == "unknown":
        mod_type = input("Unable to determine your mod type. Please provide your mod type by entering either forge or fabric.\nMod type: ")
        print(f"{mod_type.capitalize()} selected as mod type.") if mod_type.lower() == "fabric" else print(f"{mod_type.capitalize()} selected as mod type.")
    # If the mod type isn't unknown, likely forge or fabric, then we print a positive message to the user letting them know the mod type was automatically determined
    else:
        print(f"Mods containing keyword {mod_type.lower()} were found; {mod_type.lower()} selected.")

    # Now we let the user know that we need to build the mod links that correspond to the curse forge website
    print("\nAttempting to build mod links to CurseForge...")
    
    process_links(mod_type)


def process_links(mod_type, delay=5) -> None:
    global mods_dict
    global known_aliases

    while True:
        is_403 = False

        # We initialize a CloudFare bypass scraper (works the exact same as requests library)
        scraper = cloudscraper.create_scraper(delay=10)

        # We loop through all the mods
        for key in mods_dict:
            # We try to determine if there's a mod name that got taken in but it's two words. for example MouseTweaks.
            multi_word = re.findall('[A-Z][^A-Z]*', key)
            
            # We instantiate a variable to store the formatted mod name which will be used to pull the respective mod page
            key_fmtd = key

            # If multi_word was true, meaning there were perhaps two words (which has been split by the re.findall method)
            if multi_word:
                # We want to reset the formatted mod name variable so as to build it up ourselves
                key_fmtd = ""
                # We loop through each word that was found, for example ['Mouse', 'Tweaks']
                for word in multi_word:
                    # if the word in multi is the last word, dont include the spacer dash
                    if word == multi_word[-1]:
                        key_fmtd += word.lower()
                    # otherwise include it, most links use it. example: curseforge.com/minecraft/mc-mods/mouse-tweaks
                    else:
                        key_fmtd += word.lower() + "-"

            # Now we want to see if there were any outliers, so we take the formatted mod name and try running it through any known aliases
            # If there are no errors, it means that mod name had an alias which has been set to the formatted mod name, otherwise we continue
            try: key_fmtd = known_aliases[key_fmtd]
            except KeyError: pass

            # Now we just build the final mod url using all the previously processed bits and pieces and let the user know
            mod_url = f"{curseforge_url}{key_fmtd}/files?sort={mod_types[mod_type]}"
            print(f"Processing {key_fmtd}: ".ljust(37) + f"| {mod_url}")

            # And here we begin scraping the webpages. We spoof the user agent as firefox and let cloudscraper hopefuly bypass cloudfare
            # Please note that during my very limited testing (ie. like a few hours) it's kind of inconsistent. Sometimes the requests will go
            # through, and sometimes we're met with a 403 error because of captcha. I'm trying to get an api key from curse forge to circumvent
            # this issue, but that seems to be the case for now. 
            # 
            # Just please do not abuse the update checks; requesting too frequently and you will likely get captcha blocked.
            # TODO: The actual request portion has been commented out while I work on the rest of functionality so as not to constantly send reqs.

            # res = scraper.get(mod_url, headers={'User-Agent': 'Mozilla/5.0'})
            #
            # if res.ok:
            #     print("Response: ".ljust(37) + f"| {res.status_code}: OK.       (✓)\n")
            # elif res.status_code == 404:
            #     print("Response: ".ljust(37) + f"| {res.status_code}: NOT FOUND (?); CHECK URL MANUALLY.\n")
            # else:
            #     print("Response: ".ljust(37) + f"| {res.status_code}: FORBIDDEN (X); LIKELY REQUEST IS CAPTCHA BLOCKED.\n")
            #     is_403 = True

        if is_403:
            print("\nSome if not all links returned Status code: 403 (forbidden). Waiting 3 seconds to retry...\n")
            time.sleep(delay)
            continue
        else:
            break


if __name__ == '__main__':
    main()
