Basically a simple python script which does tiling on any windowmanager (Perfectly on pekwm and openbox. Partly on compiz due to the fact that compiz says it has a single desktop even if there are 4 virtual desktops, which means all the windows you have will be tiled).
It uses wmctrl to get the info and manage the windows. Bind it to a key or to autowhatever-on-window-creation-hook.

Currently options are
simple 		- The basic tiling layout . 1 Main + all other at the side.
left,right 	- Does the new windows7 ish style of sticking to the sides.
swap 		- Will swap the active window to master column
cycle 		- Cycle all the windows in the master pane
vertical 	- Simple vertical tiling
horizontal 	- Simple horizontal tiling
maximize 	- Maximize the active window/ for openbox which doesn't permit resizing of max windows
max_all 	- Maximize all windows

On first run it will create a config file ~/.stilerrc. Modify the values to suit your window decorations/Desktop padding. 

If you need other layouts modify get_simple_tile 
