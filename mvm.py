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
import time
import re
import requests


__version__ = "1.0.0"
mods_folder = r"C:\Users\shoai\AppData\Roaming\.minecraft\mods"
mods_dict = {}
curseforge_url = r"https://www.curseforge.com/minecraft/mc-mods/"


def main():
    global mods_folder
    global mods_dict
    global curseforge_url

    print(f"Welcome to Mod Version Maintainer (MVM) v{__version__} - Copyright 2022 Doomlad\n\nPreparing first launch...\n")

    yn_default = input(f"Default mods folder location: [{mods_folder}]\nConfirm? (Y)es/(N)o: ")
    if yn_default.lower() in ["n", "no"]: mods_folder = input("Mods folder not in default location, please provide the full path to your mods folder.\nPath: ")

    db_connect = sqlite3.connect('mods.db')
    print("\nMods database created.")

    cursor = db_connect.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS mods (name text, file text)''')
    print("Mods table created.\n\nScanning for mods...")

    mods = glob.glob(f"{mods_folder}/*.jar")
    for mod in mods: 
        jar_file = mod.split('\\')[-1]

        if '-' in jar_file:
            mod_name = jar_file.split('-')[0]
        elif '_' in jar_file:
            mod_name = jar_file.split('_')[0]

        mods_dict.update({mod_name: jar_file})
        print(f"{mods.index(mod) + 1}. {mod_name.ljust(31)} (/) {jar_file}")
        # time.sleep(0.10)

    print(f"Total mods parsed: {len(mods)}\n\nAttempting to test mod links against CurseForge...")
    
    for key in mods_dict:
        multi_word = re.findall('[A-Z][^A-Z]*', key)
        key_fmtd = key

        if multi_word:
            key_fmtd = ""
            for word in multi_word:
                # if the word in multi is the last word, dont include the spacer dash
                if word == multi_word[-1]:
                    key_fmtd += word.lower()
                # otherwise include it, most links use it. example: mouse-tweaks
                else:
                    key_fmtd += word.lower() + "-"

        mod_url = f"{curseforge_url}{key_fmtd}"

        print(f"Processing {key_fmtd}: ".ljust(35) + f"(?) {mod_url}")
        
        # res = requests.request("GET", mod_url, headers={'User-Agent': 'Mozilla/5.0'})
        # print(res)
        # print(req.status)

        # response = requests.get(mod_url, headers=headers) ('User-agent', 'Mozilla/5.0')
        # print(response.status_code)
        # if response.status_code == 200:
        #     print("Status: OK".ljust(35))
        # time.sleep(0.10)


if __name__ == '__main__':
    main()
