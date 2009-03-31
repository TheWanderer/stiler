#!/usr/bin/python

############################################################################
# Copyright (c) 2009   unohu <unohu0@gmail.com>                            #
#                                                                          #
# Permission to use, copy, modify, and/or distribute this software for any #
# purpose with or without fee is hereby granted, provided that the above   #
# copyright notice and this permission notice appear in all copies.        #
#                                                                          #
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES #
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF         #
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR  #
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES   #
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN    #
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF  #
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.           #
#                                                                          #
############################################################################

from __future__ import with_statement
import sys
import os
import commands
import pickle
import ConfigParser

def initconfig():
    rcfile=os.getenv('HOME')+"/.stilerrc"
    if not os.path.exists(rcfile):
        cfg=open(rcfile,'w')
        cfg.write("""#Tweak these values 
[default]
BottomPadding = 0
TopPadding = 0
LeftPadding = 0
RightPadding = 0
WinTitle = 21
WinBorder = 1
MwFactor = 0.65
Monitors = 1
GridWidths = 0.50,0.67,0.33
TempFile = /tmp/tile_winlist
""")
        cfg.close()

    config=ConfigParser.RawConfigParser()
    config.read(rcfile)
    return config


def initialize():
    desk_output = commands.getoutput("wmctrl -d").split("\n")
    desk_list = [line.split()[0] for line in desk_output]

    current =  filter(lambda x: x.split()[1] == "*" , desk_output)[0].split()

    desktop = current[0]
    width =  current[8].split("x")[0]
    height =  current[8].split("x")[1]
    orig_x =  current[7].split(",")[0]
    orig_y =  current[7].split(",")[1]

    win_output = commands.getoutput("wmctrl -lG").split("\n")
    win_list = {}

    for desk in desk_list:
        win_list[desk] = map(lambda y: hex(int(y.split()[0],16)) , filter(lambda x: x.split()[1] == desk, win_output ))

    return (desktop,orig_x,orig_y,width,height,win_list)


def get_active_window():
    active_window_list = str(hex(int(commands.getoutput("xdotool getactivewindow 2>/dev/null").split()[0])))
    return filter_excluded(active_window_list) 
    
# return a list of [width,height]
def get_active_window_width_height():
    active_window = get_active_window()
    return commands.getoutput(" xwininfo -id "+active_window+" | egrep \"Height|Width\" | cut -d: -f2 | tr -d \" \"").split("\n")

# return a list of [x,y]
def get_window_x_y(windowid):
    return commands.getoutput("xwininfo -id "+windowid+" | grep 'Corners' | cut -d' ' -f5 | cut -d'+' -f2,3").split("+")

def store(object,file):
    with open(file, 'w') as f:
        pickle.dump(object,f)
    f.close()


def retrieve(file):
    try:
        with open(file,'r+') as f:
            obj = pickle.load(f)
        f.close()
        return(obj)
    except:
        f = open(file,'w')
        f.close
        dict = {}
        return (dict)


# Get all global variables
Config = initconfig()
BottomPadding = Config.getint("default","BottomPadding")
TopPadding = Config.getint("default","TopPadding")
LeftPadding = Config.getint("default","LeftPadding")
RightPadding = Config.getint("default","RightPadding")
WinTitle = Config.getint("default","WinTitle")
WinBorder = Config.getint("default","WinBorder")
MwFactor = Config.getfloat("default","MwFactor")
TempFile = Config.get("default","TempFile")
Monitors = Config.getint("default","Monitors")
CORNER_WIDTHS = map(lambda y:float(y)/Monitors,Config.get("default","GridWidths").split(","))
CENTER_WIDTHS = [1.0/Monitors,min(CORNER_WIDTHS)]

(Desktop,OrigXstr,OrigYstr,MaxWidthStr,MaxHeightStr,WinList) = initialize()
MaxWidth = int(MaxWidthStr) - LeftPadding - RightPadding
MaxHeight = int(MaxHeightStr) - TopPadding - BottomPadding
OrigX = int(OrigXstr) + LeftPadding
OrigY = int(OrigYstr) + TopPadding 
OldWinList = retrieve(TempFile)

# give the current closest width
def get_width_constant(width, width_constant_array):
    return min ( map (lambda y: [abs(y-width),y], width_constant_array))[1]

# get the next width in the width_constant_array
def get_next_width(current_width,width_array):

    active_width = float(current_width)/MaxWidth

    active_width_constant = width_array.index(get_width_constant(active_width,width_array))

    width_multiplier = width_array[(active_width_constant+1)%len(width_array)]

    return int(MaxWidth*width_multiplier)

def get_simple_tile(wincount):
    rows = wincount - 1
    layout = [] 
    if rows == 0:
        layout.append((OrigX,OrigY,MaxWidth,MaxHeight-WinTitle-WinBorder))
        return layout
    else:
        layout.append((OrigX,OrigY,int(MaxWidth*MwFactor),MaxHeight-WinTitle-WinBorder))

    x=OrigX + int((MaxWidth*MwFactor)+(2*WinBorder))
    width=int((MaxWidth*(1-MwFactor))-2*WinBorder)
    height=int(MaxHeight/rows - WinTitle-WinBorder)
    
    for n in range(0,rows):
        y= OrigY+int((MaxHeight/rows)*(n))
        layout.append((x,y,width,height))

    return layout


