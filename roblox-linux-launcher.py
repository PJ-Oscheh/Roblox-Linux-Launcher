#Roblox Linux Launcher - play Roblox on Linux!
#You will need Google Chrome (not Chromium!) for this to work. This is because Chrome can log console output using a launch flag, and we can use this to pull our Roblox Launch Arugment.
#There is no need to sign into Chrome if you don't want to.
#After selecting a game, Chrome will close. Logging will not be enabled for future general Chrome sessions - it only gets enabled in Roblox Linux Launcher.
import os
import time
import threading

home = os.getenv("HOME")

rll_version="1.0-alpha"

def getRobloxVersion(): #Roblox version strings seem to be random. To check if Roblox has updated, we see if any new directories have been created. If they have, make that the current directory.
    if os.path.isfile(f"{home}/roblox-linux-launcher/versions.txt") == False:
        print("versions.txt doesn't exist. Generating...")
        newFile = open(f"{home}/roblox-linux-launcher/versions.txt","w")
        newFile.close()
    if os.path.isfile(f"{home}/roblox-linux-launcher/current_version.txt") == False:
        print("current_version.txt doesn't exist. Generating...")
        newFile = open(f"{home}/roblox-linux-launcher/current_version.txt","w")
        newFile.close()
    versions_folder = f"{home}/.wine/drive_c/Program Files (x86)/Roblox/Versions"
    versions_folder_entries = (os.listdir(versions_folder))
    all_versions = open(f"{home}/roblox-linux-launcher/versions.txt","r")
    all_text = all_versions.read()
    all_versions.close()

    for i in range(len(versions_folder_entries)):
        

        if os.path.isdir(f"{versions_folder}/{versions_folder_entries[i]}") == True:
            if f"{versions_folder}/{versions_folder_entries[i]}" not in all_text:
                print(f"New Version Found: {versions_folder_entries[i]}")
                all_versions = open(f"{home}/roblox-linux-launcher/versions.txt","a")
                all_versions.write(f"{versions_folder}/{versions_folder_entries[i]}\n")
                all_versions.close()
                current_version = open(f"{home}/roblox-linux-launcher/current_version.txt","w")
                current_version.write(f"{versions_folder}/{versions_folder_entries[i]}")
                current_version.close()
                print(f"{versions_folder_entries[i]} is now the current version.")

def openRobloxSite():
    chromeCheck = os.system('pgrep chrome')
    if chromeCheck != 256:
        print('Google Chrome is already running. It must be restarted to work with Roblox Linux Launcher. Restart Chrome? (y/N)')
        choice = input('>')
        if choice.lower() == "y":
            os.system('killall chrome')
        else:
            exit()
    checkFunction = threading.Thread(target=checkForLaunchArg)
    checkFunction.start()
    os.system('google-chrome-stable --app=https://www.roblox.com --window-size=1280,720 --enable-logging')
    checkFunction.join()
    
def checkForLaunchArg(): #Check for a launch argument ever 1.5 seconds.
    haveLaunchArg = False
    while haveLaunchArg == False:
        time.sleep(1.5)
        launcharg = os.popen('grep -i "roblox-player:" ~/.config/google-chrome/chrome_debug.log').read()
        if launcharg != '':
            haveLaunchArg = True
    os.system('killall chrome')
    launchGame(launcharg)

def launchGame(launcharg):
    current_version = open(f"{home}/roblox-linux-launcher/current_version.txt","r")
    current_version_text = current_version.read()
    current_version.close()
    launcharg = launcharg[81:-72]
    print(f"Launch Arg: {launcharg}")
    print(f"Current Version Text: {current_version_text}")
    os.system(f'wine "{current_version_text}/RobloxPlayerLauncher.exe" {launcharg}')


print(f"Roblox Linux Launcher {rll_version}")
print('IMPORTANT:When prompted to open with "xdg-open" select "Open". We suggest checking the box to enable this by default.')
getRobloxVersion()
openRobloxSite()