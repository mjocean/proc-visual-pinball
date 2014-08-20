proc-visual-pinball
===================
An updated/maintained version of 'register_vpcom' a Visual Pinball to P-ROC "COM Bridge" to enable the use of PyProcGame/P-ROC game development against a virtual table composed in Visual Pinball.  In short, this provides a P-ROC-less and pinball-machine-less path to  PyProcGame development, simulation, and testing.  This is for Windows only, as that's the only place Visual Pinball works.

All credit should goes to destruk, Gerry Stellenberg and Adam Preble for creating the original version; all I'm doing is trying to keep it current.  The basic idea is to make this option better for folks doing pyprocgame development using VP to test imperfect code.  In this latest version you should have to make fewer changes to the VBScript in a VP table for this to work, error logging is greatly improved, and VP will display a dialog box when Python code fails instead of failing silently.

For questions, general discussion, and such, head to:
http://www.pinballcontrollers.com/forum/index.php?board=23.0

There are some tips at the bottom of this page.  NOTE: System 11 and Data East games are a bit harder to get working in VP, but have been done successfully in several instances.

-- MOcean


Changes: 
-----
* 8.12.2014:
    0. Fixed some bugs that were still preventing full stack traces to be logged 
        on "initialization time" failures
* 8.03.2014:
    0. Full stack traces will be logged on "initialization time" failures
* 5.30.2014:
    0. Added the ability to track if the game has crashed and respond to successive COM
        calls with a COMException so that Visual Pinball will show a dialog box on Python
        failure, and the dialog actually tells you where in the Python the code crashed.
    1. Fixed the formatting on the logged stack trace on failure. 
* 5.25.2014:
    0. Switches to the directory that contains the game prior to running.  Without this
       you might have needed a lot of changes to your game code to not use '.' in paths
    1. Better logging throughout.  Anything in the PyProcGame side that causes 
       the game code to crash at any point (from init to execution) will now add an
       exception into the log file.  This makes debugging possible
            TIP: use the MinGW command 'tail' to monitor your log as you execute!
                For me this is: tail -f /c/P-ROC/shared/log.txt 
    2. added an optional second arg to Run --apparently some tables send it and
       I don't know why.  Ignoring it is safe.
    3. Removed the separate init path for CCC -- epthegeek changed his code a while back
       such that this is no longer required
* 01.03.2013:
    1.  Added another SetMech interface/method with three args so fewer VP tables 
    need to be editted before running
    2.  Some hacks are in the code with very alpha support for Mechs in T2 (which are 
    supported in the simulator files (t2.cpp) in PinMame);  Check setMech and getMech

How to guide (for CCC, as an example):
====
basic installation stuff
----
1. Use Compy's One-Click P-ROC development Environment installer @ http://www.pinballcontrollers.com/forum/index.php?topic=626.0
2. Install Visual Pinball v9.14 (http://www.pinballcontrollers.com/wiki/Pyprocgame_vp ; follow from "Install Visual Pinball (Available on vpforums.org in the Getting Started menu)." to the end of that section -- note you will need to install the scripts and such).
3. Get the Python code for the game you want to play --e.g., Cactus Canyon Continued, Judge Dredd, etc. -- and unzip it into a directory under c:\P-ROC\games.  You'll need to make sure you have all the DMD and audio assets, too.  Example: In the case of CCC you'll  have your game here:

    c:\P-ROC\games\cactuscanyon

register_vpcom.py stuff:
---
4. Get/run the PythonWin32 installer (this allows Python code to run as a COM object) 
   http://sourceforge.net/projects/pywin32/files/pywin32/Build216/pywin32-216.win32-py2.6.exe/download
5. Copy the register_vpcom.py file available from this GitHub repo into c:\P-ROC\tools
6. On the command line: (to get a command line, you can always use [win]+[R], "cmd", [enter]) 

Code:

    cd \P-ROC\
    python tools\register_vpcom.py --register

(you might be able to just double-click the register_vpcom.py, but I haven't tested how this changes path expectations)  

it will ask for elevation of privledge.  Allow it.

Config changes to your P-ROC settings to use the Visual Pinball/ Virtual P-ROC bridge:
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
(feel free to omit my over-the-top comments, I find these things helpful)
*Get/edit the .vpt file:*
9. Go to vpforums.org, register, and download a Visual Pinball table (.vpt) for the game you want to run.  For Example, for Cactus Canyon I recommend this one: CactusCanyon_1-1_Sun9.vpt 
and place the vpt in c:\P-ROC; location should not matter, if your config files are in the right places.
10. Run Visual Pinball as administrator!!  I can't stress that enough...
11. Open the vpt file and edit the script (button on the left).  Find the line: 

    Set Controller = CreateObject("VPinMAME.Controller")

and change it to:
    
    Set Controller = CreateObject("VPROC.Controller")

12. Launch Cactus Canyon (or whatever) in Visual Pinball (F5) to test.

Again, always make sure you're running Visual Pinball as an Administrator otherwise you will get a python error because it won't be able to open the necessary files.  

Important tips for success:
---
0. The log file for your execution will wind up in c:\P-ROC\shared\log.txt (by default).  If you want to view your log in "real-time" while the game runs, a tool like 'tail' will help.  I use the MinGW command 'tail' to monitor your log as you execute!
                For me this is: tail -f /c/P-ROC/shared/log.txt 
1. Your Python game code should NOT use plain print() statements!  When running through the COM bridge, a print statement will cause an IOError for a bad file descriptor.  If you see that error in your log, the problem is clearly a print statement.  Change these to logging.log() instead.
2. The VPROC.Controller does not support everything the VPinMame.Controller did.  You may need to comment out some specific VBScript lines in the Visual Pinball table script.
3. In your Python/PyProcGame game code, the file that contains the definition for your "main" game class for your game (the object that extends BasicGame) must not just immediately create the object at the bottom of the file.  Instead, the object should be created in a main function, and use the if __name__ == "__main__" convention of calling the main function.  This is described, here: https://docs.python.org/2/library/__main__.html
4. System11 and Data East games are MUCH more annoying to get working due to differences in switch/lamp numbering and the ACRelay (or LRRelay in the case of DataEast).  It can be, and has been, done for several games (SoF, F14, and Earthshaker).  Contact me for help.
