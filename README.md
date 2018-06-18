# Roblox-Linux-Launcher
Launch Roblox on Linux (maybe one day?)

Currently, this application works as expected; however, you are immediatly kicked from the server. I'll be investigating this issue and hopefully find a way to solve it.
To use this, run `startChromium.sh`. This will start Chromium and, when it exits, find the Roblox launch protocol (which contains the placeId, browser tracker, etc.) and apply it to `startRoblox.sh`. This only works on version `93d53bf391334501` but can easily work with newer versions by changing the string of the path to the Roblox executable in `startRoblox.sh`. (I made this kinda quick, but I plan to make it work universally in the future. I'm focused on getting the core features complete.)

This program requires `chromium-browser` and `wine`. (I tested with the development branch)

lol I'm just a fello trying to play [Phantom Forces](https://www.roblox.com/games/292439477/Phantom-Forces) on linux
