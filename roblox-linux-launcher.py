#Roblox Linux Launcher - play Roblox on Linux!
#You will need Google Chrome or Brave  for this to work. Because we need to log console output using a launch flag, and we can use this to pull our Roblox Launch Arugment.
#There is no need to sign into Chrome if you don't want to.
#After selecting a game, the browser will close. Logging will not be enabled for future general Chrome sessions - it only gets enabled in Roblox Linux Launcher.
import os
import time
import threading
import logging
import sys
from sys import version_info
from sys import argv 
from distutils import spawn

#Create a log file local to the module.
current_module = sys.modules[__name__]
moduledir=os.path.dirname(current_module.__file__)
logfile=os.path.join(moduledir, 'robloxLauncher.log')
print('Check logfile: ' + logfile)

logger = logging.getLogger(__name__)
logging.basicConfig(filename=logfile, filemode='w', level=logging.DEBUG)

#Log all unhandled exceptions
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        # call the default excepthook saved at __excepthook__
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_unhandled_exception

class Browser:
  def __init__(self, p, exe, l, i):
    self.pgrep_pattern = p
    self.browser_exe = exe
    self.log_location = l
    self.invocation = i
  def __str__(self):
    return self.pgrep_pattern

BRAVE = Browser("brave", "brave-browser", "~/.config/BraveSoftware/Brave-Browser/chrome_debug.log",
        'brave-browser --app --window-size=1280,720 --enable-logging https://www.roblox.com'
        )
CHROME = Browser("chrome", "google-chrome-stable", "~/.config/google-chrome/chrome_debug.log",
        'google-chrome-stable --app=https://www.roblox.com --window-size=1280,720 --enable-logging'
        )
CHROMIUM = Browser("chromium", "chromium", "~/.config/chromium/chrome_debug.log",
        'chromium --app=https://www.roblox.com --window-size=1280,720 --enable-logging'
        )

browser_list = [BRAVE, CHROME, CHROMIUM]
launcher_name = argv[0]

def launcher_help():
    print("All browses are supported when " + launcher_name +
        " is selected as the roblox opening application.")
    print("Valid browses for independent invocation are: " +
        str([str(webb) for webb in browser_list]))
    print("Execute examples:")
    print("To execute the default browser: $ "+launcher_name)
    print("To execute the brave browser: $ "+launcher_name + " " +
            BRAVE.pgrep_pattern)

browser = None
robloxData = None

if len(argv) == 2:
    robloxArg = argv[1]
    if robloxArg.startswith("roblox-player:"):
        robloxData=robloxArg
    else:
        web_browser_type = argv[1]
        for web_browser in browser_list:
            if web_browser.pgrep_pattern == web_browser_type:
                browser = web_browser;
                break;

        if browser is None:
            print("Invalid browser selected: " + web_browser_type)
            launcher_help()
            quit()
else:
    browser = CHROME

if robloxData is None:
    if (not spawn.find_executable(browser.browser_exe)):
        print("Executable does not exist: "+browser.browser_exe);
        launcher_help()
        quit()

home = os.getenv("HOME")
rll_version="1.0-alpha"
wineprefix = os.getenv("WINEPREFIX",f"{home}/.wine")
if os.path.isfile(wineprefix) == False:
  logging.critical("WINE does not exist: " + wineprefix)
  quit()

def getRobloxVersion(): #Roblox version strings seem to be random. To check if Roblox has updated, we see if any new directories have been created. If they have, make that the current directory.
    if os.path.isfile(f"{home}/roblox-linux-launcher/versions.txt") == False:
        print("versions.txt doesn't exist. Generating...")
        os.mkdir(f"{home}/roblox-linux-launcher")
        newFile = open(f"{home}/roblox-linux-launcher/versions.txt","w")
        newFile.close()
    if os.path.isfile(f"{home}/roblox-linux-launcher/current_version.txt") == False:
        print("current_version.txt doesn't exist. Generating...")
        newFile = open(f"{home}/roblox-linux-launcher/current_version.txt","w")
        newFile.close()
    versions_folder = f"{wineprefix}/drive_c/Program Files (x86)/Roblox/Versions"
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
    chromeCheck = os.system(f"pgrep {browser.pgrep_pattern}")
    if chromeCheck != 256:
        print('Web browser is already running. It must be restarted to work with Roblox Linux Launcher. Restart the browser? (y/N)')
        choice = input('>')
        if choice.lower() == "y":
            os.system(f"pkill {browser.pgrep_pattern}")
        else:
            exit()
    checkFunction = threading.Thread(target=checkForLaunchArg)
    checkFunction.start()
    os.system(browser.invocation)
    checkFunction.join()
    
def checkForLaunchArg(): #Check for a launch argument every 1.5 seconds.
    haveLaunchArg = False
    while haveLaunchArg == False:
        time.sleep(1.5)
        log_grep = 'grep -i "roblox-player:" ' + browser.log_location
        launcharg = os.popen(log_grep).read()
        if launcharg != '':
            haveLaunchArg = True
    os.system(f"pkill {browser.pgrep_pattern}")
    launchGame(launcharg)

def launchGame(launcharg):
    current_version = open(f"{home}/roblox-linux-launcher/current_version.txt","r")
    current_version_text = current_version.read()
    current_version.close()
    trimLaunchArgStart = launcharg.find('roblox-player')
    trimLaunchArgEnd = launcharg.find('channel:')
    launcharg = launcharg[trimLaunchArgStart:(trimLaunchArgEnd+8)]
    print(f"Launch Arg: {launcharg}")
    print(f"Current Version Text: {current_version_text}")
    os.system(f'wine "{current_version_text}/RobloxPlayerLauncher.exe" {launcharg}')


print(f"Roblox Linux Launcher {rll_version}")
print('IMPORTANT:When prompted to open with "xdg-open" select "Open". We suggest checking the box to enable this by default.')
getRobloxVersion()
if robloxData is not None:
  launchGame(robloxData)
else:
  openRobloxSite()
