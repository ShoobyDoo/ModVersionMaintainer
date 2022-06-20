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

import glob
import re
import time
import cloudscraper
import urllib.request
import json
from pprint import pprint
from bs4 import BeautifulSoup
from colorama import Back, Fore, Style


# Some global variables
__version__ = "1.0.0"
mods_folder = r"C:\Users\shoai\AppData\Roaming\.minecraft\mods"
mods_dict = {}
curseforge_url = r"https://www.curseforge.com/minecraft/mc-mods/"
minecraft_versions_api = r"https://launchermeta.mojang.com/mc/game/version_manifest.json"
all_minecraft_versions = []
# TODO: release types are r = release b = beta, not fabric or forge. rewrite this.
# mod_types = {'forge': 'releasetype', 'fabric': '-releasetype'}
all_files = []

# List of known aliases, for when some mod name urls dont resolve after auto split
# Will be most likely moved to a publicly accessible file and regularly updated once
# further testing is performed.
known_aliases = {
    'fabric': 'fabric-api',
    'xaeros': 'xaeros-minimap',
    'iris': 'irisshaders'
    }

known_outliers = {
    'wurst': 'https://www.wurstclient.net/download/all/'
}


def process_links(mod_type, mc_version = 1.19, delay=3) -> None:
    global mods_dict
    global known_aliases
    global all_files

    # TODO: IMPLEMENT MC_VERSION ABOVE

    RESPONSE_PADDING = 37
    RESPONSE_MESSAGE_PADDING = 20
    STATUS_CODE_GOOGLE_LINK = "https://www.google.ca/search?q=status+code+"

    while True:
        is_403 = False

        print(f"{Fore.LIGHTGREEN_EX}Initializing CloudFare web-scraper.")
        # We initialize a CloudFare bypass scraper (works the exact same as requests library)
        scraper = cloudscraper.create_scraper(delay=10)
        print(f"{Fore.LIGHTGREEN_EX}Scraper ready, starting to build and crawl mod links.{Style.RESET_ALL}\n")

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
            mod_url = f"{curseforge_url}{key_fmtd}/files"
            print(f"Processing mod {Fore.LIGHTCYAN_EX}{key_fmtd}{Style.RESET_ALL}: ".ljust(46) + f"{Style.RESET_ALL}| {Fore.LIGHTCYAN_EX}{mod_url}{Style.RESET_ALL}")

            # And here we begin scraping the webpages. We give a generic user agent and let cloudscraper hopefuly bypass cloudfare.
            # Please note that during my very limited testing (ie. like a few hours) it's kind of inconsistent. Sometimes the requests will go
            # through, and sometimes we're met with a 403 error because of captcha.
            # 
            # Just please do not abuse the update checks; requesting too frequently and you will likely get captcha blocked.
            # TODO: The actual request portion has been commented out while I work on the rest of functionality so as not to constantly send reqs.

            res = scraper.get(mod_url, headers={'User-Agent': 'Mozilla/5.0'})
            
            counter = 0
            file_headers = ['Type', 'Name', 'Size', 'Uploaded', 'Game Version', 'Downloads', 'Actions']
            file_attr_dict = {}

            if res.ok:
                soup = BeautifulSoup(res.text, "html.parser")
                for tr in soup.select("tr"):
                    counter = 0
                    for td in tr.find_all("td"):
                        if '\n' in td.text.strip():
                            file_attr = td.text.strip().split('\n')[0]
                        else:
                            file_attr = td.text.strip()
                        file_attr_dict.update({file_headers[counter]: file_attr})
                        counter += 1

                    all_files.append(file_attr_dict)

                print("Response: ".ljust(RESPONSE_PADDING) + f"| {Fore.LIGHTGREEN_EX}{res.status_code}: OK.".ljust(RESPONSE_MESSAGE_PADDING) + f"(✓){Style.RESET_ALL}\n")

            elif res.status_code == 404:
                if key_fmtd in known_outliers.keys():
                    print("Response: ".ljust(RESPONSE_PADDING) + f"| {Fore.LIGHTYELLOW_EX}{res.status_code}: KNOWN MOD.".ljust(RESPONSE_MESSAGE_PADDING) + f"(*) -> SEE: {known_outliers[key_fmtd]}{Style.RESET_ALL}\n")
                else:
                    print("Response: ".ljust(RESPONSE_PADDING) + f"| {Fore.LIGHTYELLOW_EX}{res.status_code}: NOT FOUND.".ljust(RESPONSE_MESSAGE_PADDING) + f"(*) -> CHECK URL MANUALLY.{Style.RESET_ALL}\n")

            elif res.status_code == 403:
                print("Response: ".ljust(RESPONSE_PADDING) + f"| {Fore.LIGHTRED_EX}{res.status_code}: FORBIDDEN.".ljust(RESPONSE_MESSAGE_PADDING) + f"(X) -> LIKELY REQUEST IS CAPTCHA BLOCKED.{Style.RESET_ALL}\n")
                is_403 = True

            elif res.status_code == 503:
                print("Response: ".ljust(RESPONSE_PADDING) + f"| {Fore.LIGHTRED_EX}{res.status_code}: UNAVAILABLE.".ljust(RESPONSE_MESSAGE_PADDING) + f"(X) -> SERVER IS OVERLOADED OR IN MAINTENANCE.{Style.RESET_ALL}\n")

            elif res.status_code == 504:
                print("Response: ".ljust(RESPONSE_PADDING) + f"| {Fore.LIGHTRED_EX}{res.status_code}: TIMED OUT.".ljust(RESPONSE_MESSAGE_PADDING) + f"(X) -> REQUEST WAS TIMED OUT. IS CURSEFORGE DOWN?{Style.RESET_ALL}\n")

            else:
                print("Response: ".ljust(RESPONSE_PADDING) + f"| {Fore.LIGHTYELLOW_EX}{res.status_code}: UNKNOWN.".ljust(RESPONSE_MESSAGE_PADDING) + f"(?) -> SEE: {STATUS_CODE_GOOGLE_LINK}{res.status_code}{Style.RESET_ALL}\n")

        if is_403:
            print(f"{Fore.LIGHTYELLOW_EX}Some if not all links returned status code: 403 (forbidden). Waiting 3 seconds to retry...{Style.RESET_ALL}\n")
            time.sleep(delay)
            continue
        else:
            break


