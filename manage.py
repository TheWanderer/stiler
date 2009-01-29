#!/usr/bin/python
import sys
import os
import commands

BottomPadding = 0
TopPadding = 0
LeftPadding = 0
RightPadding = 0
WinTitle = 21
WinBorder = 1

def get_desktop():
    output = commands.getoutput("wmctrl -d").split("\n")
    current =  filter(lambda x: x.split()[1] == "*" , output)[0].split()
    print current
    desktop = current[0]
    width =  current[8].split("x")[0]
    height =  current[8].split("x")[1]
    orig_x =  current[7].split(",")[0]
    orig_y =  current[7].split(",")[1]
    return (desktop,orig_x,orig_y,width,height)

(DESKTOP,OrigXstr,OrigYstr,MaxWidthStr,MaxHeightStr) = get_desktop()
MaxWidth = int(MaxWidthStr) - LeftPadding - RightPadding
MaxHeight = int(MaxHeightStr) - TopPadding - BottomPadding
OrigX = int(OrigXstr) + LeftPadding
OrigY = int(OrigYstr) + TopPadding 

MwFactor = 0.5

def get_windows(desktop):
    output = commands.getoutput("wmctrl -lG").split("\n")
    return filter(lambda x: x.split()[1] == desktop, output )

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

def move_active(PosX,PosY,Width,Height):
  command =  " wmctrl -r :ACTIVE: -e 0," + str(PosX) + "," + str(PosY)+ "," + str(Width) + "," + str(Height)
  os.system(command)

def move_window(windowid,PosX,PosY,Width,Height):
  command =  " wmctrl -i -r " + windowid +  " -e 0," + str(PosX) + "," + str(PosY)+ "," + str(Width) + "," + str(Height)
  print command
  os.system(command)
  command = "wmctrl -i -r " + windowid + " -b remove,hidden,shaded"
  print command
  os.system(command)

def left():
    Width=MaxWidth/2-1
    Height=MaxHeight
    PosX=0
    PosY=0
    move_active(PosX,PosY,Width,Height)

def right():
    Width=MaxWidth/2-1
    Height=MaxHeight
    PosX=MaxWidth/2
    PosY=0
    move_active(PosX,PosY,Width,Height)

def simple():
    Windows = get_windows(DESKTOP)
    WinCount = len(Windows)
    Layout =   get_simple_tile(WinCount)

    for n in range(0,WinCount):
        window = Windows[n].split()[0]
        x = Layout[n][0]
        y = Layout[n][1]
        w = Layout[n][2]
        h = Layout[n][3]
        move_window(window,x,y,w,h)

    

if sys.argv[1] == "left":
    left()
elif sys.argv[1] == "right":
    right()
elif sys.argv[1] == "simple":
    simple()