def get_vertical_tile(wincount):
    layout = [] 
    y = OrigY
    width = int(MaxWidth/wincount)
    height = MaxHeight - WinTitle - WinBorder
    for n in range(0,wincount):
        x= OrigX + n * width
        layout.append((x,y,width,height))

    return layout


def get_horiz_tile(wincount):
    layout = [] 
    x = OrigX
    height = int(MaxHeight/wincount - WinTitle - WinBorder)
    width = MaxWidth
    for n in range(0,wincount):
        y= OrigY + int((MaxHeight/wincount)*(n))
        layout.append((x,y,width,height))

    return layout

def get_max_all(wincount):
    layout = [] 
    x = OrigX
    y = OrigY 
    height = MaxHeight - WinTitle - WinBorder
    width = MaxWidth
    for n in range(0,wincount):
        layout.append((x,y,width,height))

    return layout



def move_active(PosX,PosY,Width,Height):
    windowid = ":ACTIVE:"
    move_window(windowid,PosX,PosY,Width,Height)


# resize and move the given window
def move_window(windowid,PosX,PosY,Width,Height):
    if windowid == ":ACTIVE:":
		window = "-r "+windowid
    else:
        window = "-i -r "+windowid

	# NOTE: metacity doesn't like resizing and moving in the same step
    # resize
    command =  " wmctrl " + window +  " -e 0,-1,-1," + str(Width) + "," + str(Height)
    os.system(command)
    # move
    command =  " wmctrl " + window +  " -e 0," + str(PosX) + "," + str(PosY)+ ",-1,-1"
    os.system(command)
    # set properties
    command = "wmctrl " + window + " -b remove,hidden,shaded"
    os.system(command)


def raise_window(windowid):
    if windowid == ":ACTIVE:":
        command = "wmctrl -a :ACTIVE: "
    else:
        command = "wmctrl -i -a " + windowid
    
    os.system(command)

def bottom():
    active = get_active_window()
    Width=get_next_width(int(get_active_window_width_height()[0]),CENTER_WIDTHS)
    Height=(MaxHeight - WinBorder)/2 - WinTitle
    PosX = get_next_posx(int(get_window_x_y(active)[0]),Width+WinBorder/2);
    PosY=MaxHeight/2+WinTitle
    move_window(active,PosX,PosY,Width,Height)
    raise_window(active)

def get_next_posx(current_x,new_width):

    PosX = 0

    if current_x < MaxWidth/Monitors:
        if new_width < MaxWidth/Monitors - WinBorder:
            PosX=LeftPadding+new_width
        else:
            PosX=LeftPadding
    else:
        if new_width < MaxWidth/Monitors - WinBorder:
            PosX=MaxWidth/Monitors+LeftPadding+new_width
        else:
            PosX=LeftPadding+MaxWidth/Monitors
        
    return PosX

def top():
    active = get_active_window()
    Width=get_next_width(int(get_active_window_width_height()[0]),CENTER_WIDTHS)
    Height=(MaxHeight -WinBorder)/2 - WinTitle
    PosX = get_next_posx(int(get_window_x_y(active)[0]),Width+WinBorder/2);
    PosY=TopPadding
    move_window(active,PosX,PosY,Width,Height)
    raise_window(active)

def middle():
    active = get_active_window()
    Width=get_next_width(int(get_active_window_width_height()[0]),CENTER_WIDTHS)
    Height=MaxHeight - WinTitle -WinBorder
    PosX = get_next_posx(int(get_window_x_y(active)[0]),Width+WinBorder/2);
    PosY=TopPadding
    move_window(active,PosX,PosY,Width,Height)
    raise_window(active)

def top_left():
    active = get_active_window()
    Width=get_next_width(int(get_active_window_width_height()[0]),CORNER_WIDTHS) - WinBorder
    Height=(MaxHeight -WinBorder)/2 - WinTitle
    PosX = get_next_posx(int(get_window_x_y(active)[0]),0);
    PosY=TopPadding
    move_window(active,PosX,PosY,Width,Height)
    raise_window(active)

def top_right():
    active = get_active_window()
    Width=get_next_width(int(get_active_window_width_height()[0]),CORNER_WIDTHS) - WinBorder
    Height=(MaxHeight -WinBorder)/2 - WinTitle
    PosX = get_next_posx(int(get_window_x_y(active)[0]),MaxWidth/Monitors-Width);
    PosY=TopPadding
    move_window(active,PosX,PosY,Width,Height)
    raise_window(active)

