proc-visual-pinball
===================
An updated/maintained version of 'register_vpcom' a Visual Pinball to P-ROC "COM Bridge" to enable the use of PyProcGame/P-ROC game development against a virtual table composed in Visual Pinball.  In short, this provides a P-ROC-less and pinball-machine-less path to  PyProcGame development, simulation, and testing.  This is for Windows only, as that's the only place Visual Pinball works.

All credit should goes to destruk, Gerry Stellenberg and Adam Preble for creating the original version; all I'm doing is trying to keep it current.  The basic idea is to make this option better for folks doing pyprocgame development using VP to test imperfect code.  In this latest version you should have to make fewer changes to the VBScript in a VP table for this to work, error logging is greatly improved, and VP will display a dialog box when Python code fails instead of failing silently.

Major features/additions this verions provides over the original version are:
* This bridge is no longer run as an InProc COM object; this means when you hit play on Visual Pinball it will reload everything and run fresh.  No more R6034 error messages.  Crashes in Python game code should no longer crash Visual Pinball.  You don't need to quit VP and relaunch.
* ability to load game-specific config.yaml or pyprocgame/ directories embedded in the game's directory (defaults to system-wide if not present)
* support for System-11 switch/lamp/driver renumbering using the Controller switch: Controller.Sys11 = True
* better logging throughout.  Anything in the PyProcGame side that causes the game code to crash at any point (from init to execution) will now add an exception into the log file.  This makes debugging possible
            TIP: use the MinGW command 'tail' to monitor your log as you execute!
                For me this is: tail -f /c/P-ROC/shared/log.txt 
* if the Python game crashes, raise a COMException (or respond to the next COM request with one) so Visual Pinball will show a dialog box (and the dialog indicates where in the Python the code crashed).
* changes to the directory that contains the game to support relative directories in Python game code.
* added some extra SetMech interface/methods so fewer VPT script changes are required

For questions, general discussion, and such, head to:
http://www.pinballcontrollers.com/forum/index.php?board=23.0

There are some tips at the bottom of this page.  NOTE: System 11 and Data East games are now *very* easy to get working in VP.  Very few VBScript changes to the VPT file should be required.

-- MOcean

How to guide (Try JD, as an example):
====
basic installation stuff
----
1. Use the new One-Click HD P-ROC Development Environment (+SkeletonGame) installer @ https://dl.dropboxusercontent.com/u/254844/proc-environment-installer/proc_env_installer_wHD.exe
2. Install Visual Pinball v9.14 (http://www.pinballcontrollers.com/wiki/Pyprocgame_vp ; follow from "Install Visual Pinball (Available on vpforums.org in the Getting Started menu)." to the end of that section -- note you will need to install the scripts and such).  You may need to copy the files `libgcc_s_dw2-1.dll` and `libstdc++-6.dll` into your `C:\windows\SysWOW64` folder (or System32); You may also need to swap in my build sdl2_ttf.dll, which you can download here (https://dl.dropboxusercontent.com/u/254844/proc-environment-installer/SDL2_ttf.dll)
3. Get the Python code for the game you want to play --e.g., Judge Dredd (https://github.com/preble/JD-pyprocgame). -- and unzip it into a directory under c:\P-ROC\games.  You'll need to make sure you have the "media pack" (all the DMD and audio assets), too.  Example: In the case of JD you'll  have your game here:

    c:\P-ROC\games\jd

register_vpcom.py stuff:
---
4. Get/run the PythonWin32 installer (this allows Python code to run as a COM object) 
   http://sourceforge.net/projects/pywin32/files/pywin32/Build216/pywin32-216.win32-py2.6.exe/download
5. Copy the register_vpcom.py and config.py files from this GitHub repo into c:\P-ROC\tools (you will need to make this directory)
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
9. Go to vpforums.org, register, and download a Visual Pinball table (.vpt) for the game you want to run.  For Example, Judge Dredd 
and place the vpt in c:\P-ROC; location should not matter, if your config files are in the right places.
10. Run Visual Pinball as administrator!!  I can't stress that enough...
11. Open the vpt file and edit the script (button on the left).  Find the line: 

    Set Controller = CreateObject("VPinMAME.Controller")

and change it to:
    
    Set Controller = CreateObject("VPROC.Controller")

(For VPX/Visual Pinball 10, you will instead set PROC=1)

12. 'Play' the table in Visual Pinball (F5) to test.

Again, always make sure you're running Visual Pinball as an Administrator otherwise you will get a python error because it won't be able to open the necessary files.  

Important tips for success:
---
0. The log file for your execution will wind up in c:\P-ROC\shared\log.txt (by default).  If you want to view your log in "real-time" while the game runs, a tool like 'tail' will help.  I use the MinGW command 'tail' to monitor your log as you execute!
                For me this is: tail -f /c/P-ROC/shared/log.txt 
1. You will not see plain print() statements from your python code.  ~When running through the COM bridge, a print statement will cause an IOError for a bad file descriptor.  If you see that error in your log, the problem is clearly a print statement.~  It would be better to use `logging.log()`, as those entries will be logged into the `c:\p-roc\shared\log.txt` file.  To see the print statements you will need to run (double-click) `C:\Python26\Lib\site-packages\win32\lib\win32traceutil.pyc`
2. The VPROC.Controller does not support everything the VPinMame.Controller did.  You may need to comment out some specific VBScript lines in the Visual Pinball table script.
3. In your Python/PyProcGame game code, the file that contains the definition for your "main" game class for your game (the object that extends BasicGame) must not just immediately create the object at the bottom of the file.  Instead, the object should be created in a main function, and use the `if __name__ == "__main__"` convention of calling the main function.  This is described, here: https://docs.python.org/2/library/__main__.html
4. I assume that your Python game class does not require any arguments on creation.  Many people still pass the machine type into the game constructor, but this is really unnecessary (is the machine type going to change?).  If you need to modify your game code and have questions, send me an email and I'll be happy to help.
5. System11 and Data East games were once MUCH more annoying to get working due to differences in switch/lamp numbering and the ACRelay (or LRRelay in the case of DataEast).  Now all you have to do is set Controller.Sys11 = True in the VBscript of the Visual Pinball table, and this code will automatically do the renumbering of switches, lamps and driver numbers on the ACRelay (just like VPinMame does) for you so the VPT scripts can have far fewer statements.
