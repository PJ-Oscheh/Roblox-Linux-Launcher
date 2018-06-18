#!/bin/bash
echo "Roblox Linux Launcher setup"
if [[ $PWD == "$HOME/roblox-linux-launcher" ]]; then
echo "Already in roblox-linux-launcher"
else
echo "Creating directories..."
mkdir ~/roblox-linux-launcher
echo "Copying files..."
cp ./startChromium.sh ~/roblox-linux-launcher
cp ./startRoblox.sh ~/roblox-linux-launcher
cd ~/roblox-linux-launcher
fi
echo "This will install the following packages:"
echo "chromium-browser"
echo "wine-development"
echo "Unless they are already installed. Continue? (y/n)"
read choice
if [[ $choice == "y" ]]; then
sudo apt-get install chromium-browser
sudo apt-get install wine-development
else
echo "Abort."
exit 0
fi
echo "Making 'startChromium.sh' and 'startRoblox.sh' executable."
chmod +x ~/roblox-linux-launcher/startChromium.sh
chmod +x ~/roblox-linux-launcher/startRoblox.sh
echo "Move 'roblox' to '/usr/bin/' and make it executable? This will allow you to run Roblox from any directory. (y/n)"
read choice2
if [[ $choice2 == "y" ]]; then
sudo cp ./roblox /usr/bin/
sudo chmod +x /usr/bin/roblox
echo "Done!"
else
echo "Roblox hasn't been added to '/usr/bin'. Please run 'startChromium' from '~/roblox-linux-launcher'"
echo "Done!"
exit 0
fi