def bottom_right():
    active = get_active_window()
    Width=get_next_width(int(get_active_window_width_height()[0]),CORNER_WIDTHS) - WinBorder
    Height=(MaxHeight -WinBorder)/2 - WinTitle
    PosX = get_next_posx(int(get_window_x_y(active)[0]),MaxWidth/Monitors-Width);
    PosY=MaxHeight/2 + WinTitle
    move_window(active,PosX,PosY,Width,Height)
    raise_window(active)

def bottom_left():
    active = get_active_window()
    Width=get_next_width(int(get_active_window_width_height()[0]),CORNER_WIDTHS) - WinBorder
    Height=(MaxHeight -WinBorder)/2 - WinTitle
    PosX = get_next_posx(int(get_window_x_y(active)[0]),0);
    PosY=MaxHeight/2 + WinTitle
    move_window(active,PosX,PosY,Width,Height)
    raise_window(active)

def left():
    active = get_active_window()
    Width=get_next_width(int(get_active_window_width_height()[0]),CORNER_WIDTHS) - WinBorder
    Height=MaxHeight - WinTitle -WinBorder
    PosX = get_next_posx(int(get_window_x_y(active)[0]),0);
    PosY=TopPadding
    move_window(active,PosX,PosY,Width,Height)
    raise_window(active)

def right():
    active = get_active_window()
    Width=get_next_width(int(get_active_window_width_height()[0]),CORNER_WIDTHS) - WinBorder
    Height=MaxHeight - WinTitle - WinBorder 
    PosX = get_next_posx(int(get_window_x_y(active)[0]),MaxWidth/Monitors-Width);
    PosY=TopPadding
    move_window(active,PosX,PosY,Width,Height)
    raise_window(active)
    

def compare_win_list(newlist,oldlist):
    templist = []
    for window in oldlist:
        if newlist.count(window) != 0:
            templist.append(window)
    for window in newlist:
        if oldlist.count(window) == 0: 
            templist.append(window)
    return templist


def create_win_list():
    Windows = WinList[Desktop]

    if OldWinList == {}:
        pass
    else:
        OldWindows = OldWinList[Desktop]
        if Windows == OldWindows:
            pass
        else:
            Windows = compare_win_list(Windows,OldWindows)

    Windows = filter_excluded(Windows)

    return Windows


# remove windows that shouldn't be tiled
def filter_excluded(Windows):

    for win in Windows:
    	window_type = commands.getoutput("xprop -id "+win+" _NET_WM_WINDOW_TYPE | cut -d_ -f10").split("\n")[0]
        window_state = commands.getoutput("xprop -id "+win+" WM_STATE | grep \"window state\" | cut -d: -f2").split("\n")[0]
	
	if window_type == "UTILITY" or window_state == " Iconic" :
		Windows.remove(win)

    return Windows

def arrange(layout,windows):
    for win , lay  in zip(windows,layout):
        move_window(win,lay[0],lay[1],lay[2],lay[3])
    WinList[Desktop]=windows
    store(WinList,TempFile)


def simple():
    Windows = create_win_list()
    arrange(get_simple_tile(len(Windows)),Windows)
   

def swap():
    winlist = create_win_list()
    active = get_active_window()
    winlist.remove(active)
    winlist.insert(0,active)
    arrange(get_simple_tile(len(winlist)),winlist)


def vertical():
    winlist = create_win_list()
    active = get_active_window()
    winlist.remove(active)
    winlist.insert(0,active)
    arrange(get_vertical_tile(len(winlist)),winlist)


def horiz():
    winlist = create_win_list()
    active = get_active_window()
    winlist.remove(active)
    winlist.insert(0,active)
    arrange(get_horiz_tile(len(winlist)),winlist)


def cycle():
    winlist = create_win_list()
    winlist.insert(0,winlist[len(winlist)-1])
    winlist = winlist[:-1]
    arrange(get_simple_tile(len(winlist)),winlist)


def maximize():
    Width=MaxWidth
    Height=MaxHeight - WinTitle -WinBorder
    PosX=LeftPadding
    PosY=TopPadding
    move_active(PosX,PosY,Width,Height)
    raise_window(":ACTIVE:")

def max_all():
    winlist = create_win_list()
    active = get_active_window()
    winlist.remove(active)
    winlist.insert(0,active)
    arrange(get_max_all(len(winlist)),winlist)



if sys.argv[1] == "left":
    left()
elif sys.argv[1] == "right":
    right()
elif sys.argv[1] == "simple":
    simple()
elif sys.argv[1] == "vertical":
    vertical()
elif sys.argv[1] == "horizontal":
    horiz()
elif sys.argv[1] == "swap":
    swap()
elif sys.argv[1] == "cycle":
    cycle()
elif sys.argv[1] == "maximize":
    maximize()
elif sys.argv[1] == "top_left":
    top_left()
elif sys.argv[1] == "top_right":
    top_right()
elif sys.argv[1] == "top":
    top()
elif sys.argv[1] == "bottom_left":
    bottom_left()
elif sys.argv[1] == "bottom_right":
    bottom_right()
elif sys.argv[1] == "bottom":
    bottom()
elif sys.argv[1] == "middle":
    middle()
elif sys.argv[1] == "max_all":
    max_all()

