echo "Starting chromium with logging enabled to pull roblox launch argument."
chromium-browser --enable-logging
launchArg=`grep -i "roblox-player:" ~/.config/chromium/chrome_debug.log | awk '{print $17}' | tr -d ["'"]`
~/roblox-linux-launcher/startRoblox.sh "$launchArg"
