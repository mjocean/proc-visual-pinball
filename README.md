proc-visual-pinball
===================
An updated/maintained version of register_vpcom for Visual Pinball emulation support for P-ROC-less and pinball-machine-less pyprocgame simulation and testing. 

-- MOcean


All credit really goes to Gerry Stellenberg, Adam Premble, destruk, and many others
 
Changes: 
-----
* Added another (overloaded) SetMech method with three args so fewer VP tables need to be editted before running
* Some hacks are in the code with very alpha support for Mechs in T2 (which are supported in the simulator files (t2.cpp) in PinMame);  Check setMech and getMech
* Separate initilization path that detects Cactus Canyon Continued so that CCC doesn't need a re-write and VP can emulate the current version

How to guide (for CCC, as an example):
====
basic installation stuff
----
1. Use Compy's 1.1 installer @ http://www.pinballcontrollers.com/forum/index.php?topic=626.0
2. Install visual pinball (http://www.pinballcontrollers.com/wiki/Pyprocgame_vp ; follow from "Install Visual Pinball (Available on vpforums.org in the Getting Started menu).
" to the end of that section)
3. Get Cactus Canyon Continued (all of it) and unzip it into c:\P-ROC\games so you have:

    c:\P-ROC\games\cactuscanyon

register_vpcom.py stuff:
---
4. Get/run the PythonWin32 installer 
   http://sourceforge.net/projects/pywin32/files/pywin32/Build216/pywin32-216.win32-py2.6.exe/download
5. Copy the register_vpcom.py filer from here into c:\P-ROC\tools
6. On the command line: ([win]+[R], "cmd", [enter]) 

Code:
    cd \P-ROC\
    python tools\register_vpcom.py --register
  (you might be able to just double-click the register_vpcom.py, but I haven't tested how this changes path expectations)  

it will ask for elevation of privledge.  Allow it.

Config changes for Visual Pinball in P-ROC:
---
7. modify your config.yaml to ensure the following values:

Code:

    # config path is the path to machine specific YAMLs
    config_path: /P-ROC/shared/config/

    # this enables the virutual P-ROC hardware; comment it out when
    # connecting to a real machine!
    pinproc_class: procgame.fakepinproc.FakePinPROC
    
    # this is where I put my map...
    vp_game_map_file: /P-ROC/shared/vp_game_map.yaml
8. drop/merge my sample vp_game_map.yaml into \P-ROC\shared
(feel free to omit my over-the-top comments, I find these things helpful since my memory is terrible)
*Get/edit the .vpt file:*
9. Go to vpforums.org, register, and download a Cactus Canyon .vpt.  I recommend this one: CactusCanyon_1-1_Sun9.vpt 
place the vpt in c:\P-ROC; location should not matter, if your config files are in the right places.
10. Run Visual Pinball as administrator!!  I can't stress that enough...
11. Open the vpt file and edit the script (button on the left).  Find the line: 


    Set Controller = CreateObject("VPinMAME.Controller")

and change it to:
    
    Set Controller = CreateObject("VPROC.Controller")
12. Launch Cactus Canyon in Visual Pinball (F5) to test.
Again, always make sure you're running Visual Pinball as an Administrator otherwise you will get a python error because it won't be able to open the necessary files.  