def main():
    global mods_folder
    global mods_dict
    global curseforge_url
    global all_minecraft_versions

    # TODO: Welcome banner, temporarily has prepping first launch msg, will be changed once config file is implemented
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

    # Prompt user for %appdata% roaming .minecraft/mods folder
    # TODO: Store this in a config file and just read from it instead of asking everytime.
    yn_default = input(f"\n{Fore.LIGHTGREEN_EX}Default mods folder location: [{mods_folder}]\n{Fore.LIGHTMAGENTA_EX}Confirm? (Y)es/(N)o: {Style.RESET_ALL}")

    # If its not in the default location, have the user provide the absolute path
    if yn_default.lower() in ["n", "no"]: mods_folder = input(f"\nMods folder not in default location, please provide the full path to your mods folder.\n{Fore.LIGHTMAGENTA_EX}Path: {Style.RESET_ALL}")

    # Set mod type to unknown for now, will be updated if keywords fabric or forge are found in jars
    mod_type = "unknown"
    print(f"\n{Fore.LIGHTMAGENTA_EX}Scanning your mods folder...\n{Style.RESET_ALL}")

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

        mods_dict.update({mod_name: jar_file})

        # Get index of current mod + 1 since zero indexed to get the mod in the list and print the mod and file name
        print(f"{mods.index(mod) + 1}. {mod_name.ljust(33)} | {jar_file}")

    # Let user know how many total mods were parsed, then let user know that we're checking for the mod type
    # This will be later used to determine the filter that needs to be applied when scraping the webpage for download links
    print(f"\n{Fore.LIGHTGREEN_EX}Total mods parsed: {len(mods)}{Style.RESET_ALL}\n\n{Fore.LIGHTMAGENTA_EX}Determining mods type (forge/fabric)...{Style.RESET_ALL}")

    # If the mod type remained unknown, it means none of the mods gave an indication of what type they were. We need to prompt the user instead
    if mod_type == "unknown":
        mod_type = input(f"Unable to determine your mod type. Please provide your mod type by entering either forge or fabric.\n{Fore.LIGHTMAGENTA_EX}Mod type: {Style.RESET_ALL}")
        print(f"{Fore.LIGHTGREEN_EX}{mod_type.capitalize()} selected as mod type.{Style.RESET_ALL}") if mod_type.lower() == "fabric" else print(f"{Fore.LIGHTGREEN_EX}{mod_type.capitalize()} selected as mod type.{Style.RESET_ALL}")
    # If the mod type isn't unknown, likely forge or fabric, then we print a positive message to the user letting them know the mod type was automatically determined
    else:
        print(f"{Fore.LIGHTGREEN_EX}Mods containing keyword {mod_type.lower()} were found; {mod_type.lower()} selected.{Style.RESET_ALL}")

    # Let user know we are trying to determine the appropriate minecraft version
    print(f"\n{Fore.LIGHTMAGENTA_EX}Trying to automatically determine Minecraft version...\nQuerying Minecraft versions API...{Style.RESET_ALL}")

    # TODO: query the minecraft versions api and extract list of minecraft versions, then loop through and find a match by looping thru modfiles
    with urllib.request.urlopen(minecraft_versions_api) as api:
        json_obj = json.loads(api.read().decode())
        for _versions in json_obj['versions']:
            if _versions['type'] == 'release':
                all_minecraft_versions.append(_versions)
        del json_obj

    print(f"{Fore.LIGHTGREEN_EX}{len(all_minecraft_versions)} total versions were pulled.{Style.RESET_ALL}")

    # Now we let the user know that we need to build the mod links that correspond to the curse forge website
    print(f"\n{Fore.LIGHTMAGENTA_EX}Attempting to build mod links to CurseForge...{Style.RESET_ALL}")
    
    # Process links based on game version and mod type
    process_links(mod_type)

    print(f"All links resolved, successfully returned {len(all_files)} attributes for {len(mods)} mods.")
    # pprint(all_files, sort_dicts=False)


if __name__ == '__main__':
    main()
