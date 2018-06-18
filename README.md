# Roblox-Linux-Launcher
Launch Roblox on Linux
Currently, this application works as expected, but you are immediatly kicked from the server. I'll be investigating this issue and hopefully find a way to solve it.
To use this, run `startChromium.sh`. This will start Chromium and, when it exits, find the Roblox launch protocol (which contains the placeId, browser tracker, etc.) and apply it to `startRoblox.sh`. This only works on version `93d53bf391334501` but can easily work with newer ones by changing the string in `startRoblox.sh`. (I made this kinda quick, but I plan to make it work universally in the future. I'm focused on getting the core features complete.)
