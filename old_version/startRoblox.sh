#!/bin/bash
if [[ $1 == "" ]]; then
echo "No game information specified!"
else
echo "Starting Roblox"
launchArg=$1
wine ~/.wine/drive_c/"Program Files (x86)"/Roblox/Versions/version-93d53bf391334501/RobloxPlayerLauncher.exe "$launchArg"
fi
