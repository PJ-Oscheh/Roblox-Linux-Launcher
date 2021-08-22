#Roblox Linux Launcher - play Roblox on Linux!
#You will need Google Chrome or Brave  for this to work. Because we need to log console output using a launch flag, and we can use this to pull our Roblox Launch Arugment.
#There is no need to sign into Chrome if you don't want to.
#After selecting a game, the browser will close. Logging will not be enabled for future general Chrome sessions - it only gets enabled in Roblox Linux Launcher.
import os
import time
import threading
import logging
import logging.config
import json
import subprocess
import sys
from sys import version_info
from sys import argv
from distutils import spawn

#Configure logging.
current_module = sys.modules[__name__]
moduledir=os.path.dirname(current_module.__file__)
logfile=os.path.join(moduledir, "robloxLauncher.log")
configLogfileName=os.path.join(moduledir, "log.cfg")

if (os.path.exists(configLogfileName)):
    logConfigFile = open(configLogfileName)
    config = json.load(logConfigFile)
    logging.config.dictConfig(config)
else:
    logging.basicConfig(level=logging.DEBUG, format="%(levelname)s %(message)s")

#Log all unhandled exceptions
def handle_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Handler for unhandled exceptions that will write to the logs"""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logging.critical("Unhandled exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_unhandled_exception
logging.info("Starting roblox launcher: " + " ".join(argv))

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
    print()
    print("All browses are supported when " + launcher_name + "\n"
        "is configured for xdg-open. xdg-open associates the url \n"
        "prefix 'roblox-player:' with an application to handle the url.")
    print("Install, test then in your browser select the roblox game play button.")
    print()
    print("Install xdg-open config: $ " + launcher_name + " install ")
    print("Test xdg-open : $ " + launcher_name + " test ")
    print("Uninstall xdg-open config: $ " + launcher_name + " uninstall ")
    print()
    print("Enable logging to file for debugging: $ " + launcher_name + " logon ")
    print("Captures and stores messages for launcher xdg-open invocation.")
    print("Disable by removing the log.cfg file.")
    print()
    print("Valid browses for invocation without configuring xdg-open: " +
    str([str(webb) for webb in browser_list]))
    print("Execute examples:")
    print("Execute the default browser: $ "+ launcher_name)
    print("Execute the brave browser: $ "+ launcher_name + " "
        + BRAVE.pgrep_pattern)

#Configure logging to file for debug. Delete the file to disable.
def logon():
    LOGGING_CONFIG=\
        {
            "version": 1,
            "disable_existing_loggers": "true",
            "formatters": {
                "simple": {
                    "format": "%(asctime)s %(levelname)s %(filename)s %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S"
                },
                "console": {
                    "format": "%(levelname)s %(message)s"
                }
            },
            "handlers": {
                "file_handler": {
                    "level": "INFO",
                    "class": "logging.handlers.RotatingFileHandler",
                    "formatter": "simple",
                    "filename": logfile,
                    "backupCount": 1,
                    "maxBytes": 2048,
                    "mode": "a",
                    "encoding": "utf8"
                },
                "console": {
                    "level": "INFO",
                    "class": "logging.StreamHandler",
                    "formatter": "console"
                }
            },
            "loggers": {},
            "root": {
                "handlers": [
                    "file_handler",
                    "console"
                ],
                "level": "DEBUG"
            }
        }
    configFile=open(configLogfileName,'w')
    configFile.write(json.dumps(LOGGING_CONFIG, indent=4))
    configFile.close()

#Create the xdg-open .desktop file and install or uninstall.
def setDesktopFile(filetype):
    desktopFile=os.path.join(moduledir, "robloxlinux-launcher.desktop")
    if (filetype == "install"):
        desktopData="[Desktop Entry]\nVersion=1.0\n" \
          + "Type=Application\nName=Roblox Player\nNoDisplay=true\n" \
          + "Comment=Roblox Game Launcher\n" \
          + "MimeType=x-scheme-handler/roblox-player;\nCategories=Game;\n" \
          + "Exec=/opt/game/Roblox-Linux-Launcher/runRoblox.py\n"
        print("Installing " + desktopFile)
        with open(desktopFile, 'w') as file:
            file.write(desktopData)
        os.system("xdg-desktop-menu install " + desktopFile)
        os.system("xdg-mime default " \
          + "robloxlinux-launcher.desktop x-scheme-handler/roblox-player")
    else:
        #uninstall
        if os.path.exists(desktopFile):
          os.system("xdg-desktop-menu uninstall " + desktopFile)
          os.remove(desktopFile)
        else:
          print("The desktop file is not installed.")

browser = None
robloxData = None

home = os.getenv("HOME")
rll_version="1.0-alpha"
wineprefix = os.getenv("WINEPREFIX",f"{home}/.wine")
if os.path.isdir(wineprefix) == False:
    logging.critical("WINE does not exist: " + wineprefix)
    quit()

versions_folder = f"{wineprefix}/drive_c/Program Files (x86)/Roblox/Versions"
if os.path.isdir(versions_folder) == False:
    logging.critical("Roblox is not installed: " + versions_folder)
    quit()

def getRobloxVersion(): #Roblox version strings seem to be random. To check if Roblox has updated, we see if any new directories have been created. If they have, make that the current directory.
    logging.info("Checking Roblox version.")
    if os.path.isfile(f"{home}/roblox-linux-launcher/versions.txt") == False:
        logging.info("versions.txt doesn't exist. Generating...")
        os.mkdir(f"{home}/roblox-linux-launcher")
        newFile = open(f"{home}/roblox-linux-launcher/versions.txt","w")
        newFile.close()
    if os.path.isfile(f"{home}/roblox-linux-launcher/current_version.txt") == False:
        logging.info("current_version.txt doesn't exist. Generating...")
        newFile = open(f"{home}/roblox-linux-launcher/current_version.txt","w")
        newFile.close()
    versions_folder_entries = (os.listdir(versions_folder))
    all_versions = open(f"{home}/roblox-linux-launcher/versions.txt","r")
    all_text = all_versions.read()
    all_versions.close()

    for i in range(len(versions_folder_entries)):


        if os.path.isdir(f"{versions_folder}/{versions_folder_entries[i]}") == True:
            if f"{versions_folder}/{versions_folder_entries[i]}" not in all_text:
                logging.info(f"New Version Found: {versions_folder_entries[i]}")
                all_versions = open(f"{home}/roblox-linux-launcher/versions.txt","a")
                all_versions.write(f"{versions_folder}/{versions_folder_entries[i]}\n")
                all_versions.close()
                current_version = open(f"{home}/roblox-linux-launcher/current_version.txt","w")
                current_version.write(f"{versions_folder}/{versions_folder_entries[i]}")
                current_version.close()
                logging.info(f"{versions_folder_entries[i]} is now the current version.")

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
    logging.info(f"Launch Arg: {launcharg}")
    logging.info(f"Current Version Text: {current_version_text}")
    os.system(f'wine "{current_version_text}/RobloxPlayerLauncher.exe" {launcharg}')

if len(argv) == 2:
    robloxArg = argv[1]
    if robloxArg.startswith("roblox-player:"):
        #either a roblox game or our xdg-open test
        robloxData=robloxArg
    elif robloxArg == "install" or robloxArg == "uninstall":
        #turn on xdg output
        os.environ["XDG_UTILS_DEBUG_LEVEL"] = "2"
        #Install mimetype handler config ie .desktop file
        if robloxArg == "install":
            setDesktopFile("install")
        else:
            setDesktopFile("uninstall")
        os.environ["XDG_UTILS_DEBUG_LEVEL"] = "0"
        quit()
    elif robloxArg == "logon":
        #setup logging output log file.
        logon()
        quit()
    elif robloxArg == "test":
        #test xdg-open operation for roblox url.
        os.environ["XDG_UTILS_DEBUG_LEVEL"] = "2"
        cmd = "xdg-open roblox-player:test"
        logging.info("Run: " + cmd)
        os.system(cmd)
        logging.info("Test end. (previous message should say success.)")
        os.environ["XDG_UTILS_DEBUG_LEVEL"] = "0"
        quit()
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

print(f"Roblox Linux Launcher {rll_version}")
print('IMPORTANT:When prompted to open with "xdg-open" select "Open". We suggest checking the box to enable this by default.')
getRobloxVersion()

if robloxData is not None:
    if robloxArg.startswith("roblox-player:test"):
        logging.info("xdg-open test success! You do not need to run this script again,\n"
            + "    xdg-open will execute it from your browser.\n"
            + "    Just press play for the roblox game in your browser.")
    else:
        logging.info("Launching roblox. Please wait.")
        launchGame(robloxData)
else:
    if (spawn.find_executable(browser.browser_exe)):
        #Check if robloxlinux-launcher.desktop is installed.
        launcherfile=os.path.join(moduledir, "robloxlinux-launcher.desktop")
        if (os.path.exists(configLogfileName)):
            logging.error("Configuration is for xdg-open. No need to execute " + launcher_name + ",\n"
                    + "just press the play button for the game on the roblox site.\n"
                    + "Else uninstall the xdg config: " + launcher_name + " uninstall")
            quit()
        #open browser, check browser log for roblox data, launch roblox.
        logging.info("Opening roblox site.")
        openRobloxSite()
    else:
        logging.error("Executable does not exist: "+browser.browser_exe);
        launcher_help()

# vim: tabstop=4 shiftwidth=4 expandtab:
