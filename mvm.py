# --------------------------------
# File      : mvm.py
# Author    : Doomlad
# Date      : 06/22/2022
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


class ModVersionMaintainer:
    def __init__(self) -> None:
        # Constants
        self._CURSEFORGE_URL = r"https://www.curseforge.com/minecraft/mc-mods/"
        self._MINECRAFT_VERSIONS_API = r"https://launchermeta.mojang.com/mc/game/version_manifest.json"
        self._KNOWN_ALIASES_GITHUB_LINK = r"https://raw.githubusercontent.com/ShoobyDoo/ModVersionMaintainer/main/known_aliases.json"
        self._KNOWN_OUTLIERS_GITHUB_LINK = r"https://raw.githubusercontent.com/ShoobyDoo/ModVersionMaintainer/main/known_outliers.json"
        
        # Instance variables
        self._mods_folder = r"C:\Users\shoai\AppData\Roaming\.minecraft\mods"
        self._mods_dict = {}
        self._all_minecraft_versions = []
        self._all_files = []
        self._mods = []

        self._mod_type = 'unknown'
        self._mc_version = 'unknown'

        # List of known aliases, for when some mod name urls dont resolve after auto split
        # Will be most likely moved to a publicly accessible file and regularly updated once further testing is performed.
        with urllib.request.urlopen(self._KNOWN_ALIASES_GITHUB_LINK) as api: self._known_aliases = json.loads(api.read().decode())
        with urllib.request.urlopen(self._KNOWN_OUTLIERS_GITHUB_LINK) as api: self._known_outliers = json.loads(api.read().decode())

    @property
    def mods_folder(self):
        return self._mods_folder
    
    @mods_folder.setter
    def mods_folder(self, mods_folder):
        self._mods_folder = mods_folder

    @property
    def mods_dict(self):
        return self._mods_dict
    
    @mods_dict.setter
    def mods_dict(self, new_mods_dict):
        self._mods_dict = new_mods_dict
    
    @property
    def all_minecraft_versions(self):
        return self._all_minecraft_versions
    
    @all_minecraft_versions.setter
    def all_minecraft_versions(self, new_url):
        self._curseforge_url = new_url
    
    @property
    def all_files(self):
        return self._all_files
    
    @all_minecraft_versions.setter
    def all_files(self, *args, mode = 'a'):
        if mode == 'a': 
            for arg in args: 
                self._all_files.append(arg)
        else:
            self._all_files = args[0]

    @property
    def mod_type(self):
        return self._mod_type
    
    @mod_type.setter
    def mod_type(self, mod_type):
        self._mod_type = mod_type
    
    @property
    def mc_version(self):
        return self._mc_version

    @mc_version.setter
    def mc_version(self, mc_version):
        self._mc_version = mc_version

    @property
    def mods(self):
        return self._mods
    
    @mods.setter
    def mods(self, mods):
        self._mods = mods

    @property
    def known_aliases(self):
        return self._known_aliases
    
    @known_aliases.setter
    def known_aliases(self, *args, mode = 'a', **kwargs):
        # mode a = append
        # mode r = remove
        if mode == 'a':
            for key, value in kwargs.items():
                self._known_aliases.update({key: value})
        elif mode == 'r':
            for alias in args:
                self._known_aliases.pop(alias)

    @property
    def known_outliers(self):
        return self._known_outliers

    @known_outliers.setter
    def known_outliers(self, *args, mode = 'a', **kwargs):
        # mode a = append
        # mode r = remove
        if mode == 'a':
            for key, value in kwargs.items():
                self._known_outliers.update({key: value})
        elif mode == 'r':
            for alias in args:
                self._known_outliers.pop(alias)


    def process_links(self, mod_type = 1, mc_version = "latest", delay=3) -> None:
        # mod_type 1: fabric
        # mod_type 2: forge
        # TODO: IMPLEMENT MC_VERSION ABOVE

        RESPONSE_PADDING = 37
        RESPONSE_MESSAGE_PADDING = 25
        STATUS_CODE_GOOGLE_LINK = "https://www.google.ca/search?q=status+code+"

        # Now we let the user know that we need to build the mod links that correspond to the curse forge website
        print(f"\n{Fore.LIGHTMAGENTA_EX}Attempting to build mod links to CurseForge...{Style.RESET_ALL}")

        while True:
            is_403 = False

            # We initialize a CloudFare bypass scraper (works the exact same as requests library)
            scraper = cloudscraper.create_scraper(delay=10)
            print(f"{Fore.LIGHTGREEN_EX}CloudFare bypass web-scraper initialized, starting to build and crawl mod links.{Style.RESET_ALL}\n")

            # We loop through all the mods
            for key in self.mods_dict:
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
                try: key_fmtd = self.known_aliases[key_fmtd]
                except KeyError: pass

                # Now we just build the final mod url using all the previously processed bits and pieces and let the user know
                mod_url = f"{self._CURSEFORGE_URL}{key_fmtd}/files"
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

                # TODO: MAKE LIST IN BETTER MORE ORGANIZED FASHION (BASED ON MOD_TYPE, )
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

                        self.all_files.append(file_attr_dict)

                    print("Response: ".ljust(RESPONSE_PADDING) + f"| {Fore.LIGHTGREEN_EX}{res.status_code}: OK.".ljust(RESPONSE_MESSAGE_PADDING) + f"(✓){Style.RESET_ALL}\n")

                elif res.status_code == 404:
                    if key_fmtd in self.known_outliers.keys():
                        print("Response: ".ljust(RESPONSE_PADDING) + f"| {Fore.LIGHTYELLOW_EX}{res.status_code}: KNOWN MOD.".ljust(RESPONSE_MESSAGE_PADDING) + f"(*) -> SEE: {self.known_outliers[key_fmtd]}{Style.RESET_ALL}\n")
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
            
        print(f"All links resolved, successfully returned {Fore.LIGHTGREEN_EX}{len(self.all_files)}{Style.RESET_ALL} attributes for {Fore.LIGHTCYAN_EX}{len(self.mods)}{Style.RESET_ALL} mods.")
        
        # TODO: Now we need to build the links to each of those mods

    
    def process_mods(self):
        # Set mod type to unknown for now, will be updated if keywords fabric or forge are found in jars
        # mod_type = "unknown"
        print(f"\n{Fore.LIGHTMAGENTA_EX}Scanning your mods folder...\n{Style.RESET_ALL}")

        # Search for all .jar files in the mods folder
        self.mods = glob.glob(f"{self._mods_folder}/*.jar")

        # Master loop; most processing will happen here; loop through each mod in the mods folder
        for mod in self.mods: 
            # Split at path folders to extract just the .jar file name
            jar_file = mod.split('\\')[-1]

            # Search for those keywords in the jar file name and update the mod_type variable to respective value
            if "fabric" in jar_file.lower():
                self.mod_type = "fabric"
            elif "forge" in jar_file.lower():
                self.mod_type = "forge"

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

            self.mods_dict.update({mod_name: jar_file})

            # Get index of current mod + 1 since zero indexed to get the mod in the list and print the mod and file name
            print(f"{self.mods.index(mod) + 1}. {mod_name.ljust(33)} | {jar_file}")

        # Let user know how many total mods were parsed, then let user know that we're checking for the mod type
        # This will be later used to determine the filter that needs to be applied when scraping the webpage for download links
        print(f"\n{Fore.LIGHTGREEN_EX}Total mods parsed: {len(self.mods)}{Style.RESET_ALL}\n\n{Fore.LIGHTMAGENTA_EX}Determining mods type (forge/fabric)...{Style.RESET_ALL}")

        # If the mod type remained unknown, it means none of the mods gave an indication of what type they were. We need to prompt the user instead
        if self.mod_type == "unknown":
            self.mod_type = input(f"Unable to determine your mod type. Please provide your mod type by entering either forge or fabric.\n{Fore.LIGHTMAGENTA_EX}Mod type: {Style.RESET_ALL}")
            print(f"{Fore.LIGHTGREEN_EX}{self.mod_type.capitalize()} selected as mod type.{Style.RESET_ALL}") if self.mod_type.lower() == "fabric" else print(f"{Fore.LIGHTGREEN_EX}{self.mod_type.capitalize()} selected as mod type.{Style.RESET_ALL}")
        # If the mod type isn't unknown, likely forge or fabric, then we print a positive message to the user letting them know the mod type was automatically determined
        else:
            print(f"{Fore.LIGHTGREEN_EX}Mods containing keyword {self.mod_type.lower()} were found; {self.mod_type.lower()} selected.{Style.RESET_ALL}")
        
        # Let user know we are trying to determine the appropriate minecraft version
        print(f"\n{Fore.LIGHTMAGENTA_EX}Trying to automatically determine Minecraft version...\nQuerying Minecraft versions API...{Style.RESET_ALL}")

        # Query the minecraft versions api and extract list of minecraft versions
        with urllib.request.urlopen(self._MINECRAFT_VERSIONS_API) as api:
            json_obj = json.loads(api.read().decode())
            for _versions in json_obj['versions']:
                if _versions['type'] == 'release':
                    self.all_minecraft_versions.append(_versions)

        print(f"{Fore.LIGHTGREEN_EX}Latest 'release' version of MC: {json_obj['latest']['release']} was successfully pulled, along with {len(self.all_minecraft_versions) - 1} others.{Style.RESET_ALL}")
        del json_obj # Discord giant json obj since we dont need it anymore

        is_match = False
        # Loop through and find a match by looping thru modfiles
        for mc_ver in self.all_minecraft_versions:
            if is_match: break
            for mod in self.mods:
                if str(mc_ver['id']).strip() in mod:
                    guessed_mc_version = mc_ver['id']
                    is_match = True
                    break
                else:
                    guessed_mc_version = None
        
        # TODO: FINISH UP
        if guessed_mc_version:
            is_correct = input(f"{Fore.LIGHTGREEN_EX}Auto detection found a potential match on the Minecraft version. Is {guessed_mc_version} correct?{Fore.LIGHTMAGENTA_EX}\n(Y)es/(N)o: {Style.RESET_ALL}")
        else:
            is_correct = input(f"{Fore.LIGHTYELLOW_EX}Auto detection could not detect the Minecraft version.\n{Fore.LIGHTMAGENTA_EX}Please enter your desired Minecraft version: {Style.RESET_ALL}")